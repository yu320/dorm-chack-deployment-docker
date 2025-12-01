from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Type
from sqlalchemy import insert, select
from sqlalchemy.orm import class_mapper

from .. import models

class CRUDBackup:
    async def get_all_records_from_model(self, db: AsyncSession, model: Type[models.Base]) -> List[Dict[str, Any]]:
        """
        Fetches all records from a given model and returns them as a list of dictionaries.
        """
        result = await db.execute(select(model))
        records = result.scalars().all()
        
        # Serialize records to dicts
        return [
            {c.key: getattr(r, c.key) for c in class_mapper(model).columns}
            for r in records
        ]

    async def import_all_data(self, db: AsyncSession, data_to_import: Dict[str, List[Dict[str, Any]]], import_order: List[Type[models.Base]]):
        """
        Imports all data from a dictionary into the database, respecting foreign key dependencies
        and ensuring atomicity with a database transaction.
        """
        async with db.begin():
            for model in import_order:
                table_name = model.__tablename__
                records_to_insert = data_to_import.get(table_name, [])

                if not records_to_insert:
                    continue

                # Convert dictionary keys to column names for SQLAlchemy
                # This is a simplified conversion, actual implementation might need more robust mapping
                model_mapper = class_mapper(model)
                mapped_records = []
                for record_data in records_to_insert:
                    mapped_record = {}
                    for key, value in record_data.items():
                        # Handle special cases like UUID strings to actual UUID objects
                        if isinstance(value, str) and (key == 'id' or key.endswith('_id')) and len(value) == 36 and '-' in value:
                            try:
                                value = str(value) # ensure it's treated as string for insertion
                            except ValueError:
                                pass # not a UUID, keep as string
                        mapped_record[key] = value
                    mapped_records.append(mapped_record)

                if mapped_records:
                    await db.execute(insert(model).values(mapped_records))

backup_crud = CRUDBackup()

