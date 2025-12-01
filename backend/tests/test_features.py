import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas, models # Ensure app is imported correctly
from httpx import AsyncClient # Ensure AsyncClient is imported
from .conftest import get_auth_client # Import get_auth_client from conftest
from typing import List, Dict

async def test_room_crud(async_client: AsyncClient, db_session: AsyncSession):
    # Create admin user and get authenticated client
    admin_client = await get_auth_client(async_client, db_session, "admin_room", "password", "STUDENT001", ["Admin"])

    # Create a building first
    response = await admin_client.post("/api/v1/buildings/", json={"name": "Test Building"})
    assert response.status_code == 201
    building_id = response.json()["id"]

    # Test Create Room
    room_data = {"building_id": building_id, "room_number": "R101", "household": "H101", "room_type": "Standard"}
    response = await admin_client.post("/api/v1/rooms/", json=room_data)
    assert response.status_code == 201
    created_room = response.json()
    assert created_room["room_number"] == "R101"
    assert created_room["building_id"] == building_id

    # Test Read Room
    response = await admin_client.get(f"/api/v1/rooms/{created_room['id']}")
    assert response.status_code == 200
    read_room = response.json()
    assert read_room["room_number"] == "R101"

    # Test Update Room
    update_data = {"room_type": "Deluxe"}
    response = await admin_client.put(f"/api/v1/rooms/{created_room['id']}", json=update_data)
    assert response.status_code == 200
    updated_room = response.json()
    assert updated_room["room_type"] == "Deluxe"

    # Test Delete Room
    response = await admin_client.delete(f"/api/v1/rooms/{created_room['id']}")
    assert response.status_code == 204

    response = await admin_client.get(f"/api/v1/rooms/{created_room['id']}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_student_bed_assignment(async_client: AsyncClient, db_session: AsyncSession):
    admin_client = await get_auth_client(async_client, db_session, "admin_assign", "password", "STUDENT002", ["Admin"])

    # Create building, room, bed
    response = await admin_client.post("/api/v1/buildings/", json={"name": "B2"})
    building_id = response.json()["id"]
    response = await admin_client.post("/api/v1/rooms/", json={"building_id": building_id, "room_number": "R201"})
    room_id = response.json()["id"]
    response = await admin_client.post("/api/v1/beds/", json={"room_id": room_id, "bed_number": "B1"})
    bed_id = response.json()["id"]

    # Create a student
    response = await admin_client.post("/api/v1/students/", json={"student_id_number": "S001", "full_name": "Student One"})
    student_id = response.json()["id"]

    # Test Assign Student to Bed
    response = await admin_client.put(f"/api/v1/students/{student_id}/assign-bed", json={"bed_id": bed_id})
    assert response.status_code == 200
    assigned_student = response.json()
    assert assigned_student["bed"]["id"] == bed_id

    # Test Unassign Student from Bed
    response = await admin_client.put(f"/api/v1/students/{student_id}/assign-bed", json={"bed_id": None})
    assert response.status_code == 200
    unassigned_student = response.json()
    assert unassigned_student["bed"] is None

@pytest.mark.asyncio
async def test_inspection_record_submission_and_admin_actions(async_client: AsyncClient, db_session: AsyncSession):
    # Setup: Admin and Student users, building, room, bed, inspection item
    admin_client = await get_auth_client(async_client, db_session, "admin_inspect", "password", "STUDENT003", ["Admin"])
    student_client = await get_auth_client(async_client, db_session, "student_inspect", "password", "STUDENT004", ["Student"])

    response = await admin_client.post("/api/v1/buildings/", json={"name": "B3"})
    building_id = response.json()["id"]
    response = await admin_client.post("/api/v1/rooms/", json={"building_id": building_id, "room_number": "R301"})
    room_id = response.json()["id"]
    response = await admin_client.post("/api/v1/beds/", json={"room_id": room_id, "bed_number": "B1"})
    bed_id = response.json()["id"]

    # Assign student to bed
    student_user = await crud.crud_user.get_user_by_username(db_session, "student_inspect")
    await crud.crud_student.assign_bed(db_session, student_user.student, bed_id)

    response = await admin_client.post("/api/v1/items/", json={"name": "Desk", "description": "Desk condition"})
    item_id = response.json()["id"]

    # Test Student Submission
    inspection_payload = {
        "details": [
            {"item_id": item_id, "status": "damaged", "comment": "Scratches", "photos": []}
        ],
        "signature": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    }
    response = await student_client.post("/api/v1/inspections/", json=inspection_payload)
    assert response.status_code == 201
    record_id = response.json()["id"]

    # Test Admin View Record
    response = await admin_client.get(f"/api/v1/inspections/{record_id}")
    assert response.status_code == 200
    record = response.json()
    assert record["id"] == record_id
    assert record["details"][0]["status"] == "damaged"

    # Test Admin Update Record Status
    update_status_payload = {"status": "approved"}
    response = await admin_client.put(f"/api/v1/inspections/{record_id}", json=update_status_payload)
    assert response.status_code == 200
    updated_record = response.json()
    assert updated_record["status"] == "approved"

    # Test PDF Export (check status code and content type)
    response = await admin_client.get(f"/api/v1/inspections/{record_id}/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

    # Test Email Report (mock send_email)
    # For actual testing, you'd mock the send_email function to check if it was called
    email_payload = {"recipient_email": "test@example.com"}
    response = await admin_client.post(f"/api/v1/inspections/{record_id}/email", json=email_payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Inspection report emailed successfully."

@pytest.mark.asyncio
async def test_data_export(async_client: AsyncClient, db_session: AsyncSession):
    admin_client = await get_auth_client(async_client, db_session, "admin_export", "password", "STUDENT005", ["Admin"])

    # Create some data to export
    await admin_client.post("/api/v1/buildings/", json={"name": "B4"})
    await admin_client.post("/api/v1/items/", json={"name": "Chair", "description": "Chair condition"})

    # Test Data Export
    export_payload = {"table_names": ["buildings", "inspection_items"]}
    response = await admin_client.post("/api/v1/admin/export-data", json=export_payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

    # You could further unpack the zip and check CSV contents if needed
    # For now, checking status and content-type is sufficient for integration test
