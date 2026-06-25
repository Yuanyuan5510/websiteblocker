"""
数据模式模块
"""

from .domain import (
    BlockedDomainCreate,
    WhitelistDomainCreate,
    BlockedDomainResponse,
    WhitelistDomainResponse
)
from .schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse
)

__all__ = [
    "BlockedDomainCreate",
    "WhitelistDomainCreate",
    "BlockedDomainResponse",
    "WhitelistDomainResponse",
    "ScheduleCreate",
    "ScheduleUpdate",
    "ScheduleResponse"
]
