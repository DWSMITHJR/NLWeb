import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from .base import BaseRetriever
from backend.models import Document


class FAISSRetriever(BaseRetriever):
    """Implements a FAISS-based retriever for dense vector similarity search."""

    @property
    def name(self) -> str:
        """Returns the name of the retriever."""
        return "faiss_retriever"

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        normalize_embeddings: bool = True,
        **kwargs
    ):
        """
        Initializes the FAISSRetriever.

        Args:
            model_name: The name of the sentence transformer model to use.
            normalize_embeddings: Whether to normalize the embeddings to unit length.
            **kwargs: Additional arguments for the SentenceTransformer model.
        """
        super().__init__(**kwargs)
        self.model_name = model_name
        self.normalize_embeddings = normalize_embeddings
        self.model = SentenceTransformer(model_name, **kwargs)
        self.documents = []
        self.index = None
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    @property
    def config(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "normalize_embeddings": self.normalize_embeddings,
            "embedding_dim": self.embedding_dim,
        }

    def _normalize(self, embeddings: np.ndarray) -> np.ndarray:
        """Normalize embeddings if needed"""
        if not self.normalize_embeddings:
            return embeddings
        return embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-12)

    def add_documents(self, documents: List[Document]) -> None:
        """
        Adds a list of documents to the FAISS index.

        Args:
            documents: A list of Document objects to be added.
        """
        if not documents:
            return

        self.documents.extend(documents)

        # Encode documents
        texts = [doc.content for doc in documents]
        embeddings = self.model.encode(
            texts, convert_to_numpy=True, show_progress_bar=False
        )

        # Convert to float32 for FAISS
        embeddings = embeddings.astype("float32")

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

    def retrieve(self, query: str, top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieves the top_k most relevant documents for a given query using FAISS.

        Args:
            query: The query string to search for.
            top_k: The number of top documents to retrieve.
            **kwargs: Additional retriever-specific parameters.

        Returns:
            A list of dictionaries, where each dictionary represents a
            retrieved document and its score.
        """
        if not self.documents or self.index is None:
            return []

        query_embedding = self.model.encode([query], convert_to_numpy=True).astype(
            "float32"
        )

        if self.normalize_embeddings:
            query_embedding = self._normalize(query_embedding)

        top_k = min(top_k, len(self.documents))
        scores, indices = self.index.search(query_embedding, top_k)

        retrieved_docs = [self.documents[i] for i in indices[0] if i != -1]
        retrieved_scores = [scores[0][j] for j, i in enumerate(indices[0]) if i != -1]

        return self._format_results(retrieved_docs, retrieved_scores)
