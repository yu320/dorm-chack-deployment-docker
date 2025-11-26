from typing import List, Optional
import uuid
from datetime import datetime

from sqlalchemy.future import select
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, func

from ..models import Bed, InspectionItem, Photo, InspectionDetail, InspectionRecord, Student, Room, InspectionStatus
from ..schemas import InspectionItemCreate, InspectionItemUpdate, InspectionRecordCreate, InspectionRecordUpdate, InspectionDetailCreate, PhotoCreate, ItemStatus, InspectionCreate


async def get_inspection_record(db: AsyncSession, record_id: uuid.UUID) -> Optional[InspectionRecord]:
    result = await db.execute(
        select(InspectionRecord)
        .filter(InspectionRecord.id == str(record_id))
        .options(
            joinedload(InspectionRecord.student).joinedload(Student.bed).joinedload(Bed.room).joinedload(Room.building),
            selectinload(InspectionRecord.room).selectinload(Room.building),
            selectinload(InspectionRecord.details).selectinload(InspectionDetail.item),
            selectinload(InspectionRecord.details).selectinload(InspectionDetail.photos)
        )
    )
    return result.scalars().first()

async def get_active_inspection_by_student(db: AsyncSession, student_id: uuid.UUID) -> Optional[InspectionRecord]:
    result = await db.execute(
        select(InspectionRecord)
        .filter(
            InspectionRecord.student_id == student_id,
            InspectionRecord.status == InspectionStatus.pending
        )
        .options(selectinload(InspectionRecord.student))
    )
    return result.scalars().first()

async def get_inspection_records(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    student_id: Optional[uuid.UUID] = None,
    room_id: Optional[int] = None,
    status: Optional[ItemStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    student_full_name: Optional[str] = None,
    item_status: Optional[ItemStatus] = None,
    sort_by: Optional[str] = "created_at",
    sort_direction: Optional[str] = "desc"
) -> dict:
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
    if status:
        query = query.filter(InspectionRecord.status == status)
    if start_date:
        query = query.filter(InspectionRecord.created_at >= start_date)
    if end_date:
        query = query.filter(InspectionRecord.created_at <= end_date)
    if student_full_name:
        query = query.join(Student).filter(Student.full_name.ilike(f"%{student_full_name}%"))
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

async def search_inspections(
    db: AsyncSession,
    student_name: Optional[str] = None,
    room_number: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> dict:
    query = select(InspectionRecord).options(
        joinedload(InspectionRecord.student).joinedload(Student.bed).joinedload(Bed.room).joinedload(Room.building),
        selectinload(InspectionRecord.room).selectinload(Room.building),
        selectinload(InspectionRecord.details).selectinload(InspectionDetail.item),
        selectinload(InspectionRecord.details).selectinload(InspectionDetail.photos)
    )

    if student_name:
        query = query.join(Student).filter(Student.full_name.ilike(f"%{student_name}%"))
    
    if room_number:
        query = query.join(Room).filter(Room.room_number.ilike(f"%{room_number}%"))

    if status:
        query = query.filter(InspectionRecord.status == status)

    if start_date:
        query = query.filter(InspectionRecord.created_at >= start_date)

    if end_date:
        query = query.filter(InspectionRecord.created_at <= end_date)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    records_query = query.offset(skip).limit(limit)
    records_result = await db.execute(records_query)
    records = list(records_result.scalars().all())
    
    return {"total": total, "records": records}

async def get_inspection_records_by_student(
    db: AsyncSession,
    student_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> dict:
    query = select(InspectionRecord).filter(InspectionRecord.student_id == student_id).options(
        joinedload(InspectionRecord.student).joinedload(Student.bed).joinedload(Bed.room).joinedload(Room.building),
        selectinload(InspectionRecord.room).selectinload(Room.building),
        selectinload(InspectionRecord.details).selectinload(InspectionDetail.item),
        selectinload(InspectionRecord.details).selectinload(InspectionDetail.photos)
    )

    if start_date:
        query = query.filter(InspectionRecord.created_at >= start_date)
    if end_date:
        query = query.filter(InspectionRecord.created_at <= end_date)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    records_query = query.order_by(InspectionRecord.created_at.desc()).offset(skip).limit(limit)
    records_result = await db.execute(records_query)
    records = list(records_result.scalars().unique().all())

    return {"total": total, "records": records}


async def update_inspection_record(db: AsyncSession, db_record: InspectionRecord, record_in: InspectionRecordUpdate) -> InspectionRecord:
    update_data = record_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)
    db.add(db_record)
    await db.commit()
    await db.refresh(db_record)
    return db_record

async def get_image_by_filename(db: AsyncSession, filename: str) -> Optional[Photo]:
    result = await db.execute(
        select(Photo)
        .filter(Photo.file_path == filename)
        .options(
            selectinload(Photo.inspection_detail)
            .selectinload(InspectionDetail.record)
            .selectinload(InspectionRecord.student)
        )
    )
    return result.scalars().first()

async def get_inspection_items(db: AsyncSession, skip: int = 0, limit: int = 100) -> dict:
    query = select(InspectionItem)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    records_query = query.order_by(InspectionItem.name).offset(skip).limit(limit)
    records_result = await db.execute(records_query)
    records = list(records_result.scalars().all())

    return {"total": total, "records": records}

async def create_inspection_item(db: AsyncSession, item: InspectionItemCreate) -> InspectionItem:
    db_item = InspectionItem(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def get_inspection_item(db: AsyncSession, item_id: uuid.UUID) -> Optional[InspectionItem]:
    result = await db.execute(select(InspectionItem).filter(InspectionItem.id == item_id))
    return result.scalars().first()

async def update_inspection_item(db: AsyncSession, item_id: uuid.UUID, item_update: InspectionItemUpdate) -> Optional[InspectionItem]:
    result = await db.execute(select(InspectionItem).filter(InspectionItem.id == item_id))
    db_item = result.scalars().first()
    if not db_item:
        return None
    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def delete_inspection_item(db: AsyncSession, item_id: uuid.UUID) -> Optional[InspectionItem]:
    result = await db.execute(select(InspectionItem).filter(InspectionItem.id == item_id))
    db_item = result.scalars().first()
    if db_item:
        await db.delete(db_item)
        await db.commit()
    return db_item

async def batch_create_inspection_records(
    db: AsyncSession,
    inspections_in: List[InspectionCreate],
    inspector_id: uuid.UUID
) -> List[InspectionRecord]:
    created_records = []
    
    for inspection_in in inspections_in:
        if not inspection_in.student_id:
            continue # Skip if no student ID (should be validated before)

        db_inspection_record = InspectionRecord(
            student_id=str(inspection_in.student_id),
            room_id=inspection_in.room_id,
            inspector_id=str(inspector_id),
            signature=None, # Batch create typically doesn't have individual signatures per record unless passed, handled below
            status=InspectionStatus.submitted,
            submitted_at=datetime.now(),
        )
        
        # Handle signature if present in individual inspection
        if inspection_in.signature_base64:
             # This assumes signature handling (upload) is done in service layer and passed as filename, 
             # but here we are in CRUD receiving InspectionCreate which has base64.
             # Ideally service handles upload and passes a DTO with filenames.
             # For simplicity in this refactor, we might need to update the schema passed to CRUD 
             # or handle upload in Service loop. Let's stick to Service handling upload.
             # Wait, InspectionCreate has `signature_base64`. 
             # `create_inspection_record` takes `signature_filename`.
             # We should probably change `BatchInspectionCreate` to use a different schema or handle logic in Service.
             pass # Will be handled by setting signature attribute if passed separately?
             # Actually, let's assume Service handles uploads and we need a way to pass filenames.
             # But `inspections_in` is `List[InspectionCreate]`.
             # Let's modify this function to accept `List[dict]` or similar where we have processed data?
             # Or, let's keep it simple: Batch inspection usually implies admin doing it, maybe no student signature?
             # Or admin signature?
             
        db.add(db_inspection_record)
        await db.flush() # Need ID for details

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
    
    # Refetch is expensive for batch. Maybe just return IDs or basic info?
    # Or refetch if needed. Let's skip full refetch for performance unless required.
    return created_records

async def batch_create_inspection_records(
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

async def create_inspection_record(
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
    
    # Re-fetch the record with all relationships loaded to avoid MissingGreenlet error during serialization
    result = await db.execute(
        select(InspectionRecord)
        .filter(InspectionRecord.id == str(db_inspection_record.id))
        .options(
            joinedload(InspectionRecord.student),
            joinedload(InspectionRecord.room).joinedload(Room.building),
            selectinload(InspectionRecord.details).selectinload(InspectionDetail.item),
            selectinload(InspectionRecord.details).selectinload(InspectionDetail.photos)
        )
    )
    return result.scalars().first()

async def get_inspection_images(db: AsyncSession, inspection_id: uuid.UUID) -> List[Photo]:
    result = await db.execute(select(Photo).filter(Photo.inspection_id == inspection_id))
    return list(result.scalars().all())

async def get_inspection_image_path(db: AsyncSession, image_id: uuid.UUID) -> Optional[str]:
    result = await db.execute(select(Photo).filter(Photo.id == image_id))
    image = result.scalars().first()
    return image.image_path if image else None

async def delete_inspection_image(db: AsyncSession, image_id: uuid.UUID) -> Optional[Photo]:
    result = await db.execute(select(Photo).filter(Photo.id == image_id))
    db_image = result.scalars().first()
    if db_image:
        await db.delete(db_image)
        await db.commit()
    return db_image

async def get_inspections_count_today(db: AsyncSession) -> int:
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count(InspectionRecord.id))
        .filter(InspectionRecord.created_at >= today_start)
    )
    return result.scalar_one()

async def get_inspection_issues_count(db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count(InspectionDetail.id))
        .filter(InspectionDetail.status.in_(['damaged', 'missing']))
    )
    return result.scalar_one()

async def get_inspection_status_distribution(db: AsyncSession) -> dict:
    result = await db.execute(
        select(InspectionRecord.status, func.count(InspectionRecord.id))
        .group_by(InspectionRecord.status)
    )
    return {status.name: count for status, count in result.all()}

async def get_damage_ranking(db: AsyncSession, limit: int = 5) -> List[dict]:
    result = await db.execute(
        select(InspectionItem.name, func.count(InspectionDetail.id).label('count'))
        .join(InspectionItem, InspectionDetail.item_id == InspectionItem.id)
        .filter(InspectionDetail.status.in_(['damaged', 'missing']))
        .group_by(InspectionItem.name)
        .order_by(func.count(InspectionDetail.id).desc())
        .limit(limit)
    )
    return [{"name": name, "count": count} for name, count in result.all()]
