; Email Automation Bot - Inno Setup Installer Script
; This script creates a Windows installer for the Email Automation Bot

#define MyAppName "Email Automation Bot"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "MD JOBAYER ARAFAT"
#define MyAppURL "https://github.com/jobayerarafat/Email-Automation-Bot"
#define MyAppExeName "EmailAutomationBot.exe"
#define MyAppIcon "icon.png"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{8B5A2C1D-4E3F-4A2B-9C8D-1E5F6A7B8C9D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=README.md
OutputDir=installer_output
OutputBaseFilename=EmailAutomationBot_Setup_v{#MyAppVersion}
SetupIconFile={#MyAppIcon}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "release\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "release\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "release\USER_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "release\INSTALLATION.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "release\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\User Guide"; Filename: "{app}\USER_GUIDE.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: files; Name: "{app}\*.db"
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.key"

[Code]
// Custom installation logic
function InitializeSetup(): Boolean;
begin
  Result := True;
  // Check Windows version
  if not IsWin64 then
  begin
    MsgBox('This application requires a 64-bit version of Windows.', mbError, MB_OK);
    Result := False;
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
  if MsgBox('Do you want to remove all user data including email configurations and logs?', mbConfirmation, MB_YESNO) = IDYES then
  begin
    // User data will be removed by UninstallDelete section
  end;
end;

// Post-installation message
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('Installation completed successfully!' + #13#10 + #13#10 +
           'Important Notes:' + #13#10 +
           '• The application may require internet access for email operations' + #13#10 +
           '• Your firewall may prompt for network permissions' + #13#10 +
           '• Check the User Guide for configuration instructions' + #13#10 + #13#10 +
           'Thank you for using Email Automation Bot!', mbInformation, MB_OK);
  end;
end;