import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Request # Import Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Optional

from ... import crud, schemas, models # Import models
from ...database import get_db
from ...auth import get_current_active_user, PermissionChecker
from ...utils.audit import audit_log # Import audit_log

router = APIRouter()

permission_checker = PermissionChecker("manage_patrol_locations")

@router.post(
    "/",
    response_model=schemas.PatrolLocation,
    status_code=201,
    dependencies=[Depends(permission_checker)],
)
@audit_log(action="CREATE", resource_type="PatrolLocation")
async def create_patrol_location(
    location_in: schemas.PatrolLocationCreate,
    request: Request, # Added
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user), # Added
):
    """
    Create a new patrol location.

    A user must have the **manage_patrol_locations** permission to use this.
    """
    location = await crud.create_patrol_location(db=db, location_in=location_in)
    return location


@router.get(
    "/",
    response_model=schemas.PaginatedPatrolLocations,
    dependencies=[Depends(permission_checker)],
)
async def read_patrol_locations(
    request: Request,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    building_id: Optional[int] = Query(None, description="Filter locations by building ID"),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Retrieve a list of patrol locations.

    Allows filtering by building.
    A user must have the **manage_patrol_locations** permission to use this.
    """
    if building_id is None:
        raise HTTPException(status_code=400, detail="building_id query parameter is required.")
    
    locations_data = await crud.get_patrol_locations_by_building(
        db=db, skip=skip, limit=limit, building_id=building_id
    )
    return locations_data

@router.get(
    "/{location_id}",
    response_model=schemas.PatrolLocation,
    dependencies=[Depends(permission_checker)],
)
async def read_patrol_location(
    location_id: uuid.UUID,
    request: Request, # Added for audit_log decorator to work
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user), # Added for audit_log decorator to work
):
    """
    Get a specific patrol location by its ID.
    """
    db_location = await crud.get_patrol_location(db, location_id=location_id)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Patrol location not found")
    return db_location


@router.put(
    "/{location_id}",
    response_model=schemas.PatrolLocation,
    dependencies=[Depends(permission_checker)],
)
@audit_log(action="UPDATE", resource_type="PatrolLocation", resource_id_src="location_id")
async def update_patrol_location(
    location_id: uuid.UUID,
    location_in: schemas.PatrolLocationUpdate,
    request: Request, # Added
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user), # Added
):
    """
    Update a patrol location.
    """
    db_location = await crud.get_patrol_location(db, location_id=location_id)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Patrol location not found")
    
    updated_location = await crud.update_patrol_location(
        db=db, db_location=db_location, location_in=location_in
    )
    return updated_location


@router.delete(
    "/{location_id}",
    response_model=schemas.PatrolLocation,
    dependencies=[Depends(permission_checker)],
)
@audit_log(action="DELETE", resource_type="PatrolLocation", resource_id_src="location_id")
async def delete_patrol_location(
    location_id: uuid.UUID,
    request: Request, # Added
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user), # Added
):
    """
    Delete a patrol location.
    """
    db_location = await crud.get_patrol_location(db, location_id=location_id)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Patrol location not found")
    
    deleted_location = await crud.delete_patrol_location(db=db, db_location=db_location)
    return deleted_location
