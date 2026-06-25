from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def get_config():
    """获取所有配置"""
    return {}

@router.put("")
async def update_config():
    """更新配置"""
    return {"success": True, "message": "Config updated successfully"}

@router.post("/reset")
async def reset_config():
    """重置配置"""
    return {"success": True, "message": "Config reset successfully"}
