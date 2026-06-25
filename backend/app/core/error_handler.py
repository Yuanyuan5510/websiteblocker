from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Union, Dict, Any
import traceback
from .logger import logger

class ErrorCode:
    """错误代码定义"""
    # 通用错误
    INTERNAL_ERROR = "internal_error"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    
    # 权限相关错误
    PERMISSION_DENIED = "permission_denied"
    UNAUTHORIZED = "unauthorized"
    
    # 资源相关错误
    RESOURCE_EXISTS = "resource_exists"
    RESOURCE_NOT_FOUND = "resource_not_found"
    
    # 文件操作相关错误
    FILE_OPERATION_FAILED = "file_operation_failed"
    FILE_NOT_FOUND = "file_not_found"
    
    # 域名相关错误
    INVALID_DOMAIN = "invalid_domain"
    DOMAIN_ALREADY_BLOCKED = "domain_already_blocked"
    DOMAIN_NOT_BLOCKED = "domain_not_blocked"
    
    # DNS相关错误
    DNS_SERVER_ERROR = "dns_server_error"
    
    # 调度器相关错误
    SCHEDULER_ERROR = "scheduler_error"

class WebsiteBlockerException(Exception):
    """自定义异常类"""
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 400,
        details: Dict[str, Any] = None
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

async def custom_exception_handler(request: Request, exc: WebsiteBlockerException) -> JSONResponse:
    """自定义异常处理器"""
    logger.error(
        f"Custom exception: {exc.error_code} - {exc.message}",
        extra={"request": request.url.path, "details": exc.details}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

async def http_exception_handler(request: Request, exc: Union[HTTPException, StarletteHTTPException]) -> JSONResponse:
    """HTTP异常处理器"""
    logger.error(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={"request": request.url.path}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": exc.detail
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """请求验证异常处理器"""
    logger.error(
        f"Validation exception: {exc.errors()}",
        extra={"request": request.url.path}
    )
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.VALIDATION_ERROR,
                "message": "请求参数验证失败",
                "details": exc.errors()
            }
        }
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"request": request.url.path, "traceback": traceback.format_exc()}
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "服务器内部错误",
                "details": {"error_type": type(exc).__name__}
            }
        }
    )

def register_exception_handlers(app):
    """注册所有异常处理器"""
    app.add_exception_handler(WebsiteBlockerException, custom_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
