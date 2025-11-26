import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi import Request # Add Request import
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from fastapi.responses import StreamingResponse
from datetime import datetime
from fastapi.concurrency import run_in_threadpool # Import run_in_threadpool

from ... import schemas, models
from ...crud import crud_inspection as crud_inspection_module, crud_user, crud_dorm # Import crud_dorm
from ...services.pdf_service import generate_inspection_pdf # Import the new service
from ...services.auth_service import AuthService, get_auth_service # 新增 AuthService 相關導入
from ...services.inspection_service import InspectionService, get_inspection_service # 新增 InspectionService 相關導入
from ...services.notification_service import notification_service # 新增 NotificationService 相關導入
from ...auth import get_current_active_user, PermissionChecker # 引入 get_current_active_user, PermissionChecker
from ...utils.audit import audit_log # Import audit_log

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/batch", response_model=List[schemas.InspectionRecord], status_code=status.HTTP_201_CREATED, dependencies=[Depends(PermissionChecker("inspections:submit"))])
@audit_log(action="BATCH_CREATE", resource_type="InspectionRecord")
async def batch_create_inspections(
    *,
    request: Request,
    inspection_service: InspectionService = Depends(get_inspection_service),
    batch_in: schemas.BatchInspectionCreate,
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Batch create inspection records.
    """
    inspector_id = current_user.id
    return await inspection_service.batch_create_inspection_reports(
        batch_in=batch_in,
        inspector_id=inspector_id
    )

@router.post("/", response_model=schemas.InspectionRecord, status_code=status.HTTP_201_CREATED, dependencies=[Depends(PermissionChecker("inspections:submit"))])
@audit_log(action="CREATE", resource_type="InspectionRecord")
async def create_inspection(
    *,
    request: Request, # Added Request
    inspection_service: InspectionService = Depends(get_inspection_service),
    inspection_in: schemas.InspectionCreate, # 這裡使用 InspectionCreate 來自 schemas
    current_user: models.User = Depends(get_current_active_user) # 使用 AuthService
):
    """
    Create new inspection record.
    """
    try:
        target_student_id = None
        
        # 1. Determine Target Student
        if inspection_in.student_id:
            # Admin/Inspector submitting for someone else
            target_student_id = inspection_in.student_id
        elif current_user.student:
            # Student submitting for themselves
            target_student_id = current_user.student.id
        else:
            raise HTTPException(status_code=400, detail="No student identified for this inspection.")

        # 2. Fetch Student Data to validate and get Room
        db_student = await crud_dorm.get_student(inspection_service.db, target_student_id)
        if not db_student:
            raise HTTPException(status_code=404, detail="Student not found.")

        # 3. Determine/Validate Room
        if inspection_in.room_id is None:
            if db_student.bed and db_student.bed.room:
                inspection_in.room_id = db_student.bed.room.id
            else:
                 raise HTTPException(status_code=400, detail="Student is not assigned to a room, and no room_id provided.")
        
        inspector_id = current_user.id
        
        record = await inspection_service.create_inspection_report(
            inspection_in=inspection_in,
            student_id=target_student_id,
            inspector_id=inspector_id,
        )
        return record
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating inspection: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/search", response_model=schemas.PaginatedInspectionRecords, dependencies=[Depends(PermissionChecker("inspections:view"))])
async def search_inspections(
    inspection_service: InspectionService = Depends(get_inspection_service),
    student_name: Optional[str] = None,
    room_number: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Advanced search for inspection records.
    """
    paginated_results = await crud_inspection_module.search_inspections(
        inspection_service.db,
        student_name=student_name,
        room_number=room_number,
        start_date=start_date,
        end_date=end_date,
        status=status,
        skip=skip,
        limit=limit,
    )
    return paginated_results

@router.get("/", response_model=schemas.PaginatedInspectionRecords)
async def read_inspections(
    inspection_service: InspectionService = Depends(get_inspection_service),
    current_user: models.User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    student_id: Optional[uuid.UUID] = None,
    room_id: Optional[int] = None,
    status: Optional[schemas.InspectionStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    student_full_name: Optional[str] = None,
    item_status: Optional[schemas.ItemStatus] = None,
    sort_by: Optional[str] = "created_at",
    sort_direction: Optional[str] = "desc"
):
    """
    Retrieve inspection records with advanced filtering.
    - Users with 'view_all_records' get all records.
    - Others get only their own records.
    """
    # Check permissions from pre-loaded user data (avoid lazy loading)
    has_view_all = any(perm.name == "view_all_records" for role in current_user.roles for perm in role.permissions)
    
    paginated_results: dict
    if has_view_all:
        paginated_results = await crud_inspection_module.get_inspection_records(
            inspection_service.db,
            skip=skip,
            limit=limit,
            student_id=student_id,
            room_id=room_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            student_full_name=student_full_name,
            item_status=item_status,
            sort_by=sort_by,
            sort_direction=sort_direction
        )
    else:
        if not current_user.student:
            # Return an empty paginated response if user is not a student
            return {"total": 0, "records": []}
            
        # Students can only view their own records, so override student_id filter
        paginated_results = await crud_inspection_module.get_inspection_records_by_student(
            inspection_service.db,
            student_id=current_user.student.id,
            skip=skip,
            limit=limit
        )
    return paginated_results

@router.get("/{record_id}", response_model=schemas.InspectionRecord)
async def read_inspection(
    record_id: uuid.UUID,
    inspection_service: InspectionService = Depends(get_inspection_service),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Retrieve a single inspection record.
    - Admins can retrieve any record.
    - Students can only retrieve their own records.
    """
    record = await crud_inspection_module.get_inspection_record(inspection_service.db, record_id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Inspection record not found")
    
    # Debug permissions
    user_permissions = {perm.name for role in current_user.roles for perm in role.permissions}
    # logger.info(f"User {current_user.username} permissions: {user_permissions}")

    # Check permissions
    has_view_all = "inspections:view" in user_permissions
    
    if not has_view_all:
        if not current_user.student:
            raise HTTPException(status_code=400, detail="User is not linked to a student record.")
        if record.student_id != str(current_user.student.id): # Ensure comparison is string to string
            raise HTTPException(status_code=403, detail="Not authorized to view this record")
        
    return record

@router.put("/{record_id}", response_model=schemas.InspectionRecord, dependencies=[Depends(PermissionChecker("inspections:review"))])
@audit_log(action="UPDATE_STATUS", resource_type="InspectionRecord", resource_id_src="record_id")
async def update_inspection_status(
    record_id: uuid.UUID,
    record_in: schemas.InspectionRecordUpdate,
    request: Request, # Added Request
    current_user: models.User = Depends(get_current_active_user), # Added User
    inspection_service: InspectionService = Depends(get_inspection_service),
):
    """
    Update an inspection record's status. (Requires 'update_any_record' permission).
    """
    db_record = await crud_inspection_module.get_inspection_record(inspection_service.db, record_id=record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Inspection record not found")
    
    updated_record = await crud_inspection_module.update_inspection_record(db=inspection_service.db, db_record=db_record, record_in=record_in)
    return updated_record

@router.get("/{record_id}/pdf")
async def export_inspection_pdf(
    record_id: uuid.UUID,
    inspection_service: InspectionService = Depends(get_inspection_service),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Export an inspection record as a PDF.
    """
    record = await crud_inspection_module.get_inspection_record(inspection_service.db, record_id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Inspection record not found")

    # Check permissions from pre-loaded user data (avoid lazy loading)
    has_view_all = any(perm.name == "inspections:view" for role in current_user.roles for perm in role.permissions)
    if not has_view_all:
        if not current_user.student:
            raise HTTPException(status_code=400, detail="User is not linked to a student record.")
        if record.student_id != str(current_user.student.id):
            raise HTTPException(status_code=403, detail="Not authorized to export this record")

    buffer = await run_in_threadpool(generate_inspection_pdf, record) # Call the service function in a threadpool
    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=inspection_report_{record.id}.pdf"
    })


@router.post("/{record_id}/email", status_code=status.HTTP_200_OK, dependencies=[Depends(PermissionChecker("inspections:view"))])
@audit_log(action="EMAIL_REPORT", resource_type="InspectionRecord", resource_id_src="record_id")
async def email_inspection_report(
    record_id: uuid.UUID,
    email_request: schemas.InspectionReportEmailRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    inspection_service: InspectionService = Depends(get_inspection_service),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Email an inspection record as a PDF.
    Requires 'view_all_records' permission.
    """
    record = await crud_inspection_module.get_inspection_record(inspection_service.db, record_id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Inspection record not found")

    # Permission check (reusing logic from export_inspection_pdf)
    # Check permissions from pre-loaded user data (avoid lazy loading)
    has_view_all = any(perm.name == "inspections:view" for role in current_user.roles for perm in role.permissions)
    if not has_view_all:
        if not current_user.student:
            raise HTTPException(status_code=400, detail="User is not linked to a student record.")
        if record.student_id != str(current_user.student.id):
            raise HTTPException(status_code=403, detail="Not authorized to email this record")

    buffer = await generate_inspection_pdf(record) # Call the service function

    # Detect language
    accept_language = request.headers.get("accept-language", "en")
    lang = "zh" if "zh" in accept_language.lower() else "en"

    # Send email using notification service in background
    background_tasks.add_task(
        notification_service.send_inspection_report_email,
        to_email=email_request.recipient_email,
        student_name=record.student.full_name,
        room_number=record.room.room_number,
        pdf_content=buffer.getvalue(),
        filename=f"inspection_report_{record.id}.pdf",
        lang=lang
    )
    
    return {"message": "Inspection report emailed successfully."}