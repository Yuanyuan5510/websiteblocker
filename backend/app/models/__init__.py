"""
数据模型模块
"""

from .blocked_domain import BlockedDomain
from .whitelist import WhitelistDomain
from .schedule import Schedule
from .config import Config

__all__ = ["BlockedDomain", "WhitelistDomain", "Schedule", "Config"]
