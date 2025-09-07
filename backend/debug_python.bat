@echo off
echo Testing Python execution...
python --version > python_version.txt 2>&1
type python_version.txt
del python_version.txt

echo.
echo Running a simple Python command...
python -c "print('Python command execution test')" > python_test.txt 2>&1
type python_test.txt
del python_test.txt

pause
