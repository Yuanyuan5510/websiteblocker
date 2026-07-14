; ============================================================================
; Website Blocker v2.9 - Inno Setup Installation Script
; Copyright (c) 2025-2026 yuanyuan5510/wang.station
; Licensed under CC BY-NC 4.0
; ============================================================================

#define MyAppName "Website Blocker"
#define MyAppDisplayName "Website Blocker"
#define MyAppVersion "2.9"
#define MyAppPublisher "yuanyuan5510/wang.station"
#define MyAppURL "https://websiteblocker.wangstation.dpdns.org/"
#define AppGUID "{{6f1330ab-8f4f-438e-a02a-c8453d10ff1f}}"

; ============================================================================
; [Setup] - Basic Configuration
; ============================================================================
[Setup]
AppId={#AppGUID}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (c) 2025-2026 {#MyAppPublisher}

DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\Website Blocker.exe
UninstallDisplayName={#MyAppName}

OutputDir=Output
OutputBaseFilename=WebsiteBlocker_Setup_v{#MyAppVersion}
SetupIconFile=app_icon.ico
LicenseFile=LICENSE.txt

; Compression Settings
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=4

; Permissions
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; UI Settings
WizardStyle=modern
WindowVisible=yes
WindowShowCaption=yes
WindowResizable=no
DisableProgramGroupPage=yes
AllowNoIcons=yes

; Signature Settings (Configure in Inno Setup Compiler)
SignTool=SignTool
SignedUninstaller=yes

; ============================================================================
; [Languages] - Multi-language Support
; ============================================================================
[Languages]
Name: "ChineseSimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "English"; MessagesFile: "compiler:Languages\EnglishBritish.isl"

; ============================================================================
; [Messages] - Custom Messages
; ============================================================================
[Messages]
ChineseSimplified.WelcomeLabel1=Welcome to {#MyAppDisplayName} Setup Wizard
ChineseSimplified.WelcomeLabel2=This program will install {#MyAppDisplayName} {#MyAppVersion} on your computer.%n%nClick Next to continue or Cancel to exit.

English.WelcomeLabel1=Welcome to {#MyAppDisplayName} Setup Wizard
English.WelcomeLabel2=This program will install {#MyAppDisplayName} {#MyAppVersion} on your computer.%n%nClick Next to continue or Cancel to exit.

; ============================================================================
; [CustomMessages] - Custom Message Variables
; ============================================================================
[CustomMessages]
ChineseSimplified.AppDesc={#MyAppDisplayName}
ChineseSimplified.LaunchApp=Run {#MyAppDisplayName}

English.AppDesc={#MyAppDisplayName}
English.LaunchApp=Run {#MyAppDisplayName}

; ============================================================================
; [Tasks] - Installation Tasks
; ============================================================================
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

; ============================================================================
; [Files] - Installation Files
; ============================================================================
[Files]
; Main Executable
Source: "dist\Website Blocker.exe"; DestDir: "{app}"; Flags: ignoreversion signonce

; Icon File
Source: "dist\app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

; Configuration File
Source: "config.json"; DestDir: "{userappdata}\WebsiteBlocker"; Flags: onlyifdoesntexist ignoreversion

; Library Directory
Source: "dist\lib\*"; DestDir: "{app}\lib"; Flags: ignoreversion recursesubdirs createallsubdirs

; Share Directory (Tcl Resources)
Source: "dist\share\*"; DestDir: "{app}\share"; Flags: ignoreversion recursesubdirs createallsubdirs

; Python DLL
Source: "dist\python*.dll"; DestDir: "{app}"; Flags: ignoreversion

; Other DLL files
Source: "dist\*.dll"; DestDir: "{app}"; Flags: ignoreversion

; License File
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

; ============================================================================
; [Icons] - Shortcuts
; ============================================================================
[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\Website Blocker.exe"; WorkingDir: "{app}"; Comment: "{cm:AppDesc}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; Comment: "Uninstall {#MyAppName}"

; Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\Website Blocker.exe"; WorkingDir: "{app}"; Comment: "{cm:AppDesc}"; Tasks: desktopicon

; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\Website Blocker.exe"; WorkingDir: "{app}"; Tasks: quicklaunchicon

; ============================================================================
; [Run] - Post-installation
; ============================================================================
[Run]
Filename: "{app}\Website Blocker.exe"; Description: "{cm:LaunchApp}"; Flags: nowait postinstall skipifsilent unchecked

; ============================================================================
; [Registry] - Registry Configuration
; ============================================================================
[Registry]
; Application Information
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Publisher"; ValueData: "{#MyAppPublisher}"

; Firewall Rules (Requires Admin)
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\FirewallRules"; ValueType: string; ValueName: "{#MyAppName}_In"; ValueData: "v2.10|Action=Allow|Active=TRUE|Dir=In|App={app}\Website Blocker.exe|Name={#MyAppDisplayName}|"; Flags: uninsdeletevalue
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\FirewallRules"; ValueType: string; ValueName: "{#MyAppName}_Out"; ValueData: "v2.10|Action=Allow|Active=TRUE|Dir=Out|App={app}\Website Blocker.exe|Name={#MyAppDisplayName}|"; Flags: uninsdeletevalue

; ============================================================================
; [Code] - Pascal Script
; ============================================================================
[Code]
var
  OldVersion: String;
  ErrorCode: Integer;

function InitializeSetup(): Boolean;
begin
  // Check for existing version
  if RegQueryStringValue(HKLM, 'Software\{#MyAppPublisher}\{#MyAppName}', 'Version', OldVersion) then
  begin
    if MsgBox('Version ' + OldVersion + ' is already installed. Do you want to uninstall it first?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      if RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppGUID}_is1', 'UninstallString', OldVersion) then
      begin
        OldVersion := RemoveQuotes(OldVersion);
        Exec(OldVersion, '/SILENT /NORESTART', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
      end;
    end;
  end;
  Result := True;
end;

function InitializeUninstall(): Boolean;
begin
  if MsgBox('Are you sure you want to uninstall {#MyAppName}?', mbConfirmation, MB_YESNO) = IDYES then
    Result := True
  else
    Result := False;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ConfigPath: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Ask to keep configuration
    if MsgBox('Do you want to keep your configuration files?', mbConfirmation, MB_YESNO) = IDNO then
    begin
      ConfigPath := ExpandConstant('{userappdata}\WebsiteBlocker');
      DelTree(ConfigPath, True, True, True);
    end;
  end;
end;

[UninstallDelete]
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.tmp"
Type: dirifempty; Name: "{app}\lib"
Type: dirifempty; Name: "{app}\share"
Type: dirifempty; Name: "{app}"

; ============================================================================
; [UninstallRun] - Pre-uninstall
; ============================================================================
[UninstallRun]
Filename: "taskkill.exe"; Parameters: "/f /im ""Website Blocker.exe"""; Flags: runhidden; RunOnceId: "KillApp"

; ============================================================================
; Build Instructions:
; ============================================================================
; 1. Ensure dist directory contains built executables
; 2. Configure SignTool in Inno Setup Compiler:
;    Tools -> Configure Sign Tools -> Add:
;    Name: SignTool
;    Command: "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" sign /f "cert.pfx" /p $p /tr http://timestamp.digicert.com /td sha256 /fd sha256 $f
; 3. Build with: ISCC.exe /SSignTool=password website_blocker.iss
; ============================================================================