# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    python -m venv venv
}

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest test_automl_integration.py -v

# Keep the window open to see the results
Read-Host -Prompt "Press Enter to exit"
