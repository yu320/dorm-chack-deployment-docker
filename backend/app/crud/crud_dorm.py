from typing import List, Optional
import uuid
from datetime import datetime # Import datetime

from sqlalchemy.future import select
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, func

from ..models import Student, Room, Building, Bed
from .. import schemas, models
from ..schemas import StudentCreate, StudentUpdate, RoomCreate, RoomUpdate

# Student CRUD
async def create_student(db: AsyncSession, student: StudentCreate) -> Student:
    db_student = Student(**student.model_dump())
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    return db_student

async def get_student(db: AsyncSession, student_id: uuid.UUID) -> Optional[Student]:
    result = await db.execute(
        select(Student)
        .filter(Student.id == str(student_id))
        .options(
            joinedload(Student.bed).joinedload(Bed.room).joinedload(Room.building),
            joinedload(Student.user)
        )
    )
    return result.scalars().first()

async def get_student_by_id_number(db: AsyncSession, student_id_number: str) -> Optional[Student]:
    result = await db.execute(select(Student).filter(Student.student_id_number == student_id_number))
    return result.scalars().first()

async def get_students(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    full_name: Optional[str] = None,
    student_id_number: Optional[str] = None,
    class_name: Optional[str] = None,
    gender: Optional[str] = None,
    bed_id: Optional[int] = None,
    room_id: Optional[int] = None,
    building_id: Optional[int] = None,
    household: Optional[str] = None, # Added household
) -> dict:
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

async def update_student(db: AsyncSession, student_id: uuid.UUID, student_in: StudentUpdate) -> Optional[Student]:
    result = await db.execute(select(Student).filter(Student.id == str(student_id)))
    db_student = result.scalars().first()
    if not db_student:
        return None
    update_data = student_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_student, key, value)
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    return db_student

async def delete_student(db: AsyncSession, db_student: Student) -> None:
    # Free up the bed if assigned
    if db_student.bed_id:
        bed = await get_bed(db, db_student.bed_id)
        if bed:
            bed.status = "available"
            db.add(bed)
    
    await db.delete(db_student)
    await db.commit()

# Room CRUD
async def get_room(db: AsyncSession, room_id: int) -> Optional[Room]:
    result = await db.execute(select(Room).filter(Room.id == room_id).options(joinedload(Room.building)))
    return result.scalars().first()

async def get_rooms(db: AsyncSession, building_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> dict:
    query = select(Room).options(joinedload(Room.building))
    if building_id:
        query = query.filter(Room.building_id == building_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    records_query = query.order_by(Room.room_number).offset(skip).limit(limit)
    records_result = await db.execute(records_query)
    records = list(records_result.scalars().all())

    return {"total": total, "records": records}

async def get_room_by_building_and_number(db: AsyncSession, building_id: int, room_number: str) -> Optional[Room]:
    result = await db.execute(
        select(Room).filter(Room.building_id == building_id, Room.room_number == room_number)
    )
    return result.scalars().first()

async def create_room(db: AsyncSession, room: RoomCreate) -> Room:
    db_room = Room(**room.model_dump())
    db.add(db_room)
    await db.commit()
    await db.refresh(db_room)
    return db_room

async def update_room(db: AsyncSession, room_id: int, room_update: RoomUpdate) -> Optional[Room]:
    result = await db.execute(select(Room).filter(Room.id == room_id))
    db_room = result.scalars().first()
    if not db_room:
        return None
    update_data = room_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_room, key, value)
    db.add(db_room)
    await db.commit()
    await db.refresh(db_room)
    return db_room

async def delete_room(db: AsyncSession, room_id: int) -> Optional[Room]:
    result = await db.execute(select(Room).filter(Room.id == room_id))
    db_room = result.scalars().first()
    if db_room:
        await db.delete(db_room)
        await db.commit()
    return db_room

# Building CRUD
async def create_building(db: AsyncSession, building: schemas.BuildingCreate) -> Building:
    db_building = Building(**building.model_dump())
    db.add(db_building)
    await db.commit()
    await db.refresh(db_building)
    return db_building

async def get_building(db: AsyncSession, building_id: int) -> Optional[Building]:
    result = await db.execute(select(Building).filter(Building.id == building_id))
    return result.scalars().first()

async def get_building_by_name(db: AsyncSession, name: str) -> Optional[Building]:
    result = await db.execute(select(Building).filter(Building.name == name))
    return result.scalars().first()

async def get_buildings(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Building]:
    result = await db.execute(select(Building).offset(skip).limit(limit))
    return list(result.scalars().all())

async def update_building(db: AsyncSession, db_building: Building, building_in: schemas.BuildingCreate) -> Building:
    update_data = building_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_building, key, value)
    db.add(db_building)
    await db.commit()
    await db.refresh(db_building)
    return db_building

async def delete_building(db: AsyncSession, db_building: Building) -> None:
    await db.delete(db_building)
    await db.commit()

async def get_buildings_full_tree(db: AsyncSession) -> List[Building]:
    result = await db.execute(
        select(Building).options(
            selectinload(Building.rooms).selectinload(Room.beds)
        ).order_by(Building.name)
    )
    return list(result.scalars().unique().all())


async def search_students(db: AsyncSession, query: str, skip: int = 0, limit: int = 100) -> dict:
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

async def search_rooms(db: AsyncSession, query: str, skip: int = 0, limit: int = 100) -> dict:
    search_pattern = f"%{query.lower()}%"
    
    # Base query with filters
    base_query = select(Room).options(joinedload(Room.building)).filter(
        or_(
            Room.room_number.ilike(search_pattern),
            Room.household.ilike(search_pattern)
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

async def get_students_count(db: AsyncSession) -> int:
    result = await db.execute(select(func.count(Student.id)))
    return result.scalar_one()

async def get_rooms_count(db: AsyncSession) -> int:
    result = await db.execute(select(func.count(Room.id)))
    return result.scalar_one()


# Bed CRUD
async def get_bed(db: AsyncSession, bed_id: int) -> Optional[Bed]:
    result = await db.execute(select(Bed).filter(Bed.id == bed_id))
    return result.scalars().first()

async def get_student_by_bed_id(db: AsyncSession, bed_id: int) -> Optional[Student]:
    result = await db.execute(select(Student).filter(Student.bed_id == bed_id))
    return result.scalars().first()

async def get_students_by_room(db: AsyncSession, room_id: int) -> List[Student]:
    result = await db.execute(
        select(Student)
        .join(Bed)
        .join(Room)
        .filter(Room.id == room_id)
        .options(joinedload(Student.bed).joinedload(Bed.room))
    )
    return list(result.scalars().all())

async def get_students_by_household(db: AsyncSession, household: str) -> List[Student]:
    result = await db.execute(
        select(Student)
        .join(Bed)
        .join(Room)
        .filter(Room.household == household)
        .options(joinedload(Student.bed).joinedload(Bed.room))
    )
    return list(result.scalars().all())

async def get_students_by_building(db: AsyncSession, building_id: int) -> List[Student]:
    result = await db.execute(
        select(Student)
        .join(Bed)
        .join(Room)
        .filter(Room.building_id == building_id)
        .options(joinedload(Student.bed).joinedload(Bed.room))
    )
    return list(result.scalars().all())

async def assign_student_to_bed(db: AsyncSession, db_student: Student, bed_id: Optional[int]) -> Student:
    # 1. If student had a previous bed, free it
    if db_student.bed_id:
        prev_bed = await get_bed(db, db_student.bed_id)
        if prev_bed:
            prev_bed.status = "available"
            db.add(prev_bed)
    
    # 2. Assign new bed
    db_student.bed_id = bed_id
    
    # 3. Mark new bed as occupied (only if bed_id is not None)
    if bed_id:
        new_bed = await get_bed(db, bed_id)
        if new_bed:
            new_bed.status = "occupied"
            db.add(new_bed)
        
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    return db_student

# Bed CRUD
async def create_bed(db: AsyncSession, bed_in: schemas.BedCreate) -> Bed:
    db_bed = Bed(**bed_in.model_dump())
    db.add(db_bed)
    await db.commit()
    await db.refresh(db_bed)
    return db_bed

async def get_bed(db: AsyncSession, bed_id: int) -> Optional[Bed]:
    result = await db.execute(select(Bed).filter(Bed.id == bed_id).options(joinedload(Bed.room).joinedload(Room.building)))
    return result.scalars().first()

async def get_bed_by_number(db: AsyncSession, room_id: int, bed_number: str) -> Optional[Bed]:
    result = await db.execute(
        select(Bed).filter(Bed.room_id == room_id, Bed.bed_number == bed_number)
    )
    return result.scalars().first()

async def get_beds(db: AsyncSession, skip: int = 0, limit: int = 100) -> dict:
    query = select(Bed).options(joinedload(Bed.room).joinedload(Room.building))
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    records_query = query.order_by(Bed.bed_number).offset(skip).limit(limit)
    records_result = await db.execute(records_query)
    records = list(records_result.scalars().all())

    return {"total": total, "records": records}

async def update_bed(db: AsyncSession, db_bed: Bed, bed_in: schemas.BedUpdate) -> Bed:
    update_data = bed_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_bed, key, value)
    db.add(db_bed)
    await db.commit()
    await db.refresh(db_bed)
    return db_bed

async def delete_bed(db: AsyncSession, db_bed: Bed) -> None:
    await db.delete(db_bed)
    await db.commit()

# Lights Out Patrol CRUD
async def create_lights_out_patrol(db: AsyncSession, patrol_in: schemas.LightsOutPatrolCreate, patroller_id: uuid.UUID) -> models.LightsOutPatrol:
    async with db.begin_nested():
        db_patrol = models.LightsOutPatrol(
            building_id=patrol_in.building_id,
            patroller_id=patroller_id,
            patrol_time=datetime.now()
        )
        db.add(db_patrol)
        await db.flush() # Flush to get patrol.id
        
        for check_in in patrol_in.checks:
            db_check = models.LightsOutCheck(
                patrol_id=db_patrol.id,
                patrol_location_id=check_in.patrol_location_id,
                status=check_in.status,
                notes=check_in.notes
            )
            db.add(db_check)
        await db.commit()
    await db.refresh(db_patrol, attribute_names=["building", "patroller", "checks"])
    return db_patrol

async def get_lights_out_patrols(db: AsyncSession, skip: int = 0, limit: int = 100, building_id: Optional[int] = None) -> dict:
    query = select(models.LightsOutPatrol).options(
        joinedload(models.LightsOutPatrol.building),
        joinedload(models.LightsOutPatrol.patroller),
        joinedload(models.LightsOutPatrol.checks).joinedload(models.LightsOutCheck.location)
    )
    if building_id:
        query = query.filter(models.LightsOutPatrol.building_id == building_id)
        
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    records_query = query.order_by(models.LightsOutPatrol.patrol_time.desc()).offset(skip).limit(limit)
    records_result = await db.execute(records_query)
    records = list(records_result.scalars().unique().all())

    return {"total": total, "records": records}

async def get_or_create_building(db: AsyncSession, name: str) -> Building:
    db_building = await get_building_by_name(db, name=name)
    if db_building:
        return db_building
    building_in = schemas.BuildingCreate(name=name)
    return await create_building(db=db, building=building_in)

async def get_or_create_room(db: AsyncSession, building_id: int, room_number: str, household: Optional[str] = None, room_type: Optional[str] = None) -> Room:
    db_room = await get_room_by_building_and_number(db, building_id=building_id, room_number=room_number)
    if db_room:
        return db_room
    room_in = schemas.RoomCreate(building_id=building_id, room_number=room_number, household=household, room_type=room_type)
    return await create_room(db=db, room=room_in)

async def get_or_create_bed(db: AsyncSession, room_id: int, bed_number: str, bed_type: Optional[str] = None, status: Optional[str] = "available") -> Bed:
    db_bed = await get_bed_by_number(db, room_id=room_id, bed_number=bed_number)
    if db_bed:
        return db_bed
    bed_in = schemas.BedCreate(room_id=room_id, bed_number=bed_number, bed_type=bed_type, status=status)
    return await create_bed(db=db, bed_in=bed_in)

async def update_or_create_student(db: AsyncSession, student_data: schemas.StudentCreate) -> Student:
    existing_student = await get_student_by_id_number(db, student_id_number=student_data.student_id_number)
    if existing_student:
        # Update existing student
        student_update = schemas.StudentUpdate(**student_data.model_dump(exclude_unset=True))
        return await update_student(db=db, student_id=existing_student.id, student_update=student_update)
    else:
        # Create new student
        return await create_student(db=db, student=student_data)

# Patrol Location CRUD
async def create_patrol_location(db: AsyncSession, location_in: schemas.PatrolLocationCreate) -> models.PatrolLocation:
    db_location = models.PatrolLocation(**location_in.model_dump())
    db.add(db_location)
    await db.commit()
    await db.refresh(db_location)
    return db_location

async def get_patrol_location(db: AsyncSession, location_id: uuid.UUID) -> Optional[models.PatrolLocation]:
    result = await db.execute(
        select(models.PatrolLocation)
        .filter(models.PatrolLocation.id == str(location_id))
        .options(joinedload(models.PatrolLocation.building))
    )
    return result.scalars().first()

async def get_patrol_locations_by_building(
    db: AsyncSession, building_id: int, skip: int = 0, limit: int = 100
) -> dict:
    query = (
        select(models.PatrolLocation)
        .filter(models.PatrolLocation.building_id == building_id)
        .options(joinedload(models.PatrolLocation.building))
    )
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    records_query = query.order_by(models.PatrolLocation.name).offset(skip).limit(limit)
    records_result = await db.execute(records_query)
    records = list(records_result.scalars().all())

    return {"total": total, "records": records}


async def update_patrol_location(
    db: AsyncSession, db_location: models.PatrolLocation, location_in: schemas.PatrolLocationUpdate
) -> models.PatrolLocation:
    update_data = location_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_location, key, value)
    db.add(db_location)
    await db.commit()
    await db.refresh(db_location)
    return db_location

async def delete_patrol_location(db: AsyncSession, db_location: models.PatrolLocation) -> models.PatrolLocation:
    await db.delete(db_location)
    await db.commit()
    return db_location

async def validate_student_bed(db: AsyncSession, student_id: str, bed_number: str) -> bool:
    """
    Validates if the student is assigned to the bed with the given bed_number.
    """
    result = await db.execute(
        select(Student)
        .join(Bed, Student.bed_id == Bed.id)
        .filter(Student.id == student_id, Bed.bed_number == bed_number)
    )
    student = result.scalars().first()
    return student is not None
