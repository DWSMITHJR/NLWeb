import unittest
from unittest.mock import MagicMock, patch, ANY
import numpy as np
import sys
from pathlib import Path

# Import the module to test
sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.models import Document, DocumentChunk, ChunkingStrategy, DocumentProcessorConfig

# Import the module to test after setting up mocks
from backend.automl.orchestrator import AutoMLOrchestrator

class TestAutoMLOrchestrator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.output_dir = "test_automl_results"
        self.orchestrator = AutoMLOrchestrator(output_dir=self.output_dir, max_workers=2)
        
        # Create test documents
        self.test_docs = [
            Document(
                id="doc1",
                content="This is a test document about machine learning.",
                metadata={"source": "test"}
            ),
            Document(
                id="doc2",
                content="Another document about artificial intelligence and deep learning.",
                metadata={"source": "test"}
            )
        ]
        
        # Create test queries
        self.test_queries = [
            {"query": "What is machine learning?", "relevant_doc_ids": ["doc1"]},
            {"query": "Tell me about AI", "relevant_doc_ids": ["doc2"]}
        ]
    
    def test_initialization(self):
        """Test that the orchestrator initializes correctly."""
        self.assertEqual(self.orchestrator.output_dir, Path(self.output_dir))
        self.assertEqual(self.orchestrator.max_workers, 2)
        self.assertEqual(self.orchestrator.best_score, -float("inf"))
        self.assertIsNone(self.orchestrator.best_config)
    
    def test_create_retriever_faiss(self):
        """Test creating a FAISS retriever."""
        # Import the module after patching
        import sys
        if 'backend.automl.orchestrator' in sys.modules:
            del sys.modules['backend.automl.orchestrator']
        
        with patch('backend.automl.orchestrator.FAISSRetriever') as mock_faiss:
            # Setup mocks
            mock_instance = MagicMock()
            mock_faiss.return_value = mock_instance

            config = {
                "retriever_type": "faiss",
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "normalize_embeddings": True
            }
            
            # Import the orchestrator after patching
            from backend.automl.orchestrator import AutoMLOrchestrator
            orchestrator = AutoMLOrchestrator()
            
            # Call the method under test
            retriever = orchestrator._create_retriever(config)
            
            # Verify the FAISS retriever was created with correct parameters
            mock_faiss.assert_called_once_with(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                normalize_embeddings=True
            )
            self.assertEqual(retriever, mock_instance)
    
    def test_create_retriever_bm25(self):
        """Test creating a BM25 retriever."""
        # Import the module after patching
        import sys
        if 'backend.automl.orchestrator' in sys.modules:
            del sys.modules['backend.automl.orchestrator']
        
        # Create the mock before importing the module
        with patch('backend.automl.retrievers.bm25_retriever.BM25Retriever') as mock_bm25:
            # Setup the mock to return an instance
            mock_instance = MagicMock()
            mock_bm25.return_value = mock_instance
            
            # Now import the module with the patch in place
            from backend.automl.orchestrator import AutoMLOrchestrator
            orchestrator = AutoMLOrchestrator()
            
            # Call the method under test
            config = {"retriever_type": "bm25"}
            retriever = orchestrator._create_retriever(config)
            
            # Verify the retriever was created and returned
            mock_bm25.assert_called_once()
            self.assertEqual(retriever, mock_instance)
    
    def test_create_processor_config(self):
        """Test creating a processor config."""
        config = {
            "chunk_size": 512,
            "chunk_overlap": 100,
            "chunking_strategy": "sentence"
        }
        
        processor_config = self.orchestrator._create_processor_config(config)
        self.assertEqual(processor_config.chunk_size, 512)
        self.assertEqual(processor_config.chunk_overlap, 100)
        self.assertEqual(processor_config.chunking_strategy, ChunkingStrategy.SENTENCE)
    
    @patch('backend.automl.orchestrator.RetrievalMetrics')
    @patch('backend.automl.retrievers.bm25_retriever.BM25Retriever')
    def test_evaluate_retrieval(self, mock_bm25_class, mock_metrics_class):
        """Test retrieval evaluation."""
        # Import the module here to ensure proper patching
        import sys
        if 'backend.automl.orchestrator' in sys.modules:
            del sys.modules['backend.automl.orchestrator']
        if 'backend.automl.retrievers.bm25_retriever' in sys.modules:
            del sys.modules['backend.automl.retrievers.bm25_retriever']
        
        # Create a mock BM25 retriever instance
        mock_retriever = MagicMock()
        
        # Mock the return value to match what the orchestrator expects
        mock_retriever.retrieve.return_value = [
            {
                "document": {
                    "id": "doc1", 
                    "content": "This is a test document about machine learning.",
                    "metadata": {}
                },
                "score": 0.9
            },
            {
                "document": {
                    "id": "doc2", 
                    "content": "Another document about AI.",
                    "metadata": {}
                },
                "score": 0.8
            }
        ]
        
        # Set up the BM25 class to return our mock instance
        mock_bm25_class.return_value = mock_retriever
        
        # Helper to create DocumentChunk instances with all required fields
        def create_document_chunk(id, content, metadata=None):
            return DocumentChunk(
                id=id,
                document_id=id,  # Using same ID for simplicity
                content=content,
                metadata=metadata or {},
                chunk_index=0,
                chunk_strategy=ChunkingStrategy.FIXED
            )
        
        # Create a mock metrics instance
        mock_metrics_instance = MagicMock()
        mock_metrics_class.return_value = mock_metrics_instance
        
        # Setup the return value for calculate_metrics
        mock_metrics_instance.calculate_metrics.return_value = {
            "precision@1": 1.0,
            "recall@3": 0.8,
            "ndcg@5": 0.85,
            "mrr": 0.9
        }
        
        # Mock the static methods to return expected values
        def mock_calculate_precision_recall(retrieved, relevant, k=5):
            return {"precision@1": 1.0, "recall@3": 0.8, "ndcg@5": 0.85}
            
        def mock_calculate_mrr(retrieved, relevant):
            return 0.9
            
        mock_metrics_class.calculate_precision_recall = mock_calculate_precision_recall
        mock_metrics_class.calculate_mrr = mock_calculate_mrr
        
        test_queries = [
            {
                "query": "machine learning", 
                "relevant_docs": [
                    {
                        "id": "doc1",
                        "content": "This is a test document about machine learning.",
                        "metadata": {}
                    }
                ]
            },
            {
                "query": "artificial intelligence", 
                "relevant_docs": [
                    {
                        "id": "doc2",
                        "content": "Another document about AI.",
                        "metadata": {}
                    }
                ]
            }
        ]
        
        # Import the orchestrator after patching
        from backend.automl.orchestrator import AutoMLOrchestrator, RetrievalMetrics
        
        # Create the orchestrator
        orchestrator = AutoMLOrchestrator()
        
        # Call the method under test
        results = orchestrator._evaluate_retrieval(
            mock_retriever, test_queries, top_k=3
        )
        
        # Verify the results contain expected metrics
        self.assertIn("metrics", results)
        self.assertIn("mean_metrics", results)
        self.assertEqual(len(results["metrics"]), len(test_queries))
        self.assertIn("mean_precision", results["mean_metrics"])
        
        # Verify retriever.retrieve was called for each query
        self.assertEqual(mock_retriever.retrieve.call_count, len(test_queries))
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up test output directory
        import shutil
        if Path(self.output_dir).exists():
            shutil.rmtree(self.output_dir)

if __name__ == '__main__':
    unittest.main()
