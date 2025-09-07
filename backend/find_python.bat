@echo off
echo Checking for Python in common locations...

echo.
echo Checking Program Files...
dir /s /b "C:\Program Files\Python*\python.exe" 2>nul
dir /s /b "C:\Program Files (x86)\Python*\python.exe" 2>nul

echo.
echo Checking Local AppData...
dir /s /b "%LOCALAPPDATA%\Programs\Python\Python*\python.exe" 2>nul

echo.
echo Checking User AppData...
dir /s /b "%APPDATA%\Local\Programs\Python\Python*\python.exe" 2>nul

echo.
echo Checking PATH environment variable...
echo %PATH% | find /i "python" >nul
if %ERRORLEVEL% EQU 0 (
    echo Python is in PATH
) else (
    echo Python is NOT in PATH
)

pause
