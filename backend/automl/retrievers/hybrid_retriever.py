from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from .base import BaseRetriever
from .faiss_retriever import FAISSRetriever
from .bm25_retriever import BM25Retriever
from backend.models import Document


class HybridRetriever(BaseRetriever):
    """Implements a hybrid retriever that combines scores from BM25 and FAISS."""

    @property
    def name(self) -> str:
        """Returns the name of the retriever."""
        return "hybrid_retriever"
        
    @property
    def config(self) -> Dict[str, Any]:
        """Returns the configuration of the retriever as a dictionary."""
        # Get faiss config safely
        faiss_config = {}
        if hasattr(self.faiss, 'model_name'):
            faiss_config['faiss_model_name'] = self.faiss.model_name
        if hasattr(self.faiss, 'normalize_embeddings'):
            faiss_config['normalize_embeddings'] = self.faiss.normalize_embeddings
            
        return {
            "bm25_weight": self.bm25_weight,
            "faiss_weight": self.faiss_weight,
            **faiss_config
        }

    def __init__(
        self,
        bm25_weight: float = 0.5,
        faiss_weight: float = 0.5,
        faiss_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        normalize_embeddings: bool = True,
        **kwargs
    ):
        """
        Initializes the HybridRetriever.

        Args:
            bm25_weight: The weight to assign to the BM25 score (0-1).
            faiss_weight: The weight to assign to the FAISS score (0-1).
            faiss_model_name: The name of the sentence transformer model for FAISS.
            normalize_embeddings: Whether to normalize embeddings for FAISS.
            **kwargs: Additional arguments for the base class.
        """
        super().__init__(**kwargs)
        self.bm25_weight = bm25_weight
        self.faiss_weight = faiss_weight
        self.bm25 = BM25Retriever()
        self.faiss = FAISSRetriever(
            model_name=faiss_model_name, normalize_embeddings=normalize_embeddings
        )
        self.documents = []
        self.doc_ids = []

    def add_documents(self, documents: List[Document]) -> None:
        """
        Adds a list of documents to both the BM25 and FAISS retrievers.

        Args:
            documents: A list of Document objects to be added.
        """
        if not documents:
            return

        # Add to both retrievers
        self.bm25.add_documents(documents)
        self.faiss.add_documents(documents)

        # Keep track of documents
        self.documents.extend(documents)
        self.doc_ids.extend([doc.id for doc in documents])

    def retrieve(
        self, query: str, top_k: int = 5, score_threshold: float = 0.0, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieves documents by combining scores from BM25 and FAISS retrievers.

        Args:
            query: The query string to search for.
            top_k: The number of top documents to retrieve.
            score_threshold: The minimum hybrid score for a document to be included.
            **kwargs: Additional retriever-specific parameters.

        Returns:
            A list of dictionaries representing the retrieved documents and their scores.
        """
        bm25_results = self.bm25.retrieve(query, top_k=top_k * 2, **kwargs)
        faiss_results = self.faiss.retrieve(query, top_k=top_k * 2, **kwargs)

        combined_scores = self._combine_results(bm25_results, faiss_results)
        hybrid_results = self._calculate_hybrid_scores(combined_scores, score_threshold)

        hybrid_results.sort(key=lambda x: x["score"], reverse=True)

        return hybrid_results[:top_k]

    def _combine_results(
        self, bm25_results: List[Dict], faiss_results: List[Dict]
    ) -> Dict[str, Dict]:
        """Combines results from BM25 and FAISS into a single dictionary."""
        scores = {}

        for result in bm25_results:
            doc = result["document"]
            doc_id = doc.id if hasattr(doc, 'id') else doc.get('id')
            if doc_id not in scores:
                scores[doc_id] = {
                    "bm25": 0.0,
                    "faiss": 0.0,
                    "document": doc,
                }
            scores[doc_id]["bm25"] = result["score"]

        for result in faiss_results:
            doc = result["document"]
            doc_id = doc.id if hasattr(doc, 'id') else doc.get('id')
            if doc_id not in scores:
                scores[doc_id] = {
                    "bm25": 0.0,
                    "faiss": 0.0,
                    "document": doc,
                }
            scores[doc_id]["faiss"] = result["score"]

        return scores

    def _calculate_hybrid_scores(
        self, combined_scores: Dict, score_threshold: float
    ) -> List[Dict]:
        """Calculates the hybrid scores from the combined BM25 and FAISS scores."""
        bm25_scores = [s["bm25"] for s in combined_scores.values() if s["bm25"] > 0]
        faiss_scores = [s["faiss"] for s in combined_scores.values() if s["faiss"] > 0]

        bm25_max = max(bm25_scores) if bm25_scores else 1.0
        faiss_max = max(faiss_scores) if faiss_scores else 1.0

        results = []
        for doc_id, score_data in combined_scores.items():
            norm_bm25 = score_data["bm25"] / bm25_max if bm25_max > 0 else 0
            norm_faiss = score_data["faiss"] / faiss_max if faiss_max > 0 else 0

            hybrid_score = self.bm25_weight * norm_bm25 + self.faiss_weight * norm_faiss

            if hybrid_score >= score_threshold:
                doc = score_data["document"]
                results.append(
                    {
                        "document": doc.dict() if hasattr(doc, 'dict') else doc,
                        "score": hybrid_score,
                        "bm25_score": score_data["bm25"],
                        "faiss_score": score_data["faiss"],
                    }
                )

        return results

    def clear(self) -> None:
        """Clears all documents from both the BM25 and FAISS retrievers."""
        self.bm25.clear()
        self.faiss.clear()
        self.documents = []
        self.doc_ids = []
