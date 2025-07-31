
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
InstallDir "$PROGRAMFILES64\${APP_NAME}"
InstallDirRegKey HKCU "Software\${APP_NAME}" ""
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
  File "release\${APP_EXE}"
  File "release\README.md"
  File "release\USER_GUIDE.md"
  File "release\INSTALLATION.md"
  File "release\requirements.txt"
  File "icon.png"
  File "LICENSE.txt"
  
  ; Store installation folder
  WriteRegStr HKCU "Software\${APP_NAME}" "" $INSTDIR
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Add to Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\${APP_EXE}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "URLInfoAbout" "${APP_URL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
  
  ; Estimate size (in KB)
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "EstimatedSize" 220000
SectionEnd

Section "Desktop Shortcut" SEC02
  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
SectionEnd

Section "Start Menu Shortcuts" SEC03
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\User Guide.lnk" "$INSTDIR\USER_GUIDE.md"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
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
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
  DeleteRegKey HKCU "Software\${APP_NAME}"
  
  ; Remove files and uninstaller
  Delete "$INSTDIR\${APP_EXE}"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\USER_GUIDE.md"
  Delete "$INSTDIR\INSTALLATION.md"
  Delete "$INSTDIR\requirements.txt"
  Delete "$INSTDIR\icon.png"
  Delete "$INSTDIR\LICENSE.txt"
  Delete "$INSTDIR\Uninstall.exe"
  
  ; Remove user data (ask user)
  MessageBox MB_YESNO "Do you want to remove all user data including email configurations and logs?" IDNO skip_userdata
    RMDir /r "$INSTDIR\logs"
    Delete "$INSTDIR\*.db"
    Delete "$INSTDIR\*.log"
    Delete "$INSTDIR\*.key"
  skip_userdata:
  
  ; Remove shortcuts
  Delete "$DESKTOP\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\*.*"
  RMDir "$SMPROGRAMS\${APP_NAME}"
  
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
  MessageBox MB_OK "Installation completed successfully!$$
$$
Important Notes:$$
• The application may require internet access for email operations$$
• Your firewall may prompt for network permissions$$
• Check the User Guide for configuration instructions$$
$$
Thank you for using Email Automation Bot!"
FunctionEnd
