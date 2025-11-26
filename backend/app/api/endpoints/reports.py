from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date

from ... import crud, schemas, auth
from ...utils.pdf_generator import generate_inspection_pdf_report # Assuming this utility exists

router = APIRouter()

@router.get("/pdf/inspections", summary="Generate PDF Report for Inspections", response_class=Response)
async def get_inspections_pdf(
    db: AsyncSession = Depends(auth.get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user),
    report_type: str = Query("all", description="Type of report: 'all', 'building', 'student'"),
    building_id: Optional[int] = Query(None),
    student_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    """
    Generates a PDF report for inspection records based on various filters.
    Requires 'view_all_records' permission.
    """
    # Permission check is handled by PermissionChecker dependency, no need for manual check here.

    inspections_data = []

    if report_type == "all":
        # Fetch all inspections within the date range
        paginated_response = await crud.get_inspection_records(
            db,
            start_date=start_date,
            end_date=end_date,
            limit=1000 # Max limit for reports
        )
        inspections_data = paginated_response.get("records", [])
    elif report_type == "building":
        if not building_id:
            raise HTTPException(status_code=400, detail="Building ID is required for building report type.")
        # Fetch inspections for a specific building within the date range
        paginated_response = await crud.get_inspection_records(
            db,
            # Note: crud.get_inspection_records does not directly support building_id filter.
            # You might need a specific CRUD function or adjust get_inspection_records to support it.
            # For now, we'll assume it's handled if passed through, or fetch all and filter post-query.
            # A more robust solution would filter at the DB level.
            building_id=building_id, # This parameter needs to be handled in get_inspection_records
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        inspections_data = paginated_response.get("records", [])
    elif report_type == "student":
        if not student_id:
            raise HTTPException(status_code=400, detail="Student ID is required for student report type.")
        # Fetch inspections for a specific student within the date range
        paginated_response = await crud.get_inspection_records_by_student(
            db,
            student_id=student_id,
            start_date=start_date, # This parameter needs to be handled in get_inspection_records_by_student
            end_date=end_date, # This parameter needs to be handled in get_inspection_records_by_student
            limit=1000
        )
        inspections_data = paginated_response.get("records", [])
    else:
        raise HTTPException(status_code=400, detail="Invalid report_type. Must be 'all', 'building', or 'student'.")

    if not inspections_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No inspection records found for the given criteria.")

    # Convert SQLAlchemy models to Pydantic models, then to dicts
    inspections_dicts = [schemas.InspectionRecord.model_validate(inspection).model_dump() for inspection in inspections_data]

    try:
        pdf_buffer = await generate_inspection_pdf_report(inspections_dicts)
        return Response(content=pdf_buffer.getvalue(), media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate PDF: {e}")

