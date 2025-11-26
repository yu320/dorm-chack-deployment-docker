from fastapi import APIRouter, Depends, HTTPException, status, Request # Import Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ... import crud, schemas, auth, models # Import models
from ...utils.audit import audit_log # Import audit_log

router = APIRouter()

@router.post("/", response_model=schemas.Room, dependencies=[Depends(auth.PermissionChecker("manage_rooms"))])
@audit_log(action="CREATE", resource_type="Room")
async def create_room(room: schemas.RoomCreate, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_room = await crud.get_room_by_building_and_number(db, building_id=room.building_id, room_number=room.room_number)
    if db_room:
        raise HTTPException(status_code=400, detail="Room number already exists in this building")
    return await crud.create_room(db=db, room=room)

@router.get("/", response_model=schemas.PaginatedRooms)
async def read_rooms(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    building_id: Optional[int] = None,
    db: AsyncSession = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    rooms_data = await crud.get_rooms(db, building_id=building_id, skip=skip, limit=limit)
    return rooms_data

@router.get("/{room_id}", response_model=schemas.Room)
async def read_room(room_id: int, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)): # Add for audit log
    db_room = await crud.get_room(db, room_id=room_id)
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room

@router.put("/{room_id}", response_model=schemas.Room, dependencies=[Depends(auth.PermissionChecker("manage_rooms"))])
@audit_log(action="UPDATE", resource_type="Room", resource_id_src="room_id")
async def update_room_data(room_id: int, room_in: schemas.RoomUpdate, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_room = await crud.get_room(db, room_id=room_id)
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    return await crud.update_room(db=db, room_id=room_id, room_update=room_in)

@router.delete("/{room_id}", dependencies=[Depends(auth.PermissionChecker("manage_rooms"))])
@audit_log(action="DELETE", resource_type="Room", resource_id_src="room_id")
async def delete_room(room_id: int, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_room = await crud.get_room(db, room_id=room_id)
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    await crud.delete_room(db=db, db_room=db_room)
    return {"ok": True}
