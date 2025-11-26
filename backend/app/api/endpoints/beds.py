from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import crud, schemas, auth

router = APIRouter()

@router.post("/", response_model=schemas.Bed, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.PermissionChecker("manage_beds"))])
async def create_bed(bed: schemas.BedCreate, db: AsyncSession = Depends(auth.get_db)):
    # You might want to add a check for unique bed_number within a room
    db_bed_check = await crud.get_bed_by_number(db, room_id=bed.room_id, bed_number=bed.bed_number)
    if db_bed_check:
        raise HTTPException(status_code=400, detail="Bed number already exists in this room")
    
    new_bed = await crud.create_bed(db=db, bed_in=bed)
    # Re-fetch the bed with the relationship loaded to match the response_model
    return await crud.get_bed(db=db, bed_id=new_bed.id)

@router.get("/", response_model=schemas.PaginatedBeds)
async def read_beds(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(auth.get_db)):
    beds_data = await crud.get_beds(db, skip=skip, limit=limit)
    return beds_data

@router.get("/{bed_id}", response_model=schemas.Bed)
async def read_bed(bed_id: int, db: AsyncSession = Depends(auth.get_db)):
    db_bed = await crud.get_bed(db, bed_id=bed_id)
    if db_bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")
    return db_bed

@router.put("/{bed_id}", response_model=schemas.Bed, dependencies=[Depends(auth.PermissionChecker("manage_beds"))])
async def update_bed(
    bed_id: int,
    bed_in: schemas.BedUpdate,
    db: AsyncSession = Depends(auth.get_db)
):
    db_bed = await crud.get_bed(db, bed_id=bed_id)
    if db_bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")

    # Check for unique bed_number within the room if bed_number is being updated
    if bed_in.bed_number and bed_in.bed_number != db_bed.bed_number:
        existing_bed_with_same_number = await crud.get_bed_by_number(db, room_id=db_bed.room_id, bed_number=bed_in.bed_number)
        if existing_bed_with_same_number:
            raise HTTPException(status_code=400, detail="Bed number already exists in this room")

    return await crud.update_bed(db=db, db_bed=db_bed, bed_in=bed_in)

@router.delete("/{bed_id}", dependencies=[Depends(auth.PermissionChecker("manage_beds"))])
async def delete_bed(bed_id: int, db: AsyncSession = Depends(auth.get_db)):
    db_bed = await crud.get_bed(db, bed_id=bed_id)
    if db_bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")
    await crud.delete_bed(db=db, db_bed=db_bed)
    return {"ok": True}
