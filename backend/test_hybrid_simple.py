import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from models import Document
from automl.retrievers.hybrid_retriever import HybridRetriever

def test_hybrid_retriever():
    print("Testing Hybrid Retriever...")
    
    # Create test documents
    documents = [
        Document(
            id="doc1",
            content="The quick brown fox jumps over the lazy dog.",
            metadata={"source": "test"}
        ),
        Document(
            id="doc2",
            content="The five boxing wizards jump quickly.",
            metadata={"source": "test"}
        ),
        Document(
            id="doc3",
            content="Pack my box with five dozen liquor jugs.",
            metadata={"source": "test"}
        )
    ]
    
    # Initialize hybrid retriever
    hybrid = HybridRetriever(
        bm25_weight=0.5,
        faiss_weight=0.5,
        faiss_model_name='sentence-transformers/all-MiniLM-L6-v2'
    )
    
    # Add documents
    hybrid.add_documents(documents)
    
    # Test query
    query = "quick fox jumping"
    print(f"\nQuery: {query}")
    
    # Get results
    results = hybrid.retrieve(query, top_k=2)
    
    # Print results
    print("\nRetrieved documents:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['document']['content']} (Score: {result['score']:.4f})")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_hybrid_retriever()
