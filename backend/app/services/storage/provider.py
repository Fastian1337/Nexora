"""
Nexora Platform — File Ingest Storage Providers
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any
from app.config.logging import get_logger

logger = get_logger(__name__)


class StorageProvider(ABC):
    """
    Abstract File Storage Interface.
    Decouples document upload pipelines from storage systems (local, AWS S3, Cloudflare R2).
    """

    @abstractmethod
    async def upload_file(self, file_content: bytes, destination_path: str) -> str:
        """Upload raw file content and return storage key/URL."""
        pass

    @abstractmethod
    async def download_file(self, file_path: str) -> bytes:
        """Download file and return raw byte buffer."""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Deletes raw file from the storage system."""
        pass


class LocalStorageProvider(StorageProvider):
    """Local Workspace Sandbox file storage provider."""

    def __init__(self, base_directory: str = "./storage") -> None:
        self.base_dir = os.path.abspath(base_directory)
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_abs_path(self, target_path: str) -> str:
        return os.path.abspath(os.path.join(self.base_dir, target_path.lstrip("/")))

    async def upload_file(self, file_content: bytes, destination_path: str) -> str:
        abs_path = self._get_abs_path(destination_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        with open(abs_path, "wb") as f:
            f.write(file_content)
        
        logger.info("local_storage_upload_succeeded", destination=abs_path)
        # Return a relative reference key
        return f"/storage/{destination_path.lstrip('/')}"

    async def download_file(self, file_path: str) -> bytes:
        # Strip routing prefix if present
        clean_path = file_path.replace("/storage/", "")
        abs_path = self._get_abs_path(clean_path)
        
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found in local storage path: {abs_path}")
            
        with open(abs_path, "rb") as f:
            return f.read()

    async def delete_file(self, file_path: str) -> bool:
        clean_path = file_path.replace("/storage/", "")
        abs_path = self._get_abs_path(clean_path)
        
        if os.path.exists(abs_path):
            os.remove(abs_path)
            logger.info("local_storage_delete_succeeded", path=abs_path)
            return True
        return False


class S3StorageProvider(StorageProvider):
    """AWS S3/Cloudflare R2 mock cloud storage provider."""

    async def upload_file(self, file_content: bytes, destination_path: str) -> str:
        logger.info("s3_upload_simulated", path=destination_path)
        return f"https://nexora-knowledge.s3.amazonaws.com/{destination_path.lstrip('/')}"

    async def download_file(self, file_path: str) -> bytes:
        logger.info("s3_download_simulated", path=file_path)
        return b"Mock parsed text file content buffer."

    async def delete_file(self, file_path: str) -> bool:
        logger.info("s3_delete_simulated", path=file_path)
        return True
