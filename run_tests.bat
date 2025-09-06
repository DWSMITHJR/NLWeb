@echo off
setlocal

echo Running test suite...
echo ========================================

cd /d %~dp0
call .\venv\Scripts\activate
cd backend

:: Run pytest with verbose output
echo Running pytest with verbose output...
python -m pytest -v

:: If pytest fails, run with full traceback
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo Running with full traceback...
    python -m pytest -v --tb=long
)

:: If still failing, run tests one by one
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo Running tests one by one...
    
    for %%f in (test_*.py) do (
        echo.
        echo ===== Running %%f =====
        python -m pytest -v %%f
        if %ERRORLEVEL% NEQ 0 (
            echo Test failed in %%f
            pause
        )
    )
)

pause
