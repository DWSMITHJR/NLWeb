"""
Core functionality tests for NLWeb AutoRAG
"""

import sys
import os
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported"""
    from backend.models import Document, DocumentChunk, ChunkingStrategy
    from backend.document_processor import DocumentProcessor, DocumentProcessorConfig
    from backend.prompt_templates import PromptTemplateManager, TemplateType
    from backend.automl.retrievers.base import BaseRetriever
    from backend.automl.retrievers.faiss_retriever import FAISSRetriever
    from backend.automl.retrievers.bm25_retriever import BM25Retriever
    from backend.automl.retrievers.hybrid_retriever import HybridRetriever
    from backend.automl.orchestrator import AutoMLOrchestrator

    # If we get here, all imports succeeded
    print("✓ All core modules imported successfully")
    assert True, "All imports should succeed"


def test_document_processing():
    """Test document processing functionality"""
    from backend.models import Document, ChunkingStrategy
    from backend.document_processor import DocumentProcessor, DocumentProcessorConfig

    # Create test document
    doc = Document(
        id="test_doc",
        content="This is a test document. It has multiple sentences.\n\nWith multiple paragraphs too.",
        metadata={"source": "test"},
    )

    # Test different chunking strategies with more realistic expectations
    strategies = [
        (ChunkingStrategy.FIXED, 20, 0, 2),  # Fixed size chunks (2 chunks of 20 chars)
        (ChunkingStrategy.SENTENCE, 100, 0, 3),  # Sentence chunks (3 sentences total)
        (ChunkingStrategy.PARAGRAPH, 100, 0, 2),  # Paragraph chunks (2 paragraphs)
    ]
    
    for strategy, chunk_size, chunk_overlap, expected_chunks in strategies:
        # Create config with proper enum values
        config = DocumentProcessorConfig(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunking_strategy=strategy.value,
        )
        processor = DocumentProcessor(config)
        chunks = processor.process_document(doc)

        print(f"\n{strategy.name} chunking:")
        print(f"Expected chunks: {expected_chunks}, Got: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i+1}: {chunk.content[:50]}..." if len(chunk.content) > 50 else f"  Chunk {i+1}: {chunk.content}")
        
        # For fixed size chunks, we expect at least the minimum number of chunks
        if strategy == ChunkingStrategy.FIXED:
            assert len(chunks) >= expected_chunks, \
                f"{strategy.name} chunking failed: expected at least {expected_chunks} chunks, got {len(chunks)}"
        else:
            assert len(chunks) == expected_chunks, \
                f"{strategy.name} chunking failed: expected {expected_chunks} chunks, got {len(chunks)}"

    print("✓ Document processing tests passed")


def test_retrievers():
    """Test retriever functionality"""
    from backend.models import Document
    from backend.automl.retrievers.faiss_retriever import FAISSRetriever
    from backend.automl.retrievers.bm25_retriever import BM25Retriever
    from backend.automl.retrievers.hybrid_retriever import HybridRetriever

    # Test documents
    documents = [
        Document(id=f"doc{i}", content=content, metadata={"source": "test"})
        for i, content in enumerate(
            [
                "The quick brown fox jumps over the lazy dog.",
                "The five boxing wizards jump quickly.",
                "Pack my box with five dozen liquor jugs.",
            ]
        )
    ]

    # Test FAISS retriever
    faiss_retriever = FAISSRetriever(model_name='sentence-transformers/all-MiniLM-L6-v2')
    faiss_retriever.add_documents(documents)
    faiss_results = faiss_retriever.retrieve("quick jumping animals", top_k=2)
    assert len(faiss_results) == 2, "FAISS retriever should return top_k results"

    # Test BM25 retriever
    bm25_retriever = BM25Retriever()
    bm25_retriever.add_documents(documents)
    bm25_results = bm25_retriever.retrieve("quick jumping animals", top_k=2)
    assert len(bm25_results) == 2, "BM25 retriever should return top_k results"

    # Test hybrid retriever
    hybrid_retriever = HybridRetriever(
        bm25_weight=0.5,
        faiss_weight=0.5,
        faiss_model_name='sentence-transformers/all-MiniLM-L6-v2'
    )
    hybrid_retriever.add_documents(documents)
    hybrid_results = hybrid_retriever.retrieve("quick jumping animals", top_k=2)
    assert len(hybrid_results) == 2, "Hybrid retriever should return top_k results"

    print("✓ Retriever tests passed")


def test_prompt_templates():
    """Test prompt template functionality"""
    from backend.prompt_templates import PromptTemplateManager, TemplateType

    manager = PromptTemplateManager()

    # Test each template type
    for template_type in TemplateType:
        template = manager.get_template(template_type)
        assert template is not None, f"Template {template_type} should not be None"
        assert hasattr(template, 'template'), f"Template {template_type} should have a 'template' attribute"
        assert (
            "{context}" in template.template
        ), f"Template {template_type} should contain {{context}}"
        assert (
            "{question}" in template.template
        ), f"Template {template_type} should contain {{question}}"

    print("✓ Prompt template tests passed")
