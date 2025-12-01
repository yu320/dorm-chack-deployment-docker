from typing import List, Optional, Any, Dict
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from app.models import LightsOutPatrol, LightsOutCheck, PatrolLocation, Building, User
from app.schemas import LightsOutPatrolCreate, LightsOutCheckCreate
from .base import CRUDBase

class CRUDLightsOutPatrol(CRUDBase[LightsOutPatrol, LightsOutPatrolCreate, Dict[str, Any]]): # Using Dict for update as LightsOutPatrolUpdate might not exist
    async def get(self, db: AsyncSession, id: Any) -> Optional[LightsOutPatrol]:
        result = await db.execute(
            select(LightsOutPatrol)
            .filter(LightsOutPatrol.id == str(id))
            .options(
                joinedload(LightsOutPatrol.building),
                joinedload(LightsOutPatrol.patroller),
                joinedload(LightsOutPatrol.checks).joinedload(LightsOutCheck.location)
            )
        )
        return result.scalars().first()

    async def get_multi_filtered(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, building_id: Optional[int] = None
    ) -> Dict[str, Any]:
        query = select(LightsOutPatrol).options(
            joinedload(LightsOutPatrol.building),
            joinedload(LightsOutPatrol.patroller),
            joinedload(LightsOutPatrol.checks).joinedload(LightsOutCheck.location)
        )
        if building_id:
            query = query.filter(LightsOutPatrol.building_id == building_id)
            
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        records_query = query.order_by(LightsOutPatrol.patrol_time.desc()).offset(skip).limit(limit)
        records_result = await db.execute(records_query)
        records = list(records_result.scalars().unique().all())

        return {"total": total, "records": records}
    
    async def create_with_checks(self, db: AsyncSession, patrol_in: LightsOutPatrolCreate, patroller_id: uuid.UUID) -> LightsOutPatrol:
        async with db.begin_nested(): # Use begin_nested for transactions within an async session
            db_patrol = LightsOutPatrol(
                building_id=patrol_in.building_id,
                patroller_id=patroller_id,
                patrol_time=datetime.now()
            )
            db.add(db_patrol)
            await db.flush() # Flush to get patrol.id
            
            for check_in in patrol_in.checks:
                db_check = LightsOutCheck(
                    patrol_id=db_patrol.id,
                    patrol_location_id=check_in.patrol_location_id,
                    status=check_in.status,
                    notes=check_in.notes
                )
                db.add(db_check)
            await db.commit() # Commit the nested transaction
        
        # After commit, refresh to load relationships
        await db.refresh(db_patrol, attribute_names=["building", "patroller", "checks"])
        return db_patrol

crud_lights_out = CRUDLightsOutPatrol(LightsOutPatrol)
