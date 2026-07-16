# Website Blocker Frontend Service - 32-bit Version

## 项目概述
这是网站访问限制工具前端服务的32位版本，使用 Python + Nuitka 实现。由于 pkg 工具无法直接生成32位 Node.js 可执行文件，我们提供了 Python 的替代方案。

## 技术栈
- Python 3.8+ (32-bit)
- requests (HTTP 请求库)
- Nuitka (打包工具)
- http.server (标准库)

## 功能特性
- 提供32位前端静态文件服务
- 反向代理 API 请求到后端服务
- 支持 CORS 跨域请求
- 自动检测静态文件目录
- 支持 Nuitka 打包环境
- 轻量级部署方案

## 安装依赖

### 使用 requirements.txt 安装
```bash
pip install -r requirements-x86.txt
```

### 手动安装
```bash
pip install requests>=2.31.0
pip install nuitka>=1.8.0
```

## 运行程序

### 开发模式
```bash
cd "j:\pyiadea312\限制网站访问\4.4\frontend"
python WebsiteBlockerFrontend-x86.py
```

### 生产模式（打包后）
```bash
WebsiteBlockerFrontend-x86.exe
```

## Nuitka 打包

### 前提条件

1. **Python 3.8+ (32-bit)**
   - 下载地址: https://www.python.org/downloads/windows/
   - 选择 "Windows x86" 版本

2. **Visual Studio Build Tools** (推荐)
   - 下载地址: https://visualstudio.microsoft.com/downloads/
   - 安装 "Desktop development with C++" 组件

### 打包方法

#### 方法1: PowerShell 命令

```powershell
python -m nuitka `
    --standalone `
    --windows-console-mode=disable `
    --output-dir=dist-x86 `
    --output-filename=WebsiteBlockerFrontend-x86.exe `
    --include-package=requests `
    --include-package=urllib3 `
    --include-package=charset_normalizer `
    --include-package=idna `
    --assume-yes-for-downloads `
    --show-progress `
    --company-name="yuanyuan5510/wang.station" `
    --product-name="Website Blocker Frontend" `
    --product-version=1.1.0 `
    --file-version=1.1.0.0 `
    --file-description="Website Blocker Frontend Service - 32-bit version" `
    --copyright="Copyright (c) 2025-2026 yuanyuan5510/wang.station" `
    WebsiteBlockerFrontend-x86.py
```

#### 方法2: CMD 命令

```cmd
python -m nuitka ^
    --standalone ^
    --windows-console-mode=disable ^
    --output-dir=dist-x86 ^
    --output-filename=WebsiteBlockerFrontend-x86.exe ^
    --include-package=requests ^
    --assume-yes-for-downloads ^
    --show-progress ^
    WebsiteBlockerFrontend-x86.py
```

### 打包参数说明

| 参数 | 说明 |
|------|------|
| `--standalone` | 创建独立可执行文件，包含所有依赖 |
| `--windows-console-mode=disable` | 禁用控制台窗口（GUI 应用） |
| `--include-package` | 包含 Python 包及其依赖 |
| `--assume-yes-for-downloads` | 自动下载必要的依赖 |
| `--show-progress` | 显示打包进度 |
| `--output-dir` | 输出目录 |
| `--output-filename` | 输出文件名 |
| `--company-name` | 公司名称 |
| `--product-name` | 产品名称 |
| `--product-version` | 产品版本 |
| `--file-version` | 文件版本 |
| `--file-description` | 文件描述 |
| `--copyright` | 版权信息 |

### 打包后目录结构

#### 单文件模式 (--onefile)
```
dist-x86/
├── WebsiteBlockerFrontend-x86.exe    # 单个可执行文件
└── dist/                             # 前端静态文件（需手动复制）
    ├── assets/
    ├── index.html
    └── ...
```

#### 独立目录模式 (--standalone)
```
dist-x86/
└── WebsiteBlockerFrontend-x86.dist/
    ├── WebsiteBlockerFrontend-x86.exe  # 主程序
    ├── dist/                           # 前端静态文件
    ├── _internal/                      # Nuitka 运行时文件
    │   ├── requests/
    │   ├── urllib3/
    │   └── ...
    └── ...
```

## 技术实现细节

### 1. 路径检测机制

**Nuitka 特定调整**:
- 使用 `sys.argv[0]` 而非 `sys.executable`
  - Nuitka 打包后，`sys.executable` 可能指向 `python.exe`
  - `sys.argv[0]` 指向实际的可执行文件

**静态文件目录检测顺序**:
1. `./dist/` - 正常情况
2. `./.dist/dist/` - Nuitka 单文件模式解压目录
3. `../dist/` - 相对路径
4. 当前目录 - 兜底方案

### 2. HTTP 服务器实现

**核心类**: `FrontendHandler(SimpleHTTPRequestHandler)`

**请求处理流程**:
```python
请求 → 判断类型
├── /api/* → 反向代理到后端
└── 其他 → 提供静态文件服务
```

**支持的方法**:
- GET: 获取数据
- POST: 创建数据
- PUT: 更新数据
- DELETE: 删除数据
- PATCH: 部分更新
- OPTIONS: CORS 预检

### 3. 反向代理机制

**代理流程**:
```python
客户端请求 → FrontendHandler
→ 拦截 /api/ 请求
→ 添加 Host 头
→ 转发到后端 (http://127.0.0.1:16411)
→ 接收响应
→ 添加 CORS 头
→ 返回给客户端
```

**特性**:
- 保留原始请求头
- 支持 JSON 请求体
- 添加 CORS 支持
- 错误处理和日志记录

### 4. CORS 支持

**响应头**:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, PATCH, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400
```

## 配置文件

### 服务配置

**默认配置**:
```python
HOST = '127.0.0.1'        # 监听地址
PORT = 16410              # 前端服务端口
BACKEND_PORT = 16411      # 后端 API 端口
BACKEND_URL = "http://127.0.0.1:16411"  # 后端地址
```

### 静态文件配置

**文件结构**:
```
dist/
├── assets/
│   ├── index-CcFF7PlG.js
│   └── index-Dju6d7Nx.css
├── index.html
├── app_icon.png
└── vite.svg
```

## 与 Node.js 版本对比

| 特性 | Node.js 版本 (64位) | Python 版本 (32位) |
|------|-------------------|-------------------|
| 可执行文件 | WebsiteBlockerFrontend-x64.exe | WebsiteBlockerFrontend-x86.exe |
| 文件大小 | ~50MB | ~15MB (单文件) 或 ~20MB (独立目录) |
| 架构支持 | 64位 | 32位 |
| 启动速度 | 快 | 中等（单文件需解压） |
| 依赖管理 | 内置 | 需要打包 |
| 打包工具 | pkg | Nuitka |
| 内存占用 | ~50MB | ~30MB |
| 技术栈 | Node.js + Express | Python + http.server |

## 运行与使用

### 运行要求

- **操作系统**: Windows 7/8/10/11 (32-bit or 64-bit)
- **Python 版本**: 3.8+ (32-bit) - 仅开发时需要
- **权限要求**: 无需管理员权限
- **硬件要求**: 最低 1GB RAM, 50MB 磁盘空间

### 使用流程

1. 确保后端服务正在运行（端口 16411）
2. 双击运行 `WebsiteBlockerFrontend-x86.exe`
3. 浏览器访问 http://127.0.0.1:16410
4. 使用前端界面管理网站访问规则

### 运行日志

**启动信息**:
```
============================================================
Website Blocker Frontend Service - 32-bit version
============================================================
前端服务地址: http://127.0.0.1:16410
后端 API 地址: http://127.0.0.1:16411
静态文件目录: J:\...\dist
============================================================

检查后端服务连接...
✓ 后端服务连接正常

按 Ctrl+C 停止服务...
============================================================
```

**访问日志**:
```
[2026-07-16 12:00:00] 127.0.0.1 - "GET / HTTP/1.1" 200 -
[2026-07-16 12:00:01] 127.0.0.1 - "GET /api/domains HTTP/1.1" 200 -
```

## 常见问题

### Q1: 打包时提示找不到 requests 模块？
**A**: 确保使用32位 Python 安装 requests
```bash
# 检查 Python 版本和架构
python --version
python -c "import struct; print(struct.calcsize('P') * 8)"

# 安装 requests
pip install requests
```

### Q2: 打包后的程序启动很慢？
**A**: 使用 `--standalone` 而非 `--onefile`
- 单文件模式 (--onefile): 首次启动需要解压，启动慢
- 独立目录模式 (--standalone): 启动快，但文件多

### Q3: 静态文件找不到？
**A**: 检查以下几点
1. 确保 `dist/` 目录与可执行文件在同一目录
2. 确保 `dist/index.html` 文件存在
3. 查看启动日志中的静态文件目录路径

### Q4: API 代理失败？
**A**: 检查以下几点
1. 确保后端服务正在运行: `http://127.0.0.1:16411/api/health`
2. 检查后端服务日志是否有错误
3. 确认端口没有被其他程序占用

### Q5: 打包后体积过大？
**A**: 优化建议
1. 使用 UPX 压缩: 添加 `--windows-onefile-tempdir-spec` 参数
2. 排除不必要的模块: 使用 `--nofollow-import-to`
3. 使用单文件模式: `--onefile`

### Q6: 如何调试打包后的程序？
**A**: 启用控制台模式
```bash
python -m nuitka \
    --standalone \
    --windows-console-mode=enable \
    WebsiteBlockerFrontend-x86.py
```

## 维护与支持

### 日志管理

- **日志位置**: 控制台输出（可重定向到文件）
- **日志级别**: INFO, WARNING, ERROR
- **重定向日志**: `WebsiteBlockerFrontend-x86.exe > frontend.log 2>&1`

### 错误处理

**常见错误类型**:
- **模块导入错误**: 确保所有依赖已打包
- **路径错误**: 检查静态文件目录路径
- **端口占用**: 更改服务端口配置
- **权限错误**: 确保文件有读写权限

### 性能优化

1. **使用独立目录模式**: 提高启动速度
2. **启用压缩**: 减小文件体积
3. **预编译优化**: Nuitka 自动优化
4. **内存优化**: 使用 `--show-memory` 监控

## 部署方案

### 方案1: 单文件部署
```
分发文件:
├── WebsiteBlockerFrontend-x86.exe
└── dist/
    └── ...

优点: 文件少，便于分发
缺点: 首次启动慢
```

### 方案2: 独立目录部署
```
分发文件:
└── WebsiteBlockerFrontend-x86.dist/
    ├── WebsiteBlockerFrontend-x86.exe
    ├── dist/
    └── _internal/

优点: 启动快，稳定性高
缺点: 文件多，分发复杂
```

### 方案3: 安装程序部署
使用 Inno Setup 创建安装程序，参考 `3.9/website_blocker.iss`

## 版本信息

- **前端版本**: 1.1.0
- **Python 要求**: 3.8+ (32-bit)
- **Nuitka 版本**: 1.8.0+
- **打包时间**: 2026-07-16
- **版权**: Copyright (c) 2025-2026 yuanyuan5510/wang.station

## 相关文件

- `WebsiteBlockerFrontend-x86.py` - Python 前端服务脚本
- `requirements-x86.txt` - Python 依赖列表
- `build_x86.nuitka.bat` - 自动打包脚本
- `server.js` - Node.js 版本前端服务（64位）
- `package.json` - Node.js 项目配置

---

**文档生成日期**: 2026-07-16
**文档版本**: 1.0
**适用版本**: Website Blocker Frontend Service 1.1.0 (32-bit)