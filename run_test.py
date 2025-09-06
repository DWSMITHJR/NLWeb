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

# Create a test case
class TestEvaluateRetrieval(unittest.TestCase):
    def test_evaluate_retrieval(self):
        test_case = TestAutoMLOrchestrator('test_evaluate_retrieval')
        test_case.setUp()
        test_case.test_evaluate_retrieval()
        test_case.tearDown()

# Run the test
if __name__ == '__main__':
    unittest.main()
