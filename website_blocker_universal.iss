; ============================================================================
; Website Blocker 通用安装脚本模板
; 含数字签名配置 | Inno Setup 6.x 兼容
; ============================================================================
;
; 使用说明:
; 1. 修改 [定义区域] 中的版本号、路径等信息
; 2. 配置签名工具路径和证书信息
; 3. 根据实际打包结构调整 [Files] 段
; 4. 编译前确保所有源文件路径正确
;
; 作者: wang.station
; 版权所有 © 2025-2026 wang.station
; ============================================================================

; ============================================================================
; [定义区域] - 根据版本修改以下变量
; ============================================================================
#define AppName           "Website Blocker"
#define AppDisplayName    "Website Blocker"
#define AppVersion        "3.8.0"
#define AppVersionShort   "3.8"
#define AppPublisher      "yuanyuan5510/wang.station"
#define AppGUID           "{{6f1330ab-8f4f-438e-a02a-c8453d10ff1f}}"
#define AppURL            "https://websiteblocker.wangstation.dpdns.org/"
#define AppCopyright       "Copyright (c) 2025-2026 yuanyuan5510/wang.station"

; 输出配置
#define OutputDir         "Output"
#define OutputFileName    "WebsiteBlocker_Setup_" + AppVersionShort

; 源文件路径 (根据实际修改)
#define SourceDir         "dist"
#define IconFile          "app_icon.ico"
#define LicenseFile       "LICENSE.txt"
#define MainExe           "Website Blocker.exe"

; 签名配置 (建议通过命令行传入密码，不要硬编码)
#define SignToolName      "MyPFXSign"
#define TimestampURL      "http://timestamp.digicert.com"

; ============================================================================
; [Setup] - 安装程序基本配置
; ============================================================================
[Setup]
; ---------- 应用标识 ----------
AppId={#AppGUID}
AppName={#AppName}
AppVerName={#AppName} {#AppVersionShort}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
AppCopyright={#AppCopyright}

; ---------- 安装目录 ----------
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#IconFile}
UninstallDisplayName={#AppDisplayName}

; ---------- 输出设置 ----------
OutputBaseFilename={#OutputFileName}
OutputDir={#OutputDir}

; ---------- 压缩配置 ----------
Compression=lzma2/ultra64
SolidCompression=yes
LZMADictionarySize=65536
LZMANumFastBytes=273
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=4

; ---------- 图标设置 ----------
SetupIconFile={#IconFile}

; ---------- 许可证 ----------
LicenseFile={#LicenseFile}

; ---------- 权限设置 ----------
; 注意：写入防火墙规则需要管理员权限
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; ---------- 兼容性设置 ----------
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; ---------- 界面设置 ----------
WizardStyle=modern
DisableProgramGroupPage=no
AllowNoIcons=yes
DirExistsWarning=yes
CreateUninstallRegKey=yes
AlwaysShowDirOnReadyPage=yes
ShowLanguageDialog=yes
LanguageDetectionMethod=uilanguage
WindowVisible=yes
WindowShowCaption=yes
WindowResizable=no
WindowStartMaximized=no

; ---------- 签名设置 ----------
SignTool=SignTool
SignedUninstaller=yes
SignedUninstallerDir={#OutputDir}

; ============================================================================
; [Languages] - 多语言支持
; ============================================================================
[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:\Languages\ChineseSimplified.isl"
Name: "englishbritish"; MessagesFile: "compiler:\Languages\EnglishBritish.isl"
;Name: "french"; MessagesFile: "compiler:\Languages\French.isl"
;Name: "russian"; MessagesFile: "compiler:\Languages\Russian.isl"
;Name: "japanese"; MessagesFile: "compiler:\Languages\Japanese.isl"
;Name: "german"; MessagesFile: "compiler:\Languages\German.isl"

; ============================================================================
; [CustomMessages] - 自定义消息变量
; ============================================================================
[CustomMessages]
; 中文消息
chinesesimplified.AppDesc={#AppDisplayName}
chinesesimplified.LaunchApp=运行 {#AppDisplayName}
chinesesimplified.LaunchAppDescription=安装完成后启动程序
chinesesimplified.DesktopIcon=创建桌面快捷方式
chinesesimplified.DesktopIconDescription=在桌面创建程序快捷方式
chinesesimplified.QuickLaunchIcon=创建快速启动栏快捷方式
chinesesimplified.QuickLaunchIconDescription=在快速启动栏创建程序快捷方式
chinesesimplified.AutoStart=开机自动启动
chinesesimplified.AutoStartDescription=开机时自动启动程序
chinesesimplified.BackupConfig=备份现有配置文件
chinesesimplified.BackupConfigDescription=备份已存在的配置文件
chinesesimplified.SelectComponents=选择组件
chinesesimplified.MainProgram=主程序
chinesesimplified.MainProgramDescription=包含程序主文件和核心资源
chinesesimplified.ConfigFiles=配置文件
chinesesimplified.ConfigFilesDescription=包含默认配置文件
chinesesimplified.Documentation=文档文件
chinesesimplified.DocumentationDescription=使用说明和变更日志
chinesesimplified.InstallingLabel=正在安装 {#AppDisplayName}...
chinesesimplified.UninstallingLabel=正在卸载 {#AppDisplayName}...
chinesesimplified.StatusLabel=安装进度
chinesesimplified.RequiresAdmin=本程序需要管理员权限才能正常运行。
chinesesimplified.InstallingCert=正在安装数字证书...

; 英文消息
englishbritish.AppDesc={#AppDisplayName}
englishbritish.LaunchApp=Run {#AppDisplayName}
englishbritish.LaunchAppDescription=Launch the program after installation
englishbritish.DesktopIcon=Create desktop shortcut
englishbritish.DesktopIconDescription=Create a shortcut on the desktop
englishbritish.QuickLaunchIcon=Create quick launch shortcut
englishbritish.QuickLaunchIconDescription=Create a shortcut in quick launch bar
englishbritish.AutoStart=Auto start on boot
englishbritish.AutoStartDescription=Start the program automatically on boot
englishbritish.BackupConfig=Backup existing config
englishbritish.BackupConfigDescription=Backup existing configuration files
englishbritish.SelectComponents=Select components
englishbritish.MainProgram=Main program
englishbritish.MainProgramDescription=Contains main executable and core resources
englishbritish.ConfigFiles=Configuration files
englishbritish.ConfigFilesDescription=Contains default configuration files
englishbritish.Documentation=Documentation
englishbritish.DocumentationDescription=README and changelog files
englishbritish.InstallingLabel=Installing {#AppDisplayName}...
englishbritish.UninstallingLabel=Uninstalling {#AppDisplayName}...
englishbritish.StatusLabel=Installation Progress
englishbritish.RequiresAdmin=This program requires administrator privileges.
englishbritish.InstallingCert=Installing digital certificate...

; ============================================================================
; [Messages] - 自定义安装界面消息
; ============================================================================
[Messages]
chinesesimplified.WelcomeLabel1=欢迎使用 {#AppDisplayName} 安装向导
chinesesimplified.WelcomeLabel2=本程序将安装 {#AppDisplayName} {#AppVersion} 到您的计算机。%n%n点击 "下一步" 继续或 "取消" 退出安装向导。
chinesesimplified.FinishedHeadingLabel={#AppDisplayName} 安装完成
chinesesimplified.FinishedLabel=感谢您安装 {#AppDisplayName}！%n%n点击 "完成" 结束安装向导。

englishbritish.WelcomeLabel1=Welcome to {#AppDisplayName} Setup Wizard
englishbritish.WelcomeLabel2=This program will install {#AppDisplayName} {#AppVersion} on your computer.%n%nClick Next to continue or Cancel to exit.
englishbritish.FinishedHeadingLabel={#AppDisplayName} Setup Complete
englishbritish.FinishedLabel=Thank you for installing {#AppDisplayName}!%n%nClick Finish to exit.

; ============================================================================
; [Tasks] - 安装任务选项
; ============================================================================
[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "{cm:QuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1
Name: "autostart"; Description: "{cm:AutoStart}"; GroupDescription: "{cm:AutoStart}"; Flags: unchecked
Name: "backupconfig"; Description: "{cm:BackupConfig}"; GroupDescription: "{cm:BackupConfig}"; Flags: unchecked

; ============================================================================
; [Components] - 可选安装组件
; ============================================================================
[Components]
Name: "main"; Description: "{cm:MainProgram}"; Types: full compact custom; Flags: fixed
Name: "config"; Description: "{cm:ConfigFiles}"; Types: full
Name: "docs"; Description: "{cm:Documentation}"; Types: full

; ============================================================================
; [Dirs] - 创建目录
; ============================================================================
[Dirs]
Name: "{app}\logs"
Name: "{userappdata}\{#AppName}\logs"
Name: "{userappdata}\{#AppName}\config"

; ============================================================================
; [Files] - 安装文件列表
; ============================================================================
; 注意：签名文件的顺序很重要！
; 1. 先列出需要签名的文件（使用 signonce 标志）
; 2. 再列出其他文件（不要使用 signonce，避免重复签名）

; 1. 需要签名的核心文件（用户可见的入口文件）
[Files] 
Source: "{#SourceDir}\{#MainExe}"; DestDir: "{app}"; Flags: ignoreversion signonce; Components: main
Source: "{#SourceDir}\Website Blocker Config.exe"; DestDir: "{app}"; Flags: ignoreversion signonce; Components: main
Source: "{#SourceDir}\{#IconFile}"; DestDir: "{app}"; Flags: ignoreversion; Components: main

; 2. 许可证文件
Source: "{#LicenseFile}"; DestDir: "{app}"; Flags: ignoreversion; Components: main

; 3. Python DLL (根据实际Python版本修改)
Source: "{#SourceDir}\python*.dll"; DestDir: "{app}"; Flags: ignoreversion; Components: main

; 4. 依赖库目录 (不签名，避免递归签名所有文件)
Source: "{#SourceDir}\lib\*"; DestDir: "{app}\lib"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: main
Source: "{#SourceDir}\share\*"; DestDir: "{app}\share"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: main

; 5. 其他DLL文件
Source: "{#SourceDir}\*.dll"; DestDir: "{app}"; Flags: ignoreversion; Components: main

; 6. 配置文件 (首次安装时复制到用户目录)
Source: "config.json"; DestDir: "{userappdata}\{#AppName}"; Flags: onlyifdoesntexist ignoreversion; Components: config

; 7. 文档文件
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist; Components: docs
Source: "CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist; Components: docs

; 8. 证书文件（仅用于安装过程，安装后删除）
; 注意：证书密码应在编译时通过命令行传入，不要硬编码！
; Source: "certificates\wang_station.pfx"; DestDir: "{tmp}"; Flags: ignoreversion deleteafterinstall

; ============================================================================
; [Icons] - 快捷方式创建
; ============================================================================
[Icons]
; 开始菜单
Name: "{autoprograms}\{#AppDisplayName}"; Filename: "{app}\{#MainExe}"; IconFilename: "{app}\{#IconFile}"; Comment: "{#AppDisplayName} v{#AppVersion}"
Name: "{autoprograms}\{#AppDisplayName}\Configuration Tool"; Filename: "{app}\Website Blocker Config.exe"; IconFilename: "{app}\{#IconFile}"
Name: "{autoprograms}\{#AppDisplayName}\Uninstall {#AppDisplayName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\{#IconFile}"

; 桌面快捷方式
Name: "{autodesktop}\{#AppDisplayName}"; Filename: "{app}\{#MainExe}"; IconFilename: "{app}\{#IconFile}"; Tasks: desktopicon; Comment: "{#AppDisplayName} v{#AppVersion}"

; 快速启动栏
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppDisplayName}"; Filename: "{app}\{#MainExe}"; IconFilename: "{app}\{#IconFile}"; Tasks: quicklaunchicon

; 启动项
Name: "{commonstartup}\{#AppDisplayName}"; Filename: "{app}\{#MainExe}"; Tasks: autostart

; ============================================================================
; [Registry] - 注册表配置
; ============================================================================
[Registry]
; 应用程序注册信息
Root: HKLM; Subkey: "Software\{#AppPublisher}\{#AppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#AppVersion}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#AppPublisher}\{#AppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKLM; Subkey: "Software\{#AppPublisher}\{#AppName}"; ValueType: string; ValueName: "InstallDate"; ValueData: "{code:GetCurrentDate}"
Root: HKLM; Subkey: "Software\{#AppPublisher}\{#AppName}"; ValueType: string; ValueName: "Publisher"; ValueData: "{#AppPublisher}"

; 添加到防火墙白名单 (需要管理员权限)
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\FirewallRules"; ValueType: string; ValueName: "{#AppName}_In"; ValueData: "v2.10|Action=Allow|Active=TRUE|Dir=In|App={app}\{#MainExe}|Name={#AppDisplayName}|"; Flags: uninsdeletevalue
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\FirewallRules"; ValueType: string; ValueName: "{#AppName}_Out"; ValueData: "v2.10|Action=Allow|Active=TRUE|Dir=Out|App={app}\{#MainExe}|Name={#AppDisplayName}|"; Flags: uninsdeletevalue

; ============================================================================
; [Run] - 安装完成后运行
; ============================================================================
[Run]
; 安装证书（如果需要）
; 注意：密码应通过命令行传入 $p 参数
; Filename: "{sys}\certutil.exe"; Parameters: "-user -f -p $p -importPFX ""{tmp}\wang_station.pfx"""; StatusMsg: "{cm:InstallingCert}"; Flags: runhidden waituntilterminated

; 运行主程序
Filename: "{app}\{#MainExe}"; Description: "{cm:LaunchApp}"; Flags: nowait postinstall skipifsilent unchecked

; 查看使用说明
Filename: "{app}\README.md"; Description: "查看使用说明"; Flags: postinstall skipifsilent unchecked shellexec skipifdoesntexist

; ============================================================================
; [UninstallRun] - 卸载前执行的程序
; ============================================================================
[UninstallRun]
Filename: "taskkill.exe"; Parameters: "/f /im {#MainExe}"; Flags: runhidden; RunOnceId: "KillApp"

; ============================================================================
; [UninstallDelete] - 卸载时删除文件
; ============================================================================
[UninstallDelete]
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.tmp"
Type: dirifempty; Name: "{app}\lib"
Type: dirifempty; Name: "{app}\share"
Type: dirifempty; Name: "{app}\logs"
Type: dirifempty; Name: "{app}"

; ============================================================================
; [Code] - Pascal脚本代码
; ============================================================================
[Code] 
var
  SetupLoggingFile: string;
  InstallResult: Integer;

// 获取当前日期
function GetCurrentDate(Param: string): string;
begin
  Result := GetDateTimeString('yyyy-mm-dd', '-', ':');
end;

// 写入日志
procedure WriteLog(Msg: string);
var
  LogFile: TStringList;
  TimeStr: string;
begin
  if SetupLoggingFile = '' then
    Exit;
  try
    LogFile := TStringList.Create;
    try
      if FileExists(SetupLoggingFile) then
        LogFile.LoadFromFile(SetupLoggingFile);
      TimeStr := GetDateTimeString('yyyy-mm-dd hh:nn:ss', '-', ':');
      LogFile.Add('[' + TimeStr + '] ' + Msg);
      LogFile.SaveToFile(SetupLoggingFile);
    finally
      LogFile.Free;
    end;
  except
  end;
end;

// 初始化安装向导
procedure InitializeWizard;
begin
  SetupLoggingFile := ExpandConstant('{tmp}') + '\{#AppName}_Install_{#AppVersion}_' + GetDateTimeString('yyyy-mm-dd_hh-nn-ss', '-', ':') + '.log';
  
  if FileExists(SetupLoggingFile) then
    DeleteFile(SetupLoggingFile);
  
  WriteLog('========================================');
  WriteLog('{#AppDisplayName} 安装日志');
  WriteLog('版本: {#AppVersion}');
  WriteLog('安装时间: ' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', '-', ':'));
  WriteLog('========================================');
  WriteLog('');
end;

// 安装前检查
function InitializeSetup(): Boolean;
var
  OldVersion: String;
  ErrorCode: Integer;
begin
  WriteLog('安装程序初始化');
  
  // 检查是否已安装旧版本
  if RegQueryStringValue(HKLM, 'Software\{#AppPublisher}\{#AppName}', 'Version', OldVersion) then
  begin
    WriteLog('检测到已安装版本: ' + OldVersion);
    if MsgBox('检测到已安装版本 ' + OldVersion + '，是否先卸载旧版本？', mbConfirmation, MB_YESNO) = IDYES then
    begin
      if RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppGUID}_is1', 'UninstallString', OldVersion) then
      begin
        OldVersion := RemoveQuotes(OldVersion);
        WriteLog('正在卸载旧版本...');
        Exec(OldVersion, '/SILENT /NORESTART', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode);
      end;
    end;
  end;
  
  Result := True;
end;

// 安装前准备
function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  WriteLog('开始安装前检查...');
  
  // 检查磁盘空间（至少需要 200MB）
  // 实际项目中可以使用 GetSpaceOnDisk 函数
  
  WriteLog('安装前检查完成，开始安装');
end;

// 写入安装信息文件
procedure WriteInstallInfo;
var
  InfoFile: TStringList;
begin
  InfoFile := TStringList.Create;
  try
    InfoFile.Add('[InstallInfo]');
    InfoFile.Add('Version={#AppVersion}');
    InfoFile.Add('InstallDate=' + GetDateTimeString('yyyy-mm-dd', '-', ':'));
    InfoFile.Add('InstallPath=' + ExpandConstant('{app}'));
    InfoFile.Add('Publisher={#AppPublisher}');
    InfoFile.SaveToFile(ExpandConstant('{app}\install_info.ini'));
  finally
    InfoFile.Free;
  end;
  WriteLog('安装信息文件已写入');
end;

// 安装完成处理
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    WriteLog('安装步骤: ssPostInstall');
    WriteLog('安装路径: ' + ExpandConstant('{app}'));
    
    // 创建用户数据目录
    if not DirExists(ExpandConstant('{userappdata}\{#AppName}\logs')) then
      CreateDir(ExpandConstant('{userappdata}\{#AppName}\logs'));
    
    if not DirExists(ExpandConstant('{userappdata}\{#AppName}\config')) then
      CreateDir(ExpandConstant('{userappdata}\{#AppName}\config'));
    
    // 写入安装信息文件
    WriteInstallInfo;
    
    WriteLog('安装完成');
    InstallResult := 0;
  end;
end;

// 安装程序退出处理
procedure DeinitializeSetup;
begin
  WriteLog('安装程序退出');
  WriteLog('');
  
  // 如果安装成功，将日志复制到安装目录
  if InstallResult = 0 then
  begin
    if FileExists(SetupLoggingFile) then
      RenameFile(SetupLoggingFile, ExpandConstant('{app}\install.log'));
  end;
end;

// 卸载前确认
function InitializeUninstall(): Boolean;
begin
  if MsgBox('确定要卸载 {#AppDisplayName} 吗？', mbConfirmation, MB_YESNO) = IDNO then
    Result := False
  else
    Result := True;
end;

// 卸载完成处理
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ConfigPath: String;
begin
  if CurUninstallStep = usUninstall then
  begin
    WriteLog('========================================');
    WriteLog('{#AppDisplayName} 卸载日志');
    WriteLog('卸载时间: ' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', '-', ':'));
    WriteLog('卸载路径: ' + ExpandConstant('{app}'));
    WriteLog('========================================');
    WriteLog('');
    
    // 清理注册表
    WriteLog('清理注册表项');
    RegDeleteKeyIncludingSubkeys(HKEY_LOCAL_MACHINE, 'Software\{#AppPublisher}\{#AppName}');
    
    // 清理防火墙规则
    WriteLog('清理防火墙规则');
    RegDeleteValue(HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\FirewallRules', '{#AppName}_In');
    RegDeleteValue(HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\FirewallRules', '{#AppName}_Out');
  end;
  
  if CurUninstallStep = usPostUninstall then
  begin
    // 询问是否保留配置
    if MsgBox('是否保留配置文件？', mbConfirmation, MB_YESNO) = IDNO then
    begin
      ConfigPath := ExpandConstant('{userappdata}\{#AppName}');
      if DirExists(ConfigPath) then
      begin
        DelTree(ConfigPath, True, True, True);
        WriteLog('配置目录已删除: ' + ConfigPath);
      end;
    end;
    
    WriteLog('卸载完成');
  end;
end;