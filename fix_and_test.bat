@echo off
REM Remove existing virtual environment if it exists
if exist venv (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)

REM Create new virtual environment
echo Creating new virtual environment...
python -m venv venv

REM Activate and install requirements
call venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools
pip install -r requirements.txt
pip install -r backend\requirements-test.txt

REM Run the tests
echo Running tests...
python -m pytest tests/ -v

pause
