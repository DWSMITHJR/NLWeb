param(
    [switch]$SkipInstall
)

$ErrorActionPreference = 'Stop'

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logDir = Join-Path $PSScriptRoot 'logs'
$newItem = New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "setup_run_$timestamp.log"
Start-Transcript -Path $logPath -Force | Out-Null

Write-Host "=== NLWeb Backend: Environment Setup and Test Runner ===" -ForegroundColor Cyan
Write-Host "Log file: $logPath" -ForegroundColor DarkCyan

function Resolve-Python {
    Write-Host "\n[1] Detecting Python..." -ForegroundColor Yellow
    $pythonPath = $null
    try {
        $pythonVersion = (& python --version) 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonPath = (Get-Command python).Source
            Write-Host "Found python: $pythonPath ($pythonVersion)" -ForegroundColor Green
            return $pythonPath
        }
    } catch {}

    try {
        $pyVersion = (& py --version) 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonPath = (& py -3 -c "import sys; print(sys.executable)")
            Write-Host "Found Python via launcher: $pythonPath ($pyVersion)" -ForegroundColor Green
            return $pythonPath
        }
    } catch {}

    throw "Python not found. Please install Python 3.8+ and ensure it's in PATH."
}

$pythonExe = Resolve-Python

# Create/activate venv
$venvPath = Join-Path $PSScriptRoot '.venv'
$activatePath = Join-Path $venvPath 'Scripts\Activate.ps1'

Write-Host "\n[2] Creating virtual environment (if missing)..." -ForegroundColor Yellow
if (-not (Test-Path $venvPath)) {
    & $pythonExe -m venv $venvPath
    if ($LASTEXITCODE -ne 0) { throw "Failed to create virtual environment." }
    Write-Host "Virtual environment created at $venvPath" -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists at $venvPath" -ForegroundColor Green
}

Write-Host "\n[3] Activating venv..." -ForegroundColor Yellow
. $activatePath
Write-Host "Venv Python: $(Get-Command python).Source" -ForegroundColor Green

if (-not $SkipInstall) {
    Write-Host "\n[4] Upgrading pip/setuptools/wheel..." -ForegroundColor Yellow
    python -m pip install --upgrade pip setuptools wheel
    if ($LASTEXITCODE -ne 0) { throw "Failed to upgrade pip/setuptools/wheel." }

    Write-Host "\n[5] Installing requirements..." -ForegroundColor Yellow
    $req = Join-Path $PSScriptRoot 'requirements.txt'
    if (-not (Test-Path $req)) {
        throw "requirements.txt not found at $req"
    }
    pip install -r $req
    if ($LASTEXITCODE -ne 0) { throw "Failed to install requirements." }
} else {
    Write-Host "\n[4/5] Skipping dependency installation as requested." -ForegroundColor DarkYellow
}

# Quick environment checks
Write-Host "\n[6] Environment verification scripts..." -ForegroundColor Yellow
$checks = @('check_env.py','verify_python.py','test_python.py')
foreach ($c in $checks) {
    $p = Join-Path $PSScriptRoot $c
    if (Test-Path $p) {
        Write-Host "Running: $c" -ForegroundColor DarkCyan
        python $p
    } else {
        Write-Host "Missing: $c (skipped)" -ForegroundColor DarkGray
    }
}

# Run targeted tests first
Write-Host "\n[7] Running targeted tests..." -ForegroundColor Yellow
$pytestArgs = @('-q')
$tests = @('test_hybrid_simple.py','test_core.py')
foreach ($t in $tests) {
    $tp = Join-Path $PSScriptRoot $t
    if (Test-Path $tp) {
        Write-Host "pytest $t" -ForegroundColor DarkCyan
        python -m pytest $t -q
    } else {
        Write-Host "Missing: $t (skipped)" -ForegroundColor DarkGray
    }
}

# Run full suite
Write-Host "\n[8] Running full test suite..." -ForegroundColor Yellow
python -m pytest -q

Write-Host "\nAll steps complete." -ForegroundColor Cyan
Stop-Transcript | Out-Null
Write-Host "Transcript saved to: $logPath" -ForegroundColor DarkCyan
