@echo off
echo Running tests with logging...

:: Create logs directory if it doesn't exist
if not exist logs mkdir logs

:: Get current timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%-%dt:~10,2%-%dt:~12,2%"

:: Run tests and save output to log file
python -m pytest backend/test_core.py -v -s > "logs/test_output_%timestamp%.log" 2>&1

:: Show the log file path
echo Test output saved to: logs/test_output_%timestamp%.log

:: Open the log file in the default text editor
start "" "logs/test_output_%timestamp%.log"
