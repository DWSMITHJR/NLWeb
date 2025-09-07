@echo off
setlocal enabledelayedexpansion

echo Searching for Python in common Windows locations...
echo ===========================================

set "PYTHON_FOUND=0"

:: Check common Python installation directories
for /d /r "C:\" %%i in (Python*) do (
    if exist "%%i\python.exe" (
        echo Found Python at: %%i
        "%%i\python.exe" --version
        set "PYTHON_FOUND=1"
    )
)

:: Check Program Files directories
for %%d in ("%ProgramFiles%", "%ProgramFiles(x86)%") do (
    if exist "%%~d\Python*" (
        for /d %%i in ("%%~d\Python*") do (
            if exist "%%i\python.exe" (
                echo Found Python at: %%i
                "%%i\python.exe" --version
                set "PYTHON_FOUND=1"
            )
        )
    )
)

:: Check AppData directories
for %%d in ("%LOCALAPPDATA%\Programs\Python", "%APPDATA%\Local\Programs\Python") do (
    if exist "%%~d" (
        for /d %%i in ("%%~d\Python*") do (
            if exist "%%i\python.exe" (
                echo Found Python at: %%i
                "%%i\python.exe" --version
                set "PYTHON_FOUND=1"
            )
        )
    )
)

if "!PYTHON_FOUND!"=="0" (
    echo No Python installations found in common locations.
    echo Please install Python from https://www.python.org/downloads/
)

pause
