# <img src="app_icon.ico" alt="ico" height="30em" style="vertical-align: middle;"> WebsiteBlocker 

> A Python + Node.js based website access restriction tool that blocks specified websites by modifying the system hosts file.(4.5 version)

[![GPL v3](https://img.shields.io/badge/License-GPL-v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18.0-green.svg)](https://nodejs.org/)
[![Windows](https://img.shields.io/badge/Windows-11-green.svg)](https://www.microsoft.com/windows/)
[![Vite](https://img.shields.io/badge/Vite-4.4.9-green.svg)](https://vitejs.dev/)
[![Electron](https://img.shields.io/badge/Electron-18.0.0-green.svg)](https://www.electronjs.org/)

> [🇨🇳 中文版](README.zh.md)

---

## 📖 Introduction

WebsiteBlocker is a desktop utility for managing website access, ideal for personal time management and enterprise network control. It works by mapping target domains to `127.0.0.1` or `0.0.0.0` in the hosts file.

**Key Features:**

- 🔒 Add single or multiple websites to blacklist
- 📋 Preset site templates (Social Media, Video, Games, Shopping, etc.)
- ⚙️ Import/Export configurations in JSON format
- 🕐 Auto‑cleanup modes (scheduled, delayed, workday-only)
- 🌐 Bilingual support (English/Chinese)

---

## 📂 Version Navigation

| Version | Status | Highlights |
|---------|--------|------------|
| **[v4.5](https://github.com/Yuanyuan5510/websiteblocker/tree/4.5)** | Latest | Optimized performance, improved stability, and enhanced features. |
| **[v4.4 beta](https://github.com/Yuanyuan5510/websiteblocker/tree/4.4)** | Latest Beta | New framework, API integration, bilingual UI, auto‑cleanup modes (~1.2GB) |
| **[v3.9](https://github.com/Yuanyuan5510/websiteblocker/tree/3.9)** | Stable | PyQt6 refactor, site templates, config import/export, auto DNS cache flush |
| **[v3.9.9](https://github.com/Yuanyuan5510/websiteblocker/tree/3.9)** | Beta | Fixed admin privilege dual‑window issue, QSharedMemory unique instance check |
| **[v3.7](https://github.com/Yuanyuan5510/websiteblocker/tree/3.7)** | Stable | Fully functional baseline, lightweight and reliable |
| **[v2.9](https://github.com/Yuanyuan5510/websiteblocker/tree/2.0+)** | Legacy | Full‑featured release with improved compatibility |
| **[v1.9](https://github.com/Yuanyuan5510/websiteblocker/tree/1.0+)** | Legacy | Early version with core blocking functionality |

> 💡 **Recommendation**: For latest features, use **v4.5**; for stability, **v3.9**; for lightweight usage, **v3.8**.

---

## 📥 Download Table

All releases are available on the [Releases page](https://github.com/Yuanyuan5510/websiteblocker/releases).  
For branch‑based versions, you can also download source code archives directly.

| Version | Type | Download Link |
|---------|------|---------------|
| **v4.5** | Installer + Source | [Download from Releases](https://github.com/Yuanyuan5510/websiteblocker/releases/tag/v4.5) |
| **v4.4 beta** | Installer + Source | [Download from Releases](https://github.com/Yuanyuan5510/websiteblocker/releases/tag/v4.4-beta) |
| **v3.9** | Installer + Source | [Download from Releases](https://github.com/Yuanyuan5510/websiteblocker/releases/tag/v3.9) |
| **v3.9.9** | Installer + Source | [Download from Releases](https://github.com/Yuanyuan5510/websiteblocker/releases/tag/v3.9.9) |
| **v3.7** | Source Code (branch) | [Download from Releases](https://github.com/Yuanyuan5510/websiteblocker/releases/tag/v3.7) |
| **v2.9** | Source Code (tag) | [Download from Releases](https://github.com/Yuanyuan5510/websiteblocker/releases/tag/v2.9) |
| **v1.0+** | Source Code (branch) | [Download from Releases](https://github.com/Yuanyuan5510/websiteblocker/releases/tag/版本) |


> ℹ️ **Note**: For the latest installer versions, always check the [Releases](https://github.com/Yuanyuan5510/websiteblocker/releases) page.

---

## 🚀 Quick Start

### Requirements

- Windows 10 or later
- Python 3.10+ (for source run)
- RAM: 4 GB or more

### Run from Source

```bash
git clone -b 3.9 https://github.com/Yuanyuan5510/websiteblocker.git
cd websiteblocker
pip install -r requirements.txt
python website_blocker_ui.py
```
### Run from Installer

1. Go to the [Releases page](https://github.com/Yuanyuan5510/websiteblocker/releases).
2. Download the EXE installer for your desired version.
3. Run the installer and follow the wizard.
4. Launch the program from the Start Menu or desktop shortcut.

> ⚠️ **Important**: It is recommended to run the installer **as Administrator** to ensure proper permission to modify the hosts file.

---

## 🛠️ Usage Guide

### Basic Operations

1. **Add a website**: Enter a domain in the input field and click "Add" to block it.
2. **Batch operations**: Choose a preset template to add/remove multiple sites at once.
3. **Configuration**: Export/Import JSON files to sync settings across devices.

### Auto‑Cleanup Modes

Enable auto‑cleanup to reset the hosts file automatically:

- **Scheduled**: Resets at a specified time.
- **Delayed**: Resets after a certain number of hours.
- **Workday only**: Only active during non‑working hours.

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the [GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html).

**You are free to:**
- ✅ **Adapt** the material for personal use
- ✅ **Credit** the original author
- ❌ **Not** use it for commercial purposes

For the full license text, see [LICENSE.txt](./LICENSE.txt).

---

## 📞 Contact

- Telegram Group: [https://t.me/+88bhuIPWBcQ5OTk1](https://t.me/+88bhuIPWBcQ5OTk1)
- Issue Tracker: [GitHub Issues](https://github.com/Yuanyuan5510/websiteblocker/issues)

---

> **Last Updated**: July 2026