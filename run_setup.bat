@echo off
echo Setting up NLWeb environment and running tests...
powershell -NoProfile -ExecutionPolicy Bypass -Command "& {Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_and_test.ps1"' -Verb RunAs}
pause
