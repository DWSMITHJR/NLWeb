@echo off
echo Setting up Python environment...
call .\.venv\Scripts\activate.bat

if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment
    pause
    exit /b %ERRORLEVEL%
)

echo Running simple test...
python .\backend\simple_test.py

if %ERRORLEVEL% NEQ 0 (
    echo Test failed with error code %ERRORLEVEL%
) else (
    echo Test completed successfully
)

pause
