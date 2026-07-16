# Website Blocker v4.5

一个强大的网站访问限制工具，提供直观的Web界面和后端API，帮助用户管理和控制对特定网站的访问。

## 功能特性

- 网站访问控制：阻止和管理访问特定网站
- 定时调度：支持Cron表达式的任务调度
- Hosts文件管理：自动化Hosts文件操作
- 通知系统：跨平台通知功能（Windows、macOS、Linux）
- 白名单功能：支持域名白名单设置（存在问题，正在修复）
- 配置迁移：支持从旧版本（v1.9-v3.9）导入配置
- 端口检测：检测端口占用情况

## 技术栈

- **前端**：React + TypeScript + Vite
- **后端**：Python + FastAPI + Uvicorn
- **数据库**：SQLite3 + SQLAlchemy
- **调度**：APScheduler
- **通知**：plyer
- **DNS**：dnslib

## 项目结构

```
4.4/
├── backend/                # 后端服务
│   ├── app/
│   │   ├── main.py         # 主入口
│   │   ├── api/            # API端点
│   │   ├── core/           # 核心模块
│   │   ├── db/             # 数据库
│   │   ├── models/         # 数据模型
│   │   └── schemas/        # 数据模式
│   ├── setup.py            # cx_Freeze打包配置
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端服务（React）
├── browser/                # Electron浏览器
└── 4.4 all/                # 集成启动器
```

## 安装和运行

### 后端安装

```bash
cd backend
pip install -r requirements.txt
pip install -e .
```

### 启动后端服务

**方式1：直接运行**
```bash
python -m app.main
```

**方式2：uvicorn命令**
```bash
uvicorn app.main:app --host 127.0.0.1 --port 16411
```

**方式3：运行打包后的exe**
```bash
# 无终端版本（后台运行）
WebsiteBlockerBackend.exe
```

### 服务信息

| 项目 | 值 |
|------|------|
| 服务地址 | http://127.0.0.1:16411 |
| 健康检查 | /health |
| API文档 | /docs |
| WebSocket | /ws |

## 打包为可执行文件

### 使用cx_Freeze打包

```bash
cd backend
pip install cx_Freeze
python setup.py build
```

### 输出文件

| 文件 | 说明 | 适用场景 |
|------|------|----------|
| WebsiteBlockerBackend.exe | 无终端版本（GUI模式） | 正常使用，后台运行 |

### 打包说明

- 打包后生成 `.exe` 文件和依赖库目录（lib/）
- 运行时会自动启动API服务
- 日志自动保存到 `%APPDATA%\WebsiteBlocker\logs\`

## API端点

### 核心API

| 端点 | 方法 | 功能 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/v1/config` | GET/PUT | 配置管理 |
| `/api/v1/domains/blocked` | GET/POST | 阻止域名管理 |
| `/api/v1/domains/whitelist` | GET/POST | 白名单管理 |
| `/api/v1/hosts` | GET | Hosts文件管理 |
| `/api/v1/schedules` | GET/POST | 调度任务管理 |
| `/api/v1/database/backup` | POST | 数据库备份 |
| `/api/v1/ports/check` | GET | 端口检测 |

### 配置迁移

```bash
# 检查是否可迁移
GET /api/v1/config/check-migration

# 执行迁移
POST /api/v1/config/migrate
```

## 配置文件路径

所有配置和数据存储在统一路径：

```
Windows: %APPDATA%\WebsiteBlocker\
├── config.json          # 旧版配置（用于迁移）
├── website_blocker.db   # SQLite数据库
├── logs\                # 日志目录
│   └── website_blocker.log  # 日志文件
└── backups\             # 数据库备份
```

## 兼容性

支持从以下版本迁移配置：
- v1.9 (1.0+)
- v2.9 (2.0+)
- v3.8 (3.0+)
- v3.9

## 许可证

GPL 3.0

## 作者

yuanyuan5510/wang.station

## 支持

- Email: wang.station@hotmail.com
- Website: https://websiteblocker.wangstation.dpdns.org/