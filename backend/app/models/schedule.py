from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class Schedule(Base):
    """调度任务模型"""
    __tablename__ = "schedules"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    task_type = Column(String, nullable=False)  # block, unblock, update_hosts
    cron_expression = Column(String, nullable=False)  # Cron表达式
    params = Column(JSON, nullable=True)  # 任务参数
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    active = Column(Boolean, default=True)
    next_run_time = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Schedule(name='{self.name}', type='{self.task_type}', active={self.active})>"
