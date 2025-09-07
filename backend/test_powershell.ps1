# Test PowerShell execution
Write-Host "=== PowerShell Environment Test ===" -ForegroundColor Green

# Check Python installation
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Python is installed: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "Python is not installed or not in PATH" -ForegroundColor Red
}

# List Python executables in PATH
Write-Host "`nPython executables in PATH:" -ForegroundColor Yellow
Get-Command python -All | Format-Table -Property Source, Version

# Test basic Python command
Write-Host "`nTesting Python command execution..." -ForegroundColor Yellow
$testOutput = python -c "import sys; print(f'Python {sys.version}'); print(f'Executable: {sys.executable}')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host $testOutput -ForegroundColor Green
} else {
    Write-Host "Failed to execute Python command:" -ForegroundColor Red
    Write-Host $testOutput -ForegroundColor Red
}

# Check if we can write to the current directory
$testFile = "test_write_permission.txt"
Write-Host "`nTesting file system write permissions..." -ForegroundColor Yellow
try {
    "Test write" | Out-File -FilePath $testFile -Force
    if (Test-Path $testFile) {
        Write-Host "Successfully wrote to $testFile" -ForegroundColor Green
        Remove-Item $testFile -Force
    } else {
        Write-Host "Failed to write to file system" -ForegroundColor Red
    }
} catch {
    Write-Host "Error testing file system: $_" -ForegroundColor Red
}

Write-Host "`nTest complete. Press any key to continue..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
