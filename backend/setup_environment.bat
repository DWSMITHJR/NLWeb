@echo off
setlocal enabledelayedexpansion

echo Setting up Python environment...
echo =================================

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.7 or later from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Get Python version
for /f "tokens=2 delims= " %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
for /f "tokens=1,2 delims=. " %%a in ("!PYTHON_VERSION!") do set PYTHON_MAJOR=%%a& set PYTHON_MINOR=%%b

:: Check Python version
if !PYTHON_MAJOR! LSS 3 (
    echo Python 3.7 or later is required. Found version !PYTHON_VERSION!
    pause
    exit /b 1
)
if !PYTHON_MINOR! LSS 7 (
    echo Python 3.7 or later is required. Found version !PYTHON_VERSION!
    pause
    exit /b 1
)

echo Found Python !PYTHON_VERSION!

:: Create and activate virtual environment
echo.
echo Creating virtual environment...
python -m venv .venv
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

:: Activate the virtual environment
call .venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo Failed to upgrade pip.
    pause
    exit /b 1
)

:: Install requirements
echo.
echo Installing requirements...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo Environment setup complete!
echo To activate the virtual environment, run: .\.venv\Scripts\activate

:: Run the tests
echo.
echo Running tests...
python -m pytest test_hybrid_simple.py -v

pause
