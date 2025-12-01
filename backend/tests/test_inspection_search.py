import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from app import crud, schemas
from app.models import User, Student, Room, Building, InspectionRecord, InspectionStatus
from .conftest import get_auth_client # Import the helper

@pytest.mark.asyncio
async def test_search_inspections_error(async_client: AsyncClient, db_session: AsyncSession):
    admin_client = await get_auth_client(async_client, db_session, "admin_search", "password", "STUDENTSEARCH", ["Admin"]) # Create an authenticated admin client

    # Create data for search
    # 1. Create Building & Room
    building = await crud.crud_building.create(db_session, schemas.BuildingCreate(name="SearchBuilding"))
    room = await crud.crud_room.create(db_session, schemas.RoomCreate(building_id=building.id, room_number="S101"))
    
    # 2. Create Student
    student = await crud.crud_student.create(db_session, schemas.StudentCreate(
        student_id_number="SEARCH001",
        full_name="Search Student",
        bed_id=None
    ))
    
    # 3. Create Inspection Record
    # We need to create it manually or via crud
    # crud_inspection.create_inspection_record requires InspectionCreate schema
    # Let's just create the model directly for simplicity
    record = InspectionRecord(
        student_id=student.id,
        room_id=room.id,
        status=InspectionStatus.pending
    )
    db_session.add(record)
    await db_session.commit()
    
    # 4. Call search endpoint using the authenticated admin client
    response = await admin_client.get("/api/v1/inspections/search")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
