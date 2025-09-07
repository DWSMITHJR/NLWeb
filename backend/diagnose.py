"""Diagnostic script to check Python environment and module imports."""
import sys
import os
import platform
import importlib
from pathlib import Path

def print_section(title):
    """Print a section header."""
    print(f"\n{'='*80}
{title}\n{'='*80}")

def check_python_environment():
    """Check Python environment details."""
    print_section("Python Environment")
    print(f"Python Version: {platform.python_version()}")
    print(f"Executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Python Path: {sys.path}")

def check_imports():
    """Check if required packages are importable."""
    print_section("Checking Imports")
    
    packages = [
        'numpy',
        'pytest',
        'sentence_transformers',
        'rank_bm25',
        'faiss',
        'pydantic'
    ]
    
    for pkg in packages:
        try:
            mod = importlib.import_module(pkg)
            print(f"✓ {pkg}: {mod.__version__ if hasattr(mod, '__version__') else 'imported successfully'}")
        except ImportError as e:
            print(f"✗ {pkg}: {str(e)}")

def check_project_structure():
    """Check project structure and module paths."""
    print_section("Project Structure")
    
    project_root = Path(__file__).parent
    print(f"Project Root: {project_root}")
    
    # Check important directories
    dirs = [
        project_root / 'automl',
        project_root / 'automl' / 'retrievers',
    ]
    
    for d in dirs:
        exists = "✓" if d.exists() else "✗"
        print(f"{exists} {d.relative_to(project_root)}")
    
    # Check important files
    files = [
        project_root / 'models.py',
        project_root / 'automl' / 'retrievers' / 'base.py',
        project_root / 'automl' / 'retrievers' / 'hybrid_retriever.py',
    ]
    
    for f in files:
        exists = "✓" if f.exists() else "✗"
        print(f"{exists} {f.relative_to(project_root)}")

def check_import_paths():
    """Check if project modules can be imported."""
    print_section("Module Import Check")
    
    try:
        from models import Document
        print("✓ models.Document imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import models.Document: {str(e)}")
    
    try:
        from automl.retrievers.hybrid_retriever import HybridRetriever
        print("✓ automl.retrievers.hybrid_retriever.HybridRetriever imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import HybridRetriever: {str(e)}")
        
        # Try to diagnose the import error
        try:
            import automl
            print(f"  - automl module path: {automl.__file__}")
        except ImportError as e2:
            print(f"  - automl module not found: {str(e2)}")

def main():
    """Run all diagnostic checks."""
    print("\n" + "="*80)
    print("NLWeb Backend Diagnostics")
    print("="*80)
    
    check_python_environment()
    check_imports()
    check_project_structure()
    check_import_paths()
    
    print("\nDiagnostics complete!")

if __name__ == "__main__":
    main()
