#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Blocker Backend - 打包配置文件
用于cx_Freeze打包程序为可执行文件
生成无终端版本：WebsiteBlockerBackend.exe（GUI模式）

架构支持说明：
- cx_Freeze 只能编译当前 Python 解释器的架构
- 要构建 32 位版本，需使用 32 位 Python 解释器运行：python setup.py build
- 要构建 64 位版本，需使用 64 位 Python 解释器运行：python setup.py build
- 建议在虚拟环境中分别构建不同架构版本

构建命令：
- 32位：使用 32 位 Python 环境，运行 `python setup.py build`
- 64位：使用 64 位 Python 环境，运行 `python setup.py build`
"""

import os
import sys
from cx_Freeze import setup, Executable

# 基本信息
NAME = "WebsiteBlockerBackend"
VERSION = "4.5"
DESCRIPTION = "Website Blocker Backend Service"
AUTHOR = "yuanyuan5510/wang.station"

# 获取当前目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 判断是否为Windows系统
if sys.platform == 'win32':
    os.environ['PATH'] = os.path.join(sys.base_exec_prefix, 'Lib', 'site-packages', 'cx_Freeze', 'bases') + ';' + os.environ['PATH']

# 设置图标路径
icon_path = os.path.join(BASE_DIR, "app_icon.ico")
if not os.path.exists(icon_path):
    icon_path = os.path.join(BASE_DIR, "../browser/app_icon.png")
if not os.path.exists(icon_path):
    icon_path = None

# 需要包含的文件
include_files = []

# 需要包含的包
include_packages = [
    # 数据库相关 - 必须显式包含sqlite方言
    "sqlalchemy",
    "sqlalchemy.dialects",
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.pool",
    "sqlalchemy.engine",
    "sqlalchemy.orm",
    # Uvicorn相关 - 必须显式包含子模块
    "uvicorn",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.websockets",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    # FastAPI相关
    "fastapi",
    "starlette",
    "pydantic",
    "pydantic_settings",
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
            "excludes": [
                "tkinter",
                "tkinter.test",
                "unittest",
                "email",
                "xml",
                "pydoc",
                "doctest",
            ],
            "optimize": 2,
            "build_exe": os.path.join(BASE_DIR, "dist"),
            "include_msvcr": True,
            "zip_include_packages": "*",
            "zip_exclude_packages": "",
        }
    },
    executables=[
        # 无终端版本（GUI模式）
        Executable(
            script=os.path.join(BASE_DIR, "app", "main.py"),
            base="Win32GUI",
            target_name=NAME + ".exe",
            icon=icon_path
        )
    ]
)