from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func

from app.models import Building, Room, Bed
from app.schemas import BuildingCreate
from app.schemas import BaseModel # BuildingUpdate is likely not defined or just name? Let's check schemas.
# Checking schemas.py earlier:
# class BuildingBase(BaseModel): name: str
# class BuildingCreate(BuildingBase): pass
# class Building(BuildingBase): id: int ...
# It seems there is no explicit BuildingUpdate schema in my previous read.
# I should define one locally or generically use BuildingCreate for updates if fields match.
# Or better, define it here if missing.

class BuildingUpdate(BaseModel):
    name: Optional[str] = None

from .base import CRUDBase

class CRUDBuilding(CRUDBase[Building, BuildingCreate, BuildingUpdate]):
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Building]:
        result = await db.execute(select(Building).filter(Building.name == name))
        return result.scalars().first()

    async def get_full_tree(self, db: AsyncSession) -> List[Building]:
        result = await db.execute(
            select(Building).options(
                selectinload(Building.rooms).selectinload(Room.beds)
            ).order_by(Building.name)
        )
        return list(result.scalars().unique().all())
    
    async def get_count(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count(Building.id)))
        return result.scalar_one()

crud_building = CRUDBuilding(Building)
