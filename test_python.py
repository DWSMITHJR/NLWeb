import sys
import os

def main():
    print("Python version:", sys.version)
    print("Current working directory:", os.getcwd())
    print("Python path:", sys.path)
    
    try:
        import numpy
        print("✅ numpy is installed")
    except ImportError:
        print("❌ numpy is not installed")
    
    try:
        from models import Document
        print("✅ Document class is importable")
    except ImportError as e:
        print(f"❌ Error importing Document: {e}")

if __name__ == "__main__":
    main()
