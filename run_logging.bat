@echo off
echo Starting test script with logging...
"%ProgramFiles%\PowerShell\7\pwsh.exe" -NoProfile -ExecutionPolicy Bypass -Command "& { .\run_with_logging.ps1 }"
pause
