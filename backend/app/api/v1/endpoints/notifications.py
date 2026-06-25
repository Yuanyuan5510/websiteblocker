from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.notification_manager import notification_manager
from app.db.session import get_db

router = APIRouter()

@router.get("/config")
async def get_notification_config(db: Session = Depends(get_db)):
    """获取通知配置"""
    return notification_manager.get_config()

@router.put("/config")
async def update_notification_config(config: dict, db: Session = Depends(get_db)):
    """更新通知配置"""
    notification_manager.update_config(config)
    return {"success": True, "message": "Notification config updated successfully"}

@router.post("/toggle")
async def toggle_notifications(db: Session = Depends(get_db)):
    """切换通知开关"""
    enabled = notification_manager.toggle()
    return {"success": True, "message": f"Notifications {'enabled' if enabled else 'disabled'} successfully", "enabled": enabled}
