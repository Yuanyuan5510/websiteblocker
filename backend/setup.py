#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网站访问限制工具后端 - 打包配置文件
用于cx_Freeze打包程序为可执行文件
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from cx_Freeze import setup, Executable
from cx_Freeze.command.build_exe import build_exe
import platform



# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 基本信息配置
NAME = "WebsiteBlockerBackend"
VERSION = "4.4"
DESCRIPTION = "网站访问限制工具后端服务"
AUTHOR = "wang.station"
AUTHOR_EMAIL = "wang.station@hotmail.com"
SUPPORT_URL = "https://websiteblocker-zh.wangstation.ddns-ip.net/"
COPYRIGHT = f"Copyright © {datetime.now().year} wang.station"
LICENSE = "MIT License"

# 获取当前目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 判断是否为Windows系统
if sys.platform == 'win32':
    base = "Win32GUI"  # 使用GUI模式，不显示控制台
    # 添加Windows特定的包含项以确保C++库兼容性
    os.environ['PATH'] = os.path.join(sys.base_exec_prefix, 'Lib', 'site-packages', 'cx_Freeze', 'bases') + ';' + os.environ['PATH']
else:
    base = None

# 设置图标路径 - 使用用户指定的.ico文件
icon_path = os.path.join(BASE_DIR, "../dist-new/.icon-ico/icon.ico")

# 检查图标文件是否存在，如果不存在则使用默认图标
if not os.path.exists(icon_path):
    icon_path = None
    logger.warning(f"图标文件不存在: {icon_path}，使用默认图标")
else:
    logger.info(f"使用图标文件: {icon_path}")

# 包含所有必需的文件
include_files = [
    os.path.join(BASE_DIR, "version_info_minimal.txt"),
    # 确保包含所有必要的配置文件和资源
    (os.path.join(BASE_DIR, "app"), "app"),
]

# 需要包含的包（基于FastAPI + Uvicorn）
include_packages = [
    # FastAPI相关包
    "fastapi",
    "uvicorn",
    "starlette",
    "pydantic",
    "pydantic_settings",
    "typing_extensions",
    "email_validator",
    # 数据库相关
    "sqlalchemy",
    "alembic",
    # 核心库
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
    "math",
    "asyncio",
    "contextlib",
    "pathlib",
    "uuid",
    "hashlib",
    "base64",
    # 其他依赖
    "h11",
    "httptools",
    "watchfiles",
    "websockets",
    "pytz",
]

# 简化的打包配置
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=SUPPORT_URL,
    license=LICENSE,
    options={
        "build_exe": {
            "include_files": include_files,
            "packages": include_packages,
            "excludes": [
                "tkinter", 
                "unittest", 
                "email", 
                "xml", 
                "pydoc", 
                "doctest",
            ],
            "optimize": 0,
            "build_exe": "dist",
            "include_msvcr": True,
        },
    },
    executables=[
        Executable(
            script=os.path.join(BASE_DIR, "app", "main.py"),
            base=base,
            target_name="WebsiteBlockerBackend.exe",
            icon=icon_path
        )
    ],
)
