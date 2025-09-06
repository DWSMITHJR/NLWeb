import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import the test module
import unittest
from backend.test_automl_orchestrator import TestAutoMLOrchestrator

# Create a test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# Add the specific test case we want to run
suite.addTest(TestAutoMLOrchestrator('test_evaluate_retrieval'))

# Run the test
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Print the result
print("\nTest Result:", "OK" if result.wasSuccessful() else "FAILED")
