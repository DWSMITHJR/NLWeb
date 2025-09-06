@echo off
setlocal

REM Set the Python executable path
set PYTHON_PATH=%~dp0venv\Scripts\python.exe
set PIP_PATH=%~dp0venv\Scripts\pip.exe

REM Check if Python exists
if not exist "%PYTHON_PATH%" (
    echo Python not found at: %PYTHON_PATH%
    pause
    exit /b 1
)

echo Installing required packages...
echo =========================================

"%PIP_PATH%" install --upgrade pip
"%PIP_PATH%" install numpy
"%PIP_PATH%" install -r backend\requirements.txt

echo.
echo Installation complete!
pause
