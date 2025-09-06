import sys
import subprocess
import os
from pathlib import Path

# Add backend directory to Python path
sys.path.append(str(Path(__file__).parent))


def run_test(test_name, test_file):
    print(f"\n{'='*50}")
    print(f"Running {test_name}...")
    print(f"{'='*50}")

    try:
        # Run the test file
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
        )

        # Print the output
        if result.stdout:
            print(result.stdout)

        # Print any errors
        if result.stderr:
            print("Errors:")
            print(result.stderr)

        # Return True if the test passed
        return result.returncode == 0

    except Exception as e:
        print(f"Error running {test_name}: {str(e)}")
        return False


def main():
    # List of tests to run
    tests = [
        ("Hybrid Retriever Test", "test_hybrid_simple.py"),
        ("Prompt Templates Test", "test_prompt_templates.py"),
        ("Hybrid Retriever Full Test", "test_hybrid_retriever.py"),
        ("Core Functionality Test", "test_core.py"),
        ("AutoML Integration Test", "test_automl_integration.py"),
    ]

    # Run all tests
    all_passed = True
    for test_name, test_file in tests:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        if not os.path.exists(test_path):
            print(f"\nTest file not found: {test_file}")
            all_passed = False
            continue

        success = run_test(test_name, test_file)
        if not success:
            all_passed = False

    # Print final result
    print("\n" + "=" * 50)
    if all_passed:
        print("[PASS] All tests passed successfully!")
    else:
        print("[FAIL] Some tests failed. Please check the output above for details.")
    print("=" * 50)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
