@echo off
echo Starting simple test...
echo ----------------------

echo 1. Creating a test file...
echo This is a test file created at %time% > test_output.txt

echo 2. Displaying file contents:
type test_output.txt

echo.
echo 3. Current directory contents:
dir /b

echo.
echo 4. Environment variables:
echo USERNAME: %USERNAME%
echo COMPUTERNAME: %COMPUTERNAME%

echo.
echo 5. Trying to run Python:
python --version

if %ERRORLEVEL% NEQ 0 (
    echo Python is not in PATH or not installed.
) else (
    python -c "print('Python is working!')"
)

echo.
pause
