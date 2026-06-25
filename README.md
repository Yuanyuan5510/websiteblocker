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