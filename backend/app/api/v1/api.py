from fastapi import APIRouter

from .endpoints import (
    domains,
    hosts,
    ports,
    schedules,
    notifications,
    database,
    config,
    error_log
)

# 创建API路由实例
api_router = APIRouter(prefix="/v1")

# 注册各模块路由
api_router.include_router(domains.router, prefix="/domains", tags=["domains"])
api_router.include_router(hosts.router, prefix="/hosts", tags=["hosts"])
api_router.include_router(ports.router, prefix="/ports", tags=["ports"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(database.router, prefix="/database", tags=["database"])
api_router.include_router(config.router, prefix="/config", tags=["config"])
api_router.include_router(error_log.router, tags=["error_log"])
