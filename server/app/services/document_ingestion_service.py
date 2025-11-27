# app/services/document_ingestion_service.py
from typing import List, Dict
from fastapi import UploadFile
import os
import aiohttp
from bs4 import BeautifulSoup
import uuid
import tempfile
import logging
from datetime import datetime
from app.services.content_safety_service import ContentSafetyService
from app.services.url_validator_service import URLValidatorService
from app.services.text_extraction_service import TextExtractionService
from app.services.blob_storage_service import BlobStorageService
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import Document, DocumentStatus


logger = logging.getLogger(__name__)


class DocumentIngestionService:
    """Service to handle document and URL ingestion with safety validation"""
    
    def __init__(self):
        self.content_safety = ContentSafetyService()
        self.url_validator = URLValidatorService()
        self.text_extractor = TextExtractionService()
        self.blob_storage = BlobStorageService()
        self.document_repo = DocumentRepository()
        self.staging_path = tempfile.gettempdir()
    
    async def process_ingestion(
        self, 
        files: List[UploadFile], 
        urls: List[Dict]
    ) -> Dict:
        """
        Process uploaded files and URLs with safety validation
        """
        files_accepted = []
        files_rejected = []
        urls_accepted = []
        urls_rejected = []
        
        # Process files
        for file in files:
            try:
                result = await self._process_file(file)
                if result["safe"]:
                    files_accepted.append(file.filename)
                else:
                    files_rejected.append(f"{file.filename}: {result['reason']}")
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                files_rejected.append(f"{file.filename}: Processing error")
        
        # Process URLs
        for url_item in urls:
            try:
                url = url_item.get("url")
                result = await self._process_url(url)
                if result["safe"]:
                    urls_accepted.append(url)
                else:
                    urls_rejected.append(f"{url}: {result['reason']}")
            except Exception as e:
                logger.error(f"Error processing URL {url}: {str(e)}")
                urls_rejected.append(f"{url}: Validation error")
        
        return {
            "message": "Ingestion completed",
            "files_processed": len(files),
            "urls_processed": len(urls),
            "files_accepted": files_accepted,
            "files_rejected": files_rejected,
            "urls_accepted": urls_accepted,
            "urls_rejected": urls_rejected
        }
    
    async def _process_file(self, file: UploadFile) -> Dict:
        """Process and validate a single file"""
        # Save file temporarily
        temp_path = os.path.join(self.staging_path, file.filename)
        file_content = await file.read()
        
        with open(temp_path, "wb") as f:
            f.write(file_content)
        
        try:
            # Extract text from file
            full_text = await self.text_extractor.extract_text(temp_path, file.filename)
            
            # Validate content safety
            is_safe = await self.content_safety.validate_text(full_text)
            
            if not is_safe:
                return {"safe": False, "reason": "Content safety violation"}
            
            # Generate unique blob name
            import uuid
            file_extension = file.filename.split(".")[-1]
            blob_name = f"{uuid.uuid4()}.{file_extension}"
            
            # Upload to Azure Blob Storage
            blob_url = await self.blob_storage.upload_file(
                file_content=file_content,
                blob_name=blob_name,
                content_type=file.content_type
            )
            
            # Create document metadata in Cosmos DB
            document = Document(
                filename=blob_name,
                original_filename=file.filename,
                content_type=file.content_type,
                file_size=len(file_content),
                blob_url=blob_url,
                text_preview=full_text[:500] if full_text else None,
                full_text_extracted=True,
                status=DocumentStatus.VALIDATED,
                is_safe=True,
                validated_at=datetime.utcnow(),
                source="government",
                chunked=False,
                indexed=False
            )
            
            await self.document_repo.create_document(document)
            
            logger.info(f"Document ingested successfully: {file.filename} -> {document.id}")
            return {"safe": True, "document_id": document.id}
        
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return {"safe": False, "reason": f"Processing error: {str(e)}"}
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    async def _process_url(self, url: str) -> Dict:
        """Validate and process a single URL"""
        
        
        try:
            # Validate URL safety and governmental domain
            is_valid = await self.url_validator.validate_url(url)
            
            if not is_valid:
                return {"safe": False, "reason": "URL validation failed (non-governmental domain or unreachable)"}
            
            # Scrape content from URL
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status != 200:
                        return {"safe": False, "reason": f"URL returned status {response.status}"}
                    
                    html_content = await response.text()
            
            # Extract text from HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up text (remove extra whitespace)
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            full_text = '\n'.join(chunk for chunk in chunks if chunk)
            
            if not full_text or len(full_text) < 100:
                return {"safe": False, "reason": "Insufficient content extracted from URL"}
            
            # Validate content safety
            is_safe = await self.content_safety.validate_text(full_text[:8000])
            
            if not is_safe:
                return {"safe": False, "reason": "Content safety violation"}
            
            # Generate unique filename for URL content
            url_hash = str(uuid.uuid4())
            blob_name = f"url_{url_hash}.txt"
            
            # Upload extracted text to Blob Storage
            blob_url = await self.blob_storage.upload_file(
                file_content=full_text.encode('utf-8'),
                blob_name=blob_name,
                content_type="text/plain"
            )
            
            # Create document metadata in Cosmos DB
            from datetime import datetime
            document = Document(
                filename=blob_name,
                original_filename=url,
                content_type="text/html",
                file_size=len(full_text.encode('utf-8')),
                blob_url=blob_url,
                text_preview=full_text[:100000] if full_text else None,
                full_text_extracted=True,
                status=DocumentStatus.VALIDATED,
                is_safe=True,
                validated_at=datetime.utcnow(),
                source="url_scrape",
                chunked=False,
                indexed=False
            )
            
            await self.document_repo.create_document(document)
            
            logger.info(f"URL processed successfully: {url} -> {document.id}")
            return {"safe": True, "document_id": document.id}
        
        except aiohttp.ClientError as e:
            logger.error(f"Network error scraping URL {url}: {str(e)}")
            return {"safe": False, "reason": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            return {"safe": False, "reason": f"Processing error: {str(e)}"}


