# Website Blocker v4.4

一个强大的网站访问限制工具，提供直观的Web界面和后端API，帮助用户管理和控制对特定网站的访问。

## 功能特性

- 网站访问控制：阻止和管理访问特定网站
- 定时调度：支持Cron表达式的任务调度
- Hosts文件管理：自动化Hosts文件操作
- DNS服务器：内置DNS服务器，提供域名解析服务
- 通知系统：跨平台通知功能（Windows、macOS、Linux）
- 白名单功能：支持域名白名单设置

## 技术栈

- **前端**：React + TypeScript + Vite
- **后端**：Python + FastAPI
- **数据库**：SQLite3 + SQLAlchemy
- **调度**：APScheduler
- **通知**：plyer
- **DNS**：dnslib

## 安装和运行

### 后端安装

```bash
cd backend
pip install -r requirements.txt
pip install -e .
```

### 启动服务

```bash
website-blocker
```

## API文档

启动服务后，访问 `https://doc-websiteblocker.vercel.app/` 查看API文档。

## 许可证

Creative Commons Attribution-NonCommercial 4.0 International Public License
