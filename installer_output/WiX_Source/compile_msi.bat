
@echo off
echo ========================================
echo   Email Automation Bot - MSI Compiler
echo ========================================
echo.

REM Check for WiX Toolset
set "WIX_PATH="
if exist "C:\Program Files (x86)\WiX Toolset v3.11\bin\candle.exe" (
    set "WIX_PATH=C:\Program Files (x86)\WiX Toolset v3.11\bin"
) else if exist "C:\Program Files\WiX Toolset v3.11\bin\candle.exe" (
    set "WIX_PATH=C:\Program Files\WiX Toolset v3.11\bin"
) else (
    echo ERROR: WiX Toolset not found!
    echo Please install WiX Toolset from: https://wixtoolset.org/releases/
    pause
    exit /b 1
)

echo Found WiX Toolset at: %WIX_PATH%
echo.

echo Compiling WiX source file...
"%WIX_PATH%\candle.exe" EmailBot.wxs
if errorlevel 1 (
    echo ERROR: Compilation failed!
    pause
    exit /b 1
)

echo Linking MSI package...
"%WIX_PATH%\light.exe" EmailBot.wixobj -out "EmailAutomationBot_v1.0.0.msi"
if errorlevel 1 (
    echo ERROR: Linking failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo MSI package created successfully!
echo ========================================
echo.
echo File: EmailAutomationBot_v1.0.0.msi
echo.
pause
