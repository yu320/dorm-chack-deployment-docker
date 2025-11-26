from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import json

from ... import schemas, auth, models
from ...crud import crud_backup, crud_user

def model_to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

router = APIRouter()

@router.get("/export", summary="Export All System Data", response_model=Dict[str, List[Dict[str, Any]]], dependencies=[Depends(auth.PermissionChecker("manage_users"))])
async def export_data(db: AsyncSession = Depends(auth.get_db)):
    """
    Exports all data from the system as a JSON object.
    Requires 'manage_users' permission.
    """
    
    # Define the order of export to handle foreign key dependencies
    export_order = [
        models.Permission, models.Role, models.User, models.Building, models.Room, models.Bed, models.Student,
        models.PatrolLocation, models.InspectionItem, models.InspectionRecord,
        models.InspectionDetail, models.Photo, models.LightsOutPatrol, models.LightsOutCheck, models.TokenBlocklist
    ]

    exported_data = {}
    for model in export_order:
        model_name = model.__tablename__
        try:
            records = await crud_user.get_all_records_from_model(db, model)
            exported_data[model_name] = [model_to_dict(record) for record in records]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to export data from {model_name}: {e}")

    return exported_data

@router.post("/import", summary="Import System Data", status_code=status.HTTP_200_OK, dependencies=[Depends(auth.PermissionChecker("manage_users"))])
async def import_data(file: UploadFile = File(...), db: AsyncSession = Depends(auth.get_db)):
    """
    Imports system data from a JSON file.
    WARNING: This operation will overwrite existing data. Use with caution.
    Requires 'manage_users' permission.
    """
    
    # Read and parse the uploaded JSON file
    try:
        contents = await file.read()
        data_to_import = json.loads(contents)
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON file.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to read file: {e}")
    
    # Define the order of import to handle foreign key dependencies (reverse of export)
    import_order = [
        models.Photo, models.InspectionDetail, models.InspectionRecord, models.InspectionItem,
        models.LightsOutCheck, models.LightsOutPatrol,
        models.Student, models.Bed, models.Room, models.Building, models.PatrolLocation,
        models.User, models.Role, models.Permission, models.TokenBlocklist # TokenBlocklist is likely independent
    ]

    try:
        await crud_backup.import_all_data(db, data_to_import, import_order)
        return {"message": "Data imported successfully!"}
    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to import data: {e}. Database changes have been rolled back.")
