import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import re

from ... import auth, models
from ...crud import crud_inspection, crud_user

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.get("/{filename}")
async def get_image(
    filename: str,
    db: AsyncSession = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Serves an image file after checking user permissions.
    - The user must be the student who submitted the inspection,
    - or have 'view_all_records' permission.
    """
    # --- 安全性檢查 (Security Sanity Checks) ---
    # 檢查檔案名稱格式 (Format Check) - 應為 UUID.extension
    if not re.match(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\.\w+$", filename, re.IGNORECASE):
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename format.")

    # --- 權限驗證 (Permission Check) ---
    image_record = await crud_inspection.get_image_by_filename(db, filename=filename)

    if not image_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")

    # 取得圖片對應的學生 ID
    try:
        owner_student_id = image_record.inspection_detail.inspection.student.id
    except AttributeError:
        # 如果圖片記錄的關聯不完整，拒絕存取
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Image record is corrupted or incomplete.")

    # 檢查權限：
    # 1. 使用者是否為圖片擁有者
    is_owner = current_user.student and current_user.student.id == owner_student_id
    # 2. 使用者是否有 'view_all_records' 權限 (使用預加載數據避免懶加載)
    can_view_all = any(perm.name == "view_all_records" for role in current_user.roles for perm in role.permissions)

    if not is_owner and not can_view_all:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this image.")

    # --- 提供檔案 (Serve File) ---
    safe_upload_dir = os.path.abspath(UPLOAD_DIR)
    file_path = os.path.abspath(os.path.join(safe_upload_dir, filename))

    if not file_path.startswith(safe_upload_dir):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename, path traversal attempt detected.")

    if not os.path.isfile(file_path):
        # 這種情況不應該發生，因為資料庫中有記錄
        # 但作為一個保險措施，還是檢查一下
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image file not found on disk.")

    return FileResponse(file_path)
