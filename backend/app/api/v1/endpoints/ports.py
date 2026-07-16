from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
import socket
import psutil
import os

from app.core.logger import logger
from app.core.config import settings

router = APIRouter()


@router.get("")
async def get_used_ports():
    """获取当前进程使用的端口列表"""
    try:
        used_ports = []
        current_pid = os.getpid()
        
        # 获取当前进程打开的连接
        try:
            process = psutil.Process(current_pid)
            connections = process.connections(kind='inet')
            
            for conn in connections:
                if conn.laddr:
                    used_ports.append({
                        "port": conn.laddr.port,
                        "address": conn.laddr.ip,
                        "status": conn.status,
                        "type": "inet",
                        "pid": current_pid
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        # 获取系统监听的端口
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN':
                    if conn.laddr:
                        # 检查是否已添加
                        if not any(p["port"] == conn.laddr.port for p in used_ports):
                            try:
                                proc = psutil.Process(conn.pid) if conn.pid else None
                                used_ports.append({
                                    "port": conn.laddr.port,
                                    "address": conn.laddr.ip,
                                    "status": conn.status,
                                    "type": "inet",
                                    "pid": conn.pid,
                                    "process_name": proc.name() if proc else "unknown"
                                })
                            except:
                                used_ports.append({
                                    "port": conn.laddr.port,
                                    "address": conn.laddr.ip,
                                    "status": conn.status,
                                    "type": "inet",
                                    "pid": conn.pid
                                })
        except (psutil.AccessDenied, PermissionError):
            pass
        
        return {
            "used_ports": used_ports,
            "current_process_port": settings.server_port
        }
    except Exception as e:
        logger.error(f"获取端口列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取端口列表失败: {str(e)}")


@router.get("/check")
async def check_ports(ports: List[int] = Query(...)):
    """检查多个端口是否可用"""
    try:
        results = []
        
        for port in ports:
            is_available = check_port_available(port)
            
            result = {
                "port": port,
                "available": is_available,
                "in_use": not is_available
            }
            
            # 尝试获取使用该端口的进程
            if not is_available:
                process_info = get_process_using_port(port)
                if process_info:
                    result["process"] = process_info
            
            results.append(result)
        
        return results
    except Exception as e:
        logger.error(f"检查端口失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"检查端口失败: {str(e)}")


@router.get("/check/{port}")
async def check_single_port(port: int):
    """检查单个端口是否可用"""
    try:
        if port < 1 or port > 65535:
            raise HTTPException(status_code=400, detail="端口号必须在 1-65535 之间")
        
        is_available = check_port_available(port)
        
        result = {
            "port": port,
            "available": is_available,
            "in_use": not is_available
        }
        
        # 尝试获取使用该端口的进程
        if not is_available:
            process_info = get_process_using_port(port)
            if process_info:
                result["process"] = process_info
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"检查端口 {port} 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"检查端口失败: {str(e)}")


def check_port_available(port: int, host: str = '127.0.0.1') -> bool:
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0  # 如果连接失败(端口未被占用),返回True
    except socket.error:
        return True


def get_process_using_port(port: int) -> Dict[str, Any]:
    """获取使用指定端口的进程信息"""
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr and conn.laddr.port == port:
                if conn.pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        return {
                            "pid": conn.pid,
                            "name": proc.name(),
                            "cmdline": " ".join(proc.cmdline()[:3]) if proc.cmdline() else "",
                            "status": conn.status
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        return {
                            "pid": conn.pid,
                            "status": conn.status
                        }
        return None
    except (psutil.AccessDenied, PermissionError):
        return None
