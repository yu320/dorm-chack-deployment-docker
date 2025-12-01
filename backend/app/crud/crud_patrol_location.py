from typing import List, Optional, Any, Union
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from app.models import PatrolLocation, Building
from app.schemas import PatrolLocationCreate, PatrolLocationUpdate
from .base import CRUDBase

class CRUDPatrolLocation(CRUDBase[PatrolLocation, PatrolLocationCreate, PatrolLocationUpdate]):
    async def get(self, db: AsyncSession, id: Any) -> Optional[PatrolLocation]:
        result = await db.execute(
            select(PatrolLocation).filter(PatrolLocation.id == str(id)).options(joinedload(PatrolLocation.building))
        )
        return result.scalars().first()

    async def get_multi_by_building(
        self, db: AsyncSession, *, building_id: int, skip: int = 0, limit: int = 100
    ) -> List[PatrolLocation]:
        query = select(PatrolLocation).filter(PatrolLocation.building_id == building_id).options(joinedload(PatrolLocation.building))
        query = query.order_by(PatrolLocation.name).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_count_by_building(self, db: AsyncSession, building_id: int) -> int:
        result = await db.execute(
            select(func.count(PatrolLocation.id)).filter(PatrolLocation.building_id == building_id)
        )
        return result.scalar()
    
    async def get_by_name_and_building(self, db: AsyncSession, name: str, building_id: int, household: Optional[str] = None) -> Optional[PatrolLocation]:
        query = select(PatrolLocation).filter(
            PatrolLocation.name == name,
            PatrolLocation.building_id == building_id
        )
        if household:
            query = query.filter(PatrolLocation.household == household)
        result = await db.execute(query)
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: PatrolLocationCreate) -> PatrolLocation:
        db_obj = PatrolLocation(
            name=obj_in.name,
            building_id=obj_in.building_id,
            household=obj_in.household
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        # Re-fetch to ensure relationships are loaded
        return await self.get(db, db_obj.id)

    async def update(self, db: AsyncSession, *, db_obj: PatrolLocation, obj_in: Union[PatrolLocationUpdate, dict[str, Any]]) -> PatrolLocation:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        # Re-fetch to ensure relationships are loaded
        return await self.get(db, db_obj.id)

crud_patrol_location = CRUDPatrolLocation(PatrolLocation)
