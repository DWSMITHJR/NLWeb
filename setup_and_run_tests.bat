@echo off
REM Setup and test script for NLWeb

echo Setting up Python environment...

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Create and activate virtual environment
echo Creating virtual environment...
python -m venv .venv
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

call .venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo Failed to upgrade pip.
    pause
    exit /b 1
)

REM Install package in development mode
echo Installing package in development mode...
pip install -e .
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install package in development mode.
    pause
    exit /b 1
)

REM Install test dependencies
echo Installing test dependencies...
pip install pytest numpy sentence-transformers rank-bm25 faiss-cpu pydantic scikit-learn
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install test dependencies.
    pause
    exit /b 1
)

REM Run tests
echo Running tests...
python -m pytest backend/test_core.py -v

REM Pause to see the output
pause
