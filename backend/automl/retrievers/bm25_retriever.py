from typing import List, Dict, Any, Optional
import numpy as np
from rank_bm25 import BM25Okapi
from .base import BaseRetriever
from ...models import Document

class BM25Retriever(BaseRetriever):
    """BM25-based retriever using rank-bm25"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bm25 = None
        self.documents = []
        self.doc_ids = []
        self.tokenizer = lambda x: x.lower().split()
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the retriever"""
        if not documents:
            return
            
        # Tokenize documents
        tokenized_docs = []
        for doc in documents:
            tokens = self.tokenizer(doc.content)
            tokenized_docs.append(tokens)
            self.documents.append(doc)
            self.doc_ids.append(doc.id)
        
        # Initialize or update BM25 index
        if self.bm25 is None:
            self.bm25 = BM25Okapi(tokenized_docs)
        else:
            self.bm25.add_documents(tokenized_docs)
    
    def retrieve(self, query: str, top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve documents using BM25
        
        Args:
            query: The query string
            top_k: Number of documents to retrieve
            
        Returns:
            List of documents with scores
        """
        if not self.bm25 or not self.documents:
            return []
            
        # Tokenize query
        tokenized_query = self.tokenizer(query)
        
        # Get scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k documents
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include documents with non-zero scores
                doc = self.documents[idx]
                results.append({
                    'document': {
                        'id': doc.id,
                        'content': doc.content,
                        'metadata': doc.metadata
                    },
                    'score': float(scores[idx]),
                    'retriever': 'bm25',
                    'metadata': {}
                })
        
        return results
    
    def clear(self) -> None:
        """Clear all documents from the retriever"""
        self.bm25 = None
        self.documents = []
        self.doc_ids = []
