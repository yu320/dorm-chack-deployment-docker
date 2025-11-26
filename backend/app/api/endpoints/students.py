import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request # Import Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ... import crud, schemas, auth, models # Import models
from ...utils.audit import audit_log # Import audit_log

router = APIRouter()

@router.post("/", response_model=schemas.Student, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.PermissionChecker("manage_students"))])
@audit_log(action="CREATE", resource_type="Student")
async def create_student(student: schemas.StudentCreate, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_student = await crud.get_student_by_id_number(db, student_id_number=student.student_id_number)
    if db_student:
        raise HTTPException(status_code=400, detail="Student with this ID number already exists")
    return await crud.create_student(db=db, student=student)

@router.get("/", response_model=schemas.PaginatedStudents)
async def read_students(
    request: Request, # Added for audit_log decorator to work
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(auth.get_db),
    full_name: Optional[str] = None,
    student_id_number: Optional[str] = None,
    class_name: Optional[str] = None,
    gender: Optional[str] = None,
    bed_id: Optional[int] = None,
    room_id: Optional[int] = None,
    building_id: Optional[int] = None,
    household: Optional[str] = None, # Added household
    current_user: models.User = Depends(auth.get_current_active_user), # Added for audit_log decorator to work
):
    student_data = await crud.get_students(
        db,
        skip=skip,
        limit=limit,
        full_name=full_name,
        student_id_number=student_id_number,
        class_name=class_name,
        gender=gender,
        bed_id=bed_id,
        room_id=room_id,
        building_id=building_id,
        household=household # Pass household
    )
    return student_data

@router.get("/{student_id}", response_model=schemas.Student)
async def read_student(student_id: uuid.UUID, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)): # Added for audit_log decorator to work
    db_student = await crud.get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

@router.put("/{student_id}", response_model=schemas.Student, dependencies=[Depends(auth.PermissionChecker("manage_students"))])
@audit_log(action="UPDATE", resource_type="Student", resource_id_src="student_id")
async def update_student_data(student_id: str, student_in: schemas.StudentUpdate, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    try:
        student_uuid = uuid.UUID(student_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format")
    
    db_student = await crud.get_student(db, student_id=student_uuid)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return await crud.update_student(db=db, student_id=student_uuid, student_in=student_in)

@router.put("/{student_id}/assign-bed", response_model=schemas.Student, dependencies=[Depends(auth.PermissionChecker("manage_students"))])
@audit_log(action="UPDATE", resource_type="Student", resource_id_src="student_id")
async def assign_student_bed(
    student_id: str,
    bed_assignment: schemas.StudentAssignBed,
    request: Request,
    db: AsyncSession = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    try:
        student_uuid = uuid.UUID(student_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format")

    db_student = await crud.get_student(db, student_id=student_uuid)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if bed_assignment.bed_id is not None:
        db_bed = await crud.get_bed(db, bed_id=bed_assignment.bed_id)
        if not db_bed:
            raise HTTPException(status_code=404, detail="Bed not found")
        
        # Check if the bed is already occupied by another student
        existing_student_on_bed = await crud.get_student_by_bed_id(db, bed_id=bed_assignment.bed_id)
        if existing_student_on_bed and existing_student_on_bed.id != student_uuid:
            raise HTTPException(status_code=409, detail=f"Bed is already occupied by student {existing_student_on_bed.full_name}")
    
    return await crud.assign_student_to_bed(db=db, db_student=db_student, bed_id=bed_assignment.bed_id)

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth.PermissionChecker("manage_students"))])
@audit_log(action="DELETE", resource_type="Student", resource_id_src="student_id")
async def delete_student(student_id: uuid.UUID, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_student = await crud.get_student(db, student_id=student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    await crud.delete_student(db=db, db_student=db_student)
    return {"ok": True}
