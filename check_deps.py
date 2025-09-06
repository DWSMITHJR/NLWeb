import sys
import importlib

def check_package(package_name):
    try:
        importlib.import_module(package_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed")
        return False

# List of required packages
required_packages = [
    'numpy',
    'sentence_transformers',
    'rank_bm25',
    'faiss',
    'pytest'
]

print("Checking required packages...\n" + "="*50)

missing_packages = [pkg for pkg in required_packages if not check_package(pkg)]

if missing_packages:
    print("\nTo install missing packages, run:")
    print(f"pip install {' '.join(missing_packages)}")
else:
    print("\n✅ All required packages are installed!")
