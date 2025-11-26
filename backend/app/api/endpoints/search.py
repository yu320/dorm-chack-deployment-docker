from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import asyncio # Import asyncio

from ... import auth, schemas # Import auth for dependency
from ...crud import crud_dorm # Import crud_dorm
# from ...schemas import SearchResultItem, GlobalSearchResults, User
# from ...auth import get_current_active_user # Assuming only logged-in users can search

router = APIRouter()

@router.post("/", response_model=schemas.GlobalSearchResults, status_code=status.HTTP_200_OK)
async def global_search(
    search_request: schemas.GlobalSearchRequest, # Change query param to request body
    db: AsyncSession = Depends(auth.get_db), # Use auth.get_db
    current_user: schemas.User = Depends(auth.get_current_active_user) # Add auth dependency
):
    """
    Performs a global search across different resources like students and rooms.
    """
    query = search_request.query.strip()
    if not query: # Allow empty query for now, client can filter
        return schemas.GlobalSearchResults(results=[])

    # Perform searches in parallel
    student_task = crud_dorm.search_students(db, query=query, limit=10)
    room_task = crud_dorm.search_rooms(db, query=query, limit=10)

    paginated_students, paginated_rooms = await asyncio.gather(student_task, room_task)
    students = paginated_students.get("records", [])
    rooms = paginated_rooms.get("records", [])

    search_results: List[schemas.SearchResultItem] = []

    for student in students:
        search_results.append(schemas.SearchResultItem(
            type="student",
            id=str(student.id),
            title=f"{student.full_name} ({student.student_id_number})",
            description=f"班級: {student.class_name}" if student.class_name else None
        ))

    for room in rooms:
        search_results.append(schemas.SearchResultItem(
            type="room",
            id=str(room.id),
            title=f"寢室: {room.room_number}",
            description=f"所屬建築: {room.building.name}, 戶號: {room.household}" if room.building and room.building.name else None
        ))

    return schemas.GlobalSearchResults(results=search_results)