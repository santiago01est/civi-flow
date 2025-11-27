# app/services/blob_storage_service.py
import os
import logging
from typing import Optional
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import ResourceNotFoundError
from app.config.settings import settings


logger = logging.getLogger(__name__)


class BlobStorageService:
    """Service for Azure Blob Storage operations"""
    
    def __init__(self):
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
        self.blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )
        self.container_client = self.blob_service_client.get_container_client(
            self.container_name
        )
    
    async def upload_file(
        self, 
        file_content: bytes, 
        blob_name: str,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Upload file to Azure Blob Storage
        Returns the blob URL
        """
        try:
            from azure.storage.blob import ContentSettings
            
            blob_client = self.container_client.get_blob_client(blob_name)
            
            # Create ContentSettings object properly
            content_settings = ContentSettings(content_type=content_type)
            
            blob_client.upload_blob(
                file_content,
                overwrite=True,
                content_settings=content_settings
            )
            
            blob_url = blob_client.url
            logger.info(f"Uploaded blob: {blob_name}")
            return blob_url
            
        except Exception as e:
            logger.error(f"Error uploading blob {blob_name}: {str(e)}")
            raise
    
    async def download_file(self, blob_name: str) -> bytes:
        """Download file from Azure Blob Storage"""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_data = blob_client.download_blob()
            return blob_data.readall()
        except ResourceNotFoundError:
            logger.error(f"Blob not found: {blob_name}")
            raise
        except Exception as e:
            logger.error(f"Error downloading blob {blob_name}: {str(e)}")
            raise
    
    async def delete_file(self, blob_name: str) -> bool:
        """Delete file from Azure Blob Storage"""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
            logger.info(f"Deleted blob: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting blob {blob_name}: {str(e)}")
            return False
    
    async def get_blob_url(self, blob_name: str) -> str:
        """Get the URL of a blob"""
        blob_client = self.container_client.get_blob_client(blob_name)
        return blob_client.url
