from typing import List, Optional, Dict, Any, Union
import uuid
from sqlalchemy.future import select
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Student, Bed, Room, Building
from app.schemas import StudentCreate, StudentUpdate
from .base import CRUDBase


class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    
    async def get(self, db: AsyncSession, id: Any) -> Optional[Student]:
        result = await db.execute(
            select(Student)
            .filter(Student.id == str(id))
            .options(
                joinedload(Student.bed).joinedload(Bed.room).joinedload(Room.building),
                joinedload(Student.user)
            )
        )
        return result.scalars().first()

    async def get_by_id_number(self, db: AsyncSession, student_id_number: str) -> Optional[Student]:
        result = await db.execute(select(Student).filter(Student.student_id_number == student_id_number))
        return result.scalars().first()

    async def get_by_bed_id(self, db: AsyncSession, bed_id: int) -> Optional[Student]:
        result = await db.execute(select(Student).filter(Student.bed_id == bed_id))
        return result.scalars().first()

    async def get_multi_filtered(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        full_name: Optional[str] = None,
        student_id_number: Optional[str] = None,
        class_name: Optional[str] = None,
        gender: Optional[str] = None,
        bed_id: Optional[int] = None,
        room_id: Optional[int] = None,
        building_id: Optional[int] = None,
        household: Optional[str] = None,
    ) -> Dict[str, Any]:
        query = select(Student).options(
            joinedload(Student.bed).joinedload(Bed.room).joinedload(Room.building)
        )

        if full_name:
            query = query.filter(Student.full_name.ilike(f"%{full_name}%"))
        if student_id_number:
            query = query.filter(Student.student_id_number.ilike(f"%{student_id_number}%"))
        if class_name:
            query = query.filter(Student.class_name.ilike(f"%{class_name}%"))
        if gender:
            query = query.filter(Student.gender == gender)
        
        if bed_id or room_id or building_id or household:
            query = query.join(Student.bed)
            if bed_id:
                query = query.filter(Bed.id == bed_id)
            if room_id or building_id or household:
                query = query.join(Bed.room)
                if room_id:
                    query = query.filter(Room.id == room_id)
                if building_id:
                    query = query.filter(Room.building_id == building_id)
                if household:
                    query = query.filter(Room.household == household)

        # Get total count before applying offset and limit
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        records_query = query.order_by(Student.student_id_number).offset(skip).limit(limit)
        records_result = await db.execute(records_query)
        records = list(records_result.scalars().all())

        return {"total": total, "records": records}

    async def assign_bed(self, db: AsyncSession, db_student: Student, bed_id: Optional[int]) -> Student:
        # 1. If student had a previous bed, free it
        if db_student.bed_id:
            # We need to get the bed object to update it
            prev_bed_result = await db.execute(select(Bed).filter(Bed.id == db_student.bed_id))
            prev_bed = prev_bed_result.scalars().first()
            if prev_bed:
                prev_bed.status = "available"
                db.add(prev_bed)
        
        # 2. Assign new bed
        db_student.bed_id = bed_id
        
        # 3. Mark new bed as occupied (only if bed_id is not None)
        if bed_id:
            new_bed_result = await db.execute(select(Bed).filter(Bed.id == bed_id))
            new_bed = new_bed_result.scalars().first()
            if new_bed:
                new_bed.status = "occupied"
                db.add(new_bed)
            
        db.add(db_student)
        await db.commit()
        await db.refresh(db_student)
        return db_student
    
    async def remove(self, db: AsyncSession, *, id: Union[Any, uuid.UUID]) -> Optional[Student]:
        obj = await self.get(db, id=id)
        if obj:
            # Free up the bed if assigned
            if obj.bed_id:
                # Need to find the bed first
                bed_result = await db.execute(select(Bed).filter(Bed.id == obj.bed_id))
                bed = bed_result.scalars().first()
                if bed:
                    bed.status = "available"
                    db.add(bed)
            
            await db.delete(obj)
            await db.commit()
        return obj

    async def get_count(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count(Student.id)))
        return result.scalar_one()

    async def search(self, db: AsyncSession, query: str, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        search_pattern = f"%{query.lower()}%"
        
        # Base query with filters
        base_query = select(Student).filter(
            or_(
                Student.full_name.ilike(search_pattern),
                Student.student_id_number.ilike(search_pattern)
            )
        )

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated records
        records_query = base_query.offset(skip).limit(limit)
        records_result = await db.execute(records_query)
        records = list(records_result.scalars().all())

        return {"total": total, "records": records}

crud_student = CRUDStudent(Student)
