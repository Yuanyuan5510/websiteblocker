from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from typing import List, Dict, Any
import os
import shutil
from datetime import datetime
from pathlib import Path

from app.db.session import get_db, engine
from app.core.config import get_appdata_path
from app.core.logger import logger

router = APIRouter()


def get_database_path() -> str:
    """获取数据库文件路径"""
    return os.path.join(get_appdata_path(), 'website_blocker.db')


def get_backup_dir() -> str:
    """获取备份目录路径"""
    backup_dir = os.path.join(get_appdata_path(), 'backups')
    Path(backup_dir).mkdir(parents=True, exist_ok=True)
    return backup_dir


@router.get("/tables")
async def get_database_tables(db: Session = Depends(get_db)):
    """获取数据库表列表及其行数"""
    try:
        inspector = inspect(engine)
        tables = []
        
        for table_name in inspector.get_table_names():
            try:
                # 获取表的行数
                result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.scalar()
                
                # 获取列信息
                columns = []
                for column in inspector.get_columns(table_name):
                    columns.append({
                        "name": column["name"],
                        "type": str(column["type"]),
                        "nullable": column.get("nullable", True),
                        "primary_key": column.get("primary_key", False)
                    })
                
                tables.append({
                    "name": table_name,
                    "row_count": row_count,
                    "columns": columns
                })
            except Exception as e:
                logger.error(f"获取表 {table_name} 信息失败: {str(e)}")
                tables.append({
                    "name": table_name,
                    "row_count": 0,
                    "error": str(e)
                })
        
        return tables
    except Exception as e:
        logger.error(f"获取数据库表列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取数据库表列表失败: {str(e)}")


@router.get("/info")
async def get_database_info():
    """获取数据库基本信息"""
    try:
        db_path = get_database_path()
        
        if not os.path.exists(db_path):
            return {
                "exists": False,
                "path": db_path,
                "message": "数据库文件不存在"
            }
        
        # 获取文件大小
        file_size = os.path.getsize(db_path)
        
        # 获取修改时间
        mod_time = datetime.fromtimestamp(os.path.getmtime(db_path))
        
        return {
            "exists": True,
            "path": db_path,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "last_modified": mod_time.isoformat()
        }
    except Exception as e:
        logger.error(f"获取数据库信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取数据库信息失败: {str(e)}")


@router.post("/backup")
async def backup_database(db: Session = Depends(get_db)):
    """备份数据库"""
    try:
        db_path = get_database_path()
        
        if not os.path.exists(db_path):
            raise HTTPException(status_code=404, detail="数据库文件不存在")
        
        # 创建备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"website_blocker_backup_{timestamp}.db"
        backup_path = os.path.join(get_backup_dir(), backup_filename)
        
        # 复制数据库文件
        shutil.copy2(db_path, backup_path)
        
        # 清理旧备份（保留最近10个）
        cleanup_old_backups(max_backups=10)
        
        logger.info(f"数据库备份成功: {backup_path}")
        
        return {
            "success": True,
            "message": "Database backed up successfully",
            "backup_path": backup_path,
            "backup_filename": backup_filename,
            "backup_time": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"数据库备份失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"数据库备份失败: {str(e)}")


@router.get("/backups")
async def list_backups():
    """列出所有备份文件"""
    try:
        backup_dir = get_backup_dir()
        
        if not os.path.exists(backup_dir):
            return {"backups": []}
        
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.db'):
                filepath = os.path.join(backup_dir, filename)
                file_stat = os.stat(filepath)
                backups.append({
                    "filename": filename,
                    "path": filepath,
                    "size_bytes": file_stat.st_size,
                    "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                    "created_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                })
        
        # 按创建时间倒序排列
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {"backups": backups}
    except Exception as e:
        logger.error(f"获取备份列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取备份列表失败: {str(e)}")


@router.post("/restore/{backup_filename}")
async def restore_database(backup_filename: str, db: Session = Depends(get_db)):
    """从备份恢复数据库"""
    try:
        backup_path = os.path.join(get_backup_dir(), backup_filename)
        
        if not os.path.exists(backup_path):
            raise HTTPException(status_code=404, detail=f"备份文件不存在: {backup_filename}")
        
        db_path = get_database_path()
        
        # 创建当前数据库的备份
        if os.path.exists(db_path):
            pre_restore_backup = db_path + f".pre_restore.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(db_path, pre_restore_backup)
        
        # 恢复数据库
        shutil.copy2(backup_path, db_path)
        
        logger.info(f"数据库恢复成功: {backup_filename}")
        
        return {
            "success": True,
            "message": "Database restored successfully",
            "restored_from": backup_filename
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"数据库恢复失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"数据库恢复失败: {str(e)}")


@router.delete("/backups/{backup_filename}")
async def delete_backup(backup_filename: str):
    """删除备份文件"""
    try:
        backup_path = os.path.join(get_backup_dir(), backup_filename)
        
        if not os.path.exists(backup_path):
            raise HTTPException(status_code=404, detail=f"备份文件不存在: {backup_filename}")
        
        os.remove(backup_path)
        
        return {
            "success": True,
            "message": f"Backup {backup_filename} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除备份失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除备份失败: {str(e)}")


def cleanup_old_backups(max_backups: int = 10):
    """清理旧备份，保留最近的N个"""
    try:
        backup_dir = get_backup_dir()
        
        if not os.path.exists(backup_dir):
            return
        
        # 获取所有备份文件
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.endswith('.db'):
                filepath = os.path.join(backup_dir, filename)
                backups.append({
                    "filename": filename,
                    "path": filepath,
                    "mtime": os.path.getmtime(filepath)
                })
        
        # 按修改时间排序（最新的在前）
        backups.sort(key=lambda x: x["mtime"], reverse=True)
        
        # 删除超出数量的旧备份
        for backup in backups[max_backups:]:
            os.remove(backup["path"])
            logger.info(f"已删除旧备份: {backup['filename']}")
    except Exception as e:
        logger.error(f"清理旧备份失败: {str(e)}")
