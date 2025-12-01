from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import crud, schemas, auth
from ...crud.crud_bed import crud_bed # Import crud_bed

router = APIRouter()

@router.post("/", response_model=schemas.Bed, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.PermissionChecker("manage_beds"))])
async def create_bed(bed: schemas.BedCreate, db: AsyncSession = Depends(auth.get_db)):
    # You might want to add a check for unique bed_number within a room
    db_bed_check = await crud_bed.get_by_number(db, room_id=bed.room_id, bed_number=bed.bed_number)
    if db_bed_check:
        raise HTTPException(status_code=400, detail="Bed number already exists in this room")
    
    new_bed = await crud_bed.create(db=db, obj_in=bed)
    # Re-fetch the bed with the relationship loaded to match the response_model
    return await crud_bed.get(db=db, id=new_bed.id)

@router.get("/", response_model=schemas.PaginatedBeds)
async def read_beds(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(auth.get_db)):
    beds = await crud_bed.get_multi(db, skip=skip, limit=limit)
    total = await crud_bed.get_count(db)
    return {"total": total, "records": beds}

@router.get("/{bed_id}", response_model=schemas.Bed)
async def read_bed(bed_id: int, db: AsyncSession = Depends(auth.get_db)):
    db_bed = await crud_bed.get(db, id=bed_id)
    if db_bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")
    return db_bed

@router.put("/{bed_id}", response_model=schemas.Bed, dependencies=[Depends(auth.PermissionChecker("manage_beds"))])
async def update_bed(
    bed_id: int,
    bed_in: schemas.BedUpdate,
    db: AsyncSession = Depends(auth.get_db)
):
    db_bed = await crud_bed.get(db, id=bed_id)
    if db_bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")

    # Check for unique bed_number within the room if bed_number is being updated
    if bed_in.bed_number and bed_in.bed_number != db_bed.bed_number:
        # Use current room_id if not provided in update
        target_room_id = bed_in.room_id if bed_in.room_id else db_bed.room_id
        existing_bed_with_same_number = await crud_bed.get_by_number(db, room_id=target_room_id, bed_number=bed_in.bed_number)
        if existing_bed_with_same_number:
            raise HTTPException(status_code=400, detail="Bed number already exists in this room")

    return await crud_bed.update(db=db, db_obj=db_bed, obj_in=bed_in)

@router.delete("/{bed_id}", dependencies=[Depends(auth.PermissionChecker("manage_beds"))])
async def delete_bed(bed_id: int, db: AsyncSession = Depends(auth.get_db)):
    db_bed = await crud_bed.get(db, id=bed_id)
    if db_bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")
    await crud_bed.remove(db=db, id=bed_id)
    return {"ok": True}
