import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List

from ... import schemas, models
from ...auth import get_current_active_user, PermissionChecker
from ...crud import crud_role # Import from package init
from ...database import get_db

from ...utils.audit import audit_log

router = APIRouter()

permission_checker = PermissionChecker("manage_roles")

@router.post("/", response_model=schemas.Role, status_code=status.HTTP_201_CREATED, dependencies=[Depends(permission_checker)])
@audit_log(action="CREATE", resource_type="Role")
async def create_role(role: schemas.RoleCreate, request: Request, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """
    Create a new role.
    """
    db_role = await crud_role.get_by_name(db, name=role.name)
    if db_role:
        raise HTTPException(status_code=400, detail="Role with this name already exists")
    return await crud_role.create(db=db, obj_in=role)

@router.get("/", response_model=schemas.PaginatedRoles, dependencies=[Depends(permission_checker)])
async def read_roles(
    request: Request,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Retrieve all roles with their permissions, with pagination.
    """
    roles = await crud_role.get_multi(db, skip=skip, limit=limit)
    total = await crud_role.get_count(db)
    return {"total": total, "records": roles}

@router.get("/{role_id}", response_model=schemas.Role, dependencies=[Depends(permission_checker)])
async def read_role(role_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """
    Retrieve a single role by its ID.
    """
    db_role = await crud_role.get(db, id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.put("/{role_id}", response_model=schemas.Role, dependencies=[Depends(permission_checker)])
@audit_log(action="UPDATE", resource_type="Role", resource_id_src="role_id")
async def update_role(
    role_id: uuid.UUID,
    role_in: schemas.RoleUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Update a role's name and/or its assigned permissions.
    """
    # Eager load permissions to prevent lazy loading error
    db_role = await crud_role.get(db, id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Prevent modification of the super-admin role
    if db_role.name == "Admin":
        raise HTTPException(status_code=403, detail="Cannot modify the Admin role.")
        
    updated_role = await crud_role.update(db=db, db_obj=db_role, obj_in=role_in)
    return updated_role

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(permission_checker)])
@audit_log(action="DELETE", resource_type="Role", resource_id_src="role_id")
async def delete_role(role_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """
    Delete a role.
    """
    db_role = await crud_role.get(db, id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if db_role.name in ["Admin", "Student", "DormManager"]:
        raise HTTPException(status_code=403, detail=f"Cannot delete default role: {db_role.name}")

    await crud_role.remove(db=db, id=role_id)
    return {"message": "Role deleted successfully"}
