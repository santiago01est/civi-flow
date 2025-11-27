# app/services/rag_pipeline_service.py
import logging
from typing import Dict, List
from app.services.document_chunker_service import DocumentChunkerService
from app.services.embeddings_service import EmbeddingsService
from app.services.search_index_service import SearchIndexService
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentStatus
from datetime import datetime



logger = logging.getLogger(__name__)



class RAGPipelineService:
    """Service to orchestrate the RAG pipeline: chunking → embeddings → indexing"""
    
    def __init__(self):
        self.chunker = DocumentChunkerService()
        self.embeddings = EmbeddingsService()
        self.search_index = SearchIndexService()
        self.document_repo = DocumentRepository()
        
        logger.info("RAG Pipeline Service initialized")
    
    async def process_document(self, document_id: str) -> bool:
        """
        Process a validated document through the RAG pipeline
        
        Steps:
        1. Retrieve document from Cosmos DB
        2. Get text from text_preview (already extracted)
        3. Chunk the text
        4. Generate embeddings
        5. Index in Azure AI Search
        6. Update document status
        
        Args:
            document_id: ID of the document to process
        
        Returns:
            True if successful
        """
        try:
            # Step 1: Get document metadata
            document = await self.document_repo.get_document(document_id)
            if not document:
                logger.error(f"Document not found: {document_id}")
                return False
            
            if document.status != DocumentStatus.VALIDATED:
                logger.warning(f"Document {document_id} is not validated, skipping")
                return False
            
            logger.info(f"Processing document: {document.original_filename}")
            
            # Step 2: Get text from text_preview (already extracted during ingestion)
            full_text = document.text_preview
            
            if not full_text or len(full_text.strip()) < 10:
                logger.error(f"No text content available for document {document_id}")
                await self.document_repo.update_document(
                    document_id,
                    {"status": DocumentStatus.FAILED.value}
                )
                return False
            
            logger.info(f"Document text length: {len(full_text)} characters")
            
            # Step 3: Chunk the text
            metadata = {
                "filename": document.original_filename,
                "source": document.source,
                "category": document.category or "",
            }
            
            chunks = self.chunker.chunk_text(
                text=full_text,
                document_id=document_id,
                metadata=metadata
            )
            
            if not chunks:
                logger.warning(f"No chunks generated for document {document_id}")
                await self.document_repo.update_document(
                    document_id,
                    {"status": DocumentStatus.FAILED.value}
                )
                return False
            
            logger.info(f"Created {len(chunks)} chunks")
            
            # Step 4: Generate embeddings for all chunks
            chunk_texts = [chunk.content for chunk in chunks]
            logger.info(f"Generating embeddings for {len(chunk_texts)} chunks...")
            
            embeddings = await self.embeddings.generate_embeddings_batch(chunk_texts)
            logger.info(f"✅ Generated {len(embeddings)} embeddings")
            
            # Step 5: Index chunks in Azure AI Search
            logger.info(f"Indexing {len(chunks)} chunks in Azure AI Search...")
            await self.search_index.index_chunks(chunks, embeddings)
            logger.info(f"✅ Indexed {len(chunks)} chunks successfully")
            
            # Step 6: Update document status in Cosmos DB
            await self.document_repo.update_document(
                document_id,
                {
                    "status": DocumentStatus.INDEXED.value,
                    "chunked": True,
                    "indexed": True,
                    "chunks_count": len(chunks),
                    "indexed_at": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"🎉 Document {document.original_filename} processed successfully: {len(chunks)} chunks indexed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing document {document_id}: {str(e)}")
            logger.exception(e)  # Print full traceback
            
            # Update status to FAILED
            try:
                await self.document_repo.update_document(
                    document_id,
                    {"status": DocumentStatus.FAILED.value}
                )
            except:
                pass
            
            return False
    
    async def process_pending_documents(self, limit: int = 10) -> Dict:
        """
        Process all documents with status VALIDATED
        Useful for batch processing or scheduled jobs
        
        Args:
            limit: Maximum number of documents to process
        
        Returns:
            Dictionary with processing results
        """
        try:
            # Get documents pending processing
            documents = await self.document_repo.get_documents_by_status(
                status=DocumentStatus.VALIDATED,
                limit=limit
            )
            
            logger.info(f"Found {len(documents)} documents to process")
            
            success_count = 0
            failed_count = 0
            
            for doc in documents:
                success = await self.process_document(doc.id)
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            
            result = {
                "total_processed": len(documents),
                "successful": success_count,
                "failed": failed_count
            }
            
            logger.info(f"Batch processing complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            raise
