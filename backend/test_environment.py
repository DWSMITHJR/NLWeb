"""
Comprehensive environment and import test script for NLWeb backend.
This script will test:
1. Basic Python functionality
2. Core dependencies
3. Project imports
4. HybridRetriever functionality
"""

import sys
import os
import platform
from pathlib import Path
import importlib
import traceback

# Test results storage
test_results = {
    "python_version": "",
    "os_info": "",
    "working_dir": "",
    "python_path": [],
    "core_dependencies": {},
    "project_imports": {},
    "hybrid_retriever_test": {}
}

def print_header(title):
    print("\n" + "="*80)
    print(f" {title} ".center(80, '='))
    print("="*80)

def test_basic_environment():
    """Test basic Python environment and system information."""
    print_header("1. Testing Basic Python Environment")
    
    test_results["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    test_results["os_info"] = f"{platform.system()} {platform.release()} ({platform.version()})"
    test_results["working_dir"] = str(Path.cwd())
    test_results["python_path"] = sys.path
    
    print(f"✅ Python Version: {test_results['python_version']}")
    print(f"✅ OS: {test_results['os_info']}")
    print(f"✅ Working Directory: {test_results['working_dir']}")
    print("\nPython Path:")
    for i, path in enumerate(test_results['python_path'], 1):
        print(f"  {i}. {path}")

def test_core_dependencies():
    """Test installation of core dependencies."""
    print_header("2. Testing Core Dependencies")
    
    dependencies = [
        "numpy",
        "pydantic",
        "sentence_transformers",
        "faiss",
        "rank_bm25",
        "pytest"
    ]
    
    for dep in dependencies:
        try:
            module = importlib.import_module(dep)
            version = getattr(module, "__version__", "version not found")
            test_results["core_dependencies"][dep] = {"status": "✅", "version": version}
            print(f"✅ {dep}: {version}")
        except ImportError:
            test_results["core_dependencies"][dep] = {"status": "❌", "error": "Not installed"}
            print(f"❌ {dep}: Not installed")

def test_project_imports():
    """Test imports of project modules."""
    print_header("3. Testing Project Imports")
    
    # Add project root to path if not already there
    project_root = str(Path(__file__).parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    imports_to_test = [
        ("models", "Document"),
        ("document_processor", "DocumentProcessor"),
        ("automl.retrievers.hybrid_retriever", "HybridRetriever"),
        ("automl.retrievers.bm25_retriever", "BM25Retriever"),
        ("automl.retrievers.faiss_retriever", "FAISSRetriever")
    ]
    
    for module_path, class_name in imports_to_test:
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, class_name):
                test_results["project_imports"][f"{module_path}.{class_name}"] = "✅"
                print(f"✅ {module_path}.{class_name}")
            else:
                test_results["project_imports"][f"{module_path}.{class_name}"] = f"❌ Class {class_name} not found in module"
                print(f"❌ {module_path}.{class_name}: Class not found in module")
        except Exception as e:
            test_results["project_imports"][f"{module_path}.{class_name}"] = f"❌ {str(e)}"
            print(f"❌ {module_path}.{class_name}: {str(e)}")

def test_hybrid_retriever():
    """Test HybridRetriever with sample data."""
    print_header("4. Testing HybridRetriever Functionality")
    
    try:
        from models import Document
        from automl.retrievers.hybrid_retriever import HybridRetriever
        
        # Create test documents
        documents = [
            Document(
                id="doc1",
                content="The quick brown fox jumps over the lazy dog.",
                metadata={"source": "test"}
            ),
            Document(
                id="doc2",
                content="The five boxing wizards jump quickly.",
                metadata={"source": "test"}
            ),
            Document(
                id="doc3",
                content="Pack my box with five dozen liquor jugs.",
                metadata={"source": "test"}
            ),
        ]
        
        # Initialize retriever
        hybrid = HybridRetriever(
            bm25_weight=0.5,
            faiss_weight=0.5,
            faiss_model_name="sentence-transformers/all-MiniLM-L6-v2",
        )
        
        # Add documents
        hybrid.add_documents(documents)
        
        # Test query
        query = "quick fox jumping"
        results = hybrid.retrieve(query, top_k=2)
        
        # Check results
        if len(results) == 2:
            test_results["hybrid_retriever_test"]["status"] = "✅"
            test_results["hybrid_retriever_test"]["results"] = [
                {"id": r["document"]["id"], "score": r["score"]} for r in results
            ]
            print("✅ HybridRetriever test passed")
            print("\nRetrieved documents:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. ID: {result['document']['id']}, Score: {result['score']:.4f}")
                print(f"     Content: {result['document']['content']}")
        else:
            test_results["hybrid_retriever_test"]["status"] = f"❌ Expected 2 results, got {len(results)}"
            print(f"❌ HybridRetriever test failed: Expected 2 results, got {len(results)}")
            
    except Exception as e:
        test_results["hybrid_retriever_test"]["status"] = f"❌ {str(e)}"
        print(f"❌ HybridRetriever test failed: {str(e)}")
        traceback.print_exc()

def save_test_results():
    """Save test results to a file."""
    output_file = "test_environment_results.json"
    import json
    
    with open(output_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n✅ Test results saved to {output_file}")

if __name__ == "__main__":
    try:
        test_basic_environment()
        test_core_dependencies()
        test_project_imports()
        test_hybrid_retriever()
        save_test_results()
        
        print_header("✅ All Tests Completed Successfully ✅")
        
    except Exception as e:
        print("\n❌ An error occurred during testing:")
        traceback.print_exc()
        print("\n⚠️  Please check the error message above and fix the issues.")
        sys.exit(1)
