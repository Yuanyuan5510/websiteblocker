; 网站访问限制工具安装脚本
; 符合Inno Setup 6语法规范

#define AppName "网站访问限制工具"

[Setup]
; 基本信息
AppName=WebsiteBlocker
AppVerName=WebsiteBlocker 4.4
AppVersion=4.4.0
AppPublisher=wang.station
AppPublisherURL=https://websiteblocker-zh.wangstation.ddns-ip.net/
AppSupportURL=https://websiteblocker-zh.wangstation.ddns-ip.net/
AppUpdatesURL=https://websiteblocker-zh.wangstation.ddns-ip.net/

; 安装目录设置
DefaultDirName={autopf}\WebsiteBlocker
DefaultGroupName=WebsiteBlocker
OutputBaseFilename=WebsiteBlocker_Setup_4.4
OutputDir=Output

; 安装程序设置
Compression=lzma2/ultra64
SolidCompression=yes
SetupIconFile=J:\pyiadea312\限制网站访问\4.4\4.4 all\icon.ico
UninstallDisplayIcon={app}\icon.ico
LicenseFile=J:\pyiadea312\限制网站访问\4.4\dist-new-2\LICENSE.txt

; 安装模式
PrivilegesRequired=admin

; 其他设置
WizardStyle=modern
DisableProgramGroupPage=no
AllowNoIcons=no
DirExistsWarning=yes
CreateUninstallRegKey=yes

[Languages]
Name: "English"; MessagesFile: "compiler:\Languages\EnglishBritish.isl"
Name: "ChineseSimplified"; MessagesFile: "compiler:\Languages\ChineseSimplified.isl"
Name: "French"; MessagesFile: "compiler:\Languages\French.isl"
Name: "Russian"; MessagesFile: "compiler:\Languages\Russian.isl"

[Messages]
; 自定义安装消息
WelcomeLabel1=欢迎使用 [AppName] 安装向导
WelcomeLabel2=点击 "下一步" 继续或 "取消" 退出安装向导

DirPageLabel1=请选择 [AppName] 的安装目录：
DirPageLabel2=安装程序将在以下目录安装 [AppName]。要安装到其他目录，请点击 "浏览"。点击 "下一步" 继续。

SelectProgramGroupLabel1=选择程序组：
SelectProgramGroupLabel2=安装程序将在开始菜单中创建以下程序组。点击 "下一步" 继续。

ReadyLabel1=准备安装 [AppName]：
ReadyLabel2=点击 "安装" 开始安装。点击 "上一步" 更改设置。

FinishedLabel1=安装完成
FinishedLabel2=[AppName] 已成功安装到您的计算机上。

UninstallWelcomeLabel1=欢迎使用 [AppName] 卸载向导
UninstallWelcomeLabel2=点击 "下一步" 继续或 "取消" 退出卸载向导

UninstallReadyLabel1=准备卸载 [AppName]：
UninstallReadyLabel2=点击 "卸载" 开始卸载。点击 "上一步" 更改设置。

UninstallFinishedLabel1=卸载完成
UninstallFinishedLabel2=[AppName] 已成功从您的计算机上卸载。

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式"; Flags: checkedonce
Name: "startmenuicon"; Description: "创建开始菜单快捷方式"; GroupDescription: "快捷方式"; Flags: checkedonce

[Files]
; 主程序文件
Source: "J:\pyiadea312\限制网站访问\4.4\dist-new-2\websiteblocker_setup 4.4.0.exe"; DestDir: "{app}"; Flags: ignoreversion

; 图标文件
Source: "J:\pyiadea312\限制网站访问\4.4\4.4 all\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

; 许可证文件
Source: "J:\pyiadea312\限制网站访问\4.4\dist-new-2\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

; 应用程序目录
Source: "J:\pyiadea312\限制网站访问\4.4\dist-new-2\app\*"; DestDir: "{app}\app"; Flags: ignoreversion recursesubdirs createallsubdirs

; win-unpacked目录
Source: "J:\pyiadea312\限制网站访问\4.4\dist-new-2\win-unpacked\*"; DestDir: "{app}\win-unpacked"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 桌面快捷方式
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\websiteblocker_setup 4.4.0.exe"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"; Comment: "网站访问限制工具"

; 开始菜单快捷方式
Name: "{group}\{#AppName}"; Filename: "{app}\websiteblocker_setup 4.4.0.exe"; WorkingDir: "{app}"; IconFilename: "{app}\icon.ico"; Comment: "网站访问限制工具"
Name: "{group}\卸载 {#AppName}"; Filename: "{uninstallexe}"; Comment: "卸载网站访问限制工具"

[Run]
; 安装完成后运行程序
Filename: "{app}\websiteblocker_setup 4.4.0.exe"; Description: "运行网站访问限制工具"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时删除所有文件和目录
Type: filesandordirs; Name: "{app}"

[UninstallRun]
; 卸载前关闭正在运行的程序
Filename: "taskkill.exe"; Parameters: "/f /im websiteblocker_setup 4.4.0.exe"; Flags: runhidden
