param(
  [switch]$RecreateVenv
)

$ErrorActionPreference = 'Stop'

Write-Host "[Backend] Starting setup..." -ForegroundColor Cyan

# Ensure Python exists
python --version | Out-Null

# Venv
$venvPath = Join-Path $PSScriptRoot 'venv'
if (Test-Path $venvPath -and $RecreateVenv) {
  Write-Host "[Backend] Removing existing venv" -ForegroundColor Yellow
  Remove-Item -Recurse -Force $venvPath
}

if (!(Test-Path $venvPath)) {
  Write-Host "[Backend] Creating venv" -ForegroundColor Cyan
  python -m venv $venvPath
}

$activate = Join-Path $venvPath 'Scripts\Activate.ps1'
. $activate

Write-Host "[Backend] Installing requirements" -ForegroundColor Cyan
pip install --upgrade pip
pip install -r (Join-Path $PSScriptRoot 'requirements.txt')

Write-Host "[Backend] Running server on http://localhost:8000" -ForegroundColor Green
python (Join-Path $PSScriptRoot 'main.py')
