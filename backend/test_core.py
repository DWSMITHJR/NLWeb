"""
Core functionality tests for NLWeb AutoRAG
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from models import Document, DocumentChunk, ChunkingStrategy
        from document_processor import DocumentProcessor, DocumentProcessorConfig
        from prompt_templates import PromptTemplateManager, TemplateType
        from automl.retrievers.base import BaseRetriever
        from automl.retrievers.faiss_retriever import FAISSRetriever
        from automl.retrievers.bm25_retriever import BM25Retriever
        from automl.retrievers.hybrid_retriever import HybridRetriever
        from automl.orchestrator import AutoMLOrchestrator
        
        print("✓ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_document_processing():
    """Test document processing functionality"""
    try:
        from models import Document, ChunkingStrategy
        from document_processor import DocumentProcessor, DocumentProcessorConfig
        
        # Create test document
        doc = Document(
            id="test_doc",
            content="This is a test document. It has multiple sentences.\n\nWith multiple paragraphs too.",
            metadata={"source": "test"}
        )
        
        # Test different chunking strategies
        strategies = [
            (ChunkingStrategy.FIXED, 3, 0, 2),  # Fixed size chunks
            (ChunkingStrategy.SENTENCE, 0, 0, 3),  # Sentence chunks
            (ChunkingStrategy.PARAGRAPH, 0, 0, 2)  # Paragraph chunks
        ]
        
        for strategy, chunk_size, chunk_overlap, expected_chunks in strategies:
            config = DocumentProcessorConfig(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                chunking_strategy=strategy
            )
            processor = DocumentProcessor(config)
            chunks = processor.process_document(doc)
            
            print(f"{strategy.name}: Got {len(chunks)} chunks (expected {expected_chunks})")
            if len(chunks) != expected_chunks:
                print(f"✗ {strategy.name} chunking failed")
                return False
        
        print("✓ Document processing tests passed")
        return True
    except Exception as e:
        print(f"✗ Document processing test failed: {e}")
        return False

def test_retrievers():
    """Test retriever functionality"""
    try:
        from models import Document
        from automl.retrievers.faiss_retriever import FAISSRetriever
        from automl.retrievers.bm25_retriever import BM25Retriever
        from automl.retrievers.hybrid_retriever import HybridRetriever
        
        # Test documents
        documents = [
            Document(
                id=f"doc{i}",
                content=f"Document {i} about {'apples' if i % 2 == 0 else 'oranges'}",
                metadata={"source": "test"}
            )
            for i in range(1, 6)
        ]
        
        # Test each retriever
        retrievers = [
            ("FAISS", FAISSRetriever(model_name='sentence-transformers/all-MiniLM-L6-v2')),
            ("BM25", BM25Retriever()),
            ("Hybrid", HybridRetriever(
                bm25_weight=0.5,
                faiss_weight=0.5,
                faiss_model_name='sentence-transformers/all-MiniLM-L6-v2'
            ))
        ]
        
        for name, retriever in retrievers:
            # Add documents to retriever
            retriever.add_documents(documents)
            
            # Test retrieval
            results = retriever.retrieve("apples", top_k=2)
            print(f"{name} results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['document']['content']} (Score: {result['score']:.4f})")
            
            if len(results) != 2:
                print(f"✗ {name} retriever failed to return expected number of results")
                return False
        
        print("✓ Retriever tests passed")
        return True
    except Exception as e:
        print(f"✗ Retriever test failed: {e}")
        return False

def test_prompt_templates():
    """Test prompt template functionality"""
    try:
        from prompt_templates import PromptTemplateManager, TemplateType
        
        manager = PromptTemplateManager()
        
        # Test each template type
        for template_type in TemplateType:
            template = manager.get_template(template_type)
            formatted = template.format(
                context="Test context",
                question="Test question"
            )
            print(f"{template_type.name} template:")
            print(f"{'-'*20}")
            print(formatted)
            print(f"{'-'*20}\n")
        
        print("✓ Prompt template tests passed")
        return True
    except Exception as e:
        print(f"✗ Prompt template test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("="*50)
    print("NLWeb AutoRAG Core Functionality Tests")
    print("="*50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Document Processing", test_document_processing),
        ("Retrievers", test_retrievers),
        ("Prompt Templates", test_prompt_templates)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*20} {name} {'='*20}")
        result = test_func()
        results.append((name, result))
    
    # Print summary
    print("\n" + "="*50)
    print("Test Summary:")
    print("="*50)
    
    all_passed = True
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        color = "\033[92m" if result else "\033[91m"
        print(f"{color}{name}: {status}\033[0m")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n❌ Some tests failed. Please check the output above for details.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
