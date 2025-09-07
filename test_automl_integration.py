"""
Integration tests for AutoML Orchestrator and its components.
"""
import pytest
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

# Add project root to Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.automl.orchestrator import AutoMLOrchestrator
from backend.models import Document, DocumentProcessorConfig, ChunkingStrategy
from backend.document_processor import DocumentProcessor

# Sample test documents
TEST_DOCUMENTS = [
    Document(
        id="doc1",
        content="The quick brown fox jumps over the lazy dog.",
        metadata={"source": "test", "page": 1}
    ),
    Document(
        id="doc2",
        content="Pack my box with five dozen liquor jugs.",
        metadata={"source": "test", "page": 2}
    ),
    Document(
        id="doc3",
        content="How vexingly quick daft zebras jump!",
        metadata={"source": "test", "page": 3}
    ),
]

# Sample test queries and expected results
TEST_QUERIES = [
    ("quick jumping animals", ["doc1", "doc3"]),
    ("box with jugs", ["doc2"]),
]

class TestAutoMLIntegration:
    """Integration tests for AutoML Orchestrator."""
    
    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create a temporary output directory for test results."""
        return tmp_path / "automl_test_results"
    
    @pytest.fixture
    def automl_orchestrator(self, temp_output_dir):
        """Create an AutoMLOrchestrator instance for testing."""
        return AutoMLOrchestrator(output_dir=str(temp_output_dir), max_workers=2)
    
    @pytest.fixture
    def document_processor(self):
        """Create a DocumentProcessor instance for testing."""
        config = DocumentProcessorConfig(
            chunking_strategy=ChunkingStrategy.FIXED,
            chunk_size=100,
            chunk_overlap=20
        )
        return DocumentProcessor(config)
    
    def test_orchestrator_initialization(self, automl_orchestrator, temp_output_dir):
        """Test that the orchestrator initializes correctly."""
        # Compare string representations to handle WindowsPath vs string comparison
        assert str(automl_orchestrator.output_dir) == str(temp_output_dir)
        assert automl_orchestrator.max_workers == 2
        assert len(automl_orchestrator.results) == 0
        assert automl_orchestrator.best_score == -float("inf")
    
    def test_optimize_retrieval(self, automl_orchestrator, document_processor, temp_output_dir):
        """Test the retrieval optimization process."""
        # Convert test queries to the expected format
        test_queries = [
            {"query": query, "relevant_docs": [doc for doc in TEST_DOCUMENTS if doc.id in expected_ids]}
            for query, expected_ids in TEST_QUERIES
        ]
        
        # Base configuration
        base_config = {
            "retriever_type": "faiss",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "chunk_size": 100,
            "chunk_overlap": 20,
            "chunking_strategy": "fixed"
        }
        
        # Run optimization
        result = automl_orchestrator.run(
            train_documents=TEST_DOCUMENTS,
            test_queries=test_queries,
            base_config=base_config,
            num_configs=2,
            save_every=1
        )
        
        # Check results
        assert "best_config" in result
        assert "best_score" in result
        assert "results" in result
        assert len(result["results"]) > 0
        
        # Check that output files were created
        assert any("best_config" in f.name for f in temp_output_dir.glob("*.json"))
    
    def test_end_to_end_optimization(self, automl_orchestrator, document_processor):
        """Test the end-to-end optimization process."""
        # Convert test queries to the expected format
        test_queries = [
            {"query": query, "relevant_docs": [doc for doc in TEST_DOCUMENTS if doc.id in expected_ids]}
            for query, expected_ids in TEST_QUERIES
        ]
        
        # Base configuration
        base_config = {
            "retriever_type": "faiss",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "chunk_size": 100,
            "chunk_overlap": 20,
            "chunking_strategy": "fixed"
        }
        
        # This is a simplified test that just verifies the method runs without errors
        try:
            automl_orchestrator.run(
                train_documents=TEST_DOCUMENTS,
                test_queries=test_queries,
                base_config=base_config,
                num_configs=1,
                save_every=1
            )
            assert True  # If we get here, the test passed
        except Exception as e:
            pytest.fail(f"End-to-end optimization failed with error: {str(e)}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
