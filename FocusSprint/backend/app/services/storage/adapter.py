"""
Storage Adapter Interface and Implementation.
Handles file storage operations (Local vs Cloud/Azure).
"""
import os
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Optional, Any

from app.config import settings

logger = logging.getLogger("StorageAdapter")

# Check for Azure dependencies
try:
    from azure.storage.blob import BlobServiceClient, ContentSettings
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


class StorageAdapter(ABC):
    """Abstract interface for file storage"""

    @abstractmethod
    async def save_file(
        self, 
        file_obj: BinaryIO, 
        destination: str, 
        content_type: Optional[str] = None
    ) -> str:
        """Save a file and return its path/URL"""
        pass

    @abstractmethod
    async def get_file(self, file_path: str) -> bytes:
        """Retrieve file content as bytes"""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage"""
        pass

    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        pass

    @abstractmethod
    def get_file_url(self, file_path: str) -> str:
        """Get public URL or path to access the file"""
        pass


class LocalStorageAdapter(StorageAdapter):
    """Implementation for Local Disk Storage"""

    def __init__(self, base_path: Optional[str] = None):
        self.base_dir = Path(settings.UPLOAD_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.base_path = Path(base_path or os.getenv("LOCAL_STORAGE_PATH", "./uploads"))
        logger.info(f"📂 Local storage initialized at: {self.base_dir.absolute()}")

    async def save_file(self, file_obj: BinaryIO, destination: str, content_type: Optional[str] = None) -> str:
        try:
            # Handle potential absolute paths vs relative paths
            if os.path.isabs(destination):
                target_path = Path(destination)
            else:
                target_path = self.base_dir / destination

            # Ensure parent directories exist
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            # Ensure pointer is at start
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
                
            with open(target_path, "wb") as buffer:
                buffer.write(file_obj.read())
            
            # Return relative path for database storage consistency
            rel_path = target_path.relative_to(self.base_dir) if target_path.is_relative_to(self.base_dir) else target_path
            return str(rel_path)
            
        except Exception as e:
            logger.error(f"❌ Error saving file locally: {e}")
            raise e

    async def get_file(self, file_path: str) -> bytes:
        try:
            target_path = self.base_dir / file_path
            
            if not target_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(target_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"❌ Error reading file locally: {e}")
            raise e

    async def delete_file(self, file_path: str) -> bool:
        try:
            target_path = self.base_dir / file_path
            if target_path.exists():
                target_path.unlink()
                logger.info(f"🗑️ Deleted local file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error deleting file locally: {e}")
            return False

    async def file_exists(self, file_path: str) -> bool:
        return (self.base_dir / file_path).exists()

    def get_file_url(self, file_path: str) -> str:
        # Returns the static mount path defined in main.py (usually /uploads/...)
        return f"/uploads/{file_path}"

    def get_bytes(self, storage_path: str) -> bytes:
        """
        Read and return raw bytes for the given storage path.
        Accepts:
        - absolute paths
        - relative paths (relative to CWD)
        - paths that already include the base uploads prefix (e.g. "./uploads/2/13/original.pdf")
        - keys relative to the configured base_path (e.g. "2/13/original.pdf")
        """
        # Try as an absolute or direct relative filesystem path first
        try_path = Path(storage_path)
        if try_path.exists():
            return try_path.read_bytes()

        # Normalize and try relative to configured base_path
        rel = storage_path
        # strip leading './' or '/'
        rel = rel.lstrip("./\\")
        # if path includes the base folder name, strip that prefix
        base_name = self.base_path.name
        if rel.startswith(base_name + os.sep):
            rel = rel[len(base_name) + 1 :]

        fp = (self.base_path / rel).resolve()
        if fp.exists():
            return fp.read_bytes()

        # Final attempt: try joining raw provided string to base_path without normalization
        fp2 = (self.base_path / storage_path).resolve()
        if fp2.exists():
            return fp2.read_bytes()

        raise FileNotFoundError(
            f"Local storage file not found. Tried: {try_path.resolve()!s}, {fp!s}, {fp2!s}"
        )


class AzureBlobStorageAdapter(StorageAdapter):
    """Implementation for Azure Blob Storage"""

    def __init__(self):
        if not AZURE_AVAILABLE:
            raise ImportError("azure-storage-blob is required for Azure StorageAdapter")
        
        if not settings.AZURE_STORAGE_CONNECTION_STRING:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set")

        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                settings.AZURE_STORAGE_CONNECTION_STRING
            )
            self.container_name = settings.AZURE_STORAGE_CONTAINER
            
            # Ensure container exists
            if not self.blob_service_client.get_container_client(self.container_name).exists():
                self.blob_service_client.create_container(self.container_name, public_access="blob")
                
            logger.info(f"☁️ Azure Blob Storage initialized. Container: {self.container_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure Storage: {e}")
            raise e

    async def save_file(self, file_obj: BinaryIO, destination: str, content_type: Optional[str] = None) -> str:
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=destination
            )
            
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)

            # Set content settings (MIME type)
            cnt_settings = ContentSettings(content_type=content_type) if content_type else None

            blob_client.upload_blob(file_obj, overwrite=True, content_settings=cnt_settings)
            
            return destination
        except Exception as e:
            logger.error(f"❌ Azure upload failed: {e}")
            raise e

    async def get_file(self, file_path: str) -> bytes:
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=file_path
            )
            download_stream = blob_client.download_blob()
            return download_stream.readall()
        except Exception as e:
            logger.error(f"❌ Azure download failed: {e}")
            raise e

    async def delete_file(self, file_path: str) -> bool:
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=file_path
            )
            blob_client.delete_blob()
            logger.info(f"🗑️ Deleted Azure blob: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Azure delete failed: {e}")
            return False

    async def file_exists(self, file_path: str) -> bool:
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=file_path
            )
            return blob_client.exists()
        except Exception:
            return False

    def get_file_url(self, file_path: str) -> str:
        # Return direct URL to the blob
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, 
            blob=file_path
        )
        return blob_client.url


def get_storage_adapter() -> StorageAdapter:
    """
    Factory function to get the appropriate storage adapter
    based on deployment mode settings.
    """
    if settings.is_azure:
        if AZURE_AVAILABLE:
            return AzureBlobStorageAdapter()
        else:
            logger.warning("⚠️ Azure mode detected but azure-storage-blob not installed. Falling back to local.")
            return LocalStorageAdapter()
    
    return LocalStorageAdapter()