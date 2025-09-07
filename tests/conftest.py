"""
Test configuration and fixtures for the NLWeb project.
"""
import sys
import os
from pathlib import Path
import pytest
from backend.models import Document
from backend.automl.retrievers.hybrid_retriever import HybridRetriever

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test documents for retriever tests
TEST_DOCUMENTS = [
    {
        "id": "doc1",
        "content": "The quick brown fox jumps over the lazy dog.",
        "metadata": {"source": "test"}
    },
    {
        "id": "doc2",
        "content": "The five boxing wizards jump quickly.",
        "metadata": {"source": "test"}
    },
    {
        "id": "doc3",
        "content": "Pack my box with five dozen liquor jugs.",
        "metadata": {"source": "test"}
    },
]

@pytest.fixture
def test_documents():
    """Fixture providing test documents for retriever tests."""
    return [
        Document(
            id=f"doc{i+1}",
            content=content,
            metadata={"source": "test"}
        )
        for i, content in enumerate([
            "The quick brown fox jumps over the lazy dog.",
            "The five boxing wizards jump quickly.",
            "Pack my box with five dozen liquor jugs."
        ])
    ]

@pytest.fixture
def hybrid_retriever():
    """Fixture providing a configured HybridRetriever instance for testing."""
    return HybridRetriever(
        bm25_weight=0.5,
        faiss_weight=0.5,
        faiss_model_name="sentence-transformers/all-MiniLM-L6-v2",
    )
