import pytest_asyncio
from typing import AsyncGenerator, List, Dict
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Assuming 'main.py' is at the root of the backend package and 'app' is a module within it
from main import app
from app.database import Base, get_db
from app import crud, schemas, models # Added imports for get_auth_client

# Use a completely separate in-memory SQLite database for testing
ASYNC_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False
)

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture to create a new in-memory database session for each test function.
    Creates all tables, yields the session, and then drops all tables after the test.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture to create an httpx.AsyncClient for making API requests in tests.
    It correctly overrides the `get_db` dependency to use the in-memory test database.
    """
    # Define an override for the get_db dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    # Apply the dependency override to the app
    app.dependency_overrides[get_db] = override_get_db

    # Yield the async client
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    
    # Clean up the dependency override after the test
    del app.dependency_overrides[get_db]


class MockRateLimit:
    """A mock limiter that does nothing for testing purposes."""
    def __call__(self, *args, **kwargs):
        """Mimics the limiter decorator"""
        return lambda f: f

    def limit(self, *args, **kwargs):
        """Mimics the .limit method called by the decorator"""
        return lambda f: f

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest_asyncio.fixture(scope="function", autouse=True)
async def override_rate_limit(monkeypatch):
    """Overrides the global rate limiter with a no-op limiter during tests."""
    original_limiter = app.state.limiter # Store the original limiter
    app.state.limiter = MockRateLimit() # Replace with the mock limiter
    yield
    app.state.limiter = original_limiter # Restore the original limiter after the test
    


async def get_auth_client(client_fixture: AsyncClient, db_session: AsyncSession, username: str, password: str, student_id_number: str, roles: List[str] = None) -> AsyncClient:
    """
    Helper function to get an authenticated client.
    Creates a user, assigns roles, logs in, and returns a new AsyncClient with auth headers.
    """
    # Ensure roles exist
    if roles:
        for role_name in roles:
            if not await crud.crud_role.get_by_name(db_session, role_name):
                await crud.crud_role.create(db_session, obj_in=schemas.RoleCreate(name=role_name))
    
    # Create student
    if not await crud.crud_student.get_by_id_number(db_session, student_id_number):
        await crud.crud_student.create(db_session, obj_in=schemas.StudentCreate(student_id_number=student_id_number, full_name=f"{username} FullName"))

    # Register user (via API endpoint)
    user_data = {
        "username": username,
        "password": password,
        "student_id_number": student_id_number,
        "email": f"{username}@example.com" # Added email, required by UserCreate
    }
    response = await client_fixture.post("/api/v1/register", json=user_data)
    assert response.status_code == 201

    # Fetch the newly registered user to assign roles if specified
    db_user = await crud.crud_user.get_by_username(db_session, username)
    assert db_user is not None

    # Manually activate the user for testing purposes
    await crud.crud_user.update(db_session, db_obj=db_user, obj_in={"is_active": True})

    if roles:
        db_roles = []
        for role_name in roles:
            # Ensure the role exists, create if not
            role_obj = await crud.crud_role.get_by_name(db_session, role_name)
            if not role_obj:
                role_obj = await crud.crud_role.create(db_session, obj_in=schemas.RoleCreate(name=role_name))
            db_roles.append(role_obj.id)
        
        # Update user with roles
        await crud.crud_user.update(db_session, db_obj=db_user, obj_in=schemas.UserUpdate(roles=db_roles))
        
        # Re-fetch user to ensure roles are loaded
        db_user = await crud.crud_user.get_by_username(db_session, username)
        
    # Login
    login_data = {"username": username, "password": password}
    response = await client_fixture.post("/api/v1/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Return a new AsyncClient instance with the authentication headers
    authenticated_client = AsyncClient(transport=ASGITransport(app=client_fixture.app), base_url="http://test", headers={"Authorization": f"Bearer {token}"})
    return authenticated_client