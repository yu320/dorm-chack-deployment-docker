from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import crud, schemas, auth

router = APIRouter()

@router.post("/", response_model=schemas.Building, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.PermissionChecker("manage_buildings"))])
async def create_building(building: schemas.BuildingCreate, db: AsyncSession = Depends(auth.get_db)):
    db_building = await crud.get_building_by_name(db, name=building.name)
    if db_building:
        raise HTTPException(status_code=400, detail="Building name already registered")
    return await crud.create_building(db=db, building=building)

@router.get("/", response_model=List[schemas.Building])
async def read_buildings(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(auth.get_db)):
    buildings = await crud.get_buildings(db, skip=skip, limit=limit)
    return buildings

@router.get("/{building_id}", response_model=schemas.Building)
async def read_building(building_id: int, db: AsyncSession = Depends(auth.get_db)):
    db_building = await crud.get_building(db, building_id=building_id)
    if db_building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    return db_building

@router.get("/full-tree/", response_model=List[schemas.BuildingWithRooms])
async def read_full_tree(db: AsyncSession = Depends(auth.get_db)):
    """
    Retrieve a full tree of all buildings, rooms, and beds.
    """
    full_tree = await crud.get_buildings_full_tree(db)
    return full_tree

@router.put("/{building_id}", response_model=schemas.Building, dependencies=[Depends(auth.PermissionChecker("manage_buildings"))])
async def update_building(
    building_id: int,
    building_in: schemas.BuildingCreate,
    db: AsyncSession = Depends(auth.get_db)
):
    db_building = await crud.get_building(db, building_id=building_id)
    if db_building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    return await crud.update_building(db=db, db_building=db_building, building_in=building_in)

@router.delete("/{building_id}", dependencies=[Depends(auth.PermissionChecker("manage_buildings"))])
async def delete_building(building_id: int, db: AsyncSession = Depends(auth.get_db)):
    db_building = await crud.get_building(db, building_id=building_id)
    if db_building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    await crud.delete_building(db=db, db_building=db_building)
    return {"ok": True}
