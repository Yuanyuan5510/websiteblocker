#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网站访问限制工具 - 打包配置文件
用于cx_Freeze打包程序为可执行文件
"""

import os
import sys
import json
from cx_Freeze import setup, Executable

# 基本信息
NAME = "网站访问限制工具"
VERSION = "2.9"
DESCRIPTION = "一个简单高效的网站访问限制工具"
AUTHOR = "Administrator"

# 获取当前目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 判断是否为Windows系统
if sys.platform == 'win32':
    base = "Win32GUI"  # 使用GUI模式，不显示控制台
    # 添加Windows特定的包含项以确保C++库兼容性
    os.environ['PATH'] = os.path.join(sys.base_exec_prefix, 'Lib', 'site-packages', 'cx_Freeze', 'bases') + ';' + os.environ['PATH']
else:
    base = None

# 需要包含的文件
# 包含生成的应用图标，使用绝对路径确保cx_Freeze能找到文件
icon_path = os.path.join(BASE_DIR, "app_icon.ico")

# 检查配置文件是否存在
config_path = os.path.join(BASE_DIR, "config.json")
if not os.path.exists(config_path):
    # 如果配置文件不存在，创建一个默认的
    default_config = {
        "blocked_websites": [],
        "log_level": "INFO",
        "auto_backup": True
    }
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=4)

# 包含所有必需的文件
include_files = [
    icon_path,
    config_path,
    # 添加其他可能需要的文件
]

# 需要包含的包
include_packages = [
    "tkinter",
    "tkinter.ttk",
    "tkinter.messagebox",
    "tkinter.simpledialog",
    # 确保包含所有必要的标准库
    "os",
    "sys",
    "json",
    "shutil",
    "re",
    "ctypes",
    "logging",
    "platform",
    "time",
    "subprocess",
    "socket",
    "signal",
    "datetime",
    "atexit",
    "math"
]

# 打包配置
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    options={
        "build_exe": {
            "include_files": include_files,
            "packages": include_packages,
            "excludes": ["tkinter.test", "unittest", "email", "http", "xml", "pydoc", "doctest"],
            "optimize": 2,
            "build_exe": os.path.join(BASE_DIR, "dist"),
            "include_msvcr": True,  # 包含Microsoft Visual C++运行时库
            "zip_include_packages": "*",
            "zip_exclude_packages": "",
        }
    },
    executables=[
        # 主程序可执行文件
        Executable(
            script="website_blocker_ui.py",
            base=base,
            target_name=NAME + ".exe",
            shortcut_name=NAME,
            shortcut_dir="DesktopFolder",
            icon=icon_path
        )
    ]
)