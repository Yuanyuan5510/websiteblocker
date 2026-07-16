from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from pathlib import Path


def get_appdata_path() -> str:
    """获取统一配置路径"""
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    return os.path.join(appdata, 'WebsiteBlocker')


def get_database_path() -> str:
    """获取数据库路径"""
    config_dir = get_appdata_path()
    Path(config_dir).mkdir(parents=True, exist_ok=True)
    return os.path.join(config_dir, 'website_blocker.db')


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__"
    )
    
    # 应用基本配置
    app_name: str = "Website Blocker"
    app_version: str = "1.1.0"
    debug: bool = False
    
    # 服务器配置
    server_host: str = "127.0.0.1"
    server_port: int = 16411
    
    # 前端配置
    frontend_url: str = "http://localhost:16411"
    
    # 数据库配置 - 使用统一路径
    database_url: str = Field(default_factory=lambda: f"sqlite:///{get_database_path()}")
    
    # CORS配置
    cors_origins: List[str] = Field(default_factory=lambda: [
        "http://localhost:16410",
        "http://127.0.0.1:16410",
        "http://localhost:16411",
        "http://127.0.0.1:16411",
        "https://websiteblocker.vercel.app",
        "https://websiteblocker.wangstation.dpdns.org",
    ])
    
    # Hosts文件配置
    hosts_file_path: Optional[str] = None
    block_comment_start: str = "# WEBSITE BLOCKER START"
    block_comment_end: str = "# WEBSITE BLOCKER END"
    redirect_ip: str = "127.0.0.1"
    
    # 调度器配置
    scheduler_enabled: bool = True
    
    # 通知配置
    notifications_enabled: bool = True
    notification_frequency: str = "immediate"
    
    # 安全配置
    api_key: str = ""  # 留空则不启用API密钥验证
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 自动检测hosts文件路径
        if self.hosts_file_path is None:
            self.hosts_file_path = self._detect_hosts_path()
    
    def _detect_hosts_path(self) -> str:
        """自动检测不同平台的hosts文件路径"""
        if os.name == "nt":  # Windows
            return os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts")
        elif os.name == "posix":  # Linux/macOS
            if os.path.exists("/private/etc/hosts"):  # macOS
                return "/private/etc/hosts"
            else:  # Linux
                return "/etc/hosts"
        else:
            raise RuntimeError(f"Unsupported operating system: {os.name}")

settings = Settings()
