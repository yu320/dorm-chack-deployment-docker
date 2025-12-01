# backend/app/services/inspection_service.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends

from ..crud import crud_inspection
from ..schemas import InspectionCreate, BatchInspectionCreate

from .. import models
from .file_service import file_service
from ..database import get_db

class InspectionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def batch_create_inspection_reports(
        self,
        batch_in: BatchInspectionCreate,
        inspector_id: UUID
    ) -> List[models.InspectionRecord]:
        
        data_to_create = []

        for inspection_in in batch_in.inspections:
            # Handle signature image
            signature_filename = None
            if inspection_in.signature_base64:
                try:
                    signature_filename = await file_service.decode_and_upload_base64_image(inspection_in.signature_base64)
                except HTTPException as e:
                    # In batch, maybe log error and skip signature? Or fail whole batch?
                    # Let's fail whole batch for consistency or catch and continue.
                    # Raising exception here will stop the whole batch.
                    raise HTTPException(status_code=e.status_code, detail=f"Failed to upload signature: {e.detail}")

            # Handle images within inspection items
            for detail in inspection_in.details:
                if detail.photos:
                    for photo in detail.photos:
                        try:
                            photo_filename = await file_service.decode_and_upload_base64_image(photo.file_content)
                            photo.file_path = photo_filename
                        except HTTPException as e:
                            raise HTTPException(status_code=e.status_code, detail=f"Failed to upload item photo for item: {e.detail}")
            
            data_to_create.append((inspection_in, signature_filename))

        # Create records in database
        return await crud_inspection.batch_create(
            self.db,
            data=data_to_create,
            inspector_id=inspector_id
        )

    async def create_inspection_report(
        self,
        inspection_in: InspectionCreate,
        student_id: UUID,
        inspector_id: UUID
    ) -> models.InspectionRecord:
        """
        Coordinates the creation of an inspection report, including handling image uploads and database writes.
        """
        # Handle signature image
        signature_filename = None
        if inspection_in.signature_base64:
            try:
                signature_filename = await file_service.decode_and_upload_base64_image(inspection_in.signature_base64)
            except HTTPException as e:
                raise HTTPException(status_code=e.status_code, detail=f"Failed to upload signature: {e.detail}")

        # Handle images within inspection items
        for detail in inspection_in.details:
            if detail.photos:
                for photo in detail.photos:
                    try:
                        photo_filename = await file_service.decode_and_upload_base64_image(photo.file_content)
                        # We are modifying the Pydantic model in place.
                        # This is generally okay for a request-response cycle.
                        photo.file_path = photo_filename
                    except HTTPException as e:
                        raise HTTPException(status_code=e.status_code, detail=f"Failed to upload item photo for item: {e.detail}")

        # Create the inspection record in the database
        inspection_record = await crud_inspection.create_with_details(
            self.db,
            inspection_in=inspection_in,
            student_id=student_id,
            inspector_id=inspector_id,
            signature_filename=signature_filename
        )
        return inspection_record

# Dependency injection function to provide InspectionService instances
async def get_inspection_service(db: AsyncSession = Depends(get_db)) -> InspectionService:
    return InspectionService(db)
