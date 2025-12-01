from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models import Permission
from app.schemas import Permission as PermissionSchema # Using Permission schema for create/update is tricky as current schema is response
# Wait, schemas.py defines Permission as a response model. 
# Usually we have PermissionCreate, PermissionUpdate. Let's check schemas.py again later.
# Assuming for now base CRUDBase is enough, but let's check schemas first to be safe.
# The existing crud_user.py used raw parameters: create_permission(name, description).
# I should probably create proper schemas for PermissionCreate/Update if they don't exist or use Pydantic generic.

from .base import CRUDBase
from app.schemas import BaseModel

class PermissionCreate(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Permission]:
        result = await db.execute(select(Permission).filter(Permission.name == name))
        return result.scalars().first()
    
    async def get_count(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count(Permission.id)))
        return result.scalar_one()

permission_crud = CRUDPermission(Permission)
