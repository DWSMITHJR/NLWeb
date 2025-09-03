""
Quick test script for NLWeb AutoRAG core functionality
"""
import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.append(str(Path(__file__).parent))

def main():
    print("Testing core imports...")
    
    # Test basic imports
    try:
        from models import Document, ChunkingStrategy
        from document_processor import DocumentProcessor, DocumentProcessorConfig
        from prompt_templates import PromptTemplateManager, TemplateType
        from automl.retrievers.faiss_retriever import FAISSRetriever
        from automl.retrievers.bm25_retriever import BM25Retriever
        from automl.retrievers.hybrid_retriever import HybridRetriever
        
        print("✓ All core modules imported successfully")
        
        # Test document creation
        doc = Document(
            id="test_doc",
            content="This is a test document.",
            metadata={"source": "test"}
        )
        print(f"✓ Document created: {doc.id}")
        
        # Test prompt template
        manager = PromptTemplateManager()
        template = manager.get_template(TemplateType.SIMPLE)
        prompt = template.format(context="Test context", question="Test question")
        print("✓ Prompt template test successful")
        
        # Test retrievers
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
            retriever.add_documents([doc])
            results = retriever.retrieve("test", top_k=1)
            print(f"✓ {name} retriever test successful")
        
        print("\n✅ All tests passed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
