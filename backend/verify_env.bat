@echo off
echo Verifying Python environment...
echo ==============================

:: Check if Python is in PATH
echo.
echo Checking Python in PATH...
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Python is in PATH
    python --version
) else (
    echo [ERROR] Python is not in PATH
    echo Please install Python 3.7+ and add it to your system PATH
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2 delims= " %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
for /f "tokens=1,2 delims=. " %%a in ("%PYTHON_VERSION%") do (
    if %%a LSS 3 (
        echo [ERROR] Python 3.7 or later is required. Found version %PYTHON_VERSION%
        pause
        exit /b 1
    )
    if %%b LSS 7 (
        echo [ERROR] Python 3.7 or later is required. Found version %PYTHON_VERSION%
        pause
        exit /b 1
    )
)

echo.
echo Python %PYTHON_VERSION% is installed and accessible.

:: Check if pip is available
echo.
echo Checking pip...
python -m pip --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] pip is available
    python -m pip --version
) else (
    echo [ERROR] pip is not available
    echo Please ensure pip is installed with your Python installation
    pause
    exit /b 1
)

echo.
echo Environment verification complete!
pause
