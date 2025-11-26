from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import AuditLog, User
from ..schemas import User as UserSchema # Use Pydantic User schema for clarity

async def create_audit_log(
    db: AsyncSession,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[uuid.UUID] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    db_audit_log = AuditLog(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        details=details,
        ip_address=ip_address,
        created_at=datetime.now()
    )
    db.add(db_audit_log)
    await db.commit()
    await db.refresh(db_audit_log)
    return db_audit_log

async def get_audit_logs(
    db: AsyncSession,
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
    
    result = await db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().all())

# You might add more specific getters or update/delete (though audit logs are usually append-only)
