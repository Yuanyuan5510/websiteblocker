from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import sys
import ctypes

# 添加包路径处理逻辑，解决相对导入问题
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将相对导入改为绝对导入
from app.core.config import settings
from app.core.logger import logger
from app.core.error_handler import register_exception_handlers
from app.core.websocket_manager import websocket_manager
from app.api.v1.api import api_router
from app.db.base import Base
from app.db.session import engine


def run_as_admin():
    """检查当前进程是否具有管理员权限，如果没有则尝试提升权限"""
    try:
        # 检查是否在Windows系统上
        if os.name != 'nt':
            return True
        
        # 检查当前进程是否具有管理员权限
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        
        # 尝试以管理员权限重新启动程序
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        return False
    except Exception as e:
        logger.error(f"Failed to check/elevate admin privileges: {e}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    Args:
        app: FastAPI应用实例
    """
    # 启动时执行
    logger.info(f"Starting {settings.app_name} v{settings.app_version}...")
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    yield
    
    # 关闭时执行
    logger.info(f"Shutting down {settings.app_name} v{settings.app_version}...")

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Website Access Restriction Tool API",
    debug=settings.debug,
    lifespan=lifespan
)

# 访问限制中间件
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

@app.middleware("http")
async def check_allowed_browser(request: Request, call_next):
    """
    检查请求是否来自允许的浏览器
    """
    try:
        # 允许的User-Agent（来自指定的Electron浏览器）
        allowed_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        
        # 检查User-Agent
        user_agent = request.headers.get("user-agent", "")
        
        # 允许的路径（不需要检查的路径）
        allowed_paths = ["/health", "/version", "/ws", "/api/v1/notifications/config", "/api/v1/schedules", "/api/v1/error_log", "/docs", "/redoc", "/openapi.json", "/favicon.ico"]
        
        # 允许本地IP访问（来自127.0.0.1的请求）
        client_host = request.client.host if request.client else ""
        
        # 如果路径在允许列表中，或者User-Agent匹配，或者是本地IP请求，则允许访问
        if any(path in request.url.path for path in allowed_paths) or allowed_user_agent in user_agent or client_host == "127.0.0.1":
            response = await call_next(request)
            return response
        else:
            # 拒绝访问
            logger.warning(f"来自不允许的浏览器或IP的请求: User-Agent={user_agent}, IP={client_host}")
            return JSONResponse(
                status_code=403,
                content={"detail": "Access forbidden: Only allowed browser is permitted"}
            )
    except Exception as e:
        logger.error(f"访问限制中间件错误: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
register_exception_handlers(app)

# 注册API路由
app.include_router(api_router, prefix="/api")

# WebSocket路由
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点，用于实时更新"""
    await websocket_manager.connect(websocket)
    try:
        # 发送连接成功消息
        await websocket_manager.send_personal_message({
            "type": "connection_established",
            "message": "WebSocket连接成功",
            "timestamp": "{}".format("2026-01-04"),
            "version": settings.app_version
        }, websocket)
        
        # 保持连接并处理客户端消息
        while True:
            # 接收客户端消息（如果需要）
            data = await websocket.receive_json()
            logger.info(f"Received WebSocket message: {data}")
            
            # 可以根据需要处理客户端消息
            if data.get("type") == "ping":
                await websocket_manager.send_personal_message({
                    "type": "pong",
                    "timestamp": "{}".format("2026-01-04")
                }, websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        websocket_manager.disconnect(websocket)

@app.get("/")
async def root():
    """根路径"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.app_version
    }

@app.get("/version")
async def get_version():
    """获取应用版本"""
    return {
        "version": settings.app_version
    }

def main():
    """主函数，用于直接运行应用"""
    import logging
    
    # 配置日志，禁用终端相关功能，确保不使用uvicorn自带的格式化器
    logging_config = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "file": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "file": {
                "formatter": "file",
                "class": "logging.FileHandler",
                "filename": "website_blocker.log",
                "mode": "a",
                "encoding": "utf-8"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["file"]
        },
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False
            }
        }
    }
    
    # 使用直接引用而不是字符串路径，确保打包后能正确识别
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug,
        log_level="info",
        log_config=logging_config,  # 使用自定义日志配置
        access_log=True
    )

if __name__ == "__main__":
    if not run_as_admin():
        sys.exit(0)
    main()
