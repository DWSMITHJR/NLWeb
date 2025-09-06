import sys
import os

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

# Test imports
try:
    import backend.models
    print("Successfully imported backend.models")
    
    import backend.document_processor
    print("Successfully imported backend.document_processor")
    
    import backend.prompt_templates
    print("Successfully imported backend.prompt_templates")
    
    import pytest
    print(f"pytest version: {pytest.__version__}")
    
    # Try to run a simple test
    print("\nRunning a simple test...")
    assert 1 + 1 == 2, "Basic assertion failed"
    print("Simple test passed!")
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
