from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from .base import BaseRetriever
from .faiss_retriever import FAISSRetriever
from .bm25_retriever import BM25Retriever
from ...models import Document

class HybridRetriever(BaseRetriever):
    """Hybrid retriever that combines BM25 and FAISS"""
    
    def __init__(
        self, 
        bm25_weight: float = 0.5,
        faiss_weight: float = 0.5,
        faiss_model_name: str = 'sentence-transformers/all-MiniLM-L6-v2',
        normalize_embeddings: bool = True,
        **kwargs
    ):
        """
        Initialize the hybrid retriever
        
        Args:
            bm25_weight: Weight for BM25 scores (0-1)
            faiss_weight: Weight for FAISS scores (0-1)
            faiss_model_name: Name of the sentence transformer model for FAISS
            normalize_embeddings: Whether to normalize embeddings for FAISS
        """
        super().__init__(**kwargs)
        self.bm25_weight = bm25_weight
        self.faiss_weight = faiss_weight
        self.bm25 = BM25Retriever()
        self.faiss = FAISSRetriever(
            model_name=faiss_model_name,
            normalize_embeddings=normalize_embeddings
        )
        self.documents = []
        self.doc_ids = []
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to both retrievers"""
        if not documents:
            return
            
        # Add to both retrievers
        self.bm25.add_documents(documents)
        self.faiss.add_documents(documents)
        
        # Keep track of documents
        self.documents.extend(documents)
        self.doc_ids.extend([doc.id for doc in documents])
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 5, 
        score_threshold: float = 0.0,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents using hybrid scoring
        
        Args:
            query: The query string
            top_k: Number of documents to retrieve
            score_threshold: Minimum score threshold for results
            
        Returns:
            List of documents with hybrid scores
        """
        # Get results from both retrievers
        bm25_results = self.bm25.retrieve(query, top_k=top_k * 2)
        faiss_results = self.faiss.retrieve(query, top_k=top_k * 2)
        
        # Create a mapping of document ID to scores
        scores = {}
        
        # Process BM25 results
        for result in bm25_results:
            doc_id = result['document']['id']
            if doc_id not in scores:
                scores[doc_id] = {'bm25': 0.0, 'faiss': 0.0, 'document': result['document']}
            scores[doc_id]['bm25'] = result['score']
        
        # Process FAISS results
        for result in faiss_results:
            doc_id = result['document']['id']
            if doc_id not in scores:
                scores[doc_id] = {'bm25': 0.0, 'faiss': 0.0, 'document': result['document']}
            scores[doc_id]['faiss'] = result['score']
        
        # Normalize scores
        bm25_scores = [s['bm25'] for s in scores.values() if s['bm25'] > 0]
        faiss_scores = [s['faiss'] for s in scores.values() if s['faiss'] > 0]
        
        bm25_max = max(bm25_scores) if bm25_scores else 1.0
        faiss_max = max(faiss_scores) if faiss_scores else 1.0
        
        if bm25_max == 0:
            bm25_max = 1.0
        if faiss_max == 0:
            faiss_max = 1.0
        
        # Calculate hybrid scores
        results = []
        for doc_id, score_data in scores.items():
            # Normalize scores
            norm_bm25 = score_data['bm25'] / bm25_max
            norm_faiss = score_data['faiss'] / faiss_max
            
            # Calculate hybrid score
            hybrid_score = (
                self.bm25_weight * norm_bm25 + 
                self.faiss_weight * norm_faiss
            )
            
            if hybrid_score >= score_threshold:
                results.append({
                    'document': score_data['document'],
                    'score': hybrid_score,
                    'retriever': 'hybrid',
                    'metadata': {
                        'bm25_score': score_data['bm25'],
                        'faiss_score': score_data['faiss']
                    }
                })
        
        # Sort by hybrid score (descending)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]
    
    def clear(self) -> None:
        """Clear all documents from the retriever"""
        self.bm25.clear()
        self.faiss.clear()
        self.documents = []
        self.doc_ids = []
