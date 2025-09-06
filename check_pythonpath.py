import sys
import os

def check_python_environment():
    print("=== Python Environment ===")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Current Working Directory: {os.getcwd()}")
    print("\n=== Python Path ===")
    for path in sys.path:
        print(f"- {path}")
    
    print("\n=== Environment Variables ===")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print(f"PATH: {os.environ.get('PATH', 'Not set')}")

if __name__ == "__main__":
    check_python_environment()
