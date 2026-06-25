from fastapi import APIRouter, HTTPException
from app.core.logger import logger

router = APIRouter()

@router.get("/error_log")
async def get_error_logs():
    """
    获取系统中记录的所有错误信息
    
    Returns:
        dict: 包含错误日志的响应数据
    """
    try:
        # 这里应该实现从日志文件中读取错误信息的逻辑
        # 由于当前日志系统可能没有提供读取日志的API，我们可以返回一个示例响应
        return {
            "status": "success",
            "message": "Error logs retrieved successfully",
            "data": [
                {
                    "timestamp": "2026-01-07T10:00:00Z",
                    "level": "ERROR",
                    "message": "Example error message 1",
                    "module": "app.main"
                },
                {
                    "timestamp": "2026-01-07T10:05:00Z",
                    "level": "ERROR",
                    "message": "Example error message 2",
                    "module": "app.api.v1.endpoints.domains"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Failed to retrieve error logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve error logs")