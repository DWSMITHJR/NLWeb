@echo off
echo System Check
echo ===========

echo.
echo 1. Basic System Info:
ver
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

echo.
echo 2. Disk Information:
wmic logicaldisk get caption, freespace, size, volumename

echo.
echo 3. Environment Variables:
echo USERNAME: %USERNAME%
echo COMPUTERNAME: %COMPUTERNAME%
echo USERPROFILE: %USERPROFILE%

echo.
echo 4. Checking Python installation:
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python is in PATH
    python --version
) else (
    echo Python is NOT in PATH
)

echo.
echo 5. Checking Python in common locations:
echo - Checking Program Files...
dir /s /b "%ProgramFiles%\Python*\python.exe" 2>nul
echo - Checking Program Files (x86)...
dir /s /b "%ProgramFiles(x86)%\Python*\python.exe" 2>nul
echo - Checking Local AppData...
dir /s /b "%LOCALAPPDATA%\Programs\Python\Python*\python.exe" 2>nul

echo.
echo 6. Checking for Python launcher:
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python launcher (py) is available
    py --version
) else (
    echo Python launcher (py) is NOT available
)

echo.
pause
