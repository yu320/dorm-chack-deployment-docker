from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import SystemSetting
from app.schemas import SystemSettingCreate, SystemSettingUpdate
from .base import CRUDBase

class CRUDSystemSetting(CRUDBase[SystemSetting, SystemSettingCreate, SystemSettingUpdate]):
    async def get_by_key(self, db: AsyncSession, key: str) -> Optional[SystemSetting]:
        result = await db.execute(select(SystemSetting).filter(SystemSetting.key == key))
        return result.scalars().first()

crud_system_setting = CRUDSystemSetting(SystemSetting)
