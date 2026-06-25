; 网站访问限制工具安装脚本
; Inno Setup Script for Website Blocker Tool

#define AppName "网站访问限制工具"

[Setup]
; 基本信息
AppName=网站访问限制工具
AppVerName=网站访问限制工具 2.9
AppVersion=2.9
AppPublisher=Administrator
AppPublisherURL=https://websiteblocker-zh.wangstation.ddns-ip.net/
AppSupportURL=https://websiteblocker-zh.wangstation.ddns-ip.net/
AppUpdatesURL=https://websiteblocker-zh.wangstation.ddns-ip.net/

; 安装目录设置
DefaultDirName={autopf}\\WebsiteBlocker
DefaultGroupName=WebsiteBlocker
OutputBaseFilename=WebsiteBlocker_Setup_2.9
OutputDir=Output

; 安装程序设置
Compression=lzma2/ultra64
SolidCompression=yes
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\\app_icon.ico

; 安装模式
PrivilegesRequired=admin

; 其他设置
WizardStyle=modern
DisableProgramGroupPage=no
AllowNoIcons=no
DirExistsWarning=yes
CreateUninstallRegKey=yes

[Languages]
Name: "ChineseSimplified"; MessagesFile: "compiler:\Languages\ChineseSimplified.isl"
Name: "English"; MessagesFile: "compiler:\Languages\EnglishBritish.isl"
Name: "French"; MessagesFile: "compiler:\Languages\French.isl"
Name: "Russian"; MessagesFile: "compiler:\Languages\Russian.isl"

[Files]
; 主程序文件
Source: "dist\\网站访问限制工具.exe"; DestDir: "{app}"; Flags: ignoreversion

; 图标文件
Source: "dist\\app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

; 配置文件（如果存在）
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion

; 依赖库目录
Source: "dist\\lib\\*"; DestDir: "{app}\\lib"; Flags: ignoreversion recursesubdirs createallsubdirs

; 共享目录
Source: "dist\\share\\*"; DestDir: "{app}\\share"; Flags: ignoreversion recursesubdirs createallsubdirs

; 其他依赖文件
Source: "dist\\python313.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\\frozen_application_license.txt"; DestDir: "{app}"; Flags: ignoreversion

; C++ 运行时库文件
Source: "dist\\*.dll"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 桌面快捷方式
Name: "{autodesktop}\\{#AppName}"; Filename: "{app}\\网站访问限制工具.exe"; WorkingDir: "{app}"; IconFilename: "{app}\\app_icon.ico"; Comment: "网站访问限制工具"

; 开始菜单快捷方式
Name: "{group}\\{#AppName}"; Filename: "{app}\\网站访问限制工具.exe"; WorkingDir: "{app}"; IconFilename: "{app}\\app_icon.ico"; Comment: "网站访问限制工具"
Name: "{group}\\卸载 {#AppName}"; Filename: "{uninstallexe}"; Comment: "卸载网站访问限制工具"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式"; Flags: checkedonce
Name: "startmenuicon"; Description: "创建开始菜单快捷方式"; GroupDescription: "快捷方式"; Flags: checkedonce

[Run]
; 安装完成后运行程序
Filename: "{app}\\网站访问限制工具.exe"; Description: "运行网站访问限制工具"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; 卸载前关闭正在运行的程序
Filename: "taskkill.exe"; Parameters: "/f /im 网站访问限制工具.exe"; Flags: runhidden

[UninstallDelete]
; 卸载时删除所有文件和目录
Type: filesandordirs; Name: "{app}"

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