# Test script for Windows NLWeb AutoRAG

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "This script requires administrator privileges. Please run as administrator." -ForegroundColor Red
    exit 1
}

# Function to check if a command exists
function Test-Command {
    param([string]$command)
    try {
        $null = Get-Command $command -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Test Python environment
Write-Host "`nTesting Python environment..." -ForegroundColor Cyan
$pythonTest = python -c "import sys; print(f'Python {sys.version.split()[0]} on {sys.platform}')"
if ($?) {
    Write-Host $pythonTest -ForegroundColor Green
    
    # Test Python packages
    $packages = @("pydantic", "fastapi", "sentence_transformers", "faiss_cpu", "rank_bm25")
    $missingPackages = @()
    
    foreach ($pkg in $packages) {
        $test = python -c "import $pkg; print('$pkg version:', $pkg.__version__ if hasattr($pkg, '__version__') else 'OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $pkg: $test" -ForegroundColor Green
        } else {
            Write-Host "✗ $pkg: Not found" -ForegroundColor Red
            $missingPackages += $pkg
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Host "`nMissing Python packages. Installing..." -ForegroundColor Yellow
        pip install $missingPackages
    }
} else {
    Write-Host "Python test failed" -ForegroundColor Red
    exit 1
}

# Test Node.js environment
Write-Host "`nTesting Node.js environment..." -ForegroundColor Cyan
$nodeVersion = node --version
$npmVersion = npm --version

if ($?) {
    Write-Host "Node.js $nodeVersion" -ForegroundColor Green
    Write-Host "npm $npmVersion" -ForegroundColor Green
} else {
    Write-Host "Node.js test failed" -ForegroundColor Red
    exit 1
}

# Test backend
Write-Host "`nTesting backend..." -ForegroundColor Cyan
Set-Location backend

# Run backend tests
$testResults = python -m pytest test_*.py -v
if ($LASTEXITCODE -eq 0) {
    Write-Host "Backend tests passed" -ForegroundColor Green
} else {
    Write-Host "Backend tests failed" -ForegroundColor Red
    exit 1
}

# Start backend server in background
Write-Host "`nStarting backend server..." -ForegroundColor Cyan
$backendProcess = Start-Process -NoNewWindow -PassThru -FilePath "python" -ArgumentList "main.py"
Start-Sleep -Seconds 5  # Wait for server to start

# Test API endpoints
$apiBaseUrl = "http://localhost:8000"
$testEndpoints = @(
    "/docs",
    "/redoc",
    "/documents/",
    "/query/"
)

foreach ($endpoint in $testEndpoints) {
    $url = "${apiBaseUrl}${endpoint}"
    try {
        $response = Invoke-WebRequest -Uri $url -Method Get -ErrorAction Stop
        Write-Host "✓ GET ${endpoint}: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "✗ GET ${endpoint}: $($_.Exception.Response.StatusCode.Value__)" -ForegroundColor Red
    }
}

# Stop backend server
Stop-Process -Id $backendProcess.Id -Force

# Test frontend
Write-Host "`nTesting frontend..." -ForegroundColor Cyan
Set-Location ..\frontend

# Install frontend dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

# Run frontend tests
$frontendTest = npm test -- --watchAll=false
if ($LASTEXITCODE -eq 0) {
    Write-Host "Frontend tests passed" -ForegroundColor Green
} else {
    Write-Host "Frontend tests failed" -ForegroundColor Red
    exit 1
}

Write-Host "`nAll tests completed successfully!" -ForegroundColor Green
