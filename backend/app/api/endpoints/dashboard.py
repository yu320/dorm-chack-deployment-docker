from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List

from ... import schemas, auth
from ...crud import crud_dorm, crud_inspection

router = APIRouter()

# --- Schemas specific to this endpoint ---

class DashboardStats(BaseModel):
    total_students: int
    total_rooms: int
    inspections_today: int
    issues_found: int
    recent_inspections: List[schemas.InspectionRecord]

# --- Endpoints ---

@router.get(
    "/dashboard-stats",
    response_model=DashboardStats,
    dependencies=[Depends(auth.PermissionChecker("view_all_records"))],
)
async def get_dashboard_stats(
    db: AsyncSession = Depends(auth.get_db),
):
    """
    Get statistics for the admin dashboard.
    """
    total_students = await crud_dorm.get_students_count(db)
    total_rooms = await crud_dorm.get_rooms_count(db)
    inspections_today = await crud_inspection.get_inspections_count_today(db)
    issues_found = await crud_inspection.get_inspection_issues_count(db)
    paginated_inspections = await crud_inspection.get_inspection_records(db, limit=5)
    recent_inspections = paginated_inspections.get("records", [])

    return {
        "total_students": total_students,
        "total_rooms": total_rooms,
        "inspections_today": inspections_today,
        "issues_found": issues_found,
        "recent_inspections": recent_inspections,
    }


@router.get(
    "/dashboard-charts",
    response_model=schemas.DashboardChartData,
    dependencies=[Depends(auth.PermissionChecker("view_all_records"))],
)
async def get_dashboard_chart_data(
    db: AsyncSession = Depends(auth.get_db),
):
    """
    Retrieve data for dashboard charts.
    - Pass Rate (Pie Chart)
    - Damage Ranking (Bar Chart)
    """
    pass_rate_data = await crud_inspection.get_inspection_status_distribution(db)
    damage_ranking_data = await crud_inspection.get_damage_ranking(db, limit=5)

    return schemas.DashboardChartData(
        pass_rate=pass_rate_data,
        damage_ranking=damage_ranking_data
    )
