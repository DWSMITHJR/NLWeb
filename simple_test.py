import sys
print("Python version:", sys.version)
print("\nPython path:")
for p in sys.path:
    print(f"- {p}")

try:
    import numpy
    print("\nNumPy version:", numpy.__version__)
except ImportError:
    print("\nNumPy not found")

try:
    from backend.models import Document
    print("\nSuccessfully imported Document from backend.models")
except ImportError as e:
    print(f"\nFailed to import Document: {e}")
    import traceback
    traceback.print_exc()
