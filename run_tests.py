import sys
import os
import subprocess

def print_banner(text):
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, '='))
    print("=" * 80 + "\n")

def run_command(command, cwd=None):
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=True,
            text=True,
            capture_output=True
        )
        print("Output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}:")
        print("Output:")
        print(e.stdout)
        print("Errors:")
        print(e.stderr)
        return False

def main():
    # Print environment information
    print_banner("PYTHON ENVIRONMENT")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Current Working Directory: {os.getcwd()}")
    print("\nPython Path:")
    for path in sys.path:
        print(f"- {path}")
    
    # Run pytest with detailed output
    print_banner("RUNNING TESTS")
    test_file = os.path.join("backend", "test_core.py")
    command = f"{sys.executable} -m pytest {test_file} -v -s"
    success = run_command(command)
    
    if not success:
        print_banner("TEST FAILED - RUNNING WITH PYTHON -M")
        command = f"{sys.executable} -m pytest {test_file} -v -s"
        run_command(command)
    
    print_banner("TEST EXECUTION COMPLETE")

if __name__ == "__main__":
    main()
