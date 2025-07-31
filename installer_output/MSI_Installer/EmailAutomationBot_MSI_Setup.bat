@echo off
setlocal EnableDelayedExpansion

echo ========================================
echo   Email Automation Bot v1.0.0 Setup
echo ========================================
echo.
echo Manufacturer: MD JOBAYER ARAFAT
echo Product Code: 3bcebcb8-b841-4384-9c42-756a8666bce2
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This installer requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

echo Extracting installation files...

REM Create temp directory
set "TEMP_DIR=%TEMP%\EmailBotInstall_%RANDOM%"
mkdir "%TEMP_DIR%"

REM Extract using PowerShell
powershell -Command "Expand-Archive -Path '%~dp0EmailBot_MSI_Package.zip' -DestinationPath '%TEMP_DIR%' -Force"
if errorlevel 1 (
    echo ERROR: Failed to extract installation files
    rmdir /s /q "%TEMP_DIR%" 2>nul
    pause
    exit /b 1
)

echo Running installation...
cd /d "%TEMP_DIR%"
powershell -ExecutionPolicy Bypass -File "install.ps1"

echo Cleaning up...
cd /d "%~dp0"
rmdir /s /q "%TEMP_DIR%" 2>nul

echo.
echo Installation process completed.
pause
