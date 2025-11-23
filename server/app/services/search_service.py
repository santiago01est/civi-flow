# Azure AI Search for gov data
from typing import List, Dict, Optional
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching government documents using Azure AI Search"""
    
    def __init__(self):
        if settings.AZURE_SEARCH_ENDPOINT and settings.AZURE_SEARCH_API_KEY:
            self.client = SearchClient(
                endpoint=settings.AZURE_SEARCH_ENDPOINT,
                index_name=settings.AZURE_SEARCH_INDEX_NAME,
                credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY)
            )
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            logger.warning("Azure Search not configured - using mock data")
    
    async def search_documents(self, query: str, top: int = 3) -> List[Dict]:
        """
        Search for relevant government documents
        Returns list of documents with title, content, and metadata
        """
        if not self.enabled:
            return self._get_mock_results(query)
        
        try:
            results = self.client.search(
                search_text=query,
                top=top,
                select=["title", "content", "uri", "type", "size"]
            )
            
            documents = []
            for result in results:
                documents.append({
                    "title": result.get("title", "Untitled Document"),
                    "content": result.get("content", ""),
                    "uri": result.get("uri", "#"),
                    "type": result.get("type", "PDF"),
                    "size": result.get("size", "N/A")
                })
            
            return documents
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return self._get_mock_results(query)
    
    def _get_mock_results(self, query: str) -> List[Dict]:
        """Return mock search results for development"""
        return [
            {
                "title": "Zoning Ordinance Ch. 17, Sec. 17.20.040",
                "content": "Regulations regarding short-term rentals and residential zoning requirements...",
                "uri": "#zoning-ordinance",
                "type": "PDF",
                "size": "1.2 MB"
            },
            {
                "title": "City Council Resolution No. 2023-45",
                "content": "Resolution establishing operational standards for short-term rental properties...",
                "uri": "#council-resolution",
                "type": "PDF",
                "size": "450 KB"
            }
        ]
    
    def create_citations(self, documents: List[Dict]) -> List[Dict]:
        """Convert search results to citation format"""
        citations = []
        for idx, doc in enumerate(documents, 1):
            citations.append({
                "id": str(idx),
                "title": doc.get("title", ""),
                "uri": doc.get("uri", "#"),
                "type": doc.get("type", "PDF"),
                "size": doc.get("size", "N/A")
            })
        return citations