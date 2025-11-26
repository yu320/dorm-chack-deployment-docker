from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import crud, schemas
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
    permissions_data = await crud.get_permissions(db=db, skip=skip, limit=limit)
    return permissions_data
