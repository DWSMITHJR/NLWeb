print("Testing Python environment...")

# Test basic imports
try:
    import sys
    import os
    from pathlib import Path
    
    print("✅ Basic imports successful")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Add project root to path
    project_root = str(Path(__file__).parent)
    sys.path.insert(0, project_root)
    print(f"\nAdded to path: {project_root}")
    
    # Test project imports
    print("\nTesting project imports...")
    from models import Document
    print("✅ models.Document imported successfully")
    
    from automl.retrievers.hybrid_retriever import HybridRetriever
    print("✅ automl.retrievers.hybrid_retriever.HybridRetriever imported successfully")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
