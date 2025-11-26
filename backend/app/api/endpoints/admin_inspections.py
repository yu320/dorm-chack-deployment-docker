from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union, Optional
import uuid

from ... import crud, schemas, auth, models

router = APIRouter()

class AdminInspectionCreateRequest(schemas.BaseModel):
    target_type: str
    target_id: Union[str, int]
    details: List[schemas.InspectionDetailCreate]
    signature: Optional[str] = None

@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.PermissionChecker("create_admin_inspection"))])
async def create_admin_inspection(
    request: AdminInspectionCreateRequest,
    db: AsyncSession = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Create a new inspection as an admin.
    """
    # Logic to find students based on target_type and target_id
    students_to_inspect: List[models.Student] = []
    
    if request.target_type == "student":
        if not isinstance(request.target_id, str):
            raise HTTPException(status_code=400, detail="Student ID must be a string (UUID)")
        student = await crud.get_student(db, student_id=uuid.UUID(request.target_id))
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        students_to_inspect.append(student)
    
    elif request.target_type == "room":
        if not isinstance(request.target_id, int):
            raise HTTPException(status_code=400, detail="Room ID must be an integer")
        students_in_room = await crud.get_students_by_room(db, room_id=request.target_id)
        students_to_inspect.extend(students_in_room)

    elif request.target_type == "household":
        if not isinstance(request.target_id, str):
            raise HTTPException(status_code=400, detail="Household name must be a string")
        students_in_household = await crud.get_students_by_household(db, household=request.target_id)
        students_to_inspect.extend(students_in_household)
        
    else:
        raise HTTPException(status_code=400, detail="Invalid target_type")

    if not students_to_inspect:
        error_detail = "No students found for the given target"
        if request.target_type == "room" and isinstance(request.target_id, int):
            room = await crud.get_room(db, room_id=request.target_id)
            if room:
                error_detail = f"No students found in room '{room.room_number}'"
        elif request.target_type == "household":
             error_detail = f"No students found in household '{request.target_id}'"

        raise HTTPException(status_code=404, detail=error_detail)

    # Create inspection records for all found students
    created_records = []
    for student in students_to_inspect:
        if not student.bed or not student.bed.room:
            continue

        record_in = schemas.InspectionRecordCreate(
            details=request.details,
            signature=request.signature
        )
        record = await crud.create_inspection_record(
            db=db,
            record=record_in,
            student_id=student.id,
            room_id=student.bed.room.id
        )
        created_records.append(record)

    if not created_records:
        raise HTTPException(status_code=400, detail="Could not create any inspection records. Ensure students are assigned to rooms.")

    return {"message": f"Successfully created {len(created_records)} inspection records."}
