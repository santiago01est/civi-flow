# app/schemas/document.py
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status"""
    PENDING_VALIDATION = "pending_validation"
    VALIDATED = "validated"
    REJECTED = "rejected"
    PENDING_CHUNKING = "pending_chunking"
    INDEXED = "indexed"
    FAILED = "failed"


class URLItem(BaseModel):
    """Schema for a single URL item"""
    url: HttpUrl
    title: Optional[str] = None
    description: Optional[str] = None


class DocumentIngestRequest(BaseModel):
    """Schema for document ingestion request"""
    urls: Optional[List[URLItem]] = []
    source: Optional[str] = "government"
    category: Optional[str] = None


class DocumentIngestResponse(BaseModel):
    """Schema for document ingestion response"""
    message: str
    files_processed: int
    urls_processed: int
    files_accepted: List[str]
    files_rejected: List[str]
    urls_accepted: List[str]
    urls_rejected: List[str]


# ============================================================================
# Document Model for Cosmos DB
# ============================================================================
class Document(BaseModel):
    """Document metadata stored in Cosmos DB"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    original_filename: str
    content_type: str  # application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document
    file_size: int  # bytes
    
    # Storage
    blob_url: str  # Azure Blob Storage URL
    blob_container: str = "government-documents"
    
    # Content
    text_preview: Optional[str] = None  # First 500 chars
    full_text_extracted: bool = False
    
    # Validation
    status: DocumentStatus = DocumentStatus.PENDING_VALIDATION
    is_safe: bool = False
    safety_reason: Optional[str] = None
    
    # Metadata
    source: str = "government"  # government, user_upload, url_scrape
    category: Optional[str] = None
    language: str = "es"
    
    # RAG Processing
    chunked: bool = False
    indexed: bool = False
    chunks_count: int = 0
    
    # Timestamps
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    validated_at: Optional[datetime] = None
    indexed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


import uuid
