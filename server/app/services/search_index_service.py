# app/services/search_index_service.py
import logging
from typing import List, Dict
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)
from app.config.settings import settings
from app.services.document_chunker_service import DocumentChunk


logger = logging.getLogger(__name__)


class SearchIndexService:
    """Service to manage Azure AI Search indexing for RAG"""
    
    def __init__(self):
        """Initialize Azure AI Search client"""
        self.endpoint = settings.AZURE_SEARCH_ENDPOINT
        self.api_key = settings.AZURE_SEARCH_KEY
        self.index_name = settings.AZURE_SEARCH_INDEX_NAME
        
        self.credential = AzureKeyCredential(self.api_key)
        
        # Client for search operations
        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=self.credential
        )
        
        # Client for index management
        self.index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=self.credential
        )
        
        logger.info(f"SearchIndexService initialized for index: {self.index_name}")
    
    def create_index(self):
        """
        Create or update the search index with vector search capabilities
        Run this once during setup
        """
        try:
            fields = [
                SearchField(
                    name="id",
                    type=SearchFieldDataType.String,
                    key=True,
                    filterable=True,
                ),
                SearchField(
                    name="chunk_id",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SearchField(
                    name="document_id",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SearchField(
                    name="content",
                    type=SearchFieldDataType.String,
                    searchable=True,
                ),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,  # ada-002 dimensions
                    vector_search_profile_name="vector-profile",
                ),
                SearchField(
                    name="chunk_index",
                    type=SearchFieldDataType.Int32,
                    filterable=True,
                    sortable=True,
                ),
                SearchField(
                    name="filename",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    facetable=True,
                ),
                SearchField(
                    name="source",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    facetable=True,
                ),
                SearchField(
                    name="category",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    facetable=True,
                ),
            ]
            
            # Configure vector search
            vector_search = VectorSearch(
                profiles=[
                    VectorSearchProfile(
                        name="vector-profile",
                        algorithm_configuration_name="hnsw-config",
                    )
                ],
                algorithms=[
                    HnswAlgorithmConfiguration(name="hnsw-config")
                ],
            )
            
            # Create index
            index = SearchIndex(
                name=self.index_name,
                fields=fields,
                vector_search=vector_search,
            )
            
            result = self.index_client.create_or_update_index(index)
            logger.info(f"Search index '{self.index_name}' created/updated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error creating search index: {str(e)}")
            raise
    
    async def index_chunks(
        self, 
        chunks: List[DocumentChunk], 
        embeddings: List[List[float]]
    ) -> bool:
        """
        Index document chunks with their embeddings in Azure AI Search
        
        Args:
            chunks: List of DocumentChunk objects
            embeddings: Corresponding embedding vectors
        
        Returns:
            True if successful
        """
        try:
            if len(chunks) != len(embeddings):
                raise ValueError("Number of chunks and embeddings must match")
            
            # Prepare documents for indexing
            documents = []
            for chunk, embedding in zip(chunks, embeddings):
                doc = {
                    "id": chunk.chunk_id,
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "content_vector": embedding,
                    "chunk_index": chunk.chunk_index,
                    "filename": chunk.metadata.get("filename", ""),
                    "source": chunk.metadata.get("source", "government"),
                    "category": chunk.metadata.get("category", ""),
                }
                documents.append(doc)
            
            # Upload to Azure AI Search
            result = self.search_client.upload_documents(documents=documents)
            
            success_count = sum(1 for r in result if r.succeeded)
            logger.info(f"Indexed {success_count}/{len(documents)} chunks successfully")
            
            return success_count == len(documents)
            
        except Exception as e:
            logger.error(f"Error indexing chunks: {str(e)}")
            raise
    
    async def delete_document_chunks(self, document_id: str) -> bool:
        """
        Delete all chunks for a specific document from the index
        
        Args:
            document_id: ID of the document whose chunks should be deleted
        
        Returns:
            True if successful
        """
        try:
            # Search for all chunks of this document
            results = self.search_client.search(
                search_text="*",
                filter=f"document_id eq '{document_id}'",
                select="id"
            )
            
            # Get IDs to delete
            ids_to_delete = [{"id": doc["id"]} for doc in results]
            
            if ids_to_delete:
                self.search_client.delete_documents(documents=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} chunks for document {document_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting chunks: {str(e)}")
            return False
