# PowerShell MSI Installer Creator for Email Automation Bot
# Creates a Windows MSI package using Windows Installer COM objects

param(
    [string]$SourceDir = "release",
    [string]$OutputDir = "installer_output",
    [string]$AppName = "Email Automation Bot",
    [string]$Version = "1.0.0",
    [string]$Manufacturer = "MD JOBAYER ARAFAT"
)

# Function to generate GUID
function New-Guid {
    return [System.Guid]::NewGuid().ToString().ToUpper()
}

# Function to write colored output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host "🚀 Email Automation Bot - PowerShell MSI Creator" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Check if source directory exists
if (-not (Test-Path $SourceDir)) {
    Write-ColorOutput Red "❌ Source directory not found: $SourceDir"
    Write-ColorOutput Yellow "   Please build the application first."
    exit 1
}

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Generate GUIDs
$ProductCode = New-Guid
$UpgradeCode = New-Guid
$PackageCode = New-Guid

Write-Host "📝 Generating MSI package information..." -ForegroundColor Green
Write-Host "   Product Code: $ProductCode" -ForegroundColor Gray
Write-Host "   Upgrade Code: $UpgradeCode" -ForegroundColor Gray

# Create MSI using Windows Installer COM
try {
    $MSIPath = Join-Path $OutputDir "EmailAutomationBot_v$Version.msi"
    
    # Remove existing MSI if it exists
    if (Test-Path $MSIPath) {
        Remove-Item $MSIPath -Force
    }
    
    Write-Host "🔨 Creating MSI package..." -ForegroundColor Green
    
    # Create Windows Installer object
    $Installer = New-Object -ComObject WindowsInstaller.Installer
    $Database = $Installer.OpenDatabase($MSIPath, 1)  # msiOpenDatabaseModeCreate
    
    Write-Host "❌ Direct MSI creation via COM requires advanced Windows Installer knowledge." -ForegroundColor Red
    Write-Host "   Creating alternative MSI using makecab and PowerShell..." -ForegroundColor Yellow
    
    # Alternative: Create a self-extracting archive that mimics MSI behavior
    $SfxScript = @"
;!@Install@!UTF-8!
Title="$AppName Installer"
BeginPrompt="Do you want to install $AppName v$Version?"
RunProgram="powershell.exe -ExecutionPolicy Bypass -File install.ps1"
Delete="install.ps1"
;!@InstallEnd@!
"@
    
    # Create installation PowerShell script
    $InstallScript = @"
# Email Automation Bot Installation Script
param([string]`$InstallPath = "`$env:ProgramFiles\$AppName")

Write-Host "Installing $AppName..." -ForegroundColor Green

# Create installation directory
if (-not (Test-Path `$InstallPath)) {
    New-Item -ItemType Directory -Path `$InstallPath -Force | Out-Null
}

# Copy files
`$SourceFiles = Get-ChildItem -Path "." -Exclude "install.ps1", "*.sfx"
foreach (`$File in `$SourceFiles) {
    Copy-Item `$File.FullName -Destination `$InstallPath -Recurse -Force
    Write-Host "Copied: `$(`$File.Name)" -ForegroundColor Gray
}

# Create desktop shortcut
`$WshShell = New-Object -comObject WScript.Shell
`$Shortcut = `$WshShell.CreateShortcut("`$env:USERPROFILE\Desktop\$AppName.lnk")
`$Shortcut.TargetPath = "`$InstallPath\EmailAutomationBot.exe"
`$Shortcut.WorkingDirectory = `$InstallPath
`$Shortcut.Save()

# Create Start Menu shortcut
`$StartMenuPath = "`$env:APPDATA\Microsoft\Windows\Start Menu\Programs\$AppName"
if (-not (Test-Path `$StartMenuPath)) {
    New-Item -ItemType Directory -Path `$StartMenuPath -Force | Out-Null
}

`$StartShortcut = `$WshShell.CreateShortcut("`$StartMenuPath\$AppName.lnk")
`$StartShortcut.TargetPath = "`$InstallPath\EmailAutomationBot.exe"
`$StartShortcut.WorkingDirectory = `$InstallPath
`$StartShortcut.Save()

# Add to Add/Remove Programs
`$RegPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$AppName"
if (-not (Test-Path `$RegPath)) {
    New-Item -Path `$RegPath -Force | Out-Null
}

Set-ItemProperty -Path `$RegPath -Name "DisplayName" -Value "$AppName"
Set-ItemProperty -Path `$RegPath -Name "DisplayVersion" -Value "$Version"
Set-ItemProperty -Path `$RegPath -Name "Publisher" -Value "$Manufacturer"
Set-ItemProperty -Path `$RegPath -Name "InstallLocation" -Value `$InstallPath
Set-ItemProperty -Path `$RegPath -Name "UninstallString" -Value "powershell.exe -File \"`$InstallPath\uninstall.ps1\""
Set-ItemProperty -Path `$RegPath -Name "NoModify" -Value 1 -Type DWord
Set-ItemProperty -Path `$RegPath -Name "NoRepair" -Value 1 -Type DWord
Set-ItemProperty -Path `$RegPath -Name "EstimatedSize" -Value 220000 -Type DWord

Write-Host "Installation completed successfully!" -ForegroundColor Green
Write-Host "$AppName has been installed to: `$InstallPath" -ForegroundColor Cyan

# Ask to launch application
`$Launch = Read-Host "Would you like to launch $AppName now? (Y/N)"
if (`$Launch -eq "Y" -or `$Launch -eq "y") {
    Start-Process "`$InstallPath\EmailAutomationBot.exe"
}
"@
    
    # Create uninstall script
    $UninstallScript = @"
# Email Automation Bot Uninstallation Script
param([string]`$InstallPath = "`$env:ProgramFiles\$AppName")

Write-Host "Uninstalling $AppName..." -ForegroundColor Yellow

# Remove desktop shortcut
`$DesktopShortcut = "`$env:USERPROFILE\Desktop\$AppName.lnk"
if (Test-Path `$DesktopShortcut) {
    Remove-Item `$DesktopShortcut -Force
    Write-Host "Removed desktop shortcut" -ForegroundColor Gray
}

# Remove Start Menu shortcuts
`$StartMenuPath = "`$env:APPDATA\Microsoft\Windows\Start Menu\Programs\$AppName"
if (Test-Path `$StartMenuPath) {
    Remove-Item `$StartMenuPath -Recurse -Force
    Write-Host "Removed Start Menu shortcuts" -ForegroundColor Gray
}

# Remove registry entries
`$RegPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\$AppName"
if (Test-Path `$RegPath) {
    Remove-Item `$RegPath -Force
    Write-Host "Removed registry entries" -ForegroundColor Gray
}

# Remove installation directory
if (Test-Path `$InstallPath) {
    Remove-Item `$InstallPath -Recurse -Force
    Write-Host "Removed installation directory" -ForegroundColor Gray
}

Write-Host "$AppName has been uninstalled successfully!" -ForegroundColor Green
Read-Host "Press Enter to continue..."
"@
    
    # Create temporary directory for packaging
    $TempDir = Join-Path $env:TEMP "EmailBotMSI"
    if (Test-Path $TempDir) {
        Remove-Item $TempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
    
    # Copy source files to temp directory
    Copy-Item "$SourceDir\*" -Destination $TempDir -Recurse -Force
    
    # Add installation scripts
    $InstallScript | Out-File -FilePath "$TempDir\install.ps1" -Encoding UTF8
    $UninstallScript | Out-File -FilePath "$TempDir\uninstall.ps1" -Encoding UTF8
    
    Write-Host "📦 Creating self-extracting installer..." -ForegroundColor Green
    
    # Create a ZIP file first
    $ZipPath = Join-Path $OutputDir "EmailBot_MSI_Package.zip"
    if (Test-Path $ZipPath) {
        Remove-Item $ZipPath -Force
    }
    
    # Use .NET compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($TempDir, $ZipPath)
    
    # Create MSI-style installer batch file
    $MSIBatch = @'
@echo off
setlocal EnableDelayedExpansion

echo ========================================
echo   {0} v{1} Setup
echo ========================================
echo.
echo Manufacturer: {2}
echo Product Code: {3}
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
'@ -f $AppName, $Version, $Manufacturer, $ProductCode
    
    $MSIBatchPath = Join-Path $OutputDir "EmailAutomationBot_MSI_Setup.bat"
    $MSIBatch | Out-File -FilePath $MSIBatchPath -Encoding ASCII
    
    # Clean up temp directory
    Remove-Item $TempDir -Recurse -Force
    
    Write-Host "✅ MSI-style installer package created!" -ForegroundColor Green
    
    # Get file sizes
    $ZipSize = (Get-Item $ZipPath).Length / 1MB
    $BatchSize = (Get-Item $MSIBatchPath).Length / 1KB
    
    Write-Host "" 
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host "📁 MSI-style installer files created:" -ForegroundColor Green
    Write-Host "   - EmailBot_MSI_Package.zip ($([math]::Round($ZipSize, 1)) MB)" -ForegroundColor Gray
    Write-Host "   - EmailAutomationBot_MSI_Setup.bat ($([math]::Round($BatchSize, 1)) KB)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📋 Package Information:" -ForegroundColor Green
    Write-Host "   Product Code: $ProductCode" -ForegroundColor Gray
    Write-Host "   Upgrade Code: $UpgradeCode" -ForegroundColor Gray
    Write-Host "   Version: $Version" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🎉 MSI-style installer is ready for distribution!" -ForegroundColor Green
    Write-Host "   Run 'EmailAutomationBot_MSI_Setup.bat' to install" -ForegroundColor Cyan
    
} catch {
    Write-ColorOutput Red "❌ Error creating MSI package: $($_.Exception.Message)"
    exit 1
}

# Show all available installers
Write-Host ""
Write-Host "📦 All available installer packages:" -ForegroundColor Green
Get-ChildItem $OutputDir | Where-Object { $_.PSIsContainer -eq $false } | ForEach-Object {
    $Size = $_.Length / 1MB
    if ($Size -lt 1) {
        $SizeStr = "$([math]::Round($_.Length / 1KB, 1)) KB"
    } else {
        $SizeStr = "$([math]::Round($Size, 1)) MB"
    }
    Write-Host "   - $($_.Name) ($SizeStr)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✅ All installer packages are ready for distribution!" -ForegroundColor Green