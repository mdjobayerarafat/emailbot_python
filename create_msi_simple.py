#!/usr/bin/env python3
"""
Simple MSI-style Installer Creator for Email Automation Bot
Creates a self-extracting installer that mimics MSI behavior
"""

import os
import shutil
import zipfile
import uuid
from pathlib import Path

def create_msi_installer():
    print("🚀 Creating MSI-style installer for Email Automation Bot...")
    
    # Configuration
    app_name = "Email Automation Bot"
    version = "1.0.0"
    manufacturer = "MD JOBAYER ARAFAT"
    product_code = str(uuid.uuid4())
    upgrade_code = str(uuid.uuid4())
    
    # Paths
    project_root = Path.cwd()
    release_dir = project_root / "release"
    output_dir = project_root / "installer_output"
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    if not release_dir.exists():
        print("❌ Release directory not found!")
        return False
    
    print(f"📦 Product Code: {product_code}")
    print(f"🔄 Upgrade Code: {upgrade_code}")
    
    # Create MSI package ZIP
    msi_zip_path = output_dir / "EmailBot_MSI_Package.zip"
    print(f"📁 Creating package: {msi_zip_path}")
    
    with zipfile.ZipFile(msi_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(release_dir)
                zipf.write(file_path, arc_name)
                print(f"  ✓ Added: {arc_name}")
    
    # Create PowerShell installer script
    install_ps1 = f'''
# Email Automation Bot MSI-style Installer
# Product: {app_name} v{version}
# Product Code: {product_code}

Write-Host "Installing {app_name} v{version}..." -ForegroundColor Green

# Installation directory
$InstallDir = "$env:ProgramFiles\\EmailAutomationBot"

# Create installation directory
if (!(Test-Path $InstallDir)) {{
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Write-Host "✓ Created installation directory: $InstallDir"
}}

# Copy files
Write-Host "📁 Copying application files..."
Get-ChildItem -Path "." -Recurse | ForEach-Object {{
    $relativePath = $_.FullName.Substring((Get-Location).Path.Length + 1)
    $destPath = Join-Path $InstallDir $relativePath
    
    if ($_.PSIsContainer) {{
        if (!(Test-Path $destPath)) {{
            New-Item -ItemType Directory -Path $destPath -Force | Out-Null
        }}
    }} else {{
        $destDir = Split-Path $destPath -Parent
        if (!(Test-Path $destDir)) {{
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }}
        Copy-Item $_.FullName $destPath -Force
        Write-Host "  ✓ $relativePath"
    }}
}}

# Create desktop shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\\Desktop\\Email Automation Bot.lnk")
$Shortcut.TargetPath = "$InstallDir\\EmailAutomationBot.exe"
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "{app_name}"
$Shortcut.Save()
Write-Host "✓ Created desktop shortcut"

# Create Start Menu shortcut
$StartMenuPath = "$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs"
$StartShortcut = $WshShell.CreateShortcut("$StartMenuPath\\Email Automation Bot.lnk")
$StartShortcut.TargetPath = "$InstallDir\\EmailAutomationBot.exe"
$StartShortcut.WorkingDirectory = $InstallDir
$StartShortcut.Description = "{app_name}"
$StartShortcut.Save()
Write-Host "✓ Created Start Menu shortcut"

# Add to Add/Remove Programs
$RegPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{product_code}"
try {{
    New-Item -Path $RegPath -Force | Out-Null
    Set-ItemProperty -Path $RegPath -Name "DisplayName" -Value "{app_name}"
    Set-ItemProperty -Path $RegPath -Name "DisplayVersion" -Value "{version}"
    Set-ItemProperty -Path $RegPath -Name "Publisher" -Value "{manufacturer}"
    Set-ItemProperty -Path $RegPath -Name "InstallLocation" -Value $InstallDir
    Set-ItemProperty -Path $RegPath -Name "UninstallString" -Value "powershell.exe -ExecutionPolicy Bypass -File `\"$InstallDir\\uninstall.ps1`\""
    Set-ItemProperty -Path $RegPath -Name "DisplayIcon" -Value "$InstallDir\\EmailAutomationBot.exe"
    Set-ItemProperty -Path $RegPath -Name "NoModify" -Value 1
    Set-ItemProperty -Path $RegPath -Name "NoRepair" -Value 1
    Write-Host "✓ Registered in Add/Remove Programs"
}} catch {{
    Write-Host "⚠️ Could not register in Add/Remove Programs (requires admin rights)"
}}

# Create uninstaller
$UninstallScript = @'
# Email Automation Bot Uninstaller
Write-Host "Uninstalling Email Automation Bot..." -ForegroundColor Yellow

$InstallDir = "$env:ProgramFiles\\EmailAutomationBot"

# Remove shortcuts
Remove-Item "$env:USERPROFILE\\Desktop\\Email Automation Bot.lnk" -ErrorAction SilentlyContinue
Remove-Item "$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Email Automation Bot.lnk" -ErrorAction SilentlyContinue
Write-Host "✓ Removed shortcuts"

# Remove registry entry
try {{
    Remove-Item "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{product_code}" -Recurse -ErrorAction SilentlyContinue
    Write-Host "✓ Removed registry entries"
}} catch {{}}

# Remove installation directory
if (Test-Path $InstallDir) {{
    Remove-Item $InstallDir -Recurse -Force
    Write-Host "✓ Removed installation directory"
}}

Write-Host "✅ Email Automation Bot has been uninstalled successfully!" -ForegroundColor Green
Read-Host "Press Enter to close"
'@

$UninstallScript | Out-File -FilePath "$InstallDir\\uninstall.ps1" -Encoding UTF8

Write-Host "✅ Installation completed successfully!" -ForegroundColor Green
Write-Host "📍 Installed to: $InstallDir" -ForegroundColor Cyan
Write-Host "🖥️ Desktop shortcut created" -ForegroundColor Cyan
Write-Host "📋 Added to Start Menu" -ForegroundColor Cyan
'''
    
    # Save installer script to ZIP
    with zipfile.ZipFile(msi_zip_path, 'a') as zipf:
        zipf.writestr('install.ps1', install_ps1)
    
    # Create MSI-style batch launcher
    batch_content = f'''@echo off
setlocal EnableDelayedExpansion

echo ========================================
echo   {app_name} v{version} Setup
echo ========================================
echo.
echo Manufacturer: {manufacturer}
echo Product Code: {product_code}
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
set "TEMP_DIR=%TEMP%\\EmailBotInstall_%RANDOM%"
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
'''
    
    batch_path = output_dir / "EmailAutomationBot_MSI_Setup.bat"
    with open(batch_path, 'w', encoding='ascii') as f:
        f.write(batch_content)
    
    # Get file sizes
    zip_size = msi_zip_path.stat().st_size / (1024 * 1024)  # MB
    bat_size = batch_path.stat().st_size / 1024  # KB
    
    print("\n" + "=" * 50)
    print("🎉 MSI-style installer files created:")
    print(f"   - EmailBot_MSI_Package.zip ({zip_size:.1f} MB)")
    print(f"   - EmailAutomationBot_MSI_Setup.bat ({bat_size:.1f} KB)")
    print("\n📋 Package Information:")
    print(f"   Product Code: {product_code}")
    print(f"   Upgrade Code: {upgrade_code}")
    print(f"   Version: {version}")
    print("\n🎉 MSI-style installer is ready for distribution!")
    print("   Run EmailAutomationBot_MSI_Setup.bat to install")
    
    return True

if __name__ == "__main__":
    try:
        success = create_msi_installer()
        if success:
            print("\n✅ MSI-style installer created successfully!")
        else:
            print("\n❌ Failed to create MSI-style installer")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)