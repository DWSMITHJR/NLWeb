"""Integration test for the hybrid retriever."""
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_retriever_integration():
    """Test the hybrid retriever with a simple document set."""
    from models import Document
    from automl.retrievers.bm25_retriever import BM25Retriever
    from automl.retrievers.faiss_retriever import FAISSRetriever
    from automl.retrievers.hybrid_retriever import HybridRetriever
    
    print("\n=== Starting Retriever Integration Test ===")
    
    # Create test documents
    documents = [
        Document(
            id=f"doc{i}",
            content=content,
            metadata={"source": "test"}
        ) for i, content in enumerate([
            "The quick brown fox jumps over the lazy dog.",
            "The five boxing wizards jump quickly.",
            "Pack my box with five dozen liquor jugs.",
            "How vexingly quick daft zebras jump!",
            "Sphinx of black quartz, judge my vow.",
        ], 1)
    ]
    
    # Initialize retrievers
    print("\nInitializing retrievers...")
    bm25 = BM25Retriever()
    faiss = FAISSRetriever(model_name="sentence-transformers/all-MiniLM-L6-v2")
    hybrid = HybridRetriever(
        bm25_weight=0.5,
        faiss_weight=0.5,
        faiss_model_name="sentence-transformers/all-MiniLM-L6-v2",
    )
    
    # Add documents to retrievers
    print("Adding documents to retrievers...")
    for retriever in [bm25, faiss, hybrid]:
        retriever.add_documents(documents)
    
    # Test queries
    test_queries = [
        "quick fox jumping",
        "boxing wizards",
        "liquor jugs",
        "black quartz"
    ]
    
    for query in test_queries:
        print(f"\n=== Testing query: '{query}' ===")
        
        # Get results from each retriever
        bm25_results = bm25.retrieve(query, top_k=2)
        faiss_results = faiss.retrieve(query, top_k=2)
        hybrid_results = hybrid.retrieve(query, top_k=2)
        
        # Print results
        print("\nBM25 Results:")
        for i, r in enumerate(bm25_results, 1):
            doc = r['document']
            print(f"{i}. ID: {doc.get('id', 'N/A')}, Score: {r['score']:.4f}")
            print(f"   Content: {doc.get('content', 'N/A')[:80]}...")
        
        print("\nFAISS Results:")
        for i, r in enumerate(faiss_results, 1):
            doc = r['document']
            print(f"{i}. ID: {doc.get('id', 'N/A')}, Score: {r['score']:.4f}")
            print(f"   Content: {doc.get('content', 'N/A')[:80]}...")
        
        print("\nHybrid Results:")
        for i, r in enumerate(hybrid_results, 1):
            doc = r['document']
            print(f"{i}. ID: {doc.get('id', 'N/A')}, Score: {r['score']:.4f}")
            print(f"   Content: {doc.get('content', 'N/A')[:80]}...")
    
    print("\n=== Integration Test Completed Successfully ===")

if __name__ == "__main__":
    test_retriever_integration()
