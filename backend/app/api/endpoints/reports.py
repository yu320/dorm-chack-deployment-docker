from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date
import uuid

from ... import schemas, auth
from ...crud.crud_inspection import crud_inspection
from ...utils.pdf_generator import generate_inspection_pdf_report

router = APIRouter()

@router.get("/pdf/inspections", summary="Generate PDF Report for Inspections", response_class=Response, dependencies=[Depends(auth.PermissionChecker("reports:export"))])
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
    Requires 'reports:export' permission.
    """
    inspections_data = []
    
    # Convert dates to datetime for query if needed, or let CRUD handle it (assuming CRUD takes datetime)
    # crud_inspection expects datetime
    start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
    end_dt = datetime.combine(end_date, datetime.max.time()) if end_date else None

    if report_type == "all":
        paginated_response = await crud_inspection.get_multi_filtered(
            db,
            start_date=start_dt,
            end_date=end_dt,
            limit=1000 
        )
        inspections_data = paginated_response.get("records", [])
    elif report_type == "building":
        if not building_id:
            raise HTTPException(status_code=400, detail="Building ID is required for building report type.")
        paginated_response = await crud_inspection.get_multi_filtered(
            db,
            building_id=building_id,
            start_date=start_dt,
            end_date=end_dt,
            limit=1000
        )
        inspections_data = paginated_response.get("records", [])
    elif report_type == "student":
        if not student_id:
            raise HTTPException(status_code=400, detail="Student ID is required for student report type.")
        try:
            s_uuid = uuid.UUID(student_id)
        except ValueError:
             raise HTTPException(status_code=400, detail="Invalid Student ID format.")
             
        paginated_response = await crud_inspection.get_multi_filtered(
            db,
            student_id=s_uuid,
            start_date=start_dt,
            end_date=end_dt,
            limit=1000
        )
        inspections_data = paginated_response.get("records", [])
    else:
        raise HTTPException(status_code=400, detail="Invalid report_type. Must be 'all', 'building', or 'student'.")

    if not inspections_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No inspection records found for the given criteria.")

    # Convert SQLAlchemy models to Pydantic models, then to dicts
    # Assuming generate_inspection_pdf_report takes a list of dicts
    inspections_dicts = [schemas.InspectionRecord.model_validate(inspection).model_dump() for inspection in inspections_data]

    try:
        pdf_buffer = await generate_inspection_pdf_report(inspections_dicts)
        return Response(content=pdf_buffer.getvalue(), media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate PDF: {e}")

