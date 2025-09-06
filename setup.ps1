#Requires -RunAsAdministrator
#Requires -Version 7.0

<#
.SYNOPSIS
    Setup script for Windows NLWeb AutoRAG
.DESCRIPTION
    This script sets up the development environment for the NLWeb AutoRAG project.
    It checks for required software, sets up a Python virtual environment, and installs dependencies.
.PARAMETER Force
    Force reinstallation of all dependencies
.EXAMPLE
    .\setup.ps1
    .\setup.ps1 -Force
#>

[CmdletBinding()]
param (
    [switch]$Force
)

# Set error action preference
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Logging function
function Write-Log {
    param (
        [string]$Message,
        [ValidateSet("Info", "Success", "Warning", "Error")]
        [string]$Level = "Info"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "Success" { "Green" }
        "Warning" { "Yellow" }
        "Error"   { "Red" }
        default    { "Cyan" }
    }
    
    Write-Host "[$timestamp] $Message" -ForegroundColor $color
}

# Function to check if a command exists
function Test-CommandExists {
    param($command)
    $exists = $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
    if (-not $exists) {
        Write-Log "Command not found: $command" -Level Error
    }
    return $exists
}

# Store original location and error action preference
$originalLocation = Get-Location
$originalErrorActionPreference = $ErrorActionPreference

try {
    # Check if running as administrator
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        throw "This script requires administrator privileges. Please run as administrator."
    }

    # Check for required software
    Write-Log "Checking system requirements..."
    $requirements = @(
        @{ Name = "Python 3.8+"; Command = "python --version"; Install = "https://www.python.org/downloads/" },
        @{ Name = "Node.js 16+"; Command = "node --version"; Install = "https://nodejs.org/" },
        @{ Name = "Git"; Command = "git --version"; Install = "https://git-scm.com/download/win" }
    )

    $missingRequirements = @()
    foreach ($req in $requirements) {
        if (-not (Test-CommandExists $req.Command.Split(' ')[0])) {
            $missingRequirements += $req
            Write-Log "✗ $($req.Name) is not installed" -Level Warning
        } else {
            Write-Log "✓ $($req.Name) is installed" -Level Success
        }
    }

    if ($missingRequirements.Count -gt 0) {
        $installMessage = "The following requirements are missing:`n"
        $missingRequirements | ForEach-Object {
            $installMessage += "- $($_.Name) (Install from: $($_.Install))`n"
        }
        throw $installMessage
    }

    # Validate project structure
    $requiredDirs = @("backend", "frontend")
    foreach ($dir in $requiredDirs) {
        if (-not (Test-Path -Path $dir)) {
            throw "Required directory '$dir' not found. Please ensure you're in the project root directory."
        }
    }

    # Check Python version
    Write-Log "Checking Python installation..."
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.(\d+)") {
            $minorVersion = [int]$matches[1]
            if ($minorVersion -lt 8) {
                throw "Python 3.8 or higher is required. Found Python $pythonVersion"
            }
            Write-Log "✓ $pythonVersion" -Level Success
        }
        
        # Check Node.js version
        Write-Log "Checking Node.js installation..."
        $nodeVersion = node --version
        if ($nodeVersion -match "v(\d+)\.") {
            $majorVersion = [int]$matches[1]
            if ($majorVersion -lt 16) {
                throw "Node.js 16 or higher is required. Found $nodeVersion"
            }
            Write-Log "✓ Node.js $nodeVersion" -Level Success
        }
        
        # Set up virtual environment
        $venvPath = ".\backend\venv"
        $requirementsFiles = @("requirements.txt", "requirements-test.txt")
        
        # Check if virtual environment already exists
        if ((Test-Path $venvPath) -and (-not $Force)) {
            Write-Log "Virtual environment already exists at $venvPath. Use -Force to reinstall." -Level Warning
        } else {
            if ($Force -and (Test-Path $venvPath)) {
                Write-Log "Removing existing virtual environment..." -Level Warning
                Remove-Item -Path $venvPath -Recurse -Force -ErrorAction Stop
            }
            
            # Create virtual environment
            Write-Log "Creating Python virtual environment..."
            python -m venv $venvPath
            
            if (-not (Test-Path "$venvPath\Scripts\activate")) {
                throw "Failed to create virtual environment at $venvPath"
            }
            
            Write-Log "Virtual environment created successfully" -Level Success
            
            # Activate virtual environment and install requirements
            Write-Log "Installing Python dependencies..."
            & "$venvPath\Scripts\activate.ps1"
            
            # Upgrade pip first
            python -m pip install --upgrade pip
            
            foreach ($reqFile in $requirementsFiles) {
                $reqPath = ".\backend\$reqFile"
                if (Test-Path $reqPath) {
                    Write-Log "Installing dependencies from $reqFile..."
                    pip install -r $reqPath
                    if ($LASTEXITCODE -ne 0) {
                        throw "Failed to install dependencies from $reqFile"
                    }
                    Write-Log "Successfully installed dependencies from $reqFile" -Level Success
                } else {
                    Write-Log "Requirements file not found: $reqPath" -Level Warning
                }
            }
        }
    } catch {
        throw "Python check failed: $_"
    }

    # Check Node.js
    Write-Log "Checking Node.js installation..."
    try {
        $nodeVersion = node --version 2>&1
        if ($nodeVersion -match "v(\d+)\.") {
            $majorVersion = [int]$matches[1]
            if ($majorVersion -lt 16) {
                throw "Node.js 16 or higher is required. Found Node.js $nodeVersion"
            }
            Write-Log "✓ Node.js $nodeVersion" -Level Success
        } else {
            throw "Node.js is not installed or not in PATH"
        }
    } catch {
        throw "Node.js check failed: $_"
    }

    # Set up backend
    Write-Log "Setting up backend..."
    $backendPath = Join-Path $PSScriptRoot "backend"
    if (-not (Test-Path $backendPath)) {
        throw "Backend directory not found at $backendPath"
    }
    
    Set-Location $backendPath

    # Create and activate virtual environment
    $venvPath = Join-Path $backendPath "venv"
    if ($Force -or -not (Test-Path $venvPath)) {
        if (Test-Path $venvPath) {
            Write-Log "Removing existing virtual environment..." -Level Warning
            Remove-Item -Path $venvPath -Recurse -Force -ErrorAction Stop
        }
        
        Write-Log "Creating virtual environment..."
        & python -m venv $venvPath
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
        Write-Log "Virtual environment created successfully" -Level Success
    } else {
        Write-Log "Virtual environment already exists. Use -Force to recreate." -Level Info
    }

    # Activate virtual environment
    $activatePath = Join-Path $venvPath "Scripts\Activate.ps1"
    if (-not (Test-Path $activatePath)) {
        throw "Virtual environment activation script not found at $activatePath"
    }
    
    . $activatePath
    Write-Log "Virtual environment activated" -Level Success

    # Install Python dependencies
    Write-Log "Installing Python dependencies..."
    $requirementsFiles = @("requirements.txt", "requirements-test.txt")
    foreach ($reqFile in $requirementsFiles) {
        $reqPath = Join-Path $backendPath $reqFile
        if (Test-Path $reqPath) {
            Write-Log "Installing dependencies from $reqFile..."
            & pip install --upgrade pip
            & pip install -r $reqPath
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to install requirements from $reqFile"
            }
            Write-Log "Successfully installed dependencies from $reqFile" -Level Success
        } else {
            Write-Log "Requirements file not found: $reqPath" -Level Warning
        }
    }

    # Set up frontend
    Write-Log "Setting up frontend..."
    $frontendPath = Join-Path $PSScriptRoot "frontend"
    if (-not (Test-Path $frontendPath)) {
        throw "Frontend directory not found at $frontendPath"
    }
    
    Set-Location $frontendPath

    # Install frontend dependencies
    Write-Log "Setting up frontend dependencies..."
    if ($Force -or -not (Test-Path "node_modules")) {
        if (Test-Path "node_modules") {
            Write-Log "Removing existing node_modules..." -Level Warning
            Remove-Item -Path "node_modules" -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        Write-Log "Installing Node.js dependencies..."
        & npm ci
        if ($LASTEXITCODE -ne 0) {
            # Fallback to npm install if ci fails
            Write-Log "npm ci failed, trying npm install..." -Level Warning
            & npm install
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to install Node.js dependencies"
            }
        }
        Write-Log "Node.js dependencies installed successfully" -Level Success
    } else {
        Write-Log "Node.js dependencies already installed. Use -Force to reinstall." -Level Info
    }

    # Return to project root
    Set-Location $PSScriptRoot
    
    Write-Log "`nSetup completed successfully!" -Level Success
    Write-Host "`nNext steps:" -ForegroundColor Green
    Write-Host "1. Start the backend: cd backend; .\venv\Scripts\activate; python main.py"
    Write-Host "2. In a new terminal, start the frontend: cd frontend; npm start"
    Write-Host "`nThe application will be available at http://localhost:3000"
    
} catch {
    Write-Host "`n[ERROR] $_" -ForegroundColor Red
    Write-Host "`nSetup failed. Please fix the above issues and try again.`n" -ForegroundColor Red
    exit 1
} finally {
    # Ensure we return to the original directory even if there was an error
    if ($originalLocation) {
        Set-Location $originalLocation
    }
    
    # Reset error action preference
    $ErrorActionPreference = $originalErrorActionPreference
}
