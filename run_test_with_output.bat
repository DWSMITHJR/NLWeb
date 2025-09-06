@echo off
setlocal

REM Set the Python executable path
set PYTHON_PATH=%~dp0.venv\Scripts\python.exe

REM Check if Python exists
if not exist "%PYTHON_PATH%" (
    echo Python not found at: %PYTHON_PATH%
    pause
    exit /b 1
)

echo Running test with Python at: %PYTHON_PATH%
echo =========================================

REM Run the test and capture output
"%PYTHON_PATH%" -c "import sys; print(f'Python version: {sys.version}')"
"%PYTHON_PATH%" -c "import os; print(f'Current directory: {os.getcwd()}')"
"%PYTHON_PATH%" -c "import sys; print(f'Python path: {sys.path}')"

echo.
echo Testing imports...
"%PYTHON_PATH%" -c "try: import numpy; print('✅ numpy is installed')
except ImportError: print('❌ numpy is not installed')"

"%PYTHON_PATH%" -c "import sys; sys.path.insert(0, '.'); from models import Document; print('✅ Document import successful')"

REM Run the simple test
echo.
echo Running simple_test.py...
echo =========================================
"%PYTHON_PATH%" simple_test.py

REM Pause to see the output
pause
