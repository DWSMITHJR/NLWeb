@echo off
call .venv_new\Scripts\activate.bat
python backend/test_verify.py -v
pause
