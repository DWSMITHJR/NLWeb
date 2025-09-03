from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum

class Document(BaseModel):
    """Document model for storing text content and metadata"""
    id: str = Field(..., description="Unique identifier for the document")
    content: str = Field(..., description="Text content of the document")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional metadata about the document"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary"""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create document from dictionary"""
        return cls(
            id=data.get("id", ""),
            content=data.get("content", ""),
            metadata=data.get("metadata", {})
        )

class ChunkingStrategy(str, Enum):
    """Available document chunking strategies"""
    FIXED = "fixed"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"

class DocumentChunk(BaseModel):
    """Represents a chunk of a document"""
    id: str
    document_id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunk_index: int
    chunk_strategy: ChunkingStrategy
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary"""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "metadata": self.metadata,
            "chunk_index": self.chunk_index,
            "chunk_strategy": self.chunk_strategy.value
        }

class DocumentProcessorConfig(BaseModel):
    """Configuration for document processing"""
    chunk_size: int = 256
    chunk_overlap: int = 50
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.FIXED
    
    class Config:
        use_enum_values = True
        json_encoders = {
            ChunkingStrategy: lambda v: v.value
        }
