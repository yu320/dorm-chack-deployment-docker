from typing import List, Optional, Any, Union
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from app.models import Role, Permission
from app.schemas import RoleCreate, RoleUpdate
from .base import CRUDBase

class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    async def get(self, db: AsyncSession, id: Any) -> Optional[Role]:
        result = await db.execute(
            select(Role).filter(Role.id == str(id)).options(joinedload(Role.permissions))
        )
        return result.scalars().first()

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Role]:
        result = await db.execute(select(Role).filter(Role.name == name))
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Role]:
        query = select(Role).options(joinedload(Role.permissions))
        query = query.order_by(Role.name).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().unique().all())

    async def create(self, db: AsyncSession, *, obj_in: RoleCreate) -> Role:
        db_role = Role(name=obj_in.name)
        if obj_in.permissions:
            # Convert UUIDs to strings if needed, or let SQLAlchemy handle it if types match
            # Assuming obj_in.permissions is List[uuid.UUID] based on Schema
            perm_ids = [str(pid) for pid in obj_in.permissions]
            permissions_result = await db.execute(select(Permission).filter(Permission.id.in_(perm_ids)))
            db_role.permissions = list(permissions_result.scalars().all())
        
        db.add(db_role)
        await db.commit()
        await db.refresh(db_role)
        # Re-fetch to ensure relationships are loaded for Pydantic serialization
        return await self.get(db, db_role.id)

    async def update(self, db: AsyncSession, *, db_obj: Role, obj_in: Union[RoleUpdate, dict[str, Any]]) -> Role:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        
        if "permissions" in update_data:
            permission_ids = update_data.pop("permissions")
            if permission_ids is not None:
                if len(permission_ids) > 0:
                    perm_ids = [str(pid) for pid in permission_ids]
                    permissions_result = await db.execute(
                        select(Permission).filter(Permission.id.in_(perm_ids))
                    )
                    db_obj.permissions = list(permissions_result.scalars().all())
                else:
                    db_obj.permissions = []
        
        for field in update_data:
            setattr(db_obj, field, update_data[field])
            
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        # Re-fetch to ensure relationships are loaded for Pydantic serialization
        return await self.get(db, db_obj.id)
        
    async def get_count(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count(Role.id)))
        return result.scalar_one()

role_crud = CRUDRole(Role)
