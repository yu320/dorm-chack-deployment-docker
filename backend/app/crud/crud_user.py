from typing import List, Optional
import uuid
from datetime import datetime, timedelta

from sqlalchemy.future import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, delete, func

from ..database import Base
from .. import schemas
from ..models import User, Student, Role, TokenBlocklist, TokenType, Permission, Bed, Room
from ..schemas import UserCreate, UserUpdate
from ..utils.security import get_password_hash

# User CRUD Operations (Async with SQLAlchemy 2.0 style)

async def get_user(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    result = await db.execute(select(User).filter(User.id == str(user_id)))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(
        select(User)
        .options(joinedload(User.roles).joinedload(Role.permissions))
        .options(joinedload(User.student))
        .filter(User.username == username)
    )
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100, username: Optional[str] = None) -> dict:
    query = select(User).options(
        joinedload(User.roles).joinedload(Role.permissions),
        joinedload(User.student).joinedload(Student.bed).joinedload(Bed.room).joinedload(Room.building)
    )
    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))

    # Get total count before applying offset and limit
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Get paginated results
    records_query = query.order_by(User.username).offset(skip).limit(limit)
    records_result = await db.execute(records_query)
    records = list(records_result.scalars().unique().all())

    # Manually attach permissions to each user to avoid lazy loading in the response model
    for user in records:
        user.permissions = [perm.name for role in user.roles for perm in role.permissions]

    return {"total": total, "records": records}

async def create_user(db: AsyncSession, user_in: UserCreate, role_names: Optional[List[str]] = None) -> tuple[User, str]:
    hashed_password = get_password_hash(user_in.password)
    
    db_student = None
    if user_in.student_id_number:
        from .crud_dorm import get_student_by_id_number, validate_student_bed
        db_student = await get_student_by_id_number(db, student_id_number=user_in.student_id_number)
        
        if not db_student:
             raise ValueError(f"Student with ID number {user_in.student_id_number} not found. Please contact administrator.")

        if user_in.bed_number:
            is_valid_bed = await validate_student_bed(db, student_id=db_student.id, bed_number=user_in.bed_number)
            if not is_valid_bed:
                raise ValueError(f"Bed number {user_in.bed_number} does not match the assignment for student {user_in.student_id_number}.")
        else:
             # If bed number is not provided (e.g. admin creation), we might skip this check or enforce it.
             pass

    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=False
    )
    
    db.add(db_user)
    await db.flush()

    if db_student:
        db_student.user_id = db_user.id
        db.add(db_student)
        await db.flush()

    verification_token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(hours=24)
    token_entry = TokenBlocklist(
        jti=verification_token, 
        expires_at=expires_at, 
        user_id=db_user.id,
        token_type=TokenType.verification
    )
    db.add(token_entry)
    await db.commit()
    
    await db.refresh(db_user)
    return db_user, verification_token

async def update_user(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    
    if "roles" in update_data:
        role_ids = update_data.pop("roles")
        if role_ids is not None:
            # Convert UUIDs to strings for comparison
            role_ids_str = [str(rid) for rid in role_ids]
            roles_result = await db.execute(select(Role).filter(Role.id.in_(role_ids_str)))
            db_user.roles = list(roles_result.scalars().all())
        else:
            db_user.roles = []
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user_password(db: AsyncSession, db_user: User, new_password: str) -> User:
    db_user.hashed_password = get_password_hash(new_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, db_user: User) -> None:
    await db.delete(db_user)
    await db.commit()

# --- Permission CRUD ---
async def create_permission(db: AsyncSession, name: str, description: Optional[str] = None) -> Permission:
    db_permission = Permission(name=name, description=description)
    db.add(db_permission)
    await db.commit()
    await db.refresh(db_permission)
    return db_permission

async def get_permission_by_name(db: AsyncSession, name: str) -> Optional[Permission]:
    result = await db.execute(select(Permission).filter(Permission.name == name))
    return result.scalars().first()

async def get_permissions(db: AsyncSession, skip: int = 0, limit: int = 100) -> dict:
    query = select(Permission)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    records_query = query.order_by(Permission.name).offset(skip).limit(limit)
    records_result = await db.execute(records_query)
    records = list(records_result.scalars().all())

    return {"total": total, "records": records}

# --- Role CRUD ---
async def create_role(db: AsyncSession, name: str, permission_ids: List[uuid.UUID] = []) -> Role:
    db_role = Role(name=name)
    if permission_ids:
        permissions_result = await db.execute(select(Permission).filter(Permission.id.in_(permission_ids)))
        db_role.permissions = list(permissions_result.scalars().all())
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role

async def get_role_by_name(db: AsyncSession, name: str) -> Optional[Role]:
    result = await db.execute(select(Role).filter(Role.name == name))
    return result.scalars().first()

async def get_role(db: AsyncSession, role_id: uuid.UUID) -> Optional[Role]:
    result = await db.execute(
        select(Role).filter(Role.id == role_id).options(joinedload(Role.permissions))
    )
    return result.scalars().first()

async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 100) -> dict:
    query = select(Role).options(joinedload(Role.permissions))
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    records_query = query.order_by(Role.name).offset(skip).limit(limit)
    records_result = await db.execute(records_query)
    records = list(records_result.scalars().unique().all())

    return {"total": total, "records": records}

async def update_role(db: AsyncSession, db_role: Role, role_in: schemas.RoleUpdate) -> Role:
    update_data = role_in.model_dump(exclude_unset=True)
    
    # Handle permissions update carefully
    if "permissions" in update_data:
        permission_ids = update_data.pop("permissions")
        # Only update if permissions value is explicitly provided (not None)
        if permission_ids is not None:
            if len(permission_ids) > 0:
                # Convert UUIDs to strings for comparison
                permission_id_strs = [str(pid) for pid in permission_ids]
                permissions_result = await db.execute(
                    select(Permission).filter(Permission.id.in_(permission_id_strs))
                )
                db_role.permissions = list(permissions_result.scalars().all())
            else:
                # Empty list means clear all permissions
                db_role.permissions = []
            
    for key, value in update_data.items():
        setattr(db_role, key, value)
        
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role

async def delete_role(db: AsyncSession, db_role: Role) -> None:
    await db.delete(db_role)
    await db.commit()

# --- Authorization and Permissions ---

def get_user_permissions(user: User) -> List[str]:
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.name)
    return list(permissions)

# --- Token Blocklist ---

async def add_token_to_blocklist(db: AsyncSession, jti: str, expires_at: datetime):
    blocklisted_token = TokenBlocklist(jti=jti, expires_at=expires_at)
    db.add(blocklisted_token)
    await db.commit()
    await db.refresh(blocklisted_token)
    return blocklisted_token

async def is_token_blocklisted(db: AsyncSession, jti: str) -> bool:
    result = await db.execute(
        select(TokenBlocklist).filter(
            TokenBlocklist.jti == jti,
            TokenBlocklist.expires_at > datetime.now()
        )
    )
    return result.scalars().first() is not None

async def verify_user_account(db: AsyncSession, verification_token: str) -> Optional[User]:
    async with db.begin():
        token_entry_result = await db.execute(
            select(TokenBlocklist).filter(
                TokenBlocklist.jti == verification_token,
                TokenBlocklist.token_type == TokenType.verification,
                TokenBlocklist.expires_at > datetime.now()
            )
        )
        token_entry = token_entry_result.scalars().first()

        if not token_entry or not token_entry.user_id:
            return None
        
        user = await get_user(db, user_id=token_entry.user_id)
        if not user:
            return None
        
        user.is_active = True
        db.add(user)
        await db.delete(token_entry)
        await db.flush()
        await db.refresh(user)
        return user


async def reset_user_password(db: AsyncSession, email: str, new_password: str) -> Optional[User]:
    async with db.begin():
        user = await get_user_by_email(db, email=email)
        if not user:
            return None
        
        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

# Generic CRUD utility
async def get_all_records_from_model(db: AsyncSession, model: type[Base]) -> List:
    result = await db.execute(select(model))
    return list(result.scalars().all())
