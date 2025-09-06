# Test environment script
Write-Host "=== Environment Test ===" -ForegroundColor Cyan
Write-Host "PowerShell Version: $($PSVersionTable.PSVersion)"
Write-Host "Current Directory: $(Get-Location)"

# Check Python
Write-Host "`n=== Python Check ===" -ForegroundColor Cyan
$pythonPath = "$PSScriptRoot\.venv\Scripts\python.exe"
if (Test-Path $pythonPath) {
    Write-Host "Found Python at: $pythonPath" -ForegroundColor Green
    & $pythonPath --version
} else {
    Write-Host "Python not found at $pythonPath" -ForegroundColor Yellow
}

# Check backend directory
Write-Host "`n=== Backend Check ===" -ForegroundColor Cyan
$backendPath = "$PSScriptRoot\backend"
if (Test-Path $backendPath) {
    Write-Host "Backend directory exists" -ForegroundColor Green
    Get-ChildItem $backendPath | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
} else {
    Write-Host "Backend directory not found at $backendPath" -ForegroundColor Red
}

# Pause to see the output
Write-Host "`nPress any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
