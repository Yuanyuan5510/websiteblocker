from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.hosts_manager import HostsManager

router = APIRouter()

@router.get("")
async def get_hosts_content(db: Session = Depends(get_db)):
    """获取Hosts文件内容"""
    hosts_manager = HostsManager(db)
    content = hosts_manager.read_hosts()
    return {"content": content}

@router.post("/backup")
async def backup_hosts(db: Session = Depends(get_db)):
    """备份Hosts文件"""
    hosts_manager = HostsManager(db)
    backup_path = hosts_manager.backup_hosts()
    return {"success": True, "message": "Hosts file backed up successfully", "backup_path": backup_path}

@router.post("/refresh")
async def refresh_hosts(db: Session = Depends(get_db)):
    """从数据库刷新Hosts文件"""
    hosts_manager = HostsManager(db)
    hosts_manager.update_hosts_from_database()
    return {"success": True, "message": "Hosts file refreshed successfully"}

@router.get("/domains")
async def get_all_domains_from_hosts(db: Session = Depends(get_db)):
    """从Hosts文件获取所有域名"""
    hosts_manager = HostsManager(db)
    domains = hosts_manager.get_all_domains_from_hosts()
    return domains

@router.post("/disable")
async def disable_all_blocks(db: Session = Depends(get_db)):
    """禁用所有阻止规则"""
    hosts_manager = HostsManager(db)
    hosts_manager.disable_all_blocks()
    return {"success": True, "message": "All blocks disabled successfully"}

@router.post("/enable")
async def enable_all_blocks(db: Session = Depends(get_db)):
    """启用所有阻止规则"""
    hosts_manager = HostsManager(db)
    hosts_manager.enable_all_blocks()
    return {"success": True, "message": "All blocks enabled successfully"}
