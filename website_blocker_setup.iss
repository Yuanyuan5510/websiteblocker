; 网站访问限制工具安装脚本
; Inno Setup 6 脚本

[Setup]
AppName=网站访问限制工具
AppVersion=3.7
AppPublisher=网站访问限制工具
AppPublisherURL=https://introduction.wangstation.ddns-ip.net
DefaultDirName={pf}\网站访问限制工具
DefaultGroupName=网站访问限制工具
OutputBaseFilename=网站访问限制工具安装程序v3.7
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
WizardStyle=modern

; 优化配置
AppCopyright=© 2025 网站访问限制工具
DisableProgramGroupPage=no
LicenseFile=dist\frozen_application_license.txt
OutputDir=Output
ChangesAssociations=no
CreateAppDir=yes
AllowNoIcons=yes
AlwaysShowDirOnReadyPage=yes
ShowLanguageDialog=no
UninstallDisplayIcon={app}\网站访问限制工具.exe
UninstallDisplayName=网站访问限制工具 v3.7
; 从主程序提取图标

[Languages]
Name: "chinese"; MessagesFile: "compiler:Languages/ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1
Name: "autostart"; Description: "开机自启动"; GroupDescription: "其他选项"; Flags: unchecked

[Files]
; 主程序文件
Source: "dist\网站访问限制工具.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\网站限制配置管理器.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\python313.dll"; DestDir: "{app}"; Flags: ignoreversion

; 库文件
Source: "dist\lib\*"; DestDir: "{app}\lib"; Flags: recursesubdirs ignoreversion
Source: "dist\share\*"; DestDir: "{app}\share"; Flags: recursesubdirs ignoreversion

; 配置文件模板
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion

; 许可证文件
Source: "dist\frozen_application_license.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\网站访问限制工具 v3.7"; Filename: "{app}\网站访问限制工具.exe"
Name: "{group}\网站限制配置管理器"; Filename: "{app}\限制网站访问限制配置管理器.exe"
Name: "{group}\卸载网站访问限制工具 v3.7"; Filename: "{uninstallexe}"
Name: "{commondesktop}\网站访问限制工具 v3.7"; Filename: "{app}\网站访问限制工具.exe"; Tasks: desktopicon
Name: "{commonstartup}\网站访问限制工具"; Filename: "{app}\网站访问限制工具.exe"; Tasks: autostart

[Run]
Filename: "{app}\网站访问限制工具.exe"; Description: "运行网站访问限制工具"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.tmp"
Type: files; Name: "{app}\config.json"
Type: dirifempty; Name: "{app}\lib"
Type: dirifempty; Name: "{app}\share"
Type: dirifempty; Name: "{app}"

[UninstallRun]
Filename: "{app}\网站访问限制工具.exe"; Parameters: "--uninstall"; Flags: runhidden

[CustomMessages]
chinese.AppName=网站访问限制工具
chinese.AppVersion=3.7

[Messages]
chinese.WelcomeLabel2=欢迎使用网站访问限制工具 v3.7 安装向导。
chinese.FinishedHeadingLabel=网站访问限制工具 v3.7 安装完成