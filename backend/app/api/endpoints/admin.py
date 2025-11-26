from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from ... import auth, crud, models

router = APIRouter()

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List
import io
import zipfile
import csv
import uuid
from datetime import datetime

from ... import auth, crud, models, schemas

router = APIRouter()

# Define a mapping of table names to SQLAlchemy models for export
# Only include models that are safe and sensible to export via this endpoint
EXPORTABLE_MODELS = {
    "users": models.User,
    "roles": models.Role,
    "permissions": models.Permission,
    "buildings": models.Building,
    "rooms": models.Room,
    "beds": models.Bed,
    "students": models.Student,
    "inspection_items": models.InspectionItem,
    "inspection_records": models.InspectionRecord,
    "inspection_details": models.InspectionDetail,
    "photos": models.Photo,
    "patrol_locations": models.PatrolLocation,
    "lights_out_patrols": models.LightsOutPatrol,
    "lights_out_checks": models.LightsOutCheck,
    "token_blocklist": models.TokenBlocklist,
}

@router.post("/export-data", dependencies=[Depends(auth.PermissionChecker("manage_users"))])
async def export_data_to_csv(
    export_request: schemas.DataExportRequest,
    db: AsyncSession = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Exports data from specified tables to CSV format within a ZIP archive.
    Requires 'manage_users' permission.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for table_name in export_request.table_names:
            if table_name not in EXPORTABLE_MODELS:
                raise HTTPException(
                    status_code=400, detail=f"Table '{table_name}' is not exportable or does not exist."
                )
            
            model = EXPORTABLE_MODELS[table_name]
            records = await crud.get_all_records_from_model(db, model)

            if not records:
                # Create an empty CSV file if no records
                zip_file.writestr(f"{table_name}.csv", "")
                continue

            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)

            # Write header
            # Exclude relationship attributes and internal SQLAlchemy state
            # Get column names from the model's __table__.columns
            column_names = [column.name for column in model.__table__.columns]
            writer.writerow(column_names)

            # Write data rows
            for record in records:
                row = []
                for col_name in column_names:
                    value = getattr(record, col_name, None)
                    # Handle UUIDs and other complex types if necessary
                    if isinstance(value, uuid.UUID):
                        row.append(str(value))
                    elif isinstance(value, datetime):
                        row.append(value.isoformat())
                    elif isinstance(value, (models.InspectionStatus, models.ItemStatus, models.LightStatus)):
                        row.append(value.value)
                    else:
                        row.append(value)
                writer.writerow(row)
            
            zip_file.writestr(f"{table_name}.csv", csv_buffer.getvalue())
    
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=data_export.zip"}
    )
