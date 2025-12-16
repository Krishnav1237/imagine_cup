"""
Storage adapter interface and factory
Abstract interface for file storage (local or Azure Blob)
"""
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from pathlib import Path


class StorageAdapter(ABC):
    """Abstract interface for file storage"""
    
    @abstractmethod
    async def save_file(
        self,
        file_data: BinaryIO,
        file_path: str,
        content_type: Optional[str] = None
    ) -> str:
        """
        Save a file and return its path/URL
        
        Args:
            file_data: File binary data
            file_path: Relative path where file should be saved
            content_type: MIME type of the file
            
        Returns:
            Path or URL where file was saved
        """
        pass
    
    @abstractmethod
    async def get_file(self, file_path: str) -> bytes:
        """
        Retrieve file data
        
        Args:
            file_path: Path to the file
            
        Returns:
            File binary data
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file exists
        """
        pass
    
    @abstractmethod
    def get_file_url(self, file_path: str) -> str:
        """
        Get URL to access the file
        
        Args:
            file_path: Path to the file
            
        Returns:
            URL or path to access the file
        """
        pass


def get_storage_adapter() -> StorageAdapter:
    """
    Factory function to get the appropriate storage adapter
    based on deployment mode
    """
    from app.config import settings
    
    if settings.is_local:
        from app.services.storage.local import LocalStorageAdapter
        return LocalStorageAdapter()
    else:
        from app.services.storage.azure_blob import AzureBlobStorageAdapter
        return AzureBlobStorageAdapter()