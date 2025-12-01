from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import crud, schemas, auth

router = APIRouter()

@router.post("/", response_model=schemas.Building, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.PermissionChecker("manage_buildings"))])
async def create_building(building: schemas.BuildingCreate, db: AsyncSession = Depends(auth.get_db)):
    db_building = await crud.crud_building.get_by_name(db, name=building.name)
    if db_building:
        raise HTTPException(status_code=400, detail="Building name already registered")
    return await crud.crud_building.create(db=db, obj_in=building)

@router.get("/", response_model=List[schemas.Building])
async def read_buildings(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(auth.get_db)):
    # Remove crud.crud_building.get_multi calls if custom implementation is required or ensure get_multi works.
    # CRUDBase has get_multi. But schemas.Building expects 'id'.
    # If get_multi returns SQLAlchemy models, Pydantic handles it.
    buildings = await crud.crud_building.get_multi(db, skip=skip, limit=limit)
    return buildings

@router.get("/{building_id}", response_model=schemas.Building)
async def read_building(building_id: int, db: AsyncSession = Depends(auth.get_db)):
    # Ensure id is treated as int if model says so
    db_building = await crud.crud_building.get(db, id=building_id)
    if db_building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    return db_building

@router.get("/full-tree/", response_model=List[schemas.BuildingWithRooms])
async def read_full_tree(db: AsyncSession = Depends(auth.get_db)):
    """
    Retrieve a full tree of all buildings, rooms, and beds.
    """
    full_tree = await crud.crud_building.get_full_tree(db)
    return full_tree

@router.put("/{building_id}", response_model=schemas.Building, dependencies=[Depends(auth.PermissionChecker("manage_buildings"))])
async def update_building(
    building_id: int,
    building_in: schemas.BuildingCreate,
    db: AsyncSession = Depends(auth.get_db)
):
    db_building = await crud.crud_building.get(db, id=building_id)
    if db_building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    return await crud.crud_building.update(db=db, db_obj=db_building, obj_in=building_in)

@router.delete("/{building_id}", dependencies=[Depends(auth.PermissionChecker("manage_buildings"))])
async def delete_building(building_id: int, db: AsyncSession = Depends(auth.get_db)):
    db_building = await crud.crud_building.get(db, id=building_id)
    if db_building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    await crud.crud_building.remove(db=db, id=building_id)
    return {"ok": True}