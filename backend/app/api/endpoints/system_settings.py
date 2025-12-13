from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any

from ... import schemas, crud, auth
from ...database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.SystemSetting], dependencies=[Depends(auth.PermissionChecker("manage_system"))])
async def read_system_settings(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all system settings.
    """
    settings = await crud.crud_system_setting.get_multi(db, skip=skip, limit=limit)
    return settings

@router.get("/{key}", response_model=schemas.SystemSetting, dependencies=[Depends(auth.PermissionChecker("manage_system"))])
async def read_system_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get a specific system setting by key.
    """
    setting = await crud.crud_system_setting.get_by_key(db, key=key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.put("/{key}", response_model=schemas.SystemSetting, dependencies=[Depends(auth.PermissionChecker("manage_system"))])
async def update_system_setting(
    key: str,
    setting_in: schemas.SystemSettingUpdate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update or create a system setting.
    """
    setting = await crud.crud_system_setting.get_by_key(db, key=key)
    if setting:
        setting = await crud.crud_system_setting.update(db, db_obj=setting, obj_in=setting_in)
    else:
        # If it doesn't exist, create it (assuming key matches URL)
        create_data = schemas.SystemSettingCreate(key=key, **setting_in.model_dump())
        setting = await crud.crud_system_setting.create(db, obj_in=create_data)
    return setting

@router.post("/", response_model=schemas.SystemSetting, dependencies=[Depends(auth.PermissionChecker("manage_system"))])
async def create_system_setting(
    setting_in: schemas.SystemSettingCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new system setting.
    """
    setting = await crud.crud_system_setting.get_by_key(db, key=setting_in.key)
    if setting:
        raise HTTPException(status_code=400, detail="Setting with this key already exists")
    setting = await crud.crud_system_setting.create(db, obj_in=setting_in)
    return setting
