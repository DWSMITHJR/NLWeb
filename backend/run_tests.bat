@echo off
echo Running Python environment check...
python --version
python -c "import sys; print('Python path:', ';'.join(sys.path))"

echo.
echo Running minimal test...
python minimal_test.py

echo.
echo Running simple hybrid retriever test...
python -m pytest test_hybrid_simple.py -v

pause
