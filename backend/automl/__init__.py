"""AutoML package for NLWeb."""

# Import key classes to make them available at the package level
from .orchestrator import AutoMLOrchestrator
from .retrievers.hybrid_retriever import HybridRetriever
from .retrievers.faiss_retriever import FAISSRetriever
from .retrievers.bm25_retriever import BM25Retriever

__all__ = ["AutoMLOrchestrator", "HybridRetriever", "FAISSRetriever", "BM25Retriever"]
