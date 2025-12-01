import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ... import crud, schemas, auth, models
from ...crud.crud_student import crud_student # Import the new CRUD instance
from ...utils.audit import audit_log

router = APIRouter()

@router.post("/", response_model=schemas.Student, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.PermissionChecker("manage_students"))])
@audit_log(action="CREATE", resource_type="Student")
async def create_student(student: schemas.StudentCreate, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_student = await crud_student.get_by_id_number(db, student_id_number=student.student_id_number)
    if db_student:
        raise HTTPException(status_code=400, detail="Student with this ID number already exists")
    return await crud_student.create(db=db, obj_in=student)

@router.get("/", response_model=schemas.PaginatedStudents)
async def read_students(
    request: Request,
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
    household: Optional[str] = None,
    current_user: models.User = Depends(auth.get_current_active_user),
):
    # Check permissions dynamically
    user_permissions = {perm.name for role in current_user.roles for perm in role.permissions}
    has_view_all = "students:view_all" in user_permissions or "admin:full_access" in user_permissions
    has_view_own = "students:view_own" in user_permissions

    if not (has_view_all or has_view_own):
         raise HTTPException(status_code=403, detail="Not authorized to view students")

    # If user can only view own, override filters to match their student record
    if not has_view_all:
        if not current_user.student:
             return {"total": 0, "records": []}
        
        # Override filters to only show self
        # We can use student_id_number as a unique filter or filter by ID if get_multi_filtered supports it?
        # get_multi_filtered supports many filters but not ID directly (unless we add it).
        # Let's filter by student_id_number which is unique.
        student_id_number = current_user.student.student_id_number
        # Clear other filters that might expand scope (though ID number restricts it enough)
        full_name = None
        class_name = None
        gender = None
        bed_id = None
        room_id = None
        building_id = None
        household = None

    student_data = await crud_student.get_multi_filtered(
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
        household=household
    )
    return student_data

@router.get("/{student_id}", response_model=schemas.Student)
async def read_student(student_id: uuid.UUID, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_student = await crud_student.get(db, id=student_id)
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
    
    db_student = await crud_student.get(db, id=student_uuid)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return await crud_student.update(db=db, db_obj=db_student, obj_in=student_in)

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

    db_student = await crud_student.get(db, id=student_uuid)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if bed_assignment.bed_id is not None:
        db_bed = await crud.crud_bed.get(db, id=bed_assignment.bed_id) # Corrected to use crud_bed.get
        if not db_bed:
            raise HTTPException(status_code=404, detail="Bed not found")
        
        # Check if the bed is already occupied by another student
        existing_student_on_bed = await crud_student.get_by_bed_id(db, bed_id=bed_assignment.bed_id)
        if existing_student_on_bed and existing_student_on_bed.id != str(student_uuid): # Ensure comparison works (str vs UUID)
             # str(student_uuid) because models.Student.id is CHAR(36)
            raise HTTPException(status_code=409, detail=f"Bed is already occupied by student {existing_student_on_bed.full_name}")
    
    return await crud_student.assign_bed(db=db, db_student=db_student, bed_id=bed_assignment.bed_id)

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth.PermissionChecker("manage_students"))])
@audit_log(action="DELETE", resource_type="Student", resource_id_src="student_id")
async def delete_student(student_id: uuid.UUID, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_student = await crud_student.get(db, id=student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    await crud_student.remove(db=db, id=student_id)
    return {"ok": True}
