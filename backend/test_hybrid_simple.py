from backend.models import Document
from backend.automl.retrievers.hybrid_retriever import HybridRetriever


def test_hybrid_retriever():
    print("Testing Hybrid Retriever...")

    # Create test documents
    documents = [
        Document(
            id="doc1",
            content="The quick brown fox jumps over the lazy dog.",
            metadata={"source": "test"},
        ),
        Document(
            id="doc2",
            content="The five boxing wizards jump quickly.",
            metadata={"source": "test"},
        ),
        Document(
            id="doc3",
            content="Pack my box with five dozen liquor jugs.",
            metadata={"source": "test"},
        ),
    ]

    # Initialize hybrid retriever
    hybrid = HybridRetriever(
        bm25_weight=0.5,
        faiss_weight=0.5,
        faiss_model_name="sentence-transformers/all-MiniLM-L6-v2",
    )

    # Add documents
    hybrid.add_documents(documents)

    try:
        # Test query
        query = "quick fox jumping"
        print(f"\nQuery: {query}")

        # Get results
        print("\nRetrieving results...")
        results = hybrid.retrieve(query, top_k=2)
        print(f"Retrieved {len(results)} results")

        # Print results with detailed debugging
        print("\nRetrieved documents:")
        for i, result in enumerate(results, 1):
            try:
                doc = result.get('document', {})
                doc_id = getattr(doc, 'id', None) or doc.get('id', 'unknown')
                content = getattr(doc, 'content', '') or doc.get('content', 'no content')
                score = result.get('score', 0.0)
                print(f"{i}. ID: {doc_id}, Content: {content[:50]}... (Score: {score:.4f})")
            except Exception as e:
                print(f"Error processing result {i}: {str(e)}")
                print(f"Result object: {result}")
                raise

        # Basic assertions
        assert len(results) == 2, f"Should retrieve 2 documents, got {len(results)}"
        
        # Check result structure
        assert all(isinstance(r, dict) for r in results), "Results should be dictionaries"
        assert all('document' in r and 'score' in r for r in results), "Results missing required fields"
        
        # Extract document IDs safely
        doc_ids = []
        for r in results:
            doc = r.get('document', {})
            doc_id = getattr(doc, 'id', None) or doc.get('id')
            if doc_id:
                doc_ids.append(doc_id)
        
        print(f"Found document IDs: {doc_ids}")
        assert 'doc1' in doc_ids, f"Expected doc1 in results, got {doc_ids}"
        
        # Check score ordering
        scores = [r.get('score', 0.0) for r in results]
        print(f"Scores: {scores}")
        assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1)), \
            f"Scores not in descending order: {scores}"
            
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        print("\nDebug info:")
        print(f"Results type: {type(results) if 'results' in locals() else 'Not defined'}")
        if 'results' in locals():
            print(f"Results length: {len(results)}")
            print(f"First result type: {type(results[0]) if results else 'No results'}")
        raise

    print("\nTest completed successfully!")
