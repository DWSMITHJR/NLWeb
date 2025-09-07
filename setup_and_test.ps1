# Setup and Test Script for NLWeb

# Function to check if a command exists
function Command-Exists {
    param($command)
    $exists = $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
    return $exists
}

# Check Python installation
if (-not (Command-Exists "python")) {
    Write-Host "Python is not in your PATH. Please install Python 3.8 or higher and try again." -ForegroundColor Red
    exit 1
}

# Check Python version
$pythonVersion = (python --version 2>&1) -replace '^Python\s+', ''
$version = [System.Version]::Parse($pythonVersion)

if ($version.Major -lt 3 -or ($version.Major -eq 3 -and $version.Minor -lt 8)) {
    Write-Host "Python 3.8 or higher is required. Found Python $pythonVersion" -ForegroundColor Red
    exit 1
}

Write-Host "Using Python $pythonVersion" -ForegroundColor Green

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
$activateScript = ".\.venv\Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Host "Virtual environment activation script not found at $activateScript" -ForegroundColor Red
    exit 1
}

# Source the activation script
. $activateScript

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to upgrade pip" -ForegroundColor Yellow
}

# Install requirements
Write-Host "Installing requirements..." -ForegroundColor Cyan
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install requirements" -ForegroundColor Red
    exit 1
}

# Install in development mode
Write-Host "Installing in development mode..." -ForegroundColor Cyan
pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install in development mode" -ForegroundColor Yellow
}

# Run tests
Write-Host "Running tests..." -ForegroundColor Cyan
pytest -v

# Keep the window open
Write-Host "`nPress any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
