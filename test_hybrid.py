import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_hybrid_retriever():
    print("Testing HybridRetriever...")
    
    try:
        from backend.models import Document
        from backend.automl.retrievers.hybrid_retriever import HybridRetriever
        print("✓ Successfully imported modules")
        
        # Test documents
        documents = [
            Document(
                id=f"doc{i}",
                content=content,
                metadata={"source": "test"}
            ) for i, content in enumerate([
                "The quick brown fox jumps over the lazy dog.",
                "The five boxing wizards jump quickly.",
                "Pack my box with five dozen liquor jugs.",
            ])
        ]
        
        # Initialize hybrid retriever
        hybrid = HybridRetriever(
            bm25_weight=0.5,
            faiss_weight=0.5,
            faiss_model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Add documents
        hybrid.add_documents(documents)
        print("✓ Successfully added documents")
        
        # Test query
        query = "quick fox jumping"
        results = hybrid.retrieve(query, top_k=2)
        
        print(f"\nResults for query: '{query}'")
        for i, result in enumerate(results, 1):
            doc = result['document']
            if hasattr(doc, 'content'):
                content = doc.content
            elif isinstance(doc, dict):
                content = doc.get('content', 'No content')
            else:
                content = str(doc)
            
            print(f"\n{i}. Score: {result['score']:.4f}")
            print(f"   Content: {content}")
            print(f"   BM25 Score: {result.get('bm25_score', 'N/A'):.4f}")
            print(f"   FAISS Score: {result.get('faiss_score', 'N/A'):.4f}")
        
        print("\n✓ Test completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hybrid_retriever()
