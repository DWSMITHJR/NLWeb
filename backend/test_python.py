print("Python is working!")
print(f"Python version: {__import__('sys').version}")
print(f"Current working directory: {__import__('os').getcwd()}")

# Test basic imports
try:
    import numpy

    print(f"NumPy version: {numpy.__version__}")
except ImportError as e:
    print(f"NumPy import error: {e}")

try:
    import faiss

    print(f"FAISS version: {faiss.__version__}")
except ImportError as e:
    print(f"FAISS import error: {e}")
