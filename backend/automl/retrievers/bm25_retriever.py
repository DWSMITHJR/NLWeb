from typing import List, Dict, Any, Optional
import numpy as np
from rank_bm25 import BM25Okapi
from .base import BaseRetriever
from backend.models import Document


class BM25Retriever(BaseRetriever):
    """Implements a BM25 retriever using the rank-bm25 library."""

    @property
    def name(self) -> str:
        """Returns the name of the retriever."""
        return "bm25_retriever"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bm25 = None
        self.documents = []
        self.doc_ids = []
        self.tokenizer = lambda x: x.lower().split()

    def add_documents(self, documents: List[Document]) -> None:
        """
        Adds a list of documents to the BM25 index.

        Args:
            documents: A list of Document objects to be added.
        """
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
        Retrieves the top_k most relevant documents for a given query using BM25.

        Args:
            query: The query string to search for.
            top_k: The number of top documents to retrieve.
            **kwargs: Additional retriever-specific parameters.

        Returns:
            A list of dictionaries, where each dictionary represents a
            retrieved document and its score.
        """
        if not self.bm25 or not self.documents:
            return []

        tokenized_query = self.tokenizer(query)
        scores = self.bm25.get_scores(tokenized_query)

        # Get the indices of the top-k scores
        top_indices = np.argsort(scores)[::-1][:top_k]

        # Filter out zero-score results and format the output
        retrieved_docs = [self.documents[i] for i in top_indices if scores[i] > 0]
        retrieved_scores = [scores[i] for i in top_indices if scores[i] > 0]

        return self._format_results(retrieved_docs, retrieved_scores)

    def clear(self) -> None:
        """Clears all documents from the retriever's index."""
        self.bm25 = None
        self.documents = []
        self.doc_ids = []
