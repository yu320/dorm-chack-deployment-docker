from typing import List, Optional, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from app.models import Bed, Room, Building
from app.schemas import BedCreate, BedUpdate
from .base import CRUDBase

class CRUDBed(CRUDBase[Bed, BedCreate, BedUpdate]):
    async def get(self, db: AsyncSession, id: Any) -> Optional[Bed]:
        result = await db.execute(
            select(Bed).filter(Bed.id == int(id)).options(joinedload(Bed.room).joinedload(Room.building))
        )
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Bed]:
        query = select(Bed).options(joinedload(Bed.room).joinedload(Room.building))
        query = query.order_by(Bed.bed_number).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_number(self, db: AsyncSession, room_id: int, bed_number: str) -> Optional[Bed]:
        result = await db.execute(
            select(Bed).filter(Bed.room_id == room_id, Bed.bed_number == bed_number)
        )
        return result.scalars().first()
    
    async def get_count(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count(Bed.id)))
        return result.scalar()

crud_bed = CRUDBed(Bed)
