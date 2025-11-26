from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import uuid
import logging

from ..models import User, Role, Permission, InspectionItem
from ..utils.security import get_password_hash
from ..config import settings
from ..crud import crud_user # Import crud_user for creating the initial user

logger = logging.getLogger(__name__)

async def seed_database(db: AsyncSession):
    """
    Seeds the database with initial roles, permissions, and a default admin user.
    """
    logger.info("Checking for existing roles and permissions...")
    
    # --- Seed Permissions ---
    # Define core permissions for the system
    core_permissions_data = [
        {"name": "admin:full_access", "description": "Grants full administrative access"},
        {"name": "users:view", "description": "View user accounts"},
        {"name": "users:manage", "description": "Create, update, and delete user accounts"},
        {"name": "roles:view", "description": "View roles and their permissions"},
        {"name": "roles:manage", "description": "Create, update, and delete roles and permissions"},
        {"name": "students:view", "description": "View student information"},
        {"name": "students:manage", "description": "Create, update, and delete student information"},
        {"name": "rooms:view", "description": "View room information"},
        {"name": "rooms:manage", "description": "Create, update, and delete room information"},
        {"name": "inspections:view", "description": "View inspection records"},
        {"name": "inspections:submit", "description": "Submit new inspection records"},
        {"name": "inspections:review", "description": "Review and approve inspection records"},
        {"name": "audit_logs:view", "description": "View system audit logs"},
        {"name": "manage_items", "description": "Manage inspection items"}, # Add missing permission
        # Add more permissions as needed
    ]

    existing_permissions_result = await db.execute(select(Permission))
    existing_permissions_names = {p.name for p in existing_permissions_result.scalars().all()}
    
    permissions_to_add = []
    for p_data in core_permissions_data:
        if p_data["name"] not in existing_permissions_names:
            permissions_to_add.append(Permission(name=p_data["name"], description=p_data["description"]))
    
    if permissions_to_add:
        db.add_all(permissions_to_add)
        await db.commit()
        for p in permissions_to_add:
            await db.refresh(p)
        logger.info(f"Added {len(permissions_to_add)} new permissions.")
    else:
        logger.info("All core permissions already exist.")

    # --- Seed Roles ---
    # Fetch all current permissions for role assignment
    all_permissions_result = await db.execute(select(Permission))
    all_permissions = {p.name: p for p in all_permissions_result.scalars().all()}

    # Define core roles and their associated permissions
    roles_data = {
        "admin": ["admin:full_access", "users:view", "users:manage", "roles:view", "roles:manage",
                  "students:view", "students:manage", "rooms:view", "rooms:manage",
                  "inspections:view", "inspections:submit", "inspections:review", "audit_logs:view", "manage_items"],
        "inspector": ["students:view", "rooms:view", "inspections:view", "inspections:submit"],
        "student": ["students:view", "inspections:view"] # Students can view their own data
    }

    for role_name, perms_list in roles_data.items():
        role_result = await db.execute(
            select(Role)
            .filter(Role.name == role_name)
            .options(selectinload(Role.permissions))
        )
        db_role = role_result.scalars().first()
        
        if not db_role:
            logger.info(f"Creating role: {role_name}")
            db_role = Role(name=role_name)
            db.add(db_role)
            await db.commit()
            
            # Re-query with eager loading after creation
            role_result = await db.execute(
                select(Role)
                .filter(Role.name == role_name)
                .options(selectinload(Role.permissions))
            )
            db_role = role_result.scalars().first()
        
        # Assign permissions to the role
        current_role_permissions = {p.name for p in db_role.permissions}
        permissions_to_assign = [all_permissions[p_name] for p_name in perms_list if p_name in all_permissions and p_name not in current_role_permissions]
        
        for p in permissions_to_assign:
            db_role.permissions.append(p)
        
        if permissions_to_assign:
            await db.commit()
            logger.info(f"Assigned {len(permissions_to_assign)} new permissions to role '{role_name}'.")
        else:
            logger.info(f"Role '{role_name}' already has all its core permissions.")

    # --- Seed Default Admin User ---
    logger.info("Checking for default admin user...")
    admin_user_result = await db.execute(select(User).filter(User.username == settings.FIRST_SUPERUSER))
    admin_user = admin_user_result.scalars().first()

    if not admin_user:
        logger.info("Creating default admin user...")
        admin_role_result = await db.execute(select(Role).filter(Role.name == "admin"))
        admin_role = admin_role_result.scalars().first()

        if not admin_role:
            logger.error("Admin role not found, this should not happen if seeding ran correctly.")
            return # Should ideally re-run role seeding

        hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
        default_admin = User(
            username=settings.FIRST_SUPERUSER,
            hashed_password=hashed_password,
            is_active=True
        )
        default_admin.roles.append(admin_role)
        db.add(default_admin)
        await db.commit()
        await db.refresh(default_admin)
        logger.info("Default admin user created.")
    else:
        logger.info("Default admin user already exists.")

    # --- Seed Inspection Items ---
    logger.info("Checking for default inspection items...")
    default_items = [
        "Desk", "Chair", "Bed", "Wardrobe", "AC", "Window", "Door", "Light", "Socket", "Curtain", "Trash Can", "Mirror", "Shelf", "Cabinet"
    ]
    
    # Check which items already exist
    existing_items_result = await db.execute(select(InspectionItem.name))
    existing_item_names = {row.name for row in existing_items_result.all()}
    
    items_to_create = []
    for item_name in default_items:
        if item_name not in existing_item_names:
            items_to_create.append(InspectionItem(name=item_name, description=f"Inspection item: {item_name}"))
    
    if items_to_create:
        db.add_all(items_to_create)
        await db.commit()
        logger.info(f"Added {len(items_to_create)} default inspection items.")
    else:
        logger.info("Default inspection items already exist.")

