@echo off
echo System Verification
echo ==================

echo 1. System Information:
ver
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

echo.
echo 2. Current Directory:
echo %CD%

echo.
echo 3. Directory Contents:
dir /b

echo.
echo 4. Environment Variables:
echo USERNAME: %USERNAME%
echo COMPUTERNAME: %COMPUTERNAME%
echo USERPROFILE: %USERPROFILE%

echo.
echo 5. Testing File Operations:
echo Creating test file...
echo Test content > test_verify.txt
if exist test_verify.txt (
    echo File created successfully
    echo File contents:
    type test_verify.txt
    del test_verify.txt
) else (
    echo Failed to create file
)

echo.
pause
