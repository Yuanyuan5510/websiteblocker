#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Blocker - 打包配置文件
用于PyInstaller打包程序为可执行文件
"""

import os
import sys
from cx_Freeze import setup, Executable

# 基本信息
NAME = "Website Blocker (32bit)"
VERSION = "1.9"
DESCRIPTION = "一个简单高效的website blocking tool"
AUTHOR = "Administrator"

# 获取当前目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 判断是否为Windows系统
if sys.platform == 'win32':
    base = "Win32GUI"  # 使用GUI模式，不显示控制台
else:
    base = None

# 需要包含的文件
# 注意：现在两个程序都使用Python代码动态绘制图标，不再需要外部图标文件
# 这样确保了在打包过程中不需要包含额外的图标资源，简化了部署过程
include_files = []

# 打包配置
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    options={
        "build_exe": {
            "include_files": include_files,
            "packages": [],
            "excludes": ["tkinter.test", "unittest", "email", "http", "xml"],
            "optimize": 2,
            "build_exe": os.path.join(BASE_DIR, "dist")
        }
    },
    executables=[
        # 主程序可执行文件
        Executable(
            script="website_blocker_ui.py",
            base=base,
            target_name=NAME + ".exe",
            shortcut_name=NAME,
            shortcut_dir="DesktopFolder"
        ),
        # 配置管理器可执行文件
        Executable(
            script="config_manager.py",
            base=base,
            target_name="Website Blocker Config (32bit).exe",
            shortcut_name="Website Blocker Config (32bit)",
            shortcut_dir="DesktopFolder"
        )
    ]
)