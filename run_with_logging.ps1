# Create a timestamp for the log file
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path -Path $PSScriptRoot -ChildPath "test_log_${timestamp}.txt"

# Start transcript logging
Start-Transcript -Path $logFile -Force

try {
    Write-Host "Starting test script with logging..." -ForegroundColor Green
    Write-Host "Log file: $logFile" -ForegroundColor Cyan
    
    # Display PowerShell version
    Write-Host "`nPowerShell Version:" -ForegroundColor Yellow
    $PSVersionTable | Out-String | Write-Host -ForegroundColor White
    
    # Display current directory contents
    Write-Host "`nCurrent Directory Contents:" -ForegroundColor Yellow
    Get-ChildItem -Path . -Force | Out-String | Write-Host -ForegroundColor White
    
    # Run the test script
    Write-Host "`nRunning test_system.ps1..." -ForegroundColor Green
    & "$PSScriptRoot\test_system.ps1" -SkipFrontend -Verbose
    
    Write-Host "`nTest script completed with exit code: $LASTEXITCODE" -ForegroundColor Green
} 
catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor DarkGray
    throw $_
}
finally {
    # Stop transcript
    Stop-Transcript
    
    # Display the log file location
    Write-Host "`nLog file created at: $logFile" -ForegroundColor Cyan
    Write-Host "Script execution complete. Press any key to continue..." -ForegroundColor Green
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
}
