"""
Local filesystem storage adapter
"""
import os
import shutil
from pathlib import Path
from typing import BinaryIO, Optional
import aiofiles

from app.services.storage.adapter import StorageAdapter
from app.config import settings


class LocalStorageAdapter(StorageAdapter):
    """Local filesystem storage implementation"""
    
    def __init__(self):
        self.base_path = Path(settings.UPLOAD_DIR)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_full_path(self, file_path: str) -> Path:
        """Get full filesystem path"""
        return self.base_path / file_path
    
    async def save_file(
        self,
        file_data: BinaryIO,
        file_path: str,
        content_type: Optional[str] = None
    ) -> str:
        """Save file to local filesystem"""
        full_path = self._get_full_path(file_path)
        
        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        async with aiofiles.open(full_path, 'wb') as f:
            # Read file_data in chunks if it's large
            if hasattr(file_data, 'read'):
                content = file_data.read()
                await f.write(content)
            else:
                await f.write(file_data)
        
        return str(file_path)
    
    async def get_file(self, file_path: str) -> bytes:
        """Read file from local filesystem"""
        full_path = self._get_full_path(file_path)
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        async with aiofiles.open(full_path, 'rb') as f:
            return await f.read()
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from local filesystem"""
        full_path = self._get_full_path(file_path)
        
        try:
            if full_path.is_file():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        full_path = self._get_full_path(file_path)
        return full_path.exists() and full_path.is_file()
    
    def get_file_url(self, file_path: str) -> str:
        """Get local file path (or URL if serving files)"""
        # In production, you might serve files through FastAPI
        # For now, return the relative path
        return f"/files/{file_path}"
    
    async def save_uploaded_file(self, upload_file, destination: str) -> str:
        """
        Helper method to save FastAPI UploadFile
        """
        full_path = self._get_full_path(destination)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(full_path, 'wb') as f:
            content = await upload_file.read()
            await f.write(content)
        
        return destination