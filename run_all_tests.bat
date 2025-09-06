@echo off
setlocal enabledelayedexpansion

:: Set the Python executable path
set PYTHON=python

:: List of test files to run
set TEST_FILES=(
    "test_hybrid_simple.py"
    "test_prompt_templates.py"
    "test_hybrid_retriever.py"
    "test_core.py"
    "test_automl_integration.py"
)

echo Running all tests...
echo ========================================

set ALL_PASSED=1

:: Run each test file
for %%f in (%TEST_FILES%) do (
    echo.
    echo ===== Running %%~nxf =====
    %PYTHON% -m pytest -v "%%~f"
    if !ERRORLEVEL! NEQ 0 (
        set ALL_PASSED=0
        echo.
        echo !!! Test failed: %%~nxf
    )
)

echo.
echo ========================================
if !ALL_PASSED! EQU 1 (
    echo All tests passed successfully!
) else (
    echo Some tests failed. Please check the output above.
)

pause
