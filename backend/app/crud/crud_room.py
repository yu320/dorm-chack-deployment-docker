from typing import List, Optional, Any, Union, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func, or_

from app.models import Room, Building, Bed
from app.schemas import RoomCreate, RoomUpdate
from .base import CRUDBase

class CRUDRoom(CRUDBase[Room, RoomCreate, RoomUpdate]):
    async def get(self, db: AsyncSession, id: Any) -> Optional[Room]:
        result = await db.execute(
            select(Room).options(joinedload(Room.building)).filter(Room.id == id)
        )
        return result.scalars().first()

    async def get_count(self, db: AsyncSession, building_id: Optional[int] = None) -> int:
        query = select(func.count()).select_from(Room)
        if building_id:
            query = query.filter(Room.building_id == building_id)
        result = await db.execute(query)
        return result.scalar()

    async def search(self, db: AsyncSession, query: str, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        search_pattern = f"%{query.lower()}%"
        
        # Base query with filters
        base_query = select(Room).options(joinedload(Room.building)).filter(
            or_(
                Room.room_number.ilike(search_pattern),
                Room.household.ilike(search_pattern)
            )
        )

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated records
        records_query = base_query.offset(skip).limit(limit)
        records_result = await db.execute(records_query)
        records = list(records_result.scalars().all())

        return {"total": total, "records": records}

crud_room = CRUDRoom(Room)
