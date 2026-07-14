# -*- coding: utf-8 -*-
"""
日志配置模块
负责统一管理整个应用的日志记录
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime


def get_user_data_dir():
    """获取用户数据目录（兼容打包环境）"""
    # 优先使用环境变量（Windows）
    if os.environ.get('APPDATA'):
        return os.path.join(os.environ['APPDATA'], 'WebsiteBlocker')

    # 回退到platformdirs
    try:
        from platformdirs import user_data_dir
        return user_data_dir("WebsiteBlocker")
    except ImportError:
        # 最终回退：使用用户主目录
        if sys.platform == 'win32':
            return os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Roaming', 'WebsiteBlocker', 'log')
        else:
            return os.path.join(os.path.expanduser('~'), '.websiteblocker')


class LoggingConfig:
    """日志配置类"""

    def __init__(self, app_name="WebsiteBlocker", log_level=logging.INFO):
        self.app_name = app_name
        self.log_level = log_level

        # 获取用户数据目录，用于存储日志文件
        self.data_dir = get_user_data_dir()
        os.makedirs(self.data_dir, exist_ok=True)

        # 日志文件路径
        self.log_file = os.path.join(self.data_dir, f"{app_name}.log")

        # 初始化日志配置
        self._setup_logging()

    def _setup_logging(self):
        """设置日志配置"""
        # 创建日志记录器
        logger = logging.getLogger()
        logger.setLevel(self.log_level)

        # 清除现有的处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # 创建格式化器
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )

        # 创建文件处理器（按大小滚动）
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # 添加处理器到记录器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        logging.info(f"日志系统初始化完成，日志文件路径: {self.log_file}")

    def get_log_file_path(self):
        """获取日志文件路径"""
        return self.log_file

# 初始化全局日志配置
logging_config = LoggingConfig()

# 创建根日志记录器
logger = logging.getLogger("WebsiteBlocker")