import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import necessary modules
from backend.models import DocumentChunk
from backend.automl.retrievers.base import BaseRetriever

# Mock the RetrievalMetrics class
class MockRetrievalMetrics:
    @staticmethod
    def calculate_precision_recall(retrieved, relevant, k):
        return {"precision@1": 1.0, "recall@3": 0.8, "ndcg@5": 0.85}
    
    @staticmethod
    def calculate_mrr(retrieved, relevant):
        return 0.9

# Mock DocumentChunk
class MockDocumentChunk:
    def __init__(self, id, document_id, content, metadata):
        self.id = id
        self.document_id = document_id
        self.content = content
        self.metadata = metadata

# Import the orchestrator after setting up mocks
sys.modules['backend.automl.orchestrator'] = sys.modules[__name__]
from backend.automl.orchestrator import AutoMLOrchestrator

# Create a mock retriever
class MockRetriever(BaseRetriever):
    def add_documents(self, documents):
        pass
        
    def retrieve(self, query, top_k=5, **kwargs):
        return [
            {
                "document": {
                    "id": "doc1",
                    "content": "Test content 1",
                    "metadata": {}
                },
                "score": 0.9
            },
            {
                "document": {
                    "id": "doc2",
                    "content": "Test content 2",
                    "metadata": {}
                },
                "score": 0.8
            }
        ]

# Create test data
test_queries = [
    {
        "query": "test query",
        "relevant_docs": [
            {
                "id": "doc1",
                "content": "Test content 1",
                "metadata": {}
            }
        ]
    }
]

# Test the method
def test_evaluate_retrieval():
    orchestrator = AutoMLOrchestrator()
    retriever = MockRetriever()
    
    # Patch the DocumentChunk class
    with patch('backend.models.DocumentChunk', MockDocumentChunk):
        results = orchestrator._evaluate_retrieval(retriever, test_queries, top_k=3)
    
    print("Test Results:")
    print(f"Precision@1: {results.get('precision@1')}")
    print(f"Recall@3: {results.get('recall@3')}")
    print(f"NDCG@5: {results.get('ndcg@5')}")
    print(f"MRR: {results.get('mrr')}")

if __name__ == "__main__":
    test_evaluate_retrieval()
