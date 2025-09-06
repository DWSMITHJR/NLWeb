@echo off
echo Starting test script with PowerShell 7...
"%ProgramFiles%\PowerShell\7\pwsh.exe" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "& { Write-Host 'PowerShell Version:' $PSVersionTable.PSVersion; Write-Host 'Current Directory:' (Get-Location); Write-Host 'Running test script...'; .\test_system.ps1 -SkipFrontend -Verbose; Write-Host 'Exit Code:' $LASTEXITCODE }"
pause
