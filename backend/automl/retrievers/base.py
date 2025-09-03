from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
from ...models import Document

class BaseRetriever(ABC):
    """Base class for all retrievers"""
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the retriever"""
        pass
    
    @abstractmethod
    def retrieve(
        self, 
        query: str, 
        top_k: int = 5, 
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents relevant to the query
        
        Args:
            query: The query string
            top_k: Number of documents to retrieve
            **kwargs: Additional parameters for the retriever
            
        Returns:
            List of dictionaries containing document data and scores
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the retriever"""
        pass
    
    @property
    def config(self) -> Dict[str, Any]:
        """Return the configuration of the retriever"""
        return {}
    
    def _format_results(
        self, 
        documents: List[Document], 
        scores: List[float]
    ) -> List[Dict[str, Any]]:
        """Format retrieval results with scores"""
        return [
            {
                "document": doc.dict(),
                "score": float(score),
                "retriever": self.name,
                "config": self.config
            }
            for doc, score in zip(documents, scores)
        ]
