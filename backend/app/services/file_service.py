# backend/app/services/file_service.py
import os
import magic
import base64
import uuid
from typing import Optional, Tuple
from pathlib import Path
import asyncio

from fastapi import UploadFile, HTTPException, status

from ..config import settings

class FileService:
    def __init__(self, upload_dir: str = settings.UPLOAD_DIR):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.magic = magic.Magic(mime=True)

    def _write_file(self, file_path: Path, contents: bytes):
        with open(file_path, "wb") as f:
            f.write(contents)

    def _get_extension_from_mime(self, mime_type: str) -> Optional[str]:
        if mime_type == 'image/jpeg':
            return 'jpg'
        if mime_type == 'image/png':
            return 'png'
        if mime_type == 'image/gif':
            return 'gif'
        # Add other types as needed
        return None

    async def upload_image(self, file: UploadFile) -> str:
        """
        Processes an uploaded image file, verifies it's a valid image, and saves it to disk.
        Returns the saved filename (UUID).
        """
        # We trust the file content over the content-type header
        contents = await file.read()
        
        mime_type = self.magic.from_buffer(contents)
        file_extension = self._get_extension_from_mime(mime_type)
        
        if not file_extension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"File is not a valid image format. Detected type: {mime_type}"
            )
        
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = self.upload_dir / unique_filename

        try:
            await asyncio.to_thread(self._write_file, file_path, contents)
        except IOError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save image file."
            )
        
        return unique_filename

    async def decode_and_upload_base64_image(self, base64_string: str) -> str:
        """
        Decodes a Base64 string, verifies it's a valid image, and saves it to disk.
        Returns the saved filename (UUID).
        """
        try:
            if ',' in base64_string:
                _, base64_data = base64_string.split(',', 1)
            else:
                base64_data = base64_string
            
            image_data = base64.b64decode(base64_data)
        except (base64.binascii.Error, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Base64 string."
            )
        
        mime_type = self.magic.from_buffer(image_data)
        file_extension = self._get_extension_from_mime(mime_type)

        if not file_extension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Decoded data is not a valid image format. Detected type: {mime_type}"
            )
            
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = self.upload_dir / unique_filename

        try:
            await asyncio.to_thread(self._write_file, file_path, image_data)
        except IOError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save image from Base64 data."
            )
            
        return unique_filename

# Create a service instance for reuse elsewhere
file_service = FileService()
