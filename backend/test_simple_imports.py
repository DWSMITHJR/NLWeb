import sys

print("Testing imports...")
print("Python path:", sys.path)

try:
    print("\nTrying to import models...")
    import models

    print("✅ Successfully imported models")

    print("\nTrying to import automl...")
    import automl

    print("✅ Successfully imported automl")

    print("\nTrying to import prompt_templates...")
    import prompt_templates

    print("✅ Successfully imported prompt_templates")

    print("\n✅ All imports successful!")
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    import traceback

    traceback.print_exc()
