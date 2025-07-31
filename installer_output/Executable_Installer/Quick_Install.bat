
@echo off
echo ========================================
echo   Email Automation Bot - Quick Setup
echo ========================================
echo.

set "INSTALL_DIR=%PROGRAMFILES%\Email Automation Bot"
set "ZIP_FILE=EmailAutomationBot_Portable_v1.0.0.zip"

echo Installing Email Automation Bot...
echo.

REM Create installation directory
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    if errorlevel 1 (
        echo ERROR: Could not create installation directory
        echo Please run as administrator or choose a different location
        pause
        exit /b 1
    )
)

REM Extract files using PowerShell
echo Extracting files...
powershell -Command "Expand-Archive -Path '%~dp0%ZIP_FILE%' -DestinationPath '%INSTALL_DIR%' -Force"
if errorlevel 1 (
    echo ERROR: Failed to extract files
    pause
    exit /b 1
)

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Email Automation Bot.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\EmailAutomationBot.exe'; $Shortcut.Save()"

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo The application has been installed to:
echo %INSTALL_DIR%
echo.
echo A desktop shortcut has been created.
echo.
set /p "LAUNCH=Would you like to launch the application now? (Y/N): "
if /i "%LAUNCH%"=="Y" (
    start "" "%INSTALL_DIR%\EmailAutomationBot.exe"
)

echo.
echo Thank you for using Email Automation Bot!
pause
