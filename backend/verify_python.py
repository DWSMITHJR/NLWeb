import sys
import os
import platform

def main():
    print("Python Environment Verification")
    print("=" * 80)
    
    # Basic Python info
    print(f"Python Version: {sys.version}")
    print(f"Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Current Directory: {os.getcwd()}")
    
    # Check PATH
    print("\nPython Path:")
    for path in sys.path:
        print(f"  - {path}")
    
    # Check file system access
    print("\nFile System Access:")
    try:
        with open("test_write.txt", "w") as f:
            f.write("Test write successful")
        os.remove("test_write.txt")
        print("  - File write/delete: SUCCESS")
    except Exception as e:
        print(f"  - File write/delete: FAILED - {str(e)}")
    
    # Check imports
    print("\nTesting Imports:")
    test_imports = [
        "numpy", "pydantic", "fastapi", "sentence_transformers",
        "faiss", "rank_bm25"
    ]
    
    for lib in test_imports:
        try:
            module = __import__(lib)
            version = getattr(module, "__version__", "version not found")
            print(f"  - {lib}: {version}")
        except ImportError:
            print(f"  - {lib}: NOT INSTALLED")
    
    print("\nVerification complete!")

if __name__ == "__main__":
    main()
