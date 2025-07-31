@echo off
echo Starting Email Automation Bot...
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Run the application
python main.py

REM Keep window open if there's an error
if %ERRORLEVEL% neq 0 (
    echo.
    echo Application exited with error code %ERRORLEVEL%
    pause
)