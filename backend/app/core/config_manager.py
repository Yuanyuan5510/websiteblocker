# -*- coding: utf-8 -*-
"""
配置管理器 - 支持从旧版本迁移配置
"""
import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.core.config import get_appdata_path
from app.models.config import Config
from app.models.blocked_domain import BlockedDomain
from app.models.whitelist import WhitelistDomain


# 默认配置
DEFAULT_CONFIG = {
    "general": {
        "auto_start": False,
        "auto_clear_on_exit": True,
        "notify_blocked": True,
        "block_all_templates": False,
        "language": "zh-CN"
    },
    "ui_settings": {
        "theme": "light",
        "window_size": [1200, 800],
        "splitter_position": 300,
        "show_toolbar": True
    },
    "backup": {
        "enabled": True,
        "interval_days": 7,
        "max_backups": 10
    },
    "logging": {
        "level": "INFO",
        "enabled": True,
        "file_logging": True,
        "console_logging": True
    },
    "version_check": {
        "enabled": True,
        "check_on_startup": True,
        "update_url": "https://websiteblocker.wangstation.dpdns.org/version.txt"
    },
    "version": "4.4"
}

# 网站模板（从v3.9迁移）
DEFAULT_TEMPLATES = {
    "social_media": [
        "facebook.com", "twitter.com", "instagram.com", "linkedin.com",
        "tiktok.com", "snapchat.com", "pinterest.com", "reddit.com"
    ],
    "video": [
        "youtube.com", "bilibili.com", "netflix.com", "iqiyi.com",
        "youku.com", "vimeo.com", "dailymotion.com"
    ],
    "game": [
        "steam.com", "epicgames.com", "origin.com", "battlenet.com",
        "gog.com", "itch.io", "roblox.com"
    ],
    "shopping": [
        "amazon.com", "taobao.com", "jd.com", "ebay.com",
        "aliexpress.com", "wish.com", "tmall.com"
    ],
    "news": [
        "bbc.com", "cnn.com", "nytimes.com", "theguardian.com",
        "reuters.com", "foxnews.com", "cnbc.com"
    ],
    "entertainment": [
        "twitch.tv", "disneyplus.com", "hulu.com", "hbo.com",
        "spotify.com", "soundcloud.com"
    ]
}


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.config_dir = get_appdata_path()
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)
    
    def get_config_path(self) -> str:
        """获取旧版配置文件路径"""
        return os.path.join(self.config_dir, "config.json")
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        config_dict = {}
        configs = self.db.query(Config).all()
        for config in configs:
            config_dict[config.key] = config.value
        return config_dict if config_dict else DEFAULT_CONFIG
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """获取单个配置值"""
        config = self.db.query(Config).filter(Config.key == key).first()
        if config:
            return config.value
        return default
    
    def set_config_value(self, key: str, value: Any, description: str = None) -> Config:
        """设置单个配置值"""
        config = self.db.query(Config).filter(Config.key == key).first()
        if config:
            config.value = value
            if description:
                config.description = description
        else:
            config = Config(key=key, value=value, description=description)
            self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def update_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新多个配置"""
        for key, value in config_data.items():
            self.set_config_value(key, value)
        return self.get_all_config()
    
    def reset_config(self) -> Dict[str, Any]:
        """重置配置为默认值"""
        # 清空现有配置
        self.db.query(Config).delete()
        
        # 插入默认配置
        for key, value in DEFAULT_CONFIG.items():
            self.set_config_value(key, value)
        
        self.db.commit()
        return self.get_all_config()
    
    def check_old_config_exists(self) -> bool:
        """检查旧版配置文件是否存在"""
        config_path = self.get_config_path()
        return os.path.exists(config_path)
    
    def migrate_from_old_version(self) -> Dict[str, Any]:
        """从旧版本迁移配置"""
        config_path = self.get_config_path()
        
        if not os.path.exists(config_path):
            logger.info("未找到旧版配置文件，使用默认配置")
            return self.reset_config()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                old_config = json.load(f)
            
            logger.info(f"检测到旧版配置文件，版本: {old_config.get('version', 'unknown')}")
            
            # 备份旧配置
            backup_path = config_path + f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(config_path, backup_path)
            logger.info(f"已备份旧配置到: {backup_path}")
            
            # 迁移配置字段
            migrated_config = DEFAULT_CONFIG.copy()
            
            # 迁移基本设置
            if "blocked_websites" in old_config:
                # 迁移阻止的网站到数据库
                self._migrate_blocked_websites(old_config["blocked_websites"])
            
            # 迁移常规设置
            if "auto_clear_on_exit" in old_config:
                migrated_config["general"]["auto_clear_on_exit"] = old_config["auto_clear_on_exit"]
            if "external_storage_enabled" in old_config:
                migrated_config["general"]["block_all_templates"] = not old_config.get("external_storage_enabled", False)
            
            # 迁移模板设置（如果有）
            if "website_templates" in old_config:
                migrated_config["templates"] = old_config["website_templates"]
            
            # 迁移UI设置（如果有）
            if "ui_settings" in old_config:
                migrated_config["ui_settings"].update(old_config["ui_settings"])
            
            # 迁移版本信息
            if "version" in old_config:
                migrated_config["migrated_from"] = old_config["version"]
            
            # 保存迁移后的配置
            for key, value in migrated_config.items():
                self.set_config_value(key, value)
            
            self.db.commit()
            logger.info("配置迁移完成")
            
            return self.get_all_config()
            
        except Exception as e:
            logger.error(f"配置迁移失败: {str(e)}")
            return self.reset_config()
    
    def _migrate_blocked_websites(self, websites: List[str]):
        """迁移阻止的网站列表到数据库"""
        if not websites:
            return
        
        added_count = 0
        for website in websites:
            if isinstance(website, str):
                # 检查是否已存在
                existing = self.db.query(BlockedDomain).filter(
                    BlockedDomain.domain == website
                ).first()
                
                if not existing:
                    blocked_domain = BlockedDomain(
                        domain=website,
                        reason="从旧版本迁移",
                        category="migrated",
                        active=True
                    )
                    self.db.add(blocked_domain)
                    added_count += 1
        
        if added_count > 0:
            logger.info(f"已迁移 {added_count} 个阻止域名到数据库")
    
    def get_templates(self) -> Dict[str, List[str]]:
        """获取网站模板"""
        templates = self.get_config_value("templates", DEFAULT_TEMPLATES)
        return templates if templates else DEFAULT_TEMPLATES
    
    def add_template(self, name: str, domains: List[str]) -> Dict[str, List[str]]:
        """添加或更新模板"""
        templates = self.get_templates()
        templates[name] = domains
        self.set_config_value("templates", templates)
        return templates


def init_config_on_startup(db: Session):
    """启动时初始化配置"""
    config_manager = ConfigManager(db)
    
    # 检查是否已有配置
    existing_config = config_manager.get_all_config()
    
    if not existing_config or existing_config == DEFAULT_CONFIG:
        # 尝试从旧版本迁移
        if config_manager.check_old_config_exists():
            logger.info("检测到旧版配置文件，开始迁移...")
            return config_manager.migrate_from_old_version()
        else:
            # 使用默认配置
            logger.info("使用默认配置")
            return config_manager.reset_config()
    
    return existing_config