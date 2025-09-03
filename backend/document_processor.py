import re
from typing import List, Dict, Any, Optional
from .models import Document, DocumentChunk, ChunkingStrategy, DocumentProcessorConfig

class DocumentProcessor:
    """Process documents into chunks based on different strategies"""
    
    def __init__(self, config: Optional[DocumentProcessorConfig] = None):
        """Initialize with optional configuration"""
        self.config = config or DocumentProcessorConfig()
    
    def process_document(self, document: Document) -> List[DocumentChunk]:
        """
        Process a single document into chunks based on the configured strategy
        
        Args:
            document: The document to process
            
        Returns:
            List of document chunks
        """
        chunking_strategy = self.config.chunking_strategy
        
        if chunking_strategy == ChunkingStrategy.FIXED:
            return self._chunk_by_fixed_size(document)
        elif chunking_strategy == ChunkingStrategy.SENTENCE:
            return self._chunk_by_sentence(document)
        elif chunking_strategy == ChunkingStrategy.PARAGRAPH:
            return self._chunk_by_paragraph(document)
        else:
            raise ValueError(f"Unsupported chunking strategy: {chunking_strategy}")
    
    def _chunk_by_fixed_size(self, document: Document) -> List[DocumentChunk]:
        """Split document into fixed-size chunks"""
        text = document.content
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        
        chunks = []
        start = 0
        chunk_idx = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # Only add non-empty chunks
                chunk_id = f"{document.id}_chunk_{chunk_idx}"
                chunks.append(DocumentChunk(
                    id=chunk_id,
                    document_id=document.id,
                    content=chunk_text,
                    metadata=document.metadata.copy(),
                    chunk_index=chunk_idx,
                    chunk_strategy=self.config.chunking_strategy
                ))
                chunk_idx += 1
                
            start = end - overlap  # Apply overlap
            
            # Prevent infinite loop if overlap is too large
            if start >= len(text) - 1:
                break
                
        return chunks
    
    def _chunk_by_sentence(self, document: Document) -> List[DocumentChunk]:
        """Split document into chunks based on sentence boundaries"""
        # Simple sentence splitting - can be enhanced with NLTK or spaCy for better accuracy
        sentences = re.split(r'(?<=[.!?])\s+', document.content)
        
        chunks = []
        current_chunk = []
        current_length = 0
        chunk_idx = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_length = len(sentence.split())
            max_chunk_size = self.config.chunk_size
            
            if current_length + sentence_length > max_chunk_size and current_chunk:
                # Save current chunk and start a new one
                chunk_id = f"{document.id}_chunk_{chunk_idx}"
                chunks.append(DocumentChunk(
                    id=chunk_id,
                    document_id=document.id,
                    content=' '.join(current_chunk),
                    metadata=document.metadata.copy(),
                    chunk_index=chunk_idx,
                    chunk_strategy=self.config.chunking_strategy
                ))
                chunk_idx += 1
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add the last chunk if not empty
        if current_chunk:
            chunk_id = f"{document.id}_chunk_{chunk_idx}"
            chunks.append(DocumentChunk(
                id=chunk_id,
                document_id=document.id,
                content=' '.join(current_chunk),
                metadata=document.metadata.copy(),
                chunk_index=chunk_idx,
                chunk_strategy=self.config.chunking_strategy
            ))
            
        return chunks
    
    def _chunk_by_paragraph(self, document: Document) -> List[DocumentChunk]:
        """Split document into chunks based on paragraphs"""
        # Split by double newlines (common paragraph separator)
        paragraphs = [p.strip() for p in document.content.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        current_length = 0
        chunk_idx = 0
        
        for para in paragraphs:
            para_length = len(para.split())
            max_chunk_size = self.config.chunk_size
            
            if para_length > max_chunk_size:
                # If a single paragraph is larger than chunk size, split it
                words = para.split()
                for i in range(0, len(words), max_chunk_size):
                    chunk_words = words[i:i + max_chunk_size]
                    chunk_id = f"{document.id}_chunk_{chunk_idx}"
                    chunks.append(DocumentChunk(
                        id=chunk_id,
                        document_id=document.id,
                        content=' '.join(chunk_words),
                        metadata=document.metadata.copy(),
                        chunk_index=chunk_idx,
                        chunk_strategy=self.config.chunking_strategy
                    ))
                    chunk_idx += 1
            else:
                if current_length + para_length > max_chunk_size and current_chunk:
                    # Save current chunk and start a new one
                    chunk_id = f"{document.id}_chunk_{chunk_idx}"
                    chunks.append(DocumentChunk(
                        id=chunk_id,
                        document_id=document.id,
                        content='\n\n'.join(current_chunk),
                        metadata=document.metadata.copy(),
                        chunk_index=chunk_idx,
                        chunk_strategy=self.config.chunking_strategy
                    ))
                    chunk_idx += 1
                    current_chunk = [para]
                    current_length = para_length
                else:
                    current_chunk.append(para)
                    current_length += para_length
        
        # Add the last chunk if not empty
        if current_chunk:
            chunk_id = f"{document.id}_chunk_{chunk_idx}"
            chunks.append(DocumentChunk(
                id=chunk_id,
                document_id=document.id,
                content='\n\n'.join(current_chunk),
                metadata=document.metadata.copy(),
                chunk_index=chunk_idx,
                chunk_strategy=self.config.chunking_strategy
            ))
            
        return chunks
