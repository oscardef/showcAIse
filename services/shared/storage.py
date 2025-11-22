from minio import Minio
from minio.error import S3Error
from io import BytesIO
from typing import Optional
import logging
from .config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class StorageClient:
    """MinIO/S3 storage client."""
    
    def __init__(self):
        # Parse MinIO URL to extract host and port
        url = settings.MINIO_URL.replace("http://", "").replace("https://", "")
        secure = settings.MINIO_URL.startswith("https://")
        
        self.client = Minio(
            url,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=secure
        )
        self.bucket_name = settings.MINIO_BUCKET
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
    
    def upload_file(self, object_name: str, file_path: str, content_type: str = "application/octet-stream"):
        """Upload file to storage."""
        try:
            self.client.fput_object(
                self.bucket_name,
                object_name,
                file_path,
                content_type=content_type
            )
            logger.info(f"Uploaded: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            return False
    
    def upload_bytes(self, object_name: str, data: bytes, content_type: str = "application/octet-stream"):
        """Upload bytes to storage."""
        try:
            self.client.put_object(
                self.bucket_name,
                object_name,
                BytesIO(data),
                len(data),
                content_type=content_type
            )
            logger.info(f"Uploaded bytes: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Error uploading bytes: {e}")
            return False
    
    def download_file(self, object_name: str, file_path: str):
        """Download file from storage."""
        try:
            self.client.fget_object(self.bucket_name, object_name, file_path)
            logger.info(f"Downloaded: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Error downloading file: {e}")
            return False
    
    def get_presigned_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        """Get presigned URL for object."""
        try:
            url = self.client.presigned_get_object(self.bucket_name, object_name, expires=expires)
            return url
        except S3Error as e:
            logger.error(f"Error getting presigned URL: {e}")
            return None
    
    def delete_object(self, object_name: str):
        """Delete object from storage."""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Deleted: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting object: {e}")
            return False


# Singleton instance
storage_client = StorageClient()
