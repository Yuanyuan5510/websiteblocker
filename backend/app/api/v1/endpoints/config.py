from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.config_manager import ConfigManager, init_config_on_startup
from app.db.session import get_db

router = APIRouter()

@router.get("")
async def get_config(db: Session = Depends(get_db)):
    """获取所有配置"""
    config_manager = ConfigManager(db)
    return config_manager.get_all_config()

@router.put("")
async def update_config(config_data: Dict[str, Any], db: Session = Depends(get_db)):
    """更新配置"""
    config_manager = ConfigManager(db)
    return config_manager.update_config(config_data)

@router.post("/reset")
async def reset_config(db: Session = Depends(get_db)):
    """重置配置为默认值"""
    config_manager = ConfigManager(db)
    return config_manager.reset_config()

@router.post("/migrate")
async def migrate_config(db: Session = Depends(get_db)):
    """从旧版本迁移配置"""
    config_manager = ConfigManager(db)
    if not config_manager.check_old_config_exists():
        raise HTTPException(status_code=404, detail="未找到旧版配置文件")
    return config_manager.migrate_from_old_version()

@router.get("/check-migration")
async def check_migration(db: Session = Depends(get_db)):
    """检查是否可以迁移旧版配置"""
    config_manager = ConfigManager(db)
    return {
        "old_config_exists": config_manager.check_old_config_exists(),
        "config_path": config_manager.get_config_path()
    }
