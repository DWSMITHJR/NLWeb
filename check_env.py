import sys
import os
import subprocess

def check_python():
    print("=== Python Environment Check ===")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Python Path: {sys.path}")

def check_package_installed(package_name):
    try:
        __import__(package_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed")
        return False

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
        check_package_installed(pkg)

def check_directory_structure():
    print("\n=== Project Structure ===")
    required_dirs = [
        'backend',
        'backend/automl',
        'backend/automl/retrievers'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Missing directory: {dir_path}")

def main():
    check_python()
    check_imports()
    check_directory_structure()

if __name__ == "__main__":
    main()
