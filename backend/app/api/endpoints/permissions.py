from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import schemas
from ...crud import crud_permission # Import from package init
from ...database import get_db
from ...auth import PermissionChecker

router = APIRouter()

permission_checker = PermissionChecker("manage_roles")

@router.get(
    "/",
    response_model=schemas.PaginatedPermissions,
    dependencies=[Depends(permission_checker)],
)
async def read_permissions(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve a list of all available permissions in the system with pagination.

    A user must have the **manage_roles** permission to use this.
    """
    permissions = await crud_permission.get_multi(db=db, skip=skip, limit=limit)
    total = await crud_permission.get_count(db)
    return {"total": total, "records": permissions}
