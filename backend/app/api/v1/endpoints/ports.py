from fastapi import APIRouter, Query
from typing import List

router = APIRouter()

@router.get("")
async def get_used_ports():
    """获取当前使用的端口列表"""
    return {"used_ports": []}

@router.get("/check")
async def check_ports(ports: List[int] = Query(...)):
    """检查多个端口是否可用"""
    return []
