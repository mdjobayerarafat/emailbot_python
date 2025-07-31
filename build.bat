@echo off
echo ========================================
echo   Email Automation Bot - Windows Build
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Installing/Updating dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building Windows executable...
python build_windows.py

if errorlevel 1 (
    echo.
    echo BUILD FAILED!
    echo Check the error messages above for details.
) else (
    echo.
    echo BUILD SUCCESSFUL!
    echo The executable is ready in the 'release' folder.
    echo.
    echo You can now distribute EmailAutomationBot.exe
)

echo.
echo Press any key to exit...
pause >nul