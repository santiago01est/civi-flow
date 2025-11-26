from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import json
from app.schemas.document import DocumentIngestRequest, DocumentIngestResponse
from app.services.document_ingestion_service import DocumentIngestionService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_documents(
    files: List[UploadFile] = File(None),
    urls_json: Optional[str] = Form(None)
):
    """
    Ingest documents and URLs for RAG system.
    Validates content safety before processing.
    
    - **files**: PDF, DOCX, TXT files
    - **urls_json**: JSON string with list of URLs to validate and scrape
    """
    try:
        # Parse URLs from JSON string if provided
        urls = []
        if urls_json:
            try:
                urls_data = json.loads(urls_json)
                urls = urls_data.get("urls", [])
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON format for urls")
        
        # Initialize ingestion service
        ingestion_service = DocumentIngestionService()
        
        # Process files and URLs
        result = await ingestion_service.process_ingestion(
            files=files or [],
            urls=urls
        )
        
        return DocumentIngestResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during document ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
