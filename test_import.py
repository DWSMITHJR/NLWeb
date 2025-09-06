import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("Testing imports...")

try:
    from backend.automl.orchestrator import AutoMLOrchestrator
    print("Successfully imported AutoMLOrchestrator")
    
    # Test creating an instance
    orchestrator = AutoMLOrchestrator()
    print("Successfully created AutoMLOrchestrator instance")
    
    # Test the _create_retriever method with a simple config
    try:
        config = {"retriever_type": "bm25"}
        retriever = orchestrator._create_retriever(config)
        print(f"Successfully created retriever: {retriever}")
    except Exception as e:
        print(f"Error creating retriever: {e}")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nPython path:")
    for p in sys.path:
        print(f"  {p}")
    
    print("\nCurrent working directory:", os.getcwd())
