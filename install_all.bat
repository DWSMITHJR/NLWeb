@echo off
echo Installing Python dependencies...
call .\venv\Scripts\activate
pip install --upgrade pip
pip install pydantic numpy sentence-transformers rank-bm25 faiss-cpu
pip install -r backend\requirements.txt

echo.
echo Installation complete! You can now run the test with:
echo   cd backend
echo   python simple_test.py
pause
