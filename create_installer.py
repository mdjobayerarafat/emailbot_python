#!/usr/bin/env python3
"""
Windows Installer Creator for Email Automation Bot
This script creates a Windows installer using NSIS (Nullsoft Scriptable Install System)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_nsis_script():
    """Create NSIS installer script"""
    nsis_script = '''
; Email Automation Bot NSIS Installer Script
; Generated automatically by create_installer.py

!define APP_NAME "Email Automation Bot"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "MD JOBAYER ARAFAT"
!define APP_URL "https://github.com/jobayerarafat/Email-Automation-Bot"
!define APP_EXE "EmailAutomationBot.exe"

; Modern UI
!include "MUI2.nsh"

; General
Name "${APP_NAME}"
OutFile "EmailAutomationBot_Setup_v${APP_VERSION}.exe"
Unicode True
InstallDir "$PROGRAMFILES64\\${APP_NAME}"
InstallDirRegKey HKCU "Software\\${APP_NAME}" ""
RequestExecutionLevel user

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"

; Pages
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Version Information
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "Comments" "A powerful email automation tool"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey "LegalCopyright" "© 2024 ${APP_PUBLISHER}"
VIAddVersionKey "FileDescription" "${APP_NAME} Installer"
VIAddVersionKey "FileVersion" "${APP_VERSION}"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"

; Installer sections
Section "!${APP_NAME} (required)" SEC01
  SectionIn RO
  
  ; Set output path to the installation directory
  SetOutPath "$INSTDIR"
  
  ; Install files
  File "release\\${APP_EXE}"
  File "release\\README.md"
  File "release\\USER_GUIDE.md"
  File "release\\INSTALLATION.md"
  File "release\\requirements.txt"
  File "icon.png"
  File "LICENSE.txt"
  
  ; Store installation folder
  WriteRegStr HKCU "Software\\${APP_NAME}" "" $INSTDIR
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
  
  ; Add to Add/Remove Programs
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "UninstallString" "$INSTDIR\\Uninstall.exe"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayIcon" "$INSTDIR\\${APP_EXE}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "URLInfoAbout" "${APP_URL}"
  WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "NoRepair" 1
  
  ; Estimate size (in KB)
  WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}" "EstimatedSize" 220000
SectionEnd

Section "Desktop Shortcut" SEC02
  CreateShortcut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
SectionEnd

Section "Start Menu Shortcuts" SEC03
  CreateDirectory "$SMPROGRAMS\\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\\${APP_NAME}\\${APP_NAME}.lnk" "$INSTDIR\\${APP_EXE}"
  CreateShortcut "$SMPROGRAMS\\${APP_NAME}\\User Guide.lnk" "$INSTDIR\\USER_GUIDE.md"
  CreateShortcut "$SMPROGRAMS\\${APP_NAME}\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "Install ${APP_NAME} application files (required)"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC02} "Create a desktop shortcut for ${APP_NAME}"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC03} "Create Start Menu shortcuts for ${APP_NAME}"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller section
Section "Uninstall"
  ; Remove registry keys
  DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APP_NAME}"
  DeleteRegKey HKCU "Software\\${APP_NAME}"
  
  ; Remove files and uninstaller
  Delete "$INSTDIR\\${APP_EXE}"
  Delete "$INSTDIR\\README.md"
  Delete "$INSTDIR\\USER_GUIDE.md"
  Delete "$INSTDIR\\INSTALLATION.md"
  Delete "$INSTDIR\\requirements.txt"
  Delete "$INSTDIR\\icon.png"
  Delete "$INSTDIR\\LICENSE.txt"
  Delete "$INSTDIR\\Uninstall.exe"
  
  ; Remove user data (ask user)
  MessageBox MB_YESNO "Do you want to remove all user data including email configurations and logs?" IDNO skip_userdata
    RMDir /r "$INSTDIR\\logs"
    Delete "$INSTDIR\\*.db"
    Delete "$INSTDIR\\*.log"
    Delete "$INSTDIR\\*.key"
  skip_userdata:
  
  ; Remove shortcuts
  Delete "$DESKTOP\\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\\${APP_NAME}\\*.*"
  RMDir "$SMPROGRAMS\\${APP_NAME}"
  
  ; Remove directories
  RMDir "$INSTDIR"
SectionEnd

; Functions
Function .onInit
  ; Check if running on 64-bit Windows
  ${IfNot} ${RunningX64}
    MessageBox MB_OK "This application requires a 64-bit version of Windows."
    Abort
  ${EndIf}
FunctionEnd

Function .onInstSuccess
  MessageBox MB_OK "Installation completed successfully!$\r$\n$\r$\nImportant Notes:$\r$\n• The application may require internet access for email operations$\r$\n• Your firewall may prompt for network permissions$\r$\n• Check the User Guide for configuration instructions$\r$\n$\r$\nThank you for using Email Automation Bot!"
FunctionEnd
'''
    
    with open('installer.nsi', 'w', encoding='utf-8') as f:
        f.write(nsis_script)
    print("✅ NSIS script created: installer.nsi")

def convert_icon_to_ico():
    """Convert PNG icon to ICO format for Windows installer"""
    try:
        from PIL import Image
        
        # Open PNG and convert to ICO
        img = Image.open('icon.png')
        img.save('icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
        print("✅ Icon converted: icon.ico")
        return True
    except ImportError:
        print("⚠️  PIL not available, copying PNG as ICO")
        shutil.copy2('icon.png', 'icon.ico')
        return True
    except Exception as e:
        print(f"❌ Icon conversion failed: {e}")
        return False

def build_installer():
    """Build the installer using NSIS"""
    print("🔨 Building Windows installer...")
    
    # Check if NSIS is available
    nsis_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        "makensis.exe"  # If in PATH
    ]
    
    nsis_exe = None
    for path in nsis_paths:
        if shutil.which(path) or os.path.exists(path):
            nsis_exe = path
            break
    
    if not nsis_exe:
        print("❌ NSIS not found. Please install NSIS from https://nsis.sourceforge.io/")
        print("   After installation, run this script again.")
        return False
    
    try:
        # Run NSIS compiler
        result = subprocess.run([nsis_exe, 'installer.nsi'], 
                              capture_output=True, text=True, check=True)
        print("✅ Installer built successfully!")
        
        # Check if installer was created
        installer_file = "EmailAutomationBot_Setup_v1.0.0.exe"
        if os.path.exists(installer_file):
            file_size = os.path.getsize(installer_file) / (1024 * 1024)  # Size in MB
            print(f"📁 Installer created: {installer_file}")
            print(f"📊 File size: {file_size:.1f} MB")
            
            # Move to installer_output directory
            os.makedirs('installer_output', exist_ok=True)
            shutil.move(installer_file, f'installer_output/{installer_file}')
            print(f"📦 Installer moved to: installer_output/{installer_file}")
            
            return True
        else:
            print("❌ Installer file not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ NSIS compilation failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def create_portable_installer():
    """Create a simple portable installer using 7-Zip"""
    print("📦 Creating portable installer...")
    
    # Check if 7-Zip is available
    zip_paths = [
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
        "7z.exe"  # If in PATH
    ]
    
    zip_exe = None
    for path in zip_paths:
        if shutil.which(path) or os.path.exists(path):
            zip_exe = path
            break
    
    if not zip_exe:
        print("⚠️  7-Zip not found, creating ZIP archive with Python...")
        import zipfile
        
        os.makedirs('installer_output', exist_ok=True)
        zip_path = 'installer_output/EmailAutomationBot_Portable_v1.0.0.zip'
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add files from release folder
            for root, dirs, files in os.walk('release'):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, 'release')
                    zipf.write(file_path, arcname)
            
            # Add additional files
            zipf.write('LICENSE.txt', 'LICENSE.txt')
            zipf.write('icon.png', 'icon.png')
        
        file_size = os.path.getsize(zip_path) / (1024 * 1024)
        print(f"✅ Portable installer created: {zip_path}")
        print(f"📊 File size: {file_size:.1f} MB")
        return True
    else:
        # Use 7-Zip for better compression
        os.makedirs('installer_output', exist_ok=True)
        archive_path = 'installer_output/EmailAutomationBot_Portable_v1.0.0.7z'
        
        try:
            cmd = [zip_exe, 'a', '-t7z', '-mx=9', archive_path, 'release/*', 'LICENSE.txt', 'icon.png']
            subprocess.run(cmd, check=True, capture_output=True)
            
            file_size = os.path.getsize(archive_path) / (1024 * 1024)
            print(f"✅ Portable installer created: {archive_path}")
            print(f"📊 File size: {file_size:.1f} MB")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 7-Zip compression failed: {e}")
            return False

def main():
    print("🚀 Email Automation Bot - Windows Installer Creator")
    print("=" * 50)
    
    # Check if release folder exists
    if not os.path.exists('release/EmailAutomationBot.exe'):
        print("❌ Release folder not found. Please run build_windows.py first.")
        return False
    
    # Create installer directory
    os.makedirs('installer_output', exist_ok=True)
    
    # Convert icon
    convert_icon_to_ico()
    
    # Create NSIS script
    create_nsis_script()
    
    # Try to build NSIS installer
    nsis_success = build_installer()
    
    # Always create portable version as fallback
    portable_success = create_portable_installer()
    
    print("\n" + "=" * 50)
    if nsis_success:
        print("✅ Windows installer (.exe) created successfully!")
    else:
        print("⚠️  NSIS installer creation failed, but portable version is available.")
    
    if portable_success:
        print("✅ Portable installer created successfully!")
    
    print("\n📁 Check the 'installer_output' folder for your installers.")
    
    if nsis_success or portable_success:
        print("\n🎉 Installation packages are ready for distribution!")
        return True
    else:
        print("\n💥 Failed to create any installer packages.")
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)