from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.scheduler_manager import scheduler_manager
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from app.db.session import get_db

router = APIRouter()

@router.get("", response_model=List[ScheduleResponse])
async def get_all_schedules(db: Session = Depends(get_db)):
    """获取所有调度任务"""
    return scheduler_manager.get_all_jobs()

@router.post("")
async def add_schedule(schedule_data: ScheduleCreate, db: Session = Depends(get_db)):
    """添加调度任务"""
    job_id = scheduler_manager.add_job(schedule_data)
    return {"success": True, "message": "Schedule added successfully", "id": job_id}

@router.put("/{schedule_id}")
async def update_schedule(schedule_id: str, schedule_data: ScheduleUpdate, db: Session = Depends(get_db)):
    """更新调度任务"""
    scheduler_manager.update_job(schedule_id, schedule_data)
    return {"success": True, "message": "Schedule updated successfully"}

@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str, db: Session = Depends(get_db)):
    """删除调度任务"""
    scheduler_manager.remove_job(schedule_id)
    return {"success": True, "message": "Schedule deleted successfully"}

@router.post("/restart")
async def restart_scheduler(db: Session = Depends(get_db)):
    """重启调度器"""
    scheduler_manager.restart()
    return {"success": True, "message": "Scheduler restarted successfully"}
