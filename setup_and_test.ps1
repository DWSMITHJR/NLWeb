Write-Host "Setting up Python environment..."

# Navigate to project root
$projectRoot = "C:\Users\donal\source\repos\NLWeb"
Set-Location $projectRoot

# Remove existing virtual environment if it exists
if (Test-Path .venv) {
    Write-Host "Removing existing virtual environment..."
    Remove-Item -Recurse -Force .venv
}

# Create new virtual environment
Write-Host "Creating new virtual environment..."
python -m venv .venv

# Activate virtual environment
Write-Host "Activating virtual environment..."
.venv\Scripts\Activate.ps1

# Upgrade pip and setuptools
Write-Host "Upgrading pip and setuptools..."
python -m pip install --upgrade pip setuptools

# Install requirements
Write-Host "Installing requirements..."
pip install -r requirements.txt

# Install in development mode
Write-Host "Installing in development mode..."
pip install -e .

# Run tests
Write-Host "\nRunning tests..."
cd backend
python test_environment.py

# Run pytest
Write-Host "\nRunning pytest..."
python -m pytest -v

Write-Host "\nSetup and testing complete!"
