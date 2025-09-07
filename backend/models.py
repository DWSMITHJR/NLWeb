from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any, List, Optional
from enum import Enum


class Document(BaseModel):
    """
    Represents a single document in the knowledge base, containing text content and metadata.

    Attributes:
        id: A unique identifier for the document.
        content: The text content of the document.
        metadata: A dictionary of additional metadata about the document.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A document containing text content and metadata"
        }
    )

    id: str = Field(..., description="Unique identifier for the document")
    content: str = Field(..., description="Text content of the document")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata about the document"
    )
    
    def model_dump(self, **kwargs):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata
        }


class ChunkingStrategy(str, Enum):
    """Available document chunking strategies"""

    FIXED = "fixed"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"


class DocumentChunk(BaseModel):
    """
    Represents a chunk of a document, created by the DocumentProcessor.

    Attributes:
        id: A unique identifier for the chunk.
        document_id: The ID of the parent document.
        content: The text content of the chunk.
        metadata: A dictionary of additional metadata about the chunk.
        chunk_index: The index of this chunk within the parent document.
        chunk_strategy: The strategy used to create this chunk.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A chunk of a document with associated metadata"
        }
    )

    id: str = Field(..., description="Unique identifier for the chunk")
    document_id: str = Field(..., description="ID of the parent document")
    content: str = Field(..., description="Text content of the chunk")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata about the chunk"
    )
    chunk_index: int = Field(
        default=0, description="Index of this chunk within the parent document"
    )
    chunk_strategy: ChunkingStrategy = Field(
        default=ChunkingStrategy.FIXED,
        description="Strategy used to create this chunk",
    )
    
    def model_dump(self, **kwargs):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "metadata": self.metadata,
            "chunk_index": self.chunk_index,
            "chunk_strategy": self.chunk_strategy.value
        }


class DocumentProcessorConfig(BaseModel):
    """
    Configuration for the DocumentProcessor.

    Attributes:
        chunk_size: The maximum size of each chunk in characters.
        chunk_overlap: The number of characters to overlap between chunks.
        chunking_strategy: The strategy to use for chunking documents.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Configuration for document processing parameters"
        },
        json_encoders={ChunkingStrategy: lambda v: v.value},
        use_enum_values=True,
    )

    chunk_size: int = Field(
        default=256,
        ge=1,
        le=4096,
        description="Maximum size of each chunk in characters",
    )
    chunk_overlap: int = Field(
        default=50, ge=0, description="Number of characters to overlap between chunks"
    )
    chunking_strategy: ChunkingStrategy = Field(
        default=ChunkingStrategy.FIXED,
        description="Strategy to use for chunking documents",
    )
