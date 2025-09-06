import re
from typing import List, Dict, Any, Optional
from .models import (
    Document,
    DocumentChunk,
    ChunkingStrategy,
    DocumentProcessorConfig,
)


class DocumentProcessor:
    """Processes documents into chunks based on different strategies."""

    def __init__(self, config: Optional[DocumentProcessorConfig] = None):
        """Initializes the DocumentProcessor with an optional configuration."""
        self.config = config or DocumentProcessorConfig()

    def process_document(self, document: Document) -> List[DocumentChunk]:
        """
        Processes a single document into chunks based on the configured strategy.

        Args:
            document: The document to process.

        Returns:
            A list of document chunks.
        """
        strategy_map = {
            ChunkingStrategy.FIXED: self._chunk_by_fixed_size,
            ChunkingStrategy.SENTENCE: self._chunk_by_sentence,
            ChunkingStrategy.PARAGRAPH: self._chunk_by_paragraph,
        }

        chunking_func = strategy_map.get(self.config.chunking_strategy)

        if not chunking_func:
            raise ValueError(
                f"Unsupported chunking strategy: {self.config.chunking_strategy}"
            )

        return chunking_func(document)

    def _create_chunk(
        self, document: Document, content: str, chunk_index: int
    ) -> DocumentChunk:
        """Creates a DocumentChunk object with consistent metadata."""
        return DocumentChunk(
            id=f"{document.id}_chunk_{chunk_index}",
            document_id=document.id,
            content=content,
            metadata=document.metadata.copy(),
            chunk_index=chunk_index,
            chunk_strategy=self.config.chunking_strategy,
        )

    def _chunk_by_fixed_size(self, document: Document) -> List[DocumentChunk]:
        """Splits a document into fixed-size chunks with overlap."""
        text = document.content
        chunks = []
        start = 0
        chunk_idx = 0

        while start < len(text):
            end = start + self.config.chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(self._create_chunk(document, chunk_text, chunk_idx))
                chunk_idx += 1

            start += self.config.chunk_size - self.config.chunk_overlap
            if start >= len(text):
                break

        return chunks

    def _chunk_by_sentence(self, document: Document) -> List[DocumentChunk]:
        """Splits a document into chunks based on sentence boundaries."""
        # A more robust sentence splitter (e.g., from NLTK or spaCy) is recommended for production.
        sentences = re.split(r"(?<=[.!?])\s+", document.content)

        chunks = []
        current_chunk_sentences = []
        current_length = 0
        chunk_idx = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_length = len(sentence.split())
            if (
                current_length + sentence_length
            ) > self.config.chunk_size and current_chunk_sentences:
                chunks.append(
                    self._create_chunk(
                        document, " ".join(current_chunk_sentences), chunk_idx
                    )
                )
                chunk_idx += 1
                current_chunk_sentences = [sentence]
                current_length = sentence_length
            else:
                current_chunk_sentences.append(sentence)
                current_length += sentence_length

        if current_chunk_sentences:
            chunks.append(
                self._create_chunk(
                    document, " ".join(current_chunk_sentences), chunk_idx
                )
            )

        return chunks

    def _chunk_by_paragraph(self, document: Document) -> List[DocumentChunk]:
        """Splits a document into chunks based on paragraphs."""
        paragraphs = [p.strip() for p in document.content.split("\n\n") if p.strip()]
        chunks = []
        chunk_idx = 0

        for para in paragraphs:
            if len(para.split()) > self.config.chunk_size:
                # If a paragraph is too long, fall back to fixed-size chunking for that paragraph.
                words = para.split()
                for i in range(0, len(words), self.config.chunk_size):
                    chunk_text = " ".join(words[i : i + self.config.chunk_size])
                    chunks.append(self._create_chunk(document, chunk_text, chunk_idx))
                    chunk_idx += 1
            else:
                chunks.append(self._create_chunk(document, para, chunk_idx))
                chunk_idx += 1

        return chunks
