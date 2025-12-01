from fastapi import APIRouter, Depends, HTTPException, Query, Request # Import Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ... import schemas, models
from ...auth import get_current_active_user, PermissionChecker
from ...crud import crud_lights_out # Import from package init
from ...database import get_db
from ...utils.audit import audit_log # Import audit_log

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.LightsOutPatrol,
    status_code=201,
    dependencies=[Depends(PermissionChecker("patrols:perform"))],
)
@audit_log(action="CREATE", resource_type="LightsOutPatrol")
async def create_lights_out_patrol(
    patrol_in: schemas.LightsOutPatrolCreate,
    request: Request, # Added
    db: AsyncSession = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Create a new lights-out patrol record. Requires 'patrols:perform' permission.
    """
    patrol = await crud_lights_out.create_with_checks(
        db=db, patrol_in=patrol_in, patroller_id=current_user.id
    )
    return patrol


@router.get(
    "/",
    response_model=schemas.PaginatedLightsOutPatrols,
    dependencies=[Depends(PermissionChecker("patrols:view_all"))],
)
async def read_lights_out_patrols(
    request: Request,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    building_id: Optional[int] = Query(None, description="Filter patrols by building ID"),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Retrieve a list of lights-out patrol records. Requires 'patrols:view_all' permission.
    """
    patrols_data = await crud_lights_out.get_multi_filtered(
        db=db, skip=skip, limit=limit, building_id=building_id
    )
    return {"total": patrols_data["total"], "records": patrols_data["records"]}
