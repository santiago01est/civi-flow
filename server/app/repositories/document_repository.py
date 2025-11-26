# app/repositories/document_repository.py
import logging
from typing import Optional, List
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from app.schemas.document import Document, DocumentStatus
from app.config.settings import settings


logger = logging.getLogger(__name__)


class DocumentRepository:
    """Repository for Document operations in Cosmos DB"""
    
    def __init__(self):
        self.client = CosmosClient(
            settings.COSMOS_DB_ENDPOINT,
            settings.COSMOS_DB_KEY
        )
        self.database = self.client.get_database_client(settings.COSMOS_DB_DATABASE_NAME)
        self.container = self.database.get_container_client(
            settings.COSMOS_DB_DOCUMENTS_CONTAINER
        )
    
    async def create_document(self, document: Document) -> Document:
        """Create a new document in Cosmos DB"""
        try:
            doc_dict = document.model_dump(mode='json')
            created = self.container.create_item(body=doc_dict)
            logger.info(f"Document created: {document.id}")
            return Document(**created)
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        try:
            item = self.container.read_item(
                item=document_id,
                partition_key=document_id
            )
            return Document(**item)
        except CosmosResourceNotFoundError:
            logger.warning(f"Document not found: {document_id}")
            return None
        except Exception as e:
            logger.error(f"Error reading document: {str(e)}")
            raise
    
    async def update_document(self, document: Document) -> Document:
        """Update existing document"""
        try:
            doc_dict = document.model_dump(mode='json')
            updated = self.container.replace_item(
                item=document.id,
                body=doc_dict
            )
            logger.info(f"Document updated: {document.id}")
            return Document(**updated)
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            raise
    
    async def get_documents_by_status(
        self, 
        status: DocumentStatus,
        limit: int = 100
    ) -> List[Document]:
        """Get documents by processing status"""
        try:
            query = f"SELECT * FROM c WHERE c.status = '{status.value}' OFFSET 0 LIMIT {limit}"
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            return [Document(**item) for item in items]
        except Exception as e:
            logger.error(f"❌ Error querying documents: {str(e)}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document by ID"""
        try:
            self.container.delete_item(
                item=document_id,
                partition_key=document_id
            )
            logger.info(f"Document deleted: {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
