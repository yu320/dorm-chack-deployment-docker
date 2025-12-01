from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from ... import crud, schemas, auth, models

router = APIRouter()

@router.get("/", response_model=schemas.PaginatedAuditLogs)
async def read_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(auth.get_db),
    current_user: models.User = Depends(auth.PermissionChecker("audit_logs:view"))
):
    """
    Retrieve audit logs.
    Requires 'audit_logs:view' permission (Admin only).
    """
    # Convert user_id string to UUID if provided
    import uuid
    user_uuid = None
    if user_id:
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

    logs = await crud.crud_audit.get_audit_logs(
        db,
        skip=skip,
        limit=limit,
        action=action,
        resource_type=resource_type,
        user_id=user_uuid,
        start_date=start_date,
        end_date=end_date
    )
    
    # Basic count implementation if not available in CRUD yet
    # Ideally we should add get_count to CRUD, but for now let's fetch all count or just return len(logs) if pagination isn't strict?
    # No, we need total for pagination.
    # Let's assume crud_audit.get_count exists or we need to implement it. 
    # I'll check crud_audit.py first.
    total = await crud.crud_audit.get_count(
        db,
        action=action,
        resource_type=resource_type,
        user_id=user_uuid,
        start_date=start_date,
        end_date=end_date
    )

    return {"total": total, "records": logs}
