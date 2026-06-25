# -*- coding: utf-8 -*-
"""
配置管理模块
负责处理应用配置的加载、保存和版本迁移，确保系统间数据传递的兼容性
"""

import os
import json
import platform
from typing import Dict, Any, List, Optional
import logging
import shutil

from logging_config import logger
from error_handler import ErrorHandler, ErrorType, ErrorInfo, error_handler
from data_exchange import data_exchange

class ConfigManager:
    """配置管理类"""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.backup_dir = os.path.join(self.config_dir, "backups")
        
        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 配置默认值
        self.default_config = {
            "version": "3.9",
            "general": {
                "auto_start": False,
                "notify_blocked": True,
                "block_all_templates": False
            },
            "version_check": {
                "enabled": True,
                "check_interval_hours": 24,  # 默认每天检查一次
                "last_check_time": 0  # 最后检查时间，Unix时间戳
            },
            "website_templates": {
                "social_media": [
                    "facebook.com",
                    "twitter.com",
                    "instagram.com",
                    "linkedin.com",
                    "weibo.com",
                    "zhihu.com",
                    "douban.com",
                    "tiktok.com",
                    "youtube.com"
                ],
                "news": [
                    "bbc.com",
                    "cnn.com",
                    "nytimes.com",
                    "foxnews.com",
                    "cnbc.com",
                    "reuters.com",
                    "bloomberg.com",
                    "wsj.com"
                ],
                "entertainment": [
                    "netflix.com",
                    "hulu.com",
                    "disneyplus.com",
                    "amazonprimevideo.com",
                    "spotify.com",
                    "pandora.com",
                    "apple.com/apple-music",
                    "soundcloud.com"
                ],
                "video": [
                    "youtube.com",
                    "bilibili.com",
                    "iqiyi.com",
                    "youku.com",
                    "tudou.com",
                    "netflix.com",
                    "hulu.com",
                    "kuaishou.com"
                ],
                "game": [
                    "steamcommunity.com",
                    "origin.com",
                    "battle.net",
                    "ubisoft.com",
                    "epicgames.com",
                    "riotgames.com",
                    "blizzard.com",
                    "nintendo.com"
                ],
                "shopping": [
                    "amazon.com",
                    "ebay.com",
                    "alibaba.com",
                    "taobao.com",
                    "jd.com",
                    "pinduoduo.com",
                    "tmall.com",
                    "aliexpress.com"
                ],
                "other": [
                    "reddit.com",
                    "quora.com",
                    "stackoverflow.com",
                    "github.com",
                    "wikipedia.org",
                    "medium.com",
                    "wordpress.com",
                    "blogger.com"
                ]
            },
            "schedule": {
                "enabled": False,
                "time_ranges": []
            },
            "backup": {
                "enabled": True,
                "interval_days": 7,
                "max_backups": 10
            },
            "ui_settings": {
                "theme": "light",
                "window_size": [800, 600],
                "splitter_position": 300,
                "show_toolbar": True
            },
            "logging": {
                "level": "INFO",
                "enabled": True,
                "file_logging": True,
                "console_logging": True
            }
        }
        
        self.config = None
        self.load_config()
        
    def _get_config_dir(self) -> str:
        """获取配置文件目录"""
        system = platform.system()
        
        if system == "Windows":
            return os.path.join(os.environ.get("APPDATA", ""), "WebsiteBlocker")
        elif system == "Darwin":  # macOS
            return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "WebsiteBlocker")
        else:  # Linux
            return os.path.join(os.path.expanduser("~"), ".websiteblocker")
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                # 使用data_exchange加载配置，处理版本迁移
                loaded_config = data_exchange.load_config(self.config_file)
                
                if loaded_config:
                    self.config = loaded_config
                    logger.info(f"配置已加载，版本: {self.config.get('version', 'unknown')}")
                    return self.config
                else:
                    logger.warning("配置加载失败，使用默认配置")
            
            # 使用默认配置
            self.config = self.default_config.copy()
            self.save_config()
            logger.info("使用默认配置")
            return self.config
            
        except Exception as e:
            error_info = ErrorInfo(
                ErrorType.CONFIG_ERROR,
                f"加载配置失败",
                original_error=e,
                details={"config_file": self.config_file}
            )
            error_handler.handle_error(error_info)
            
            # 使用默认配置作为备选方案
            self.config = self.default_config.copy()
            return self.config
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            if self.config is None:
                logger.warning("配置为空，无法保存")
                return False
            
            # 确保版本号正确
            if "version" not in self.config:
                self.config["version"] = self.default_config["version"]
            
            # 使用data_exchange保存配置，确保格式兼容性
            if data_exchange.save_config(self.config, self.config_file):
                logger.info(f"配置已保存到: {self.config_file}")
                return True
            else:
                logger.error("配置保存失败")
                return False
                
        except Exception as e:
            error_info = ErrorInfo(
                ErrorType.CONFIG_ERROR,
                f"保存配置失败",
                original_error=e,
                details={"config_file": self.config_file}
            )
            error_handler.handle_error(error_info)
            return False
    
    def backup_config(self) -> Optional[str]:
        """备份配置文件"""
        try:
            import datetime
            
            if not os.path.exists(self.config_file):
                logger.warning("配置文件不存在，无法备份")
                return None
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"config_backup_{timestamp}.json"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            shutil.copy2(self.config_file, backup_path)
            logger.info(f"配置已备份到: {backup_path}")
            
            # 清理旧备份
            self._cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            error_info = ErrorInfo(
                ErrorType.CONFIG_ERROR,
                f"备份配置失败",
                original_error=e,
                details={"config_file": self.config_file, "backup_dir": self.backup_dir}
            )
            error_handler.handle_error(error_info)
            return None
    
    def _cleanup_old_backups(self) -> None:
        """清理旧备份文件，只保留最近的N个备份"""
        try:
            max_backups = self.config.get("backup", {}).get("max_backups", 10)
            
            # 获取所有备份文件，按修改时间排序
            backups = sorted(
                [os.path.join(self.backup_dir, f) for f in os.listdir(self.backup_dir) if f.startswith("config_backup_") and f.endswith(".json")],
                key=os.path.getmtime,
                reverse=True
            )
            
            # 删除超出数量限制的旧备份
            for backup in backups[max_backups:]:
                os.remove(backup)
                logger.info(f"已删除旧备份: {backup}")
                
        except Exception as e:
            logger.warning(f"清理旧备份失败: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        try:
            if self.config is None:
                return default
            
            keys = key.split(".")
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            logger.error(f"获取配置项失败: {key}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置项"""
        try:
            if self.config is None:
                self.config = self.default_config.copy()
            
            keys = key.split(".")
            config_ref = self.config
            
            # 遍历除最后一个键之外的所有键
            for k in keys[:-1]:
                if k not in config_ref or not isinstance(config_ref[k], dict):
                    config_ref[k] = {}
                config_ref = config_ref[k]
            
            # 设置最后一个键的值
            config_ref[keys[-1]] = value
            
            # 保存配置
            return self.save_config()
            
        except Exception as e:
            error_info = ErrorInfo(
                ErrorType.CONFIG_ERROR,
                f"设置配置项失败",
                original_error=e,
                details={"key": key, "value": value}
            )
            error_handler.handle_error(error_info)
            return False
    
    def get_website_templates(self) -> Dict[str, List[str]]:
        """获取网站模板"""
        return self.get("website_templates", self.default_config["website_templates"])
    
    def update_website_template(self, template_name: str, websites: List[str]) -> bool:
        """更新网站模板"""
        try:
            if "website_templates" not in self.config:
                self.config["website_templates"] = {}
            
            self.config["website_templates"][template_name] = websites
            return self.save_config()
            
        except Exception as e:
            error_info = ErrorInfo(
                ErrorType.CONFIG_ERROR,
                f"更新网站模板失败",
                original_error=e,
                details={"template_name": template_name}
            )
            error_handler.handle_error(error_info)
            return False
    
    def reset_config(self) -> bool:
        """重置配置为默认值"""
        try:
            self.config = self.default_config.copy()
            return self.save_config()
            
        except Exception as e:
            error_info = ErrorInfo(
                ErrorType.CONFIG_ERROR,
                f"重置配置失败",
                original_error=e
            )
            error_handler.handle_error(error_info)
            return False

# 创建全局ConfigManager实例
config_manager = ConfigManager()