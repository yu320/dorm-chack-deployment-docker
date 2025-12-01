from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union, Optional
import uuid

from ... import schemas, auth, models
from ...crud.crud_inspection import crud_inspection # Import crud_inspection
from ...crud.crud_student import crud_student # Import crud_student
from ...crud.crud_room import crud_room # Import crud_room

router = APIRouter()

class AdminInspectionCreateRequest(schemas.BaseModel):
    target_type: str
    target_id: Union[str, int]
    details: List[schemas.InspectionDetailCreate]
    signature: Optional[str] = None

@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.PermissionChecker("inspections:submit_any"))])
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
        # Use crud_student instance
        student = await crud_student.get(db, id=uuid.UUID(request.target_id))
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        students_to_inspect.append(student)
    
    elif request.target_type == "room":
        if not isinstance(request.target_id, int):
            raise HTTPException(status_code=400, detail="Room ID must be an integer")
        # Using crud_student.get_multi_filtered to find students in room
        # Note: crud_student.get_multi_filtered returns dict {"total": x, "records": [...]}, we need list
        result = await crud_student.get_multi_filtered(db, room_id=request.target_id, limit=1000)
        students_in_room = result['records']
        students_to_inspect.extend(students_in_room)

    elif request.target_type == "household":
        if not isinstance(request.target_id, str):
            raise HTTPException(status_code=400, detail="Household name must be a string")
        # Using crud_student.get_multi_filtered to find students in household
        result = await crud_student.get_multi_filtered(db, household=request.target_id, limit=1000)
        students_in_household = result['records']
        students_to_inspect.extend(students_in_household)
        
    else:
        raise HTTPException(status_code=400, detail="Invalid target_type")

    if not students_to_inspect:
        error_detail = "No students found for the given target"
        if request.target_type == "room" and isinstance(request.target_id, int):
            room = await crud_room.get(db, id=request.target_id)
            if room:
                error_detail = f"No students found in room '{room.room_number}'"
        elif request.target_type == "household":
             error_detail = f"No students found in household '{request.target_id}'"

        raise HTTPException(status_code=404, detail=error_detail)

    # Create inspection records for all found students
    inspection_data_list = []
    
    for student in students_to_inspect:
        if not student.bed or not student.bed.room:
            continue

        # Prepare InspectionCreate object for this student
        record_in = schemas.InspectionCreate(
            student_id=student.id, # Must set student_id
            room_id=student.bed.room.id, # Must set room_id
            details=request.details, # Shared details
            signature_base64=request.signature # Shared signature (base64)
        )
        
        inspection_data_list.append((record_in, request.signature))

    if not inspection_data_list:
         raise HTTPException(status_code=400, detail="Could not create any inspection records. Ensure students are assigned to rooms.")

    # Batch create using crud_inspection instance
    created_records = await crud_inspection.batch_create(
        db=db,
        data=inspection_data_list,
        inspector_id=current_user.id
    )

    return {"message": f"Successfully created {len(created_records)} inspection records."}
