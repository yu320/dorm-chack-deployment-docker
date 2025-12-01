import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from ... import schemas, models, auth
from ...crud.crud_user import crud_user # Import instance
from ...utils.security import verify_password
from ...utils.audit import audit_log

router = APIRouter()

@router.get("/me/", response_model=schemas.User)
async def read_users_me(request: Request, current_user: models.User = Depends(auth.get_current_active_user)):
    """
    Fetches the current logged-in user's details including permissions.
    """
    # Extract permissions from pre-loaded roles and permissions (avoid lazy loading)
    user_permissions = [
        perm.name 
        for role in current_user.roles 
        for perm in role.permissions
    ]
    user_data = schemas.User.model_validate(current_user)
    user_data.permissions = user_permissions
    return user_data

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED, dependencies=[Depends(auth.PermissionChecker("manage_users"))])
@audit_log(action="CREATE", resource_type="User")
async def create_user(user: schemas.UserCreate, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    Creates a new user.
    """
    db_user = await crud_user.get_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    try:
        return await crud_user.create(db=db, obj_in=user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=schemas.PaginatedUsers, dependencies=[Depends(auth.PermissionChecker("manage_users"))])
async def read_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    username: Optional[str] = None,
    db: AsyncSession = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Retrieve all users with pagination. (Requires 'manage_users' permission).
    """
    users = await crud_user.get_multi(db, skip=skip, limit=limit, username=username)
    total = await crud_user.get_count(db, username=username)
    return {"total": total, "records": users}

@router.put("/{user_id}", response_model=schemas.User, dependencies=[Depends(auth.PermissionChecker("manage_users"))])
@audit_log(action="UPDATE", resource_type="User", resource_id_src="user_id")
async def update_user_data(user_id: uuid.UUID, user_in: schemas.UserUpdate, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    Update a user's data. (Requires 'manage_users' permission).
    """
    # Eager load roles to prevent lazy loading error when updating
    db_user = await crud_user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await crud_user.update(db=db, db_obj=db_user, obj_in=user_in)

    # Re-fetch with all relationships for response serialization
    # We need to fetch roles and student because the response model likely includes them
    # and db.refresh() clears the loaded relationships.
    result = await db.execute(
        select(models.User)
        .filter(models.User.id == str(user_id))
        .options(
            joinedload(models.User.roles).joinedload(models.Role.permissions),
            joinedload(models.User.student)
            .joinedload(models.Student.bed)
            .joinedload(models.Bed.room)
            .joinedload(models.Room.building)
        )
    )
    return result.scalars().first()

@router.post("/change-password", response_model=schemas.User)
@audit_log(action="UPDATE_PASSWORD", resource_type="User", resource_id_src=lambda *args, **kwargs: str(kwargs['current_user'].id))
async def change_password(
    password_data: schemas.UserChangePassword,
    request: Request,
    db: AsyncSession = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    """
    Change the current user's password.
    """
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirmation do not match")
    
    return await crud_user.update_password(db=db, db_user=current_user, new_password=password_data.new_password)
