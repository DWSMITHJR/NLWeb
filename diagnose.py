"""
Diagnostic script to identify Python environment issues.
"""
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def print_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title.upper()} ".center(80, '='))
    print("=" * 80)

def run_command(cmd, cwd=None):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            check=True,
            text=True,
            capture_output=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Command failed with error {e.returncode}: {e.stderr}"

def check_python():
    """Check Python installation and version."""
    print_header("Python Installation")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    
    # Check Python in PATH
    python_path = shutil.which('python')
    print(f"Python in PATH: {python_path or 'Not found'}")
    
    # Check pip
    try:
        pip_version = run_command("pip --version")
        print(f"Pip: {pip_version}")
    except Exception as e:
        print(f"Error checking pip: {e}")

def check_environment():
    """Check environment variables and paths."""
    print_header("Environment Variables")
    
    # Important environment variables
    for var in ['PATH', 'PYTHONPATH', 'VIRTUAL_ENV', 'CONDA_PREFIX']:
        value = os.environ.get(var, 'Not set')
        print(f"{var}: {value}")
    
    # Python path
    print_header("Python Module Search Path")
    for i, path in enumerate(sys.path, 1):
        print(f"{i:>3}. {path}")

def check_project_structure():
    """Verify project directory structure."""
    print_header("Project Structure")
    
    # Expected directories and files
    expected = [
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
        'backend/automl/orchestrator.py',
        'setup.py',
        'requirements.txt'
    ]
    
    missing = []
    for path in expected:
        if not os.path.exists(path):
            missing.append(path)
    
    if missing:
        print("Missing files/directories:")
        for path in missing:
            print(f"- {path}")
    else:
        print("All expected files and directories are present.")

def check_package_installed():
    """Check if required packages are installed."""
    print_header("Installed Packages")
    
    packages = [
        'numpy',
        'sentence_transformers',
        'rank_bm25',
        'faiss',
        'pydantic',
        'pytest',
        'scikit_learn'
    ]
    
    for pkg in packages:
        try:
            __import__(pkg)
            version = sys.modules[pkg].__version__
            print(f"✅ {pkg} ({version})")
        except ImportError:
            print(f"❌ {pkg} (Not installed)")

def main():
    """Run all diagnostic checks."""
    print("\n" + "=" * 80)
    print(" PYTHON ENVIRONMENT DIAGNOSTICS ".center(80, '='))
    print("=" * 80 + "\n")
    
    check_python()
    check_environment()
    check_project_structure()
    check_package_installed()
    
    print("\n" + "=" * 80)
    print(" DIAGNOSTICS COMPLETE ".center(80, '='))
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
