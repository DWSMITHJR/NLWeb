from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
import yaml
from pathlib import Path

class RetrieverType(str, Enum):
    FAISS = "faiss"
    BM25 = "bm25"
    DPR = "dpr"

class EmbeddingModel(str, Enum):
    MINILM = "sentence-transformers/all-MiniLM-L6-v2"
    MPNET = "sentence-transformers/all-mpnet-base-v2"
    MULTI_QA = "sentence-transformers/multi-qa-mpnet-base-dot-v1"

class ChunkingStrategy(str, Enum):
    FIXED = "fixed"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"

class AutoMLConfig(BaseModel):
    """Configuration for AutoML optimization"""
    # Retriever settings
    retrievers: List[RetrieverType] = Field(
        default_factory=lambda: [RetrieverType.FAISS, RetrieverType.BM25],
        description="List of retriever types to test"
    )
    
    # Chunking settings
    chunk_sizes: List[int] = Field(
        default_factory=lambda: [128, 256, 512],
        description="List of chunk sizes (in tokens) to test"
    )
    chunk_overlap: int = Field(
        default=50,
        description="Overlap between chunks in tokens"
    )
    chunking_strategy: ChunkingStrategy = Field(
        default=ChunkingStrategy.FIXED,
        description="Strategy for splitting documents into chunks"
    )
    
    # Embedding model settings
    embedding_models: List[EmbeddingModel] = Field(
        default_factory=lambda: [EmbeddingModel.MINILM, EmbeddingModel.MPNET],
        description="List of embedding models to test"
    )
    
    # Prompt template settings
    prompt_templates: List[Dict[str, Any]] = Field(
        default_factory=lambda: [
            {
                "name": "basic",
                "template": "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
            },
            {
                "name": "detailed",
                "template": "Based on the following context, please answer the question.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer with details:"
            }
        ],
        description="List of prompt templates to test"
    )
    
    # Evaluation settings
    test_queries: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Test queries with expected answers for evaluation"
    )
    
    @classmethod
    def from_yaml(cls, file_path: str) -> 'AutoMLConfig':
        """Load configuration from YAML file"""
        with open(file_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)
    
    def to_yaml(self, file_path: str) -> None:
        """Save configuration to YAML file"""
        with open(file_path, 'w') as f:
            yaml.dump(self.dict(), f, sort_keys=False)
    
    @classmethod
    def get_default_config(cls) -> 'AutoMLConfig':
        """Get default configuration"""
        return cls()

# Default configuration path
DEFAULT_CONFIG_PATH = Path(__file__).parent / "default_config.yaml"

def load_default_config() -> AutoMLConfig:
    """Load default configuration"""
    if not DEFAULT_CONFIG_PATH.exists():
        config = AutoMLConfig.get_default_config()
        config.to_yaml(DEFAULT_CONFIG_PATH)
    return AutoMLConfig.from_yaml(DEFAULT_CONFIG_PATH)
