import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas

# Global test credentials
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword"

# All tests must be marked with pytest.mark.asyncio
# and use the 'async_client' fixture which provides an AsyncClient instance.

@pytest.mark.asyncio
async def test_user_registration_and_login(async_client: AsyncClient, db_session: AsyncSession):
    """
    Tests user registration, login, accessing a protected route, and logout.
    """
    # 1. Pre-populate student data required for registration
    student_data = schemas.StudentCreate(
        student_id_number="TEST001",
        full_name="Test User",
        class_name="Test Class",
    )
    await crud.crud_student.create(db=db_session, obj_in=student_data)

    # 2. Test user registration
    registration_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
        "email": f"{TEST_USERNAME}@example.com", # Correctly construct email
        "student_id_number": "TEST001",
    }
    # API calls are now asynchronous, so we must 'await' them
    response = await async_client.post("/api/v1/register", json=registration_data)
    assert response.status_code == 201, response.text
    user_data = response.json()
    assert user_data["username"] == TEST_USERNAME
    assert user_data["student"]["student_id_number"] == "TEST001"

    # Manually activate the user for testing purposes (since registration creates inactive users)
    db_user = await crud.crud_user.get_by_username(db_session, TEST_USERNAME)
    await crud.crud_user.update(db_session, db_obj=db_user, obj_in={"is_active": True})

    # 3. Test user login (using form data)
    login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
    }
    response = await async_client.post("/api/v1/token", data=login_data)
    assert response.status_code == 200, response.text
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    access_token = token_data["access_token"]

    # 4. Test accessing a protected endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await async_client.get("/api/v1/users/me/", headers=headers)
    assert response.status_code == 200, response.text
    me_data = response.json()
    assert me_data["username"] == TEST_USERNAME

    # 5. Test user logout
    response = await async_client.post("/api/v1/logout", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Successfully logged out"}

    # 6. Verify token is now invalid
    response = await async_client.get("/api/v1/users/me/", headers=headers)
    assert response.status_code == 401, response.text # Expect Unauthorized

@pytest.mark.asyncio
async def test_create_user_student_not_found(async_client: AsyncClient):
    """
    Tests that registration fails if the student ID does not exist.
    """
    registration_data = {
        "username": "ghostuser",
        "password": "ghostpassword",
        "student_id_number": "NONEXISTENT",
        "email": "ghost@example.com", # Correctly construct email
    }
    response = await async_client.post("/api/v1/register", json=registration_data)
    assert response.status_code == 400, response.text
    assert "Student with ID number NONEXISTENT not found" in response.json()["detail"]