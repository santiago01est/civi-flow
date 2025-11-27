# app/services/embeddings_service.py
import logging
from typing import List
from openai import AzureOpenAI
from app.config.settings import settings


logger = logging.getLogger(__name__)


class EmbeddingsService:
    """Service to generate embeddings using Azure OpenAI"""
    
    def __init__(self):
        """Initialize Azure OpenAI client for embeddings"""
        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        
        self.deployment_name = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        
        logger.info(f"EmbeddingsService initialized with deployment: {self.deployment_name}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text
        
        Args:
            text: Text to embed
        
        Returns:
            List of floats representing the embedding vector (1536 dimensions for ada-002)
        """
        try:
            # Clean and truncate text if needed (max 8191 tokens for ada-002)
            text = text.replace("\n", " ").strip()
            
            if not text:
                logger.warning("Empty text provided for embedding")
                return []
            
            # Generate embedding using new SDK
            response = self.client.embeddings.create(
                input=text,
                model=self.deployment_name
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch
        More efficient than calling generate_embedding multiple times
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        try:
            if not texts:
                logger.warning("Empty texts list provided")
                return []
            
            # Clean texts
            cleaned_texts = [text.replace("\n", " ").strip() for text in texts]
            
            # Generate embeddings in batch using new SDK
            response = self.client.embeddings.create(
                input=cleaned_texts,
                model=self.deployment_name
            )
            
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings in batch")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
