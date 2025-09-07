import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from backend.models import ChunkingStrategy
    print("Successfully imported ChunkingStrategy")
    print(f"Available strategies: {list(ChunkingStrategy)}")
    
    from backend.automl.orchestrator import AutoMLOrchestrator
    print("Successfully imported AutoMLOrchestrator")
    
    from backend.document_processor import DocumentProcessor
    print("Successfully imported DocumentProcessor")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
