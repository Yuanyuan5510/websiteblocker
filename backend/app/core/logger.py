import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

# 定义日志级别
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}


def get_appdata_path() -> str:
    """获取统一配置路径"""
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    return os.path.join(appdata, 'WebsiteBlocker')


def get_logs_dir() -> str:
    """获取日志目录路径"""
    logs_dir = os.path.join(get_appdata_path(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


def setup_logger(
    name: str = "website_blocker",
    log_level: str = "info",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_level: 日志级别
        max_bytes: 单个日志文件最大大小
        backup_count: 日志文件备份数量
        
    Returns:
        配置好的日志记录器
    """
    # 获取统一日志目录
    log_dir = get_logs_dir()
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVELS.get(log_level.lower(), logging.INFO))
    logger.propagate = False  # 防止日志重复记录
    
    # 清除现有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 创建文件处理器
    log_file = os.path.join(log_dir, f"{name}.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# 创建默认日志记录器
logger = setup_logger()