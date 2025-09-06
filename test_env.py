"""
This script tests basic Python functionality and environment setup.
"""
import sys
import os
import platform

def print_section(title):
    """Print a section header for better readability."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, '='))
    print("=" * 80)

print_section("PYTHON ENVIRONMENT INFORMATION")

# Basic Python information
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
print(f"Platform: {platform.platform()}")
print(f"Current Working Directory: {os.getcwd()}")

# Environment variables
print_section("ENVIRONMENT VARIABLES")
for key in ['PATH', 'PYTHONPATH', 'VIRTUAL_ENV']:
    print(f"{key}: {os.environ.get(key, 'Not set')}")

# Python path
print_section("PYTHON PATH")
for i, path in enumerate(sys.path, 1):
    print(f"{i:>3}. {path}")

# Test file system access
print_section("FILE SYSTEM ACCESS")
print("Current directory contents:")
try:
    for item in os.listdir('.'):
        print(f"- {item}")
except Exception as e:
    print(f"Error listing directory: {e}")

# Test file writing
print("\nTesting file writing...")
test_file = "test_write.txt"
try:
    with open(test_file, "w") as f:
        f.write("This is a test file.")
    print(f"Successfully wrote to {test_file}")
    os.remove(test_file)
    print(f"Successfully deleted {test_file}")
except Exception as e:
    print(f"Error testing file I/O: {e}")

print_section("TEST COMPLETE")
