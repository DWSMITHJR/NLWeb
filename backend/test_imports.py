import sys
import os
from pathlib import Path

print("Testing imports...")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
print(f"\nAdding to path: {project_root}")
sys.path.insert(0, project_root)

try:
    print("\nAttempting to import models...")
    from models import Document

    print("✅ Successfully imported models.Document")

    print("\nAttempting to import automl...")
    from automl import AutoMLOrchestrator

    print("✅ Successfully imported automl.AutoMLOrchestrator")

    print("\nAttempting to import prompt_templates...")
    from prompt_templates import TemplateType

    print("✅ Successfully imported prompt_templates.TemplateType")

    print("\n✅ All imports successful!")

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
