from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import asyncio 

from ... import auth, schemas 
from ...crud.crud_student import crud_student
from ...crud.crud_room import crud_room
from ...crud.crud_inspection import crud_inspection

router = APIRouter()

@router.post("/", response_model=schemas.GlobalSearchResults, status_code=status.HTTP_200_OK, dependencies=[Depends(auth.PermissionChecker("students:view_all"))])
async def global_search(
    search_request: schemas.GlobalSearchRequest, 
    db: AsyncSession = Depends(auth.get_db), 
    current_user: schemas.User = Depends(auth.get_current_active_user) 
):
    """
    Performs a global search across different resources like students, rooms, and inspections.
    """
    query = search_request.query.strip()
    if not query:
        return schemas.GlobalSearchResults(results=[])

    # Perform searches in parallel
    # Using the new modular CRUD instances' search method
    student_task = crud_student.search(db, query=query, limit=5)
    room_task = crud_room.search(db, query=query, limit=5)
    inspection_task = crud_inspection.search(db, query=query, limit=5) # New inspection search

    paginated_students, paginated_rooms, paginated_inspections = await asyncio.gather(
        student_task, room_task, inspection_task
    )
    
    students = paginated_students.get("records", [])
    rooms = paginated_rooms.get("records", [])
    inspections = paginated_inspections.get("records", [])

    search_results: List[schemas.SearchResultItem] = []

    for student in students:
        search_results.append(schemas.SearchResultItem(
            type="student",
            id=str(student.id),
            title=f"{student.full_name} ({student.student_id_number})",
            description=f"班級: {student.class_name}" if student.class_name else None
        ))

    for room in rooms:
        # Accessing relationship safely
        building_name = room.building.name if room.building else "未知建築"
        household_info = f", 戶號: {room.household}" if room.household else ""
        
        search_results.append(schemas.SearchResultItem(
            type="room",
            id=str(room.id),
            title=f"寢室: {room.room_number}",
            description=f"所屬建築: {building_name}{household_info}"
        ))
        
    for inspection in inspections:
        student_name = inspection.student.full_name if inspection.student else "未知學生"
        room_num = inspection.room.room_number if inspection.room else "未知寢室"
        date_str = inspection.created_at.strftime("%Y-%m-%d") if inspection.created_at else ""
        
        search_results.append(schemas.SearchResultItem(
            type="inspection", # Frontend might need to handle this new type or map it
            id=str(inspection.id),
            title=f"檢查紀錄: {student_name} - {room_num}",
            description=f"狀態: {inspection.status}, 日期: {date_str}"
        ))

    return schemas.GlobalSearchResults(results=search_results)