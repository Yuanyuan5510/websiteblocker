# 网站访问限制工具 v3.9

## 项目概述
这是一个基于Python的网站访问限制工具，通过修改系统hosts文件来实现网站访问控制。

## 技术栈
- Python 3.9+
- PyQt6 (用于用户界面)
- JSON (配置文件)
- Hosts文件操作

## 功能特性
- 阻止/解除阻止网站访问
- 批量管理阻止网站
- 配置模板功能
- 管理员权限自动请求
- 配置文件备份与恢复
- 完善的错误处理机制
- 跨平台支持 (Windows, macOS, Linux)

## 安装依赖
```bash
pip install -r requirements.txt
```

## 运行程序
```bash
python main.py
```

## 核心模块
- `main.py` - 程序主入口
- `website_blocker_ui.py` - 主用户界面
- `config_manager.py` - 配置文件管理
- `website_blocker.py` - 核心功能实现
- `error_handler.py` - 错误处理机制
- `data_exchange.py` - 数据交换模块
- `logging_config.py` - 日志配置

# 网站访问限制工具 3.9 版本功能系统性汇总

## 1. 项目概述

网站访问限制工具是一款基于Python和PyQt6开发的桌面应用程序，用于通过修改系统hosts文件来限制对特定网站的访问。该工具提供了直观的用户界面，支持批量网站管理、网站模板、配置导入导出等功能，适用于个人时间管理、企业网络管理等场景。

## 2. 项目结构

```
3.9/                      # 版本主目录
├── website_blocker_ui.py # 主界面文件
├── website_blocker.py    # 核心功能实现
├── config_manager.py     # 配置管理模块
├── data_exchange.py      # 数据导入导出模块
├── logging_config.py     # 日志配置模块
├── error_handler.py      # 错误处理模块
├── website_blocker_config.json # 应用配置文件
├── website_blocker.iss   # Inno Setup安装脚本
├── setup.py              # cx_Freeze打包配置
└── app_icon.ico          # 应用图标
```

## 3. 核心功能模块

### 3.1 网站阻止核心功能 (website_blocker.py)

**主要功能**：
- 系统hosts文件操作与管理
- 网站阻止/解除阻止功能
- 管理员权限检查与申请
- hosts文件备份与恢复
- DNS缓存刷新

**技术实现**：
```python
class WebsiteBlocker:
    def __init__(self):
        # 初始化hosts文件路径和备份机制
        # 实现权限检查和申请逻辑
    
    def block_websites(self, websites):
        # 实现网站阻止逻辑，修改hosts文件
    
    def unblock_websites(self, websites):
        # 实现网站解除阻止逻辑
    
    def refresh_dns_cache(self):
        # 实现DNS缓存刷新功能
    
    def backup_hosts(self):
        # 备份当前hosts文件
    
    def restore_hosts(self, backup_path):
        # 恢复hosts文件
```

### 3.2 用户界面模块 (website_blocker_ui.py)

**主要功能**：
- 基于PyQt6的现代化桌面界面
- 网站列表管理（添加、删除、批量操作）
- 网站模板选择与应用
- 配置设置界面
- 版本检查功能

**技术实现**：
- 使用PyQt6.QtWidgets构建界面组件
- 采用信号槽机制处理用户交互
- 实现多线程版本检查，避免界面卡顿
- 支持主题切换（浅色/深色模式）

### 3.3 配置管理模块 (config_manager.py)

**主要功能**：
- 应用配置的加载与保存
- 网站模板管理
- 配置验证与完整性检查
- 配置版本迁移支持

**技术实现**：
```python
class ConfigManager:
    def __init__(self, config_path):
        # 初始化配置路径和默认配置
    
    def load_config(self):
        # 加载配置文件
    
    def save_config(self):
        # 保存配置到文件
    
    def get_website_template(self, template_name):
        # 获取指定名称的网站模板
    
    def add_website_template(self, template_name, websites):
        # 添加新的网站模板
```

### 3.4 数据交换模块 (data_exchange.py)

**主要功能**：
- 配置文件的导入导出
- 数据格式验证
- 旧版本配置迁移

**技术实现**：
- 支持JSON格式的配置导入导出
- 实现数据验证逻辑，确保导入的配置格式正确
- 提供版本迁移功能，支持从旧版本平滑升级

### 3.5 日志系统 (logging_config.py)

**主要功能**：
- 文件和控制台日志记录
- 日志级别控制
- 日志文件自动滚动（10MB/个，最多保存5个）

**技术实现**：
- 使用Python标准logging模块
- 配置RotatingFileHandler实现日志滚动
- 支持DEBUG、INFO、WARNING、ERROR、CRITICAL级别

### 3.6 错误处理模块 (error_handler.py)

**主要功能**：
- 统一的错误类型定义
- 错误日志记录
- 错误回调机制
- 用户友好的错误提示

**技术实现**：
```python
class ErrorType(Enum):
    PERMISSION_ERROR = "权限错误"
    FILE_OPERATION_ERROR = "文件操作错误"
    CONFIG_ERROR = "配置错误"
    # 其他错误类型

class ErrorHandler:
    def handle_error(self, error_info):
        # 记录错误日志
        # 调用错误回调
        # 返回格式化的错误信息
```

## 4. 功能特性详细说明

### 4.1 网站阻止功能

- **核心机制**：通过将目标网站域名映射到127.0.0.1或0.0.0.0实现访问阻止
- **操作方式**：
  - 手动添加单个网站
  - 从模板中批量添加网站
  - 支持批量阻止/解除阻止
- **即时生效**：修改hosts文件后自动刷新DNS缓存

### 4.2 网站模板管理

预设模板分类：
- 社交媒体 (social_media)：Facebook, Twitter, Instagram, LinkedIn等
- 新闻网站 (news)：BBC, CNN, 纽约时报等
- 娱乐网站 (entertainment)：Netflix, Hulu, Disney+等
- 视频网站 (video)：YouTube, Bilibili, 爱奇艺等
- 游戏网站 (game)：Steam, Origin, Battle.net等
- 购物网站 (shopping)：Amazon, eBay, 淘宝等
- 其他网站 (other)：Reddit, Quora, StackOverflow等

### 4.3 配置功能

- **常规设置**：
  - 自动启动 (auto_start)
  - 阻止时通知 (notify_blocked)
  - 退出时自动清除 (auto_clear_on_exit)
- **模板设置**：
  - 阻止所有模板 (block_all_templates)
  - 自定义模板管理
- **备份设置**：
  - 自动备份 (enabled)
  - 备份间隔 (interval_days)
  - 最大备份数 (max_backups)
- **UI设置**：
  - 主题 (theme)
  - 窗口大小 (window_size)
  - 工具栏显示 (show_toolbar)

### 4.4 数据交换功能

- **配置导入**：支持导入JSON格式的配置文件
- **配置导出**：将当前配置导出为JSON文件
- **数据验证**：确保导入的配置格式正确、数据有效
- **版本兼容**：支持从旧版本配置文件迁移到当前版本

### 4.5 系统集成

- **权限管理**：自动检查并申请管理员权限
- **通知系统**：网站被阻止时的通知提示
- **自动启动**：支持设置为系统启动项

## 5. 技术实现细节

### 5.1 开发环境与依赖

- **开发语言**：Python 3.13
- **主要依赖**：
  - PyQt6：UI界面开发
  - cx_Freeze：应用打包
  - Inno Setup：安装程序制作
- **系统依赖**：
  - Windows操作系统
  - Microsoft Visual C++ 运行时库

### 5.2 核心技术机制

1. **Hosts文件修改**：
   - 路径：C:\Windows\System32\drivers\etc\hosts
   - 原理：添加"127.0.0.1 domain.com"条目实现阻止

2. **管理员权限获取**：
   - 使用ctypes.windll.shell32.IsUserAnAdmin()检查权限
   - 通过ctypes.windll.shell32.ShellExecuteW()重新启动获取权限

3. **DNS缓存刷新**：
   - 执行命令：ipconfig /flushdns
   - 确保修改后的hosts文件立即生效

4. **配置持久化**：
   - JSON格式存储配置
   - 支持自动备份和恢复

### 5.3 打包与部署

**打包流程**：
1. 使用cx_Freeze将Python代码打包为可执行文件
2. 配置setup.py设置依赖、图标和其他资源
3. 支持数字签名功能，确保应用安全性

**安装程序**：
- 使用Inno Setup制作Windows安装程序
- 支持管理员权限安装
- 自动创建桌面和开始菜单快捷方式
- 完整的卸载支持

**安装设置**：
```ini
[Setup]
PrivilegesRequired=admin
DefaultDirName={autopf}\WebsiteBlocker
OutputBaseFilename=WebsiteBlocker_Setup_3.9
```

## 6. 配置文件详解

### 6.1 主配置文件 (website_blocker_config.json)

```json
{
  "version": "3.9",
  "general": {
    "auto_start": false,
    "notify_blocked": true,
    "block_all_templates": false
  },
  "website_templates": {
    "social_media": ["facebook.com", "twitter.com", ...],
    "news": ["bbc.com", "cnn.com", ...],
    // 其他模板
  },
  "schedule": {
    "enabled": false,
    "time_ranges": []
  },
  "backup": {
    "enabled": true,
    "interval_days": 7,
    "max_backups": 10
  },
  "ui_settings": {
    "theme": "light",
    "window_size": [800, 600],
    "splitter_position": 300,
    "show_toolbar": true
  },
  "logging": {
    "level": "INFO",
    "enabled": true,
    "file_logging": true,
    "console_logging": true
  }
}
```

### 6.2 安装脚本配置 (website_blocker.iss)

- **基本信息**：应用名称、版本、发布者
- **安装目录**：默认C:\Program Files\WebsiteBlocker
- **输出设置**：安装程序名称、输出目录
- **安装选项**：管理员权限、压缩方式、图标等
- **文件部署**：主程序、依赖库、配置文件等

### 6.3 打包配置 (setup.py)

- **应用信息**：名称、版本、描述、作者
- **依赖配置**：包含的包、文件和资源
- **构建选项**：优化级别、压缩方式
- **可执行文件设置**：入口点、图标、快捷方式
- **签名支持**：数字签名配置和命令

## 7. 运行与使用

### 7.1 运行要求

- **操作系统**：Windows 7/8/10/11
- **权限要求**：必须以管理员身份运行
- **硬件要求**：最低2GB RAM，100MB磁盘空间

### 7.2 运行流程

1. 双击桌面快捷方式或开始菜单中的应用图标
2. 系统提示时，点击"是"以管理员权限运行
3. 应用启动，加载当前配置
4. 在界面中添加要阻止的网站或选择模板
5. 点击"应用"按钮使设置生效

### 7.3 常见操作

- **添加网站**：在输入框中输入域名，点击"添加"
- **批量操作**：选择多个网站，点击"批量阻止"或"批量解除"
- **使用模板**：从模板下拉菜单中选择分类，点击"应用模板"
- **导出配置**：点击"文件"→"导出配置"，选择保存位置
- **导入配置**：点击"文件"→"导入配置"，选择配置文件

## 8. 维护与支持

### 8.1 日志管理

- **日志文件位置**：用户数据目录下的WebsiteBlocker.log
- **日志内容**：操作记录、错误信息、调试信息
- **日志滚动**：每个日志文件最大10MB，最多保存5个历史日志

### 8.2 错误处理

常见错误类型及解决方法：
- **权限错误**：确保以管理员身份运行
- **文件操作错误**：检查hosts文件是否被其他程序占用
- **配置错误**：尝试重置配置或重新安装

### 8.3 卸载与重装

- **卸载**：通过控制面板或开始菜单中的卸载快捷方式
- **重装**：下载最新安装程序，以管理员身份运行并按照向导操作

## 9. 版本特性与更新

### 9.1 3.9版本新增功能

- 优化了网站模板管理界面
- 改进了配置导入导出功能，支持更多数据格式
- 增强了日志系统，提供更详细的操作记录
- 完善了错误处理机制，提供更友好的用户提示
- 支持数字签名功能，提高应用安全性
- 更新了依赖库版本，提高稳定性

### 9.2 技术改进

- 代码结构优化，提高可维护性
- 性能优化，减少资源占用
- 安全性增强，防止潜在的安全漏洞
- 兼容性改进，支持最新的Windows系统版本

## 10. 后续版本开发建议

### 10.1 功能增强

- **定时功能**：支持设定时间段自动启用/禁用网站阻止
- **多用户支持**：为不同用户提供独立的阻止规则
- **白名单功能**：允许访问特定网站，即使在全局阻止模式下
- **远程管理**：支持通过网络远程管理阻止规则
- **统计功能**：提供网站访问统计和报告

### 10.2 技术改进

- **跨平台支持**：扩展到macOS和Linux系统
- **模块化设计**：进一步优化代码结构，提高可扩展性
- **性能优化**：减少内存占用和CPU使用率
- **安全性增强**：实现更严格的权限控制和数据加密

### 10.3 用户体验

- **界面美化**：采用现代UI设计，提供更好的视觉体验
- **操作简化**：优化工作流程，减少操作步骤
- **帮助系统**：提供详细的使用说明和常见问题解答
- **反馈机制**：添加用户反馈功能，收集改进建议

---

**报告生成日期**：2025年12月14日
**报告版本**：1.0
**适用版本**：网站访问限制工具 3.9