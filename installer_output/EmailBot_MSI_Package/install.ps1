
# Email Automation Bot MSI-style Installer
# Product: Email Automation Bot v1.0.0
# Product Code: 3bcebcb8-b841-4384-9c42-756a8666bce2

Write-Host "Installing Email Automation Bot v1.0.0..." -ForegroundColor Green

# Installation directory
$InstallDir = "$env:ProgramFiles\EmailAutomationBot"

# Create installation directory
if (!(Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Write-Host "✓ Created installation directory: $InstallDir"
}

# Copy files
Write-Host "📁 Copying application files..."
Get-ChildItem -Path "." -Recurse | ForEach-Object {
    $relativePath = $_.FullName.Substring((Get-Location).Path.Length + 1)
    $destPath = Join-Path $InstallDir $relativePath
    
    if ($_.PSIsContainer) {
        if (!(Test-Path $destPath)) {
            New-Item -ItemType Directory -Path $destPath -Force | Out-Null
        }
    } else {
        $destDir = Split-Path $destPath -Parent
        if (!(Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        Copy-Item $_.FullName $destPath -Force
        Write-Host "  ✓ $relativePath"
    }
}

# Create desktop shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Email Automation Bot.lnk")
$Shortcut.TargetPath = "$InstallDir\EmailAutomationBot.exe"
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "Email Automation Bot"
$Shortcut.Save()
Write-Host "✓ Created desktop shortcut"

# Create Start Menu shortcut
$StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
$StartShortcut = $WshShell.CreateShortcut("$StartMenuPath\Email Automation Bot.lnk")
$StartShortcut.TargetPath = "$InstallDir\EmailAutomationBot.exe"
$StartShortcut.WorkingDirectory = $InstallDir
$StartShortcut.Description = "Email Automation Bot"
$StartShortcut.Save()
Write-Host "✓ Created Start Menu shortcut"

# Add to Add/Remove Programs
$RegPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\3bcebcb8-b841-4384-9c42-756a8666bce2"
try {
    New-Item -Path $RegPath -Force | Out-Null
    Set-ItemProperty -Path $RegPath -Name "DisplayName" -Value "Email Automation Bot"
    Set-ItemProperty -Path $RegPath -Name "DisplayVersion" -Value "1.0.0"
    Set-ItemProperty -Path $RegPath -Name "Publisher" -Value "MD JOBAYER ARAFAT"
    Set-ItemProperty -Path $RegPath -Name "InstallLocation" -Value $InstallDir
    Set-ItemProperty -Path $RegPath -Name "UninstallString" -Value "powershell.exe -ExecutionPolicy Bypass -File `"$InstallDir\uninstall.ps1`""
    Set-ItemProperty -Path $RegPath -Name "DisplayIcon" -Value "$InstallDir\EmailAutomationBot.exe"
    Set-ItemProperty -Path $RegPath -Name "NoModify" -Value 1
    Set-ItemProperty -Path $RegPath -Name "NoRepair" -Value 1
    Write-Host "✓ Registered in Add/Remove Programs"
} catch {
    Write-Host "⚠️ Could not register in Add/Remove Programs (requires admin rights)"
}

# Create uninstaller
$UninstallScript = @'
# Email Automation Bot Uninstaller
Write-Host "Uninstalling Email Automation Bot..." -ForegroundColor Yellow

$InstallDir = "$env:ProgramFiles\EmailAutomationBot"

# Remove shortcuts
Remove-Item "$env:USERPROFILE\Desktop\Email Automation Bot.lnk" -ErrorAction SilentlyContinue
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Email Automation Bot.lnk" -ErrorAction SilentlyContinue
Write-Host "✓ Removed shortcuts"

# Remove registry entry
try {
    Remove-Item "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\3bcebcb8-b841-4384-9c42-756a8666bce2" -Recurse -ErrorAction SilentlyContinue
    Write-Host "✓ Removed registry entries"
} catch {}

# Remove installation directory
if (Test-Path $InstallDir) {
    Remove-Item $InstallDir -Recurse -Force
    Write-Host "✓ Removed installation directory"
}

Write-Host "✅ Email Automation Bot has been uninstalled successfully!" -ForegroundColor Green
Read-Host "Press Enter to close"
'@

$UninstallScript | Out-File -FilePath "$InstallDir\uninstall.ps1" -Encoding UTF8

Write-Host "✅ Installation completed successfully!" -ForegroundColor Green
Write-Host "📍 Installed to: $InstallDir" -ForegroundColor Cyan
Write-Host "🖥️ Desktop shortcut created" -ForegroundColor Cyan
Write-Host "📋 Added to Start Menu" -ForegroundColor Cyan
