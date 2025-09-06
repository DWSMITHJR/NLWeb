import json
from typing import List, Dict, Any
import numpy as np
from datetime import datetime

from backend.models import Document
from backend.automl.retrievers.hybrid_retriever import HybridRetriever
from backend.automl.retrievers.faiss_retriever import FAISSRetriever
from backend.automl.retrievers.bm25_retriever import BM25Retriever


def load_test_data() -> tuple[List[Document], List[Dict[str, Any]]]:
    """Load test documents and queries"""
    # Sample documents
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
        Document(
            id="doc4",
            content="How vexingly quick daft zebras jump!",
            metadata={"source": "test"},
        ),
        Document(
            id="doc5",
            content="The quick brown fox is a skilled jumper.",
            metadata={"source": "test"},
        ),
    ]

    # Sample test queries with relevant documents
    test_queries = [
        {"query": "quick fox jumping", "relevant_docs": ["doc1", "doc5"]},
        {"query": "wizards jumping quickly", "relevant_docs": ["doc2"]},
        {"query": "zebras jumping", "relevant_docs": ["doc4"]},
    ]

    return documents, test_queries


def evaluate_retriever(
    retriever, test_queries: List[Dict[str, Any]], top_k: int = 3
) -> Dict[str, float]:
    """Evaluate a retriever on test queries"""
    metrics = {"precision": [], "recall": [], "f1": [], "mrr": []}

    for query_data in test_queries:
        query = query_data["query"]
        relevant_docs = set(query_data["relevant_docs"])

        # Get results
        results = retriever.retrieve(query, top_k=top_k)
        retrieved_docs = {result["document"]["id"] for result in results}

        # Calculate metrics
        if not retrieved_docs:
            metrics["precision"].append(0.0)
            metrics["recall"].append(0.0)
            metrics["f1"].append(0.0)
            metrics["mrr"].append(0.0)
            continue

        # Precision, Recall, F1
        tp = len(relevant_docs & retrieved_docs)
        precision = tp / len(retrieved_docs)
        recall = tp / len(relevant_docs) if relevant_docs else 0.0
        f1 = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        # MRR
        mrr = 0.0
        for i, result in enumerate(results, 1):
            if result["document"]["id"] in relevant_docs:
                mrr = 1.0 / i
                break

        metrics["precision"].append(precision)
        metrics["recall"].append(recall)
        metrics["f1"].append(f1)
        metrics["mrr"].append(mrr)

    # Calculate mean metrics
    return {k: float(np.mean(v)) for k, v in metrics.items()}


def test_hybrid_retriever():
    """Test the hybrid retriever and compare with individual retrievers"""
    print("Loading test data...")
    documents, test_queries = load_test_data()

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
    bm25.add_documents(documents)
    faiss.add_documents(documents)
    hybrid.add_documents(documents)

    # Test different weight combinations
    weight_combinations = [
        (0.9, 0.1),  # Mostly BM25
        (0.7, 0.3),  # More BM25
        (0.5, 0.5),  # Equal weights
        (0.3, 0.7),  # More FAISS
        (0.1, 0.9),  # Mostly FAISS
    ]

    results = {}

    # Test individual retrievers
    print("\nTesting BM25 retriever...")
    results["bm25"] = evaluate_retriever(bm25, test_queries)

    print("\nTesting FAISS retriever...")
    results["faiss"] = evaluate_retriever(faiss, test_queries)

    # Test hybrid with different weights
    for bm25_w, faiss_w in weight_combinations:
        print(f"\nTesting hybrid retriever (BM25: {bm25_w}, FAISS: {faiss_w})...")
        hybrid.bm25_weight = bm25_w
        hybrid.faiss_weight = faiss_w
        results[f"hybrid_{int(bm25_w*100)}_{int(faiss_w*100)}"] = evaluate_retriever(
            hybrid, test_queries
        )

    # Print results
    print("\n" + "=" * 80)
    print("Retrieval Performance Comparison")
    print("=" * 80)
    print(
        f"\n{'Retriever':<20} {'Precision':<10} {'Recall':<10} {'F1':<10} {'MRR':<10}"
    )
    print("-" * 60)

    for name, metrics in results.items():
        print(
            f"{name:<20} {metrics['precision']:.4f}    {metrics['recall']:.4f}    {metrics['f1']:.4f}    {metrics['mrr']:.4f}"
        )

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"hybrid_retriever_results_{timestamp}.json"
    with open(results_file, "w") as f:
        json.dump(
            {
                "test_queries": test_queries,
                "documents": [doc.model_dump() for doc in documents],
                "results": results,
                "timestamp": timestamp,
            },
            f,
            indent=2,
        )

    assert (
        results["hybrid_50_50"]["f1"] > results["bm25"]["f1"]
        or results["hybrid_50_50"]["f1"] > results["faiss"]["f1"]
    ), "Hybrid retriever should outperform at least one of its components"

    print(f"\nResults saved to {results_file}")
