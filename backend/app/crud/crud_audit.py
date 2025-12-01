from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func # Added import

from ..models import AuditLog
from ..schemas import AuditLogCreate # Assuming this exists or use Dict
from .base import CRUDBase

class CRUDAudit(CRUDBase[AuditLog, Dict[str, Any], Dict[str, Any]]):
    
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: Dict[str, Any], # Override to accept dict directly for flexibility
        user_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        db_obj = AuditLog(
            action=obj_in.get("action"),
            resource_type=obj_in.get("resource_type"),
            resource_id=obj_in.get("resource_id"),
            user_id=user_id,
            details=obj_in.get("details"),
            ip_address=ip_address,
            created_at=datetime.now()
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_audit_logs(self, *args, **kwargs):
        return await self.get_multi_filtered(*args, **kwargs)

    async def get_count(
        self,
        db: AsyncSession,
        *,
        user_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        query = select(func.count(AuditLog.id))
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        result = await db.execute(query)
        return result.scalar_one()

    async def get_multi_filtered(
        self,
        db: AsyncSession,
        *,
        user_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        query = select(AuditLog)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        query = query.order_by(AuditLog.created_at.desc()) # Default sort by date desc
        result = await db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all())

audit_log_crud = CRUDAudit(AuditLog)
