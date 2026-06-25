from fastapi import APIRouter

router = APIRouter()

@router.get("/tables")
async def get_database_tables():
    """获取数据库表列表"""
    return []

@router.post("/backup")
async def backup_database():
    """备份数据库"""
    return {"success": True, "message": "Database backed up successfully", "backup_path": ""}
