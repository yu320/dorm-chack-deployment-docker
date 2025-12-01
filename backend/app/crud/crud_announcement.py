"""
CRUD operations for announcements.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional, Any
import uuid

from app.models import Announcement
from app.schemas import AnnouncementCreate, AnnouncementUpdate
from .base import CRUDBase

class CRUDAnnouncement(CRUDBase[Announcement, AnnouncementCreate, AnnouncementUpdate]):
    
    async def get_multi(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100, 
        active_only: bool = True
    ) -> List[Announcement]:
        """獲取公告列表 (Override default get_multi to support active_only and ordering)"""
        query = select(Announcement)
        
        if active_only:
            query = query.where(Announcement.is_active == True)
        
        query = query.order_by(desc(Announcement.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_count(self, db: AsyncSession, active_only: bool = True) -> int:
        from sqlalchemy import func
        query = select(func.count()).select_from(Announcement)
        if active_only:
            query = query.filter(Announcement.is_active == True)
        result = await db.execute(query)
        return result.scalar()

    async def create_with_owner(
        self,
        db: AsyncSession,
        *,
        obj_in: AnnouncementCreate,
        owner_id: str
    ) -> Announcement:
        """建立新公告"""
        db_obj = Announcement(
            title=obj_in.title,
            title_en=obj_in.title_en,
            content=obj_in.content,
            content_en=obj_in.content_en,
            tag=obj_in.tag,
            tag_type=obj_in.tag_type,
            is_active=obj_in.is_active,
            created_by=owner_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

crud_announcement = CRUDAnnouncement(Announcement)

