# -*- coding: utf-8 -*-
"""
错误处理模块
实现更完善、更用户友好的错误处理机制
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional
import traceback

logger = logging.getLogger("WebsiteBlocker.ErrorHandler")

class ErrorType(Enum):
    """错误类型枚举"""
    PERMISSION_ERROR = "权限错误"
    FILE_OPERATION_ERROR = "文件操作错误"
    CONFIG_ERROR = "配置错误"
    NETWORK_ERROR = "网络错误"
    VALIDATION_ERROR = "验证错误"
    RUNTIME_ERROR = "运行时错误"
    UI_ERROR = "界面错误"
    UNKNOWN_ERROR = "未知错误"

class ErrorInfo:
    """错误信息类"""
    def __init__(self, error_type: ErrorType, message: str, 
                 original_error: Optional[Exception] = None, 
                 details: Optional[Dict[str, Any]] = None):
        self.error_type = error_type
        self.message = message
        self.original_error = original_error
        self.details = details or {}
        self.stack_trace = traceback.format_exc() if original_error else None

class ErrorHandler:
    """错误处理类"""
    
    def __init__(self):
        self.error_callbacks = {}
        
    def register_error_callback(self, error_type: ErrorType, callback):
        """注册特定错误类型的回调函数"""
        if error_type not in self.error_callbacks:
            self.error_callbacks[error_type] = []
        self.error_callbacks[error_type].append(callback)
    
    def handle_error(self, error_info: ErrorInfo):
        """处理错误"""
        # 记录错误日志
        self._log_error(error_info)
        
        # 调用注册的回调函数
        self._call_error_callbacks(error_info)
        
        # 返回错误信息（供UI使用）
        return self._format_error_for_ui(error_info)
    
    def _log_error(self, error_info: ErrorInfo):
        """记录错误日志"""
        log_message = f"{error_info.error_type.value}: {error_info.message}"
        
        if error_info.details:
            log_message += f" | 详细信息: {error_info.details}"
        
        if error_info.original_error:
            log_message += f" | 原始错误: {str(error_info.original_error)}"
        
        logger.error(log_message)
        
        if error_info.stack_trace:
            logger.debug(f"堆栈跟踪: {error_info.stack_trace}")
    
    def _call_error_callbacks(self, error_info: ErrorInfo):
        """调用注册的错误回调函数"""
        callbacks = self.error_callbacks.get(error_info.error_type, [])
        for callback in callbacks:
            try:
                callback(error_info)
            except Exception as e:
                logger.error(f"执行错误回调时出错: {str(e)}")
    
    def _format_error_for_ui(self, error_info: ErrorInfo) -> Dict[str, Any]:
        """格式化错误信息供UI使用"""
        return {
            "title": error_info.error_type.value,
            "message": error_info.message,
            "details": error_info.details,
            "error_type": error_info.error_type.name
        }
    
    def create_error_info(self, error_type: ErrorType, message: str, 
                         original_error: Optional[Exception] = None, 
                         details: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """创建错误信息对象"""
        return ErrorInfo(error_type, message, original_error, details)

# 创建全局错误处理器实例
error_handler = ErrorHandler()