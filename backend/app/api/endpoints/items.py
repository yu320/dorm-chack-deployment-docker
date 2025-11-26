from fastapi import APIRouter, Depends, HTTPException, status, Request # Import Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from ... import crud, schemas, auth, models # Import models
from ...utils.audit import audit_log # Import audit_log

router = APIRouter()

@router.post("/", response_model=schemas.InspectionItem, dependencies=[Depends(auth.PermissionChecker("manage_items"))])
@audit_log(action="CREATE", resource_type="InspectionItem")
async def create_inspection_item(item: schemas.InspectionItemCreate, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    return await crud.create_inspection_item(db=db, item=item)

@router.get("/", response_model=schemas.PaginatedInspectionItems)
async def read_inspection_items(request: Request, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)): # Added for audit_log decorator to work
    items_data = await crud.get_inspection_items(db, skip=skip, limit=limit)
    return items_data

@router.get("/{item_id}", response_model=schemas.InspectionItem)
async def read_inspection_item(item_id: uuid.UUID, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)): # Added for audit_log decorator to work
    item = await crud.get_inspection_item(db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inspection item not found")
    return item

@router.put("/{item_id}", response_model=schemas.InspectionItem, dependencies=[Depends(auth.PermissionChecker("manage_items"))])
@audit_log(action="UPDATE", resource_type="InspectionItem", resource_id_src="item_id")
async def update_inspection_item(
    item_id: uuid.UUID,
    item_in: schemas.InspectionItemUpdate,
    request: Request,
    db: AsyncSession = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    db_item = await crud.get_inspection_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inspection item not found")
    updated_item = await crud.update_inspection_item(db=db, db_item=db_item, item_in=item_in)
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth.PermissionChecker("manage_items"))])
@audit_log(action="DELETE", resource_type="InspectionItem", resource_id_src="item_id")
async def delete_inspection_item(item_id: uuid.UUID, request: Request, db: AsyncSession = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_item = await crud.get_inspection_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inspection item not found")
    await crud.delete_inspection_item(db=db, db_item=db_item)
    return {"ok": True}

@router.put("/batch-update-status", response_model=List[schemas.InspectionItem], dependencies=[Depends(auth.PermissionChecker("manage_items"))])
@audit_log(action="BATCH_UPDATE", resource_type="InspectionItem")
async def batch_update_item_status(
    batch_update: schemas.InspectionItemBatchUpdate,
    request: Request,
    db: AsyncSession = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    """
    Batch update the 'is_active' status of multiple inspection items.
    Requires 'manage_items' permission.
    """
    updated_items = await crud.batch_update_inspection_item_status(
        db=db,
        item_ids=batch_update.item_ids,
        is_active=batch_update.is_active
    )
    if not updated_items:
        raise HTTPException(status_code=404, detail="No inspection items found with the provided IDs")
    return updated_items
