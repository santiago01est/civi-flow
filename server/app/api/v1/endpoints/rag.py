# app/api/v1/endpoints/rag.py
from fastapi import APIRouter, HTTPException
from typing import Dict, List
from pydantic import BaseModel
import logging
import json
from pathlib import Path


logger = logging.getLogger(__name__)


router = APIRouter()


class PipelineResponse(BaseModel):
    message: str
    status: str
    summary: Dict
    steps: List[str]
    documents_processed: List[Dict]
    errors: List[str]


@router.post("/process", response_model=PipelineResponse)
async def process_full_rag_pipeline():
    """
    
    
    Response:
    {
      "message": "Pipeline completed successfully",
      "status": "success",
      "summary": {
        "files_processed": 3,
        "urls_processed": 2,
        "documents_indexed": 5,
        "total_chunks": 87
      },
      "steps": ["Step 1", "Step 2", ...],
      "documents_processed": [...],
      "errors": []
    }
    """
    steps = []
    errors = []
    documents_processed = []
    
    try:
        # ================================================================
        # STEP 1: Setup - Verificar/crear índice en Azure AI Search
        # ================================================================
        logger.info("Step 1: Setting up Azure AI Search index...")
        
        from app.services.search_index_service import SearchIndexService
        
        try:
            search_index_service = SearchIndexService()
            search_index_service.create_index()
            steps.append("Azure AI Search index ready")
            logger.info("Search index ready")
        except Exception as e:
            error_msg = f"Failed to setup search index: {str(e)}"
            errors.append(error_msg)
            logger.error(f"{error_msg}")
            # Continue anyway, index might already exist
            steps.append("Search index setup failed (might already exist)")
        
        # ================================================================
        # STEP 2: Read local files from app/files/documents/
        # ================================================================
        logger.info("Step 2: Reading files from app/files/documents/...")
        
        files_path = Path("app/files/documents")
        
        if not files_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Folder app/files/documents/ not found. Create it and add PDF/DOCX/TXT files."
            )
        
        supported_extensions = ['.pdf', '.docx', '.txt']
        local_files = [
            f for f in files_path.iterdir() 
            if f.is_file() and f.suffix.lower() in supported_extensions
        ]
        
        logger.info(f"Found {len(local_files)} files: {[f.name for f in local_files]}")
        steps.append(f"Found {len(local_files)} local files")
        
        # ================================================================
        # STEP 3: Read URLs from app/files/urls.json
        # ================================================================
        logger.info("Step 3: Reading URLs from app/files/urls.json...")
        
        urls_file_path = Path("app/files/urls.json")
        urls = []
        
        if urls_file_path.exists():
            with open(urls_file_path, 'r', encoding='utf-8') as f:
                urls_data = json.load(f)
                urls = urls_data.get("urls", [])
            
            logger.info(f"Found {len(urls)} URLs")
            steps.append(f"Found {len(urls)} URLs")
        else:
            logger.warning("app/files/urls.json not found, skipping URLs")
            steps.append("No urls.json found, skipping URLs")
        
        # ================================================================
        # STEP 4: Process files through ingestion pipeline
        # ================================================================
        logger.info("Step 4: Ingesting and validating files...")
        
        from app.services.document_ingestion_service import DocumentIngestionService
        from fastapi import UploadFile
        import io
        
        ingestion_service = DocumentIngestionService()
        
        # Convert local files to UploadFile objects
        upload_files = []
        for file_path in local_files:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Determine content type
                content_type_map = {
                    '.pdf': 'application/pdf',
                    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    '.txt': 'text/plain'
                }
                content_type = content_type_map.get(file_path.suffix.lower(), 'application/octet-stream')
                
                # Create UploadFile correctly
                upload_file = UploadFile(
                    filename=file_path.name,
                    file=io.BytesIO(content),
                    headers={'content-type': content_type} 
                )
                upload_files.append(upload_file)
                
            except Exception as e:
                error_msg = f"Error reading file {file_path.name}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"{error_msg}")
        
        # Process ingestion (validation + storage)
        ingestion_result = await ingestion_service.process_ingestion(
            files=upload_files,
            urls=urls
        )
        
        files_accepted = len(ingestion_result["files_accepted"])
        urls_accepted = len(ingestion_result["urls_accepted"])
        total_accepted = files_accepted + urls_accepted
        
        steps.append(f"Validated and stored {total_accepted} documents")
        logger.info(f"Ingestion complete: {files_accepted} files, {urls_accepted} URLs accepted")
        
        # Track rejected items
        if ingestion_result["files_rejected"]:
            for rejected in ingestion_result["files_rejected"]:
                errors.append(f"File rejected: {rejected}")
        
        if ingestion_result["urls_rejected"]:
            for rejected in ingestion_result["urls_rejected"]:
                errors.append(f"URL rejected: {rejected}")
        
        if total_accepted == 0:
            return PipelineResponse(
                message="Pipeline completed but no documents were accepted",
                status="completed_with_errors",
                summary={
                    "files_processed": len(local_files),
                    "urls_processed": len(urls),
                    "documents_indexed": 0,
                    "total_chunks": 0
                },
                steps=steps,
                documents_processed=[],
                errors=errors
            )
        
        # ================================================================
        # STEP 5: Retrieve validated documents from Cosmos DB
        # ================================================================
        logger.info("Step 5: Retrieving validated documents...")
        
        from app.repositories.document_repository import DocumentRepository
        from app.schemas.document import DocumentStatus
        
        document_repo = DocumentRepository()
        validated_docs = await document_repo.get_documents_by_status(
            DocumentStatus.VALIDATED,
            limit=100
        )
        
        logger.info(f"Found {len(validated_docs)} validated documents")
        steps.append(f"Retrieved {len(validated_docs)} validated documents")
        
        # ================================================================
        # STEP 6: Process each document through RAG pipeline
        # (Chunking → Embeddings → Indexing)
        # ================================================================
        logger.info("Step 6: Processing RAG pipeline (chunking, embeddings, indexing)...")
        
        from app.services.rag_pipeline_service import RAGPipelineService
        
        rag_pipeline = RAGPipelineService()
        
        documents_indexed = 0
        total_chunks = 0
        
        for doc in validated_docs:
            try:
                logger.info(f"Processing: {doc.original_filename}")
                
                success = await rag_pipeline.process_document(doc.id)
                
                if success:
                    # Get updated document to retrieve chunks count
                    updated_doc = await document_repo.get_document(doc.id)
                    
                    documents_indexed += 1
                    total_chunks += updated_doc.chunks_count
                    
                    documents_processed.append({
                        "id": doc.id,
                        "filename": doc.original_filename,
                        "status": "indexed",
                        "chunks": updated_doc.chunks_count
                    })
                    
                    logger.info(f"{doc.original_filename} → {updated_doc.chunks_count} chunks indexed")
                else:
                    error_msg = f"Failed to process {doc.original_filename}"
                    errors.append(error_msg)
                    
                    documents_processed.append({
                        "id": doc.id,
                        "filename": doc.original_filename,
                        "status": "failed",
                        "chunks": 0
                    })
                    
            except Exception as e:
                error_msg = f"Error processing {doc.original_filename}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"{error_msg}")
                
                documents_processed.append({
                    "id": doc.id,
                    "filename": doc.original_filename,
                    "status": "error",
                    "chunks": 0
                })
        
        steps.append(f"Chunked and generated embeddings for {documents_indexed} documents")
        steps.append(f"Indexed {total_chunks} chunks in Azure AI Search")
        
        # ================================================================
        # STEP 7: Return comprehensive results
        # ================================================================
        
        status = "success" if documents_indexed > 0 else "failed"
        if errors:
            status = "completed_with_errors" if documents_indexed > 0 else "failed"
        
        message = f"Pipeline completed: {documents_indexed}/{total_accepted} documents indexed successfully with {total_chunks} total chunks"
        
        logger.info(f"{message}")
        
        return PipelineResponse(
            message=message,
            status=status,
            summary={
                "files_processed": len(local_files),
                "urls_processed": len(urls),
                "documents_accepted": total_accepted,
                "documents_indexed": documents_indexed,
                "total_chunks": total_chunks
            },
            steps=steps,
            documents_processed=documents_processed,
            errors=errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fatal error in pipeline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed: {str(e)}"
        )
