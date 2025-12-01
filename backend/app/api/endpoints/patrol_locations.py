import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Request # Import Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ... import schemas, models # Import models
from ...crud.crud_patrol_location import crud_patrol_location # Import new CRUD instance
from ...database import get_db
from ...auth import get_current_active_user, PermissionChecker
from ...utils.audit import audit_log # Import audit_log

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.PatrolLocation,
    status_code=201,
    dependencies=[Depends(PermissionChecker("patrol_locations:manage"))],
)
@audit_log(action="CREATE", resource_type="PatrolLocation")
async def create_patrol_location(
    location_in: schemas.PatrolLocationCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Create a new patrol location. Requires 'patrol_locations:manage' permission.
    """
    # Check for existing location with same name in same building/household
    existing_location = await crud_patrol_location.get_by_name_and_building(
        db, 
        name=location_in.name, 
        building_id=location_in.building_id, 
        household=location_in.household
    )
    if existing_location:
        raise HTTPException(status_code=400, detail="Patrol location with this name and building/household already exists.")
        
    location = await crud_patrol_location.create(db=db, obj_in=location_in)
    return location


@router.get(
    "/",
    response_model=schemas.PaginatedPatrolLocations,
    dependencies=[Depends(PermissionChecker("patrol_locations:view"))],
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
    Retrieve a list of patrol locations. Requires 'patrol_locations:view' permission.
    """
    if building_id is None:
        raise HTTPException(status_code=400, detail="building_id query parameter is required.")
    
    locations = await crud_patrol_location.get_multi_by_building(
        db=db, skip=skip, limit=limit, building_id=building_id
    )
    total = await crud_patrol_location.get_count_by_building(db=db, building_id=building_id)
    
    return {"total": total, "records": locations}

@router.get(
    "/{location_id}",
    response_model=schemas.PatrolLocation,
    dependencies=[Depends(PermissionChecker("patrol_locations:view"))],
)
async def read_patrol_location(
    location_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Get a specific patrol location by its ID. Requires 'patrol_locations:view' permission.
    """
    db_location = await crud_patrol_location.get(db, id=location_id)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Patrol location not found")
    return db_location


@router.put(
    "/{location_id}",
    response_model=schemas.PatrolLocation,
    dependencies=[Depends(PermissionChecker("patrol_locations:manage"))],
)
@audit_log(action="UPDATE", resource_type="PatrolLocation", resource_id_src="location_id")
async def update_patrol_location(
    location_id: uuid.UUID,
    location_in: schemas.PatrolLocationUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Update a patrol location. Requires 'patrol_locations:manage' permission.
    """
    db_location = await crud_patrol_location.get(db, id=location_id)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Patrol location not found")
    
    # Check for existing location with same name in same building/household if name/building_id/household is updated
    if location_in.name and location_in.name != db_location.name:
        existing_location = await crud_patrol_location.get_by_name_and_building(
            db, 
            name=location_in.name, 
            building_id=location_in.building_id if location_in.building_id else db_location.building_id,
            household=location_in.household if location_in.household else db_location.household
        )
        if existing_location and existing_location.id != db_location.id:
            raise HTTPException(status_code=400, detail="Patrol location with this name and building/household already exists.")


    updated_location = await crud_patrol_location.update(
        db=db, db_obj=db_location, obj_in=location_in
    )
    return updated_location


@router.delete(
    "/{location_id}",
    response_model=schemas.PatrolLocation, # Changed to return deleted object
    dependencies=[Depends(PermissionChecker("patrol_locations:manage"))],
)
@audit_log(action="DELETE", resource_type="PatrolLocation", resource_id_src="location_id")
async def delete_patrol_location(
    location_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Delete a patrol location. Requires 'patrol_locations:manage' permission.
    """
    db_location = await crud_patrol_location.get(db, id=location_id)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Patrol location not found")
    
    deleted_location = await crud_patrol_location.remove(db=db, id=location_id)
    return deleted_location
