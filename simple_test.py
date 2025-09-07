"""
Simple test file to verify the Python environment and basic imports.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_environment():
    """Test if the environment is set up correctly."""
    try:
        import pytest
        import numpy as np
        from backend.models import Document
        print("✓ All required packages are installed")
        print(f"Python version: {sys.version}")
        print(f"Project root: {project_root}")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        return False

if __name__ == "__main__":
    print("Running environment check...")
    success = test_environment()
    if success:
        print("\nEnvironment is set up correctly!")
        print("\nNext steps:")
        print("1. Activate your virtual environment:")
        print("   .\\venv\\Scripts\\activate")
        print("2. Install requirements:")
        print("   pip install -r requirements.txt")
        print("3. Run the tests:")
        print("   python -m pytest test_automl_integration.py -v")
    else:
        print("\nThere were issues with the environment setup.")
