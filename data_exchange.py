# -*- coding: utf-8 -*-
"""
数据交换模块
处理不同版本之间的数据兼容性，提供数据验证和转换机制
"""

import json
import logging
from typing import Dict, Any, Optional, List
import os
from datetime import datetime

logger = logging.getLogger("WebsiteBlocker.DataExchange")

class DataVersionError(Exception):
    """数据版本不兼容异常"""
    pass

class DataExchange:
    """数据交换类"""
    
    CURRENT_VERSION = "3.9"
    CONFIG_SCHEMA = {
        "required_fields": ["version"],
        "default_values": {
            "version": "3.9",
            "auto_clear_on_exit": True,
            "external_storage_enabled": False,
            "last_run": datetime.now().isoformat(),
            "blocked_websites": [],
            "general": {
                "auto_start": False,
                "notify_blocked": True,
                "block_all_templates": False
            },
            "website_templates": {},
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
            },
            "version_check": {
                "enabled": True,
                "check_interval_hours": 24,
                "last_check_time": 0
            }
        }
    }
    
    def __init__(self):
        self.version_history = {
            "1.0": self._migrate_from_10,
            "2.0": self._migrate_from_20,
            "3.0": self._migrate_from_30
        }
    
    def load_config(self, file_path: str) -> Dict[str, Any]:
        """加载配置文件并处理版本兼容性"""
        if not os.path.exists(file_path):
            logger.info(f"配置文件不存在，创建默认配置: {file_path}")
            return self._create_default_config()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 验证配置文件
            self._validate_config(config)
            
            # 检查版本并进行迁移
            config = self._migrate_config(config)
            
            # 更新版本和最后运行时间
            config["version"] = self.CURRENT_VERSION
            config["last_run"] = datetime.now().isoformat()
            
            logger.info(f"配置文件加载成功: {file_path}")
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {str(e)}")
            return self._create_default_config()
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return self._create_default_config()
    
    def save_config(self, config: Dict[str, Any], file_path: str) -> bool:
        """保存配置文件，确保数据完整性"""
        try:
            # 验证配置
            self._validate_config(config)
            
            # 更新版本和最后运行时间
            config["version"] = self.CURRENT_VERSION
            config["last_run"] = datetime.now().isoformat()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置文件保存成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            return False
    
    def _validate_config(self, config: Dict[str, Any]):
        """验证配置文件格式"""
        # 检查必填字段
        for field in self.CONFIG_SCHEMA["required_fields"]:
            if field not in config:
                logger.warning(f"配置文件缺少必填字段: {field}")
        
        # 确保所有默认字段存在
        for field, default_value in self.CONFIG_SCHEMA["default_values"].items():
            if field not in config:
                logger.warning(f"配置文件缺少字段: {field}，使用默认值")
                config[field] = default_value
    
    def _migrate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """根据版本迁移配置文件"""
        if "version" not in config:
            logger.warning("配置文件缺少版本信息，默认为1.0")
            config["version"] = "1.0"
        
        current_version = config["version"]
        
        # 如果已经是当前版本，无需迁移
        if current_version == self.CURRENT_VERSION:
            return config
        
        logger.info(f"正在迁移配置文件，从版本 {current_version} 到 {self.CURRENT_VERSION}")
        
        # 按顺序进行版本迁移
        for version in sorted(self.version_history.keys()):
            if current_version < version <= self.CURRENT_VERSION:
                config = self.version_history[version](config)
                config["version"] = version
        
        # 确保所有默认字段存在
        for field, default_value in self.CONFIG_SCHEMA["default_values"].items():
            if field not in config:
                config[field] = default_value
        
        return config
    
    def _migrate_from_10(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """从1.0版本迁移"""
        logger.info("迁移配置文件从版本1.0")
        
        # 1.0版本可能没有version字段和其他高级功能
        config["version"] = "2.0"
        return config
    
    def _migrate_from_20(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """从2.0版本迁移"""
        logger.info("迁移配置文件从版本2.0")
        
        # 2.0版本可能没有external_storage_enabled字段
        if "external_storage_enabled" not in config:
            config["external_storage_enabled"] = False
        
        config["version"] = "3.0"
        return config
    
    def _migrate_from_30(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """从3.0版本迁移"""
        logger.info("迁移配置文件从版本3.0")
        
        # 确保所有默认字段存在
        for field, default_value in self.CONFIG_SCHEMA["default_values"].items():
            if field not in config:
                config[field] = default_value
        
        config["version"] = "3.9"
        return config
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        default_config = self.CONFIG_SCHEMA["default_values"].copy()
        default_config["version"] = self.CURRENT_VERSION
        default_config["last_run"] = datetime.now().isoformat()
        return default_config
    
    def validate_websites(self, websites: List[str]) -> List[str]:
        """验证网站列表格式"""
        validated_websites = []
        
        for website in websites:
            if website and isinstance(website, str):
                # 清理域名格式
                website = self._clean_domain(website)
                if website:
                    validated_websites.append(website)
        
        # 去重
        return list(set(validated_websites))
    
    def _clean_domain(self, domain: str) -> str:
        """清理域名格式，移除不必要的部分"""
        if not domain:
            return ""
            
        # 转换为小写
        domain = domain.lower()
            
        # 移除协议部分
        for protocol in ['http://', 'https://', 'ftp://', 'ftps://', 'ws://', 'wss://']:
            if domain.startswith(protocol):
                domain = domain[len(protocol):]
        
        # 移除www前缀
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # 移除路径和端口部分
        if '/' in domain:
            domain = domain.split('/', 1)[0]
        
        if ':' in domain and not domain.endswith('.com') and not domain.endswith('.cn'):
            domain = domain.split(':', 1)[0]
        
        return domain

# 创建全局数据交换实例
data_exchange = DataExchange()