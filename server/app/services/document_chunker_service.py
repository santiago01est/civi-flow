# app/services/document_chunker_service.py
import logging
from typing import List, Dict
import tiktoken


logger = logging.getLogger(__name__)


class DocumentChunk:
    """Represents a single chunk of text from a document"""
    def __init__(
        self, 
        chunk_id: str,
        document_id: str,
        content: str,
        chunk_index: int,
        total_chunks: int,
        metadata: Dict
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.content = content
        self.chunk_index = chunk_index
        self.total_chunks = total_chunks
        self.metadata = metadata


class DocumentChunkerService:
    """Service to split documents into chunks for RAG processing"""
    
    def __init__(
        self, 
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        encoding_name: str = "cl100k_base"
    ):
        """
        Initialize chunker with configurable parameters
        
        Args:
            chunk_size: Maximum tokens per chunk (default 800)
            chunk_overlap: Overlapping tokens between chunks (default 100)
            encoding_name: Tokenizer encoding (cl100k_base for GPT-4/embeddings)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)
        logger.info(f"DocumentChunker initialized: size={chunk_size}, overlap={chunk_overlap}")
    
    def chunk_text(
        self, 
        text: str, 
        document_id: str,
        metadata: Dict = None
    ) -> List[DocumentChunk]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Full text to chunk
            document_id: ID of the source document
            metadata: Additional metadata (filename, source, category, etc.)
        
        Returns:
            List of DocumentChunk objects
        """
        if not text or not text.strip():
            logger.warning(f"Empty text provided for document {document_id}")
            return []
        
        # Tokenize the full text
        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)
        
        logger.info(f"Document {document_id}: {total_tokens} tokens")
        
        chunks = []
        chunk_index = 0
        start = 0
        
        while start < total_tokens:
            # Define end position for this chunk
            end = min(start + self.chunk_size, total_tokens)
            
            # Extract chunk tokens and decode back to text
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Create chunk ID
            chunk_id = f"{document_id}_chunk_{chunk_index}"
            
            # Create DocumentChunk object
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                content=chunk_text,
                chunk_index=chunk_index,
                total_chunks=0,  # Will update after
                metadata=metadata or {}
            )
            
            chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            chunk_index += 1
        
        # Update total_chunks in all chunks
        total_chunks = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = total_chunks
        
        logger.info(f"Created {total_chunks} chunks for document {document_id}")
        return chunks
    
    def chunk_text_by_sentences(
        self, 
        text: str, 
        document_id: str,
        metadata: Dict = None
    ) -> List[DocumentChunk]:
        """
        Alternative chunking strategy: split by sentences to preserve context
        Useful for documents where semantic boundaries are important
        """
        import re
        
        # Split by sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_tokens = len(self.encoding.encode(sentence))
            
            # If adding this sentence exceeds chunk_size, save current chunk
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunk_id = f"{document_id}_chunk_{chunk_index}"
                
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    content=chunk_text,
                    chunk_index=chunk_index,
                    total_chunks=0,
                    metadata=metadata or {}
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap (keep last sentence)
                current_chunk = [current_chunk[-1]] if current_chunk else []
                current_tokens = len(self.encoding.encode(current_chunk[0])) if current_chunk else 0
                chunk_index += 1
            
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk_id = f"{document_id}_chunk_{chunk_index}"
            
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                content=chunk_text,
                chunk_index=chunk_index,
                total_chunks=0,
                metadata=metadata or {}
            )
            chunks.append(chunk)
        
        # Update total_chunks
        total_chunks = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = total_chunks
        
        logger.info(f"Created {total_chunks} sentence-based chunks for document {document_id}")
        return chunks
