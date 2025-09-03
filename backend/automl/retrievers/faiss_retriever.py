import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from .base import BaseRetriever
from ...models import Document

class FAISSRetriever(BaseRetriever):
    """FAISS-based retriever using dense vector similarity"""
    
    def __init__(
        self, 
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        normalize_embeddings: bool = True,
        **kwargs
    ):
        """
        Initialize FAISS retriever
        
        Args:
            model_name: Name of the sentence transformer model
            normalize_embeddings: Whether to normalize embeddings
            **kwargs: Additional arguments for the model
        """
        self.model_name = model_name
        self.normalize_embeddings = normalize_embeddings
        self.model = SentenceTransformer(model_name, **kwargs)
        self.documents = []
        self.index = None
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
    @property
    def name(self) -> str:
        return f"faiss_{self.model_name.split('/')[-1]}"
    
    @property
    def config(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "normalize_embeddings": self.normalize_embeddings,
            "embedding_dim": self.embedding_dim
        }
    
    def _normalize(self, embeddings: np.ndarray) -> np.ndarray:
        """Normalize embeddings if needed"""
        if not self.normalize_embeddings:
            return embeddings
        return embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-12)
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the FAISS index"""
        if not documents:
            return
            
        self.documents.extend(documents)
        
        # Encode documents
        texts = [doc.content for doc in documents]
        embeddings = self.model.encode(
            texts, 
            convert_to_numpy=True, 
            show_progress_bar=False
        )
        
        # Convert to float32 for FAISS
        embeddings = embeddings.astype('float32')
        
        # Normalize if needed
        if self.normalize_embeddings:
            embeddings = self._normalize(embeddings)
        
        # Initialize index if needed
        if self.index is None:
            self.index = faiss.IndexFlatIP(embeddings.shape[1])
            
            # Add the first batch of embeddings
            if len(embeddings) > 0:
                self.index.add(embeddings)
        else:
            # Add new embeddings to existing index
            self.index.add(embeddings)
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 5, 
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents using FAISS similarity search
        
        Args:
            query: The query string
            top_k: Number of documents to retrieve
            **kwargs: Additional parameters for the retriever
            
        Returns:
            List of dictionaries containing document data and scores
        """
        if not self.documents or self.index is None:
            return []
            
        # Encode query
        query_embedding = self.model.encode(
            [query], 
            convert_to_numpy=True, 
            show_progress_bar=False
        ).astype('float32')
        
        # Normalize if needed
        if self.normalize_embeddings:
            query_embedding = self._normalize(query_embedding)
        
        # Search in FAISS index
        top_k = min(top_k, len(self.documents))
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Get documents and scores
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < 0 or idx >= len(self.documents):
                continue
                
            results.append({
                "document": self.documents[idx].dict(),
                "score": float(score),
                "retriever": self.name,
                "config": self.config
            })
        
        return results
