import sys
import os

def check_environment():
    print("Python Environment Check")
    print("=" * 50)
    
    # Python version
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Check PATH
    print("\nSystem PATH:")
    for path in sys.path:
        print(f"  - {path}")
    
    # Try basic imports
    print("\nTesting imports...")
    try:
        import pydantic
        print(f"  - pydantic: {pydantic.__version__}")
    except ImportError:
        print("  - pydantic: NOT INSTALLED")
    
    try:
        import numpy
        print(f"  - numpy: {numpy.__version__}")
    except ImportError:
        print("  - numpy: NOT INSTALLED")
    
    try:
        import faiss
        print(f"  - faiss: {faiss.__version__}")
    except ImportError:
        print("  - faiss: NOT INSTALLED")
    
    try:
        from rank_bm25 import BM25Okapi
        print("  - rank_bm25: OK")
    except ImportError:
        print("  - rank_bm25: NOT INSTALLED")
    
    print("\nEnvironment check complete.")

if __name__ == "__main__":
    check_env()
