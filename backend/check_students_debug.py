import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import Student, Bed, Room, Building
from sqlalchemy.orm import joinedload

async def check_students():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Student).options(
                joinedload(Student.bed).joinedload(Bed.room).joinedload(Room.building)
            )
        )
        students = result.scalars().all()
        print(f"Total students found: {len(students)}")
        for student in students:
            bed_info = "N/A"
            if student.bed:
                room_info = "N/A"
                if student.bed.room:
                    room_info = f"{student.bed.room.room_number}"
                    if student.bed.room.building:
                        room_info = f"{student.bed.room.building.name} - {room_info}"
                bed_info = f"{room_info} / {student.bed.bed_number}"
            print(f"Student: {student.full_name}, ID: {student.student_id_number}, Bed: {bed_info}")

if __name__ == "__main__":
    import sys
    import os
    # Add backend directory to sys.path if not running from backend
    # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    asyncio.run(check_students())
