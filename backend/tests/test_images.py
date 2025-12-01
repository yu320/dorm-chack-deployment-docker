import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import os
import shutil
import uuid
import base64

from main import app
from app.config import settings
from app.models import User, Student, InspectionRecord, InspectionDetail, Photo, InspectionItem, ItemStatus, Role, Permission
from app import schemas
from app.schemas import UserCreate, InspectionCreate, InspectionRecordCreate, InspectionDetailCreate, PhotoCreate, RoleCreate, Permission as PermissionSchema # Renamed to avoid conflict with model
from backend.app.crud import crud_user, crud_inspection, crud_student, crud_building, crud_room, crud_bed, crud_permission, crud_role
from backend.app.utils.security import get_password_hash

# Define test user credentials and student info
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword"
TEST_STUDENT_ID_NUMBER = "S123456789"
TEST_FULL_NAME = "Test User"

# Ensure UPLOAD_DIR exists for tests
@pytest.fixture(scope="module", autouse=True)
def setup_upload_dir():
    # Ensure UPLOAD_DIR is local to the test execution, not global project 'uploads'
    test_upload_dir = os.path.join(os.path.dirname(__file__), "test_uploads")
    original_upload_dir = settings.UPLOAD_DIR # Store original for module cleanup
    settings.UPLOAD_DIR = test_upload_dir # Override for tests
    
    if os.path.exists(test_upload_dir):
        shutil.rmtree(test_upload_dir)
    os.makedirs(test_upload_dir)
    yield
    if os.path.exists(test_upload_dir):
        shutil.rmtree(test_upload_dir) # Clean up after tests
    settings.UPLOAD_DIR = original_upload_dir # Restore original setting


@pytest.fixture
async def create_test_user_and_student(db_session: AsyncSession):
    # Create student first (required before creating user)
    await crud_student.create(db_session, obj_in=schemas.StudentCreate(
        student_id_number=TEST_STUDENT_ID_NUMBER, 
        full_name=TEST_FULL_NAME
    ))
    
    # Create a user
    user_data = UserCreate(
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        student_id_number=TEST_STUDENT_ID_NUMBER, # Link user to a student
        email=f"{TEST_USERNAME}@example.com" # Correctly construct email
    )
    # The create returns user
    user = await crud_user.create(db_session, obj_in=user_data)
    # Activate user
    user.is_active = True
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user, attribute_names=["roles", "student"]) # Ensure roles and student are loaded

    # Get the associated student (crud_user.create_user already links it)
    student = await crud_student.get_by_id_number(db_session, TEST_STUDENT_ID_NUMBER)
    
    # Create a building and room for the student
    building = await crud_building.create(db_session, obj_in=schemas.BuildingCreate(name="Test Building"))
    room = await crud_room.create(db_session, obj_in=schemas.RoomCreate(building_id=building.id, room_number="R101"))
    bed = await crud_bed.create(db_session, obj_in=schemas.BedCreate(room_id=room.id, bed_number="B1"))
    
    # Assign student to bed
    student.bed_id = bed.id
    db_session.add(student)
    await db_session.commit()
    await db_session.refresh(student)

    # Create an admin user for testing admin permissions
    admin_username = "adminuser"
    admin_password = "adminpassword"
    admin_user_data = UserCreate(
        username=admin_username, 
        password=admin_password,
        student_id_number="ADMIN001", # Added student_id for admin user
        email=f"{admin_username}@example.com" # Correctly construct email
    )
    # Ensure student for admin_user_data exists
    await crud_student.create(db_session, obj_in=schemas.StudentCreate(student_id_number="ADMIN001", full_name="Admin FullName"))

    admin_user = await crud_user.create(db_session, obj_in=admin_user_data)
    admin_user.is_active = True
    admin_user_id = str(admin_user.id)  # Store ID immediately
    db_session.add(admin_user)
    await db_session.commit()
    
    # Create admin role and permissions
    view_all_records_perm = await crud_permission.get_by_name(db_session, "view_all_records")
    if not view_all_records_perm:
        view_all_records_perm = await crud_permission.create(db_session, obj_in=schemas.PermissionCreate(name="view_all_records", description="View all records"))
    perm_id = str(view_all_records_perm.id)  # Store ID immediately
    
    # Create or get admin role
    admin_role = await crud_role.get_by_name(db_session, "admin")
    if not admin_role:
        admin_role = await crud_role.create(db_session, obj_in=schemas.RoleCreate(name="admin", permissions=[uuid.UUID(perm_id)]))
    role_id = str(admin_role.id)  # Store ID immediately
    
    # Use direct SQL with stored IDs - avoids any ORM access
    from sqlalchemy import text
    await db_session.execute(
        text("INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)"),
        {"user_id": admin_user_id, "role_id": role_id}
    )
    await db_session.commit()
    
    # Reload admin_user fresh from database
    from sqlalchemy import select
    from app.models import User
    result = await db_session.execute(select(User).filter(User.id == admin_user_id))
    admin_user = result.scalars().first()
    await db_session.refresh(admin_user, attribute_names=["roles", "student"]) # Ensure roles and student are loaded

    return user, student, admin_user, admin_password

@pytest.fixture
async def authenticated_client(async_client: AsyncClient, create_test_user_and_student):
    user, _, _, _ = create_test_user_and_student
    login_data = {"username": user.username, "password": TEST_PASSWORD}
    response = await async_client.post("/api/v1/token", data=login_data)
    assert response.status_code == 200
    return async_client


@pytest.fixture
async def admin_authenticated_client(async_client: AsyncClient, create_test_user_and_student):
    _, _, admin_user, admin_password = create_test_user_and_student
    login_data = {"username": admin_user.username, "password": admin_password}
    response = await async_client.post("/api/v1/token", data=login_data)
    assert response.status_code == 200
    return async_client


@pytest.fixture
async def create_inspection_with_image(db_session: AsyncSession, create_test_user_and_student):
    user, student, _, _ = create_test_user_and_student
    
    # Create an inspection item
    # Use item_crud instead of crud_inspection.create_inspection_item
    from backend.app.crud import crud_item # Corrected import name
    inspection_item = await crud_item.create(db_session, obj_in=schemas.InspectionItemCreate(name="Test Item"))

    # Create a dummy image file for testing
    image_content_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" # 1x1 black PNG
    dummy_filename = f"{uuid.uuid4()}.png"
    # Manually save the dummy file to the test_uploads directory
    # The validate_and_save_image function is already used in create_inspection_record
    # So we don't need to manually save it here.

    # Create inspection details
    photo_create = PhotoCreate(
        file_content=image_content_b64,
        file_name=dummy_filename
    )
    detail_create = InspectionDetailCreate(
        item_id=inspection_item.id,
        status=ItemStatus.damaged,
        comment="Test comment",
        photos=[photo_create]
    )
    record_create = InspectionCreate( # Use InspectionCreate schema for service/CRUD input
        room_id=1, # Placeholder, will be overridden by logic or derived
        student_id=student.id,
        details=[detail_create],
        signature_base64="data:image/png;base64,iVBORw0KGgoAAAANSUSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    )

    # Store IDs immediately to avoid lazy loading
    student_id_str = str(student.id)
    # Get room_id from student bed
    from sqlalchemy import select as sql_select
    from app.models import Student as StudentModel, Bed as BedModel
    student_result = await db_session.execute(sql_select(StudentModel).filter(StudentModel.id == student_id_str))
    student_obj = student_result.scalars().first()
    bed_result = await db_session.execute(sql_select(BedModel).filter(BedModel.id == student_obj.bed_id))
    bed_obj = bed_result.scalars().first()
    room_id = bed_obj.room_id
    record_create.room_id = room_id # Set correct room_id
    
    # Use create_with_details instead of create_inspection_record
    # And we need to handle file upload simulation if we use the service, 
    # but here we are calling CRUD directly. 
    # CRUD create_with_details expects photo paths, not content.
    # So we need to simulate "upload" by setting file_path manually in the object passed to CRUD.
    
    # Manually "upload"
    file_path = f"{uuid.uuid4()}.png"
    # In real flow, service handles this. Here we mock it.
    record_create.details[0].photos[0].file_path = file_path
    
    inspection_record = await crud_inspection.create_with_details(
        db_session,
        inspection_in=record_create,
        student_id=student.id,
        inspector_id=user.id,
        signature_filename=f"{uuid.uuid4()}.png"
    )
    
    # Retrieve the image record to get the actual file_path (unique filename)
    image_record_result = await db_session.execute(
        select(Photo).filter(
            Photo.detail_id == inspection_record.details[0].id
        )
    )
    image_record = image_record_result.scalars().first()
    
    return inspection_record, image_record


# --- Test Cases ---

@pytest.mark.asyncio
async def test_get_image_unauthenticated(async_client: AsyncClient, create_inspection_with_image):
    _, image_record = create_inspection_with_image
    response = await async_client.get(f"/api/v1/images/{image_record.file_path}")
    assert response.status_code == 401 # Unauthorized


@pytest.mark.asyncio
async def test_get_image_by_owner(authenticated_client: AsyncClient, create_inspection_with_image):
    inspection_record, image_record = create_inspection_with_image
    response = await authenticated_client.get(f"/api/v1/images/{image_record.file_path}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


@pytest.mark.asyncio
async def test_get_image_by_admin(admin_authenticated_client: AsyncClient, create_inspection_with_image):
    _, image_record = create_inspection_with_image
    response = await admin_authenticated_client.get(f"/api/v1/images/{image_record.file_path}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


@pytest.mark.asyncio
async def test_get_image_forbidden_another_user(async_client: AsyncClient, db_session: AsyncSession, create_inspection_with_image):
    _, image_record = create_inspection_with_image

    # Create another user (not owner, not admin)
    another_username = "anotheruser@example.com"
    another_password = "anotherpassword"
    another_user_data = UserCreate(username=another_username, password=another_password)
    another_user, _ = await crud_user.create_user(db_session, another_user_data)
    another_user.is_active = True
    db_session.add(another_user)
    await db_session.commit()

    # Authenticate as another user
    login_data = {"username": another_user.username, "password": another_password}
    response = await async_client.post("/api/v1/token", data=login_data)
    assert response.status_code == 200

    # Try to access the image
    response = await async_client.get(f"/api/v1/images/{image_record.file_path}")
    assert response.status_code == 403 # Forbidden


@pytest.mark.asyncio
async def test_get_image_not_found(authenticated_client: AsyncClient):
    response = await authenticated_client.get(f"/api/v1/images/{uuid.uuid4()}.png")
    assert response.status_code == 404 # Not Found


@pytest.mark.asyncio
async def test_get_image_invalid_filename_format(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/api/v1/images/invalid_filename")
    assert response.status_code == 400 # Bad Request

    response = await authenticated_client.get("/api/v1/images/../secrets.txt")
    assert response.status_code == 400 # Bad Request (due to path traversal check)
