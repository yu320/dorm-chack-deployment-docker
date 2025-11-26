from fastapi import APIRouter, Depends, HTTPException, Query, Request # Import Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ... import crud, schemas, models # Import models
from ...database import get_db
from ...auth import get_current_active_user, PermissionChecker
from ...utils.audit import audit_log # Import audit_log

router = APIRouter()

permission_checker = PermissionChecker("lights_out_check_perform")

@router.post(
    "/",
    response_model=schemas.LightsOutPatrol,
    status_code=201,
    dependencies=[Depends(permission_checker)],
)
@audit_log(action="CREATE", resource_type="LightsOutPatrol")
async def create_lights_out_patrol(
    patrol_in: schemas.LightsOutPatrolCreate,
    request: Request, # Added
    db: AsyncSession = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Create a new lights-out patrol record.

    This endpoint records a series of lights-out checks for a specific building.
    A user must have the **lights_out_check_perform** permission to use this.
    """
    patrol = await crud.create_lights_out_patrol(
        db=db, patrol_in=patrol_in, patroller_id=current_user.id
    )
    return patrol


@router.get(
    "/",
    response_model=schemas.PaginatedLightsOutPatrols,
    dependencies=[Depends(permission_checker)],
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
    Retrieve a list of lights-out patrol records.

    Allows filtering by building.
    A user must have the **lights_out_check_perform** permission to use this.
    """
    patrols_data = await crud.get_lights_out_patrols(
        db=db, skip=skip, limit=limit, building_id=building_id
    )
    return patrols_data
