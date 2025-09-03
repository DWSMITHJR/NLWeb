# Setup script for Windows NLWeb AutoRAG

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "This script requires administrator privileges. Please run as administrator." -ForegroundColor Red
    exit 1
}

# Check Python version
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(\d+)") {
    $minorVersion = [int]$matches[1]
    if ($minorVersion -lt 8) {
        Write-Host "Python 3.8 or higher is required. Found Python $pythonVersion" -ForegroundColor Red
        exit 1
    }
    Write-Host "Found Python $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check Node.js
$nodeVersion = node --version 2>&1
if ($nodeVersion -match "v(\d+)\.") {
    $majorVersion = [int]$matches[1]
    if ($majorVersion -lt 16) {
        Write-Host "Node.js 16 or higher is required. Found Node.js $nodeVersion" -ForegroundColor Red
        exit 1
    }
    Write-Host "Found Node.js $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "Node.js is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Set up backend
Write-Host "`nSetting up backend..." -ForegroundColor Cyan
Set-Location backend

# Create and activate virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
$activatePath = ".\venv\Scripts\Activate.ps1"
if (Test-Path $activatePath) {
    . $activatePath
    Write-Host "Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-test.txt

# Set up frontend
Write-Host "`nSetting up frontend..." -ForegroundColor Cyan
Set-Location ..\frontend

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

Write-Host "`nSetup completed successfully!" -ForegroundColor Green
Write-Host "To start the backend, run: cd backend && .\venv\Scripts\activate && python main.py" -ForegroundColor Cyan
Write-Host "To start the frontend, run: cd frontend && npm start" -ForegroundColor Cyan
