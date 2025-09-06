import os
import sys
import platform
import subprocess
from pathlib import Path

def print_section(title, char='='):
    print(f"\n{char * 80}")
    print(f"{title.upper()}".center(80))
    print(f"{char * 80}")

def run_command(cmd, cwd=None):
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or os.getcwd(),
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Command failed with error {e.returncode}: {e.stderr}"

def main():
    # Basic system info
    print_section("System Information")
    print(f"Platform: {platform.platform()}")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Current Working Directory: {os.getcwd()}")

    # Environment variables
    print_section("Environment Variables")
    for var in ['PATH', 'PYTHONPATH', 'VIRTUAL_ENV']:
        print(f"{var}: {os.environ.get(var, 'Not set')}")

    # Python path
    print_section("Python Path")
    for i, path in enumerate(sys.path, 1):
        print(f"{i:>3}. {path}")

    # Check package installations
    print_section("Package Versions")
    packages = ['numpy', 'sentence_transformers', 'rank_bm25', 'faiss', 'pydantic']
    for pkg in packages:
        try:
            mod = __import__(pkg)
            print(f"{pkg}: {getattr(mod, '__version__', 'version not found')}")
        except ImportError:
            print(f"{pkg}: Not installed")

    # Try importing project modules
    print_section("Project Module Imports")
    modules = [
        'backend.models',
        'backend.document_processor',
        'backend.automl.retrievers.hybrid_retriever'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ Successfully imported {module}")
        except ImportError as e:
            print(f"✗ Failed to import {module}: {str(e)}")
            import traceback
            traceback.print_exc()

    # Try creating a document
    print_section("Document Creation Test")
    try:
        from backend.models import Document
        doc = Document(id="test", content="Test document")
        print(f"✓ Successfully created Document: {doc}")
    except Exception as e:
        print(f"✗ Failed to create Document: {str(e)}")

if __name__ == "__main__":
    main()
