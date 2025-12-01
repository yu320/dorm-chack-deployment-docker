"""
Announcement API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession # Changed from Session to AsyncSession
from typing import List

from app.database import get_db
from app.auth import get_current_user, PermissionChecker
from app.models import User # Ensure User is imported if used
from app.schemas import (
    AnnouncementResponse,
    AnnouncementCreate,
    AnnouncementUpdate,
    PaginatedAnnouncements
)
from app.crud.crud_announcement import crud_announcement # Use the instance
from app.utils.i18n import _ # Import translation function

router = APIRouter()


# --- Public Endpoints ---

@router.get("/", response_model=PaginatedAnnouncements)
async def get_all_active_announcements(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db) # Changed to AsyncSession
):
    """
    獲取公告列表（公開，僅返回啟用的公告）
    """
    # ... existing code ...
    announcements = await crud_announcement.get_multi(
        db, skip=skip, limit=limit, active_only=True
    )
    total = await crud_announcement.get_count(db, active_only=True)
    
    return PaginatedAnnouncements(total=total, records=announcements)


@router.get("/{announcement_id}", response_model=AnnouncementResponse)
async def get_single_active_announcement(
    announcement_id: str,
    db: AsyncSession = Depends(get_db) # Changed to AsyncSession
):
    """
    獲取單一公告（公開，僅返回啟用的公告）
    """
    # ... existing code ...
    announcement = await crud_announcement.get_active(db, announcement_id)
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_("announcement_not_found_or_inactive") # Use i18n
        )
    return announcement


# --- Admin Endpoints (require permission) ---

@router.post("/", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def create_announcement_admin(
    announcement_in: AnnouncementCreate, # Renamed for clarity
    current_user: User = Depends(PermissionChecker("announcements:create")),
    db: AsyncSession = Depends(get_db) # Changed to AsyncSession
):
    """
    建立新公告（需要 announcements:create 權限）
    """
    # ... existing code ...
    # CRUDBase.create handles ID generation automatically if not provided in schema
    # Add creator_id before creating the object
    announcement_data = announcement_in.model_dump()
    announcement_data["created_by"] = str(current_user.id) # Ensure UUID is string
    
    new_announcement = await crud_announcement.create(
        db, obj_in=announcement_data
    )
    return new_announcement


@router.put("/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement_admin(
    announcement_id: str,
    announcement_update: AnnouncementUpdate,
    current_user: User = Depends(PermissionChecker("announcements:edit")),
    db: AsyncSession = Depends(get_db) # Changed to AsyncSession
):
    """
    更新公告（需要 announcements:edit 權限）
    """
    # ... existing code ...
    announcement = await crud_announcement.get(db, announcement_id)
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_("announcement_not_found") # Use i18n
        )
    
    updated_announcement = await crud_announcement.update(
        db, db_obj=announcement, obj_in=announcement_update
    )
    return updated_announcement


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement_admin(
    announcement_id: str,
    current_user: User = Depends(PermissionChecker("announcements:delete")),
    db: AsyncSession = Depends(get_db) # Changed to AsyncSession
):
    """
    刪除公告（需要 announcements:delete 權限）
    """
    # ... existing code ...
    announcement = await crud_announcement.remove(db, id=announcement_id)
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_("announcement_not_found") # Use i18n
        )
    return None
