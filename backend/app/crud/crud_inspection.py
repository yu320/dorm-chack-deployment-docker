from typing import List, Optional, Any, Dict
import uuid
from datetime import datetime

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, func

from app.models import Bed, InspectionItem, Photo, InspectionDetail, InspectionRecord, Student, Room, InspectionStatus
from app.schemas import InspectionRecordCreate, InspectionRecordUpdate, InspectionCreate, ItemStatus
from .base import CRUDBase

class CRUDInspection(CRUDBase[InspectionRecord, InspectionRecordCreate, InspectionRecordUpdate]):
    
    async def get(self, db: AsyncSession, id: Any) -> Optional[InspectionRecord]:
        result = await db.execute(
            select(InspectionRecord)
            .filter(InspectionRecord.id == str(id))
            .options(
                joinedload(InspectionRecord.student).joinedload(Student.bed).joinedload(Bed.room).joinedload(Room.building),
                selectinload(InspectionRecord.room).selectinload(Room.building),
                selectinload(InspectionRecord.details).selectinload(InspectionDetail.item),
                selectinload(InspectionRecord.details).selectinload(InspectionDetail.photos)
            )
        )
        return result.scalars().first()

    async def get_active_by_student(self, db: AsyncSession, student_id: uuid.UUID) -> Optional[InspectionRecord]:
        result = await db.execute(
            select(InspectionRecord)
            .filter(
                InspectionRecord.student_id == student_id,
                InspectionRecord.status == InspectionStatus.pending
            )
            .options(selectinload(InspectionRecord.student))
        )
        return result.scalars().first()

    async def get_multi_filtered(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        student_id: Optional[uuid.UUID] = None,
        room_id: Optional[int] = None,
        building_id: Optional[int] = None, # Added
        status: Optional[ItemStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        student_full_name: Optional[str] = None,
        student_name: Optional[str] = None,
        room_number: Optional[str] = None,
        item_status: Optional[ItemStatus] = None,
        sort_by: Optional[str] = "created_at",
        sort_direction: Optional[str] = "desc"
    ) -> Dict[str, Any]:
        
        query = select(InspectionRecord).options(
            joinedload(InspectionRecord.student).joinedload(Student.bed).joinedload(Bed.room).joinedload(Room.building),
            selectinload(InspectionRecord.room).selectinload(Room.building),
            selectinload(InspectionRecord.details).selectinload(InspectionDetail.item),
            selectinload(InspectionRecord.details).selectinload(InspectionDetail.photos)
        )

        if student_id:
            query = query.filter(InspectionRecord.student_id == student_id)
        if room_id:
            query = query.filter(InspectionRecord.room_id == room_id)
        if building_id: # Added filter
            query = query.join(Room).filter(Room.building_id == building_id)
        if status:
            query = query.filter(InspectionRecord.status == status)
        if start_date:
            query = query.filter(InspectionRecord.created_at >= start_date)
        if end_date:
            query = query.filter(InspectionRecord.created_at <= end_date)
        
        # Handle both parameter names for student name search
        search_name = student_full_name or student_name
        if search_name:
            query = query.join(Student).filter(Student.full_name.ilike(f"%{search_name}%"))
            
        if room_number:
             query = query.join(Room).filter(Room.room_number.ilike(f"%{room_number}%"))

        if item_status:
            query = query.join(InspectionRecord.details).filter(InspectionDetail.status == item_status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        if sort_by == "created_at":
            order_by_column = InspectionRecord.created_at.desc() if sort_direction == "desc" else InspectionRecord.created_at.asc()
            query = query.order_by(order_by_column)

        records_query = query.offset(skip).limit(limit)
        records_result = await db.execute(records_query)
        records = list(records_result.scalars().unique().all())

        return {"total": total, "records": records}

    async def create_with_details(
        self,
        db: AsyncSession,
        inspection_in: InspectionCreate,
        student_id: uuid.UUID,
        inspector_id: uuid.UUID,
        signature_filename: Optional[str] = None
    ) -> InspectionRecord:
        db_inspection_record = InspectionRecord(
            student_id=str(student_id),
            room_id=inspection_in.room_id,
            inspector_id=str(inspector_id),
            signature=signature_filename,
            status=InspectionStatus.submitted,
            submitted_at=datetime.now(),
        )
        db.add(db_inspection_record)
        await db.flush()

        for detail_in in inspection_in.details:
            db_inspection_detail = InspectionDetail(
                record_id=str(db_inspection_record.id),
                item_id=str(detail_in.item_id),
                status=detail_in.status,
                comment=detail_in.comment
            )
            db.add(db_inspection_detail)
            await db.flush()

            if detail_in.photos:
                for photo_in in detail_in.photos:
                    db_inspection_image = Photo(
                        detail_id=str(db_inspection_detail.id),
                        file_path=photo_in.file_path
                    )
                    db.add(db_inspection_image)
        
        await db.commit()
        
        # Re-fetch
        return await self.get(db, db_inspection_record.id)

    async def batch_create(
        self,
        db: AsyncSession,
        data: List[tuple[InspectionCreate, Optional[str]]],
        inspector_id: uuid.UUID
    ) -> List[InspectionRecord]:
        created_records = []
        
        for inspection_in, signature_filename in data:
            if not inspection_in.student_id:
                continue

            db_inspection_record = InspectionRecord(
                student_id=str(inspection_in.student_id),
                room_id=inspection_in.room_id,
                inspector_id=str(inspector_id),
                signature=signature_filename,
                status=InspectionStatus.submitted,
                submitted_at=datetime.now(),
            )
            
            db.add(db_inspection_record)
            await db.flush()

            for detail_in in inspection_in.details:
                db_inspection_detail = InspectionDetail(
                    record_id=str(db_inspection_record.id),
                    item_id=str(detail_in.item_id),
                    status=detail_in.status,
                    comment=detail_in.comment
                )
                db.add(db_inspection_detail)
                await db.flush()

                if detail_in.photos:
                    for photo_in in detail_in.photos:
                        db_inspection_image = Photo(
                            detail_id=str(db_inspection_detail.id),
                            file_path=photo_in.file_path
                        )
                        db.add(db_inspection_image)
            
            created_records.append(db_inspection_record)

        await db.commit()
        return created_records

    async def update(self, db: AsyncSession, *, db_obj: InspectionRecord, obj_in: Any) -> InspectionRecord:
        # Default update mostly works, but if details change, logic is complex.
        # For now, standard field update.
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    # --- Statistics ---
    async def get_count_today(self, db: AsyncSession) -> int:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await db.execute(
            select(func.count(InspectionRecord.id))
            .filter(InspectionRecord.created_at >= today_start)
        )
        return result.scalar_one()

    async def get_issues_count(self, db: AsyncSession) -> int:
        result = await db.execute(
            select(func.count(InspectionDetail.id))
            .filter(InspectionDetail.status.in_(['damaged', 'missing']))
        )
        return result.scalar_one()

    async def get_status_distribution(self, db: AsyncSession) -> dict:
        result = await db.execute(
            select(InspectionRecord.status, func.count(InspectionRecord.id))
            .group_by(InspectionRecord.status)
        )
        return {status.name: count for status, count in result.all()}

    async def get_damage_ranking(self, db: AsyncSession, limit: int = 5) -> List[dict]:
        result = await db.execute(
            select(InspectionItem.name, func.count(InspectionDetail.id).label('count'))
            .join(InspectionItem, InspectionDetail.item_id == InspectionItem.id)
            .filter(InspectionDetail.status.in_(['damaged', 'missing']))
            .group_by(InspectionItem.name)
            .order_by(func.count(InspectionDetail.id).desc())
            .limit(limit)
        )
        return [{"name": name, "count": count} for name, count in result.all()]

    async def search(
        self,
        db: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        # Basic search by student name or room number
        search_pattern = f"%{query.lower()}%"
        
        base_query = select(InspectionRecord).options(
            joinedload(InspectionRecord.student).joinedload(Student.bed).joinedload(Bed.room).joinedload(Room.building),
            selectinload(InspectionRecord.room).selectinload(Room.building)
        ).join(Student).join(Room).filter(
            or_(
                Student.full_name.ilike(search_pattern),
                Room.room_number.ilike(search_pattern)
            )
        )

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated records
        records_query = base_query.order_by(InspectionRecord.created_at.desc()).offset(skip).limit(limit)
        records_result = await db.execute(records_query)
        records = list(records_result.scalars().unique().all())

        return {"total": total, "records": records}

crud_inspection = CRUDInspection(InspectionRecord)