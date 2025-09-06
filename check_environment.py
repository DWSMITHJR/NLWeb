import sys
import os
import subprocess

def check_python():
    print("=== Python Environment ===")
    print(f"Executable: {sys.executable}")
    print(f"Version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Python Path: {sys.path}")

def check_imports():
    print("\n=== Checking Imports ===")
    packages = [
        'numpy',
        'sentence_transformers',
        'rank_bm25',
        'faiss',
        'pydantic',
        'pytest',
        'sklearn'
    ]
    
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"✅ {pkg} is installed")
        except ImportError:
            print(f"❌ {pkg} is NOT installed")

def check_files():
    print("\n=== Checking Required Files ===")
    required_files = [
        'backend/__init__.py',
        'backend/models.py',
        'backend/document_processor.py',
        'backend/prompt_templates.py',
        'backend/automl/__init__.py',
        'backend/automl/retrievers/__init__.py',
        'backend/automl/retrievers/base.py',
        'backend/automl/retrievers/faiss_retriever.py',
        'backend/automl/retrievers/bm25_retriever.py',
        'backend/automl/retrievers/hybrid_retriever.py',
        'backend/automl/orchestrator.py'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} is missing")

if __name__ == "__main__":
    check_python()
    check_imports()
    check_files()
