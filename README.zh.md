# <img src="app_icon.ico" alt="ico" height="30em" style="vertical-align: middle;"> WebsiteBlocker（网站拦截器）

> 一款基于 Python + PyQt6 的网站访问限制工具，通过修改系统 hosts 文件实现对特定网站的访问控制。

[![CC BY-NC 4.0](https://img.shields.io/badge/许可证-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt-6.6.0-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)

> [🇬🇧 English Version](README.md)

---

## 📖 项目简介

WebsiteBlocker 是一款用于管理网站访问权限的桌面工具，适合个人时间管理、企业网络管控等场景。其核心机制是将目标网站域名映射到 `127.0.0.1` 或 `0.0.0.0`，从而实现访问阻断。

**主要功能：**

- 🔒 单个/批量添加网站至黑名单
- 📋 预设网站模板（社交媒体、视频、游戏、购物等分类）
- ⚙️ 配置导入/导出，支持 JSON 格式
- 🕐 自动清理模式（定时清理、延时清理、工作日模式）
- 🌐 中英文双语支持

---

## 📂 版本导航

| 版本 | 状态 | 特点 |
|------|------|------|
| **[v4.4 beta](https://github.com/Yuanyuan5510/websiteblocker/tree/4.4)** | 最新测试版 | 全新框架、API 调用、双语支持、自动清理模式（约 1.2GB） |
| **[v3.9](https://github.com/Yuanyuan5510/websiteblocker/tree/3.9)** | 稳定版 | PyQt6 重构、网站模板管理、配置导入导出、DNS 缓存自动刷新 |
| **[v3.9.9](https://github.com/Yuanyuan5510/websiteblocker/tree/3.9)** | 测试版 | 修复管理员权限双窗口问题、QSharedMemory 唯一实例校验 |
| **[v3.7](https://github.com/Yuanyuan5510/websiteblocker/tree/3.7)** | 稳定版 | 功能完整的基础版本，适合轻量使用 |
| **[v2.9](https://github.com/Yuanyuan5510/websiteblocker/tree/2.0+)** | 历史版 | 全功能实现，兼容性优化 |
| **[v1.9](https://github.com/Yuanyuan5510/websiteblocker/tree/1.0+)** | 早期版本 | 具备核心拦截功能 |

> 💡 **推荐**：追求最新功能请使用 **v4.4 beta**；需要稳定体验请选择 **v3.9**；轻量使用可选 **v3.7**。

---

## 📥 下载表格

所有版本均可在 [Releases 页面](https://github.com/Yuanyuan5510/websiteblocker/releases) 获取。

| 版本 | 类型 | 下载链接 |
|------|------|----------|
| **v4.4 beta** | 安装包 + 源码 | [从 Releases 下载](https://github.com/Yuanyuan5510/websiteblocker/releases) |
| **v3.9** | 安装包 + 源码 | [从 Releases 下载](https://github.com/Yuanyuan5510/websiteblocker/releases) |
| **v3.9.9** | 安装包 + 源码 | [从 Releases 下载](https://github.com/Yuanyuan5510/websiteblocker/releases) |
| **v3.7** | 源码（分支） | [从 Releases 下载](https://github.com/Yuanyuan5510/websiteblocker/releases) |
| **v1.0+** | 源码（分支） | [从 Releases 下载](https://github.com/Yuanyuan5510/websiteblocker/releases) |
| **v2.9** | 源码（标签） | [从 Releases 下载](https://github.com/Yuanyuan5510/websiteblocker/releases) |

> ℹ️ **提示**：请前往 [Releases 页面](https://github.com/Yuanyuan5510/websiteblocker/releases) 选择您需要的版本进行下载。

---

## 🚀 快速开始

### 环境要求

- 操作系统：Windows 7 及以上
- Python 3.7+（源码运行）
- 内存：2 GB 及以上

### 从源码运行

```bash
git clone -b 3.7 https://github.com/Yuanyuan5510/websiteblocker.git
cd websiteblocker
pip install -r requirements.txt
python website_blocker_ui.py
```

### 从安装包运行

1. 前往 [Releases 页面](https://github.com/Yuanyuan5510/websiteblocker/releases) 下载对应版本的 EXE 安装包。
2. 双击运行安装程序，按向导完成安装。
3. 通过开始菜单或桌面快捷方式启动软件。

> ⚠️ **注意**：建议以**管理员身份**运行安装程序，以确保 hosts 文件修改权限正常。

---

## 🛠️ 使用说明

### 基础操作

1. **添加网站**：在输入框中输入域名，点击“添加”即可加入黑名单。
2. **批量操作**：从预设模板中选择分类，一键批量添加/解除限制。
3. **配置管理**：支持导出/导入 JSON 配置文件，方便多设备同步。

### 自动清理模式

启用自动清理后，程序可定期重置 hosts 文件，在指定时间后自动恢复访问：

- **定时清理**：在设定时间点自动解除限制。
- **延时清理**：运行 X 小时后自动解除。
- **工作日模式**：仅在工作时间外生效。

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库。
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)。
3. 提交更改 (`git commit -m '添加某个新功能'`)。
4. 推送到分支 (`git push origin feature/AmazingFeature`)。
5. 开启一个 Pull Request。

---

## 📄 许可证

本项目采用 [Creative Commons Attribution‑NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/) 进行许可。

**这意味着：**
- ✅ 您可以自由**分享**和**修改**本项目的代码
- ✅ 必须**署名**（注明原作者）
- ❌ **不得用于商业目的**

完整的许可证文本请查看本仓库的 [LICENSE.txt](./LICENSE.txt) 文件。

---

## 📞 联系方式

- Telegram 交流群：[https://t.me/+88bhuIPWBcQ5OTk1](https://t.me/+88bhuIPWBcQ5OTk1)
- Issue 追踪：[GitHub Issues](https://github.com/Yuanyuan5510/websiteblocker/issues)

---

> **最后更新**：2026 年 6 月