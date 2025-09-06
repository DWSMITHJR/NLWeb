from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
from backend.models import Document


class BaseRetriever(ABC):
    """Abstract base class for all retriever implementations."""

    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """
        Adds a list of documents to the retriever's index.

        Args:
            documents: A list of Document objects to be added.
        """
        pass

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieves the top_k most relevant documents for a given query.

        Args:
            query: The query string to search for.
            top_k: The number of top documents to retrieve.
            **kwargs: Additional retriever-specific parameters.

        Returns:
            A list of dictionaries, where each dictionary represents a
            retrieved document and its score.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the retriever."""
        pass

    @property
    def config(self) -> Dict[str, Any]:
        """Returns the configuration of the retriever as a dictionary."""
        return {}

    def _format_results(
        self, documents: List[Document], scores: List[float]
    ) -> List[Dict[str, Any]]:
        """
        Formats the retrieved documents and their scores into a structured list.

        Args:
            documents: A list of retrieved Document objects.
            scores: A list of corresponding scores for each document.

        Returns:
            A list of dictionaries, each containing the document, score, and
            retriever metadata.
        """
        return [
            {
                "document": doc.model_dump(),
                "score": float(score),
                "retriever": self.name,
                "config": self.config,
            }
            for doc, score in zip(documents, scores)
        ]
