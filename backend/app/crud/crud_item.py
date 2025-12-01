from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
import uuid

from app.models import InspectionItem
from app.schemas import InspectionItemCreate, InspectionItemUpdate
from .base import CRUDBase


class CRUDItem(CRUDBase[InspectionItem, InspectionItemCreate, InspectionItemUpdate]):
    async def get_count(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count()).select_from(self.model))
        return result.scalar()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[InspectionItem]:
        stmt = select(self.model).order_by(self.model.name).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def batch_update_status(
        self, db: AsyncSession, item_ids: List[uuid.UUID], is_active: bool
    ) -> List[InspectionItem]:
        stmt = select(self.model).where(self.model.id.in_(item_ids))
        result = await db.execute(stmt)
        items = result.scalars().all()

        updated_items = []
        for item in items:
            item.is_active = is_active
            db.add(item)
            updated_items.append(item)
        
        await db.commit()
        # Refresh needed? Usually not for batch unless we need updated timestamps from DB
        return updated_items

item_crud = CRUDItem(InspectionItem)
