from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class ScheduleBase(BaseModel):
    """调度任务基础模型"""
    name: str = Field(..., description="任务名称", example="阻止娱乐网站")
    task_type: str = Field(..., description="任务类型", example="block", pattern="^(block|unblock|update_hosts)$")
    cron_expression: str = Field(..., description="Cron表达式", example="0 9 * * 1-5")
    description: Optional[str] = Field(default="", description="任务描述", example="工作日上午9点阻止娱乐网站")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="任务参数")
    
    class Config:
        extra = "forbid"

class ScheduleCreate(ScheduleBase):
    """创建调度任务模型"""
    active: bool = Field(default=True, description="是否激活")

class ScheduleUpdate(BaseModel):
    """更新调度任务模型"""
    name: Optional[str] = Field(None, description="任务名称")
    task_type: Optional[str] = Field(None, description="任务类型", pattern="^(block|unblock|update_hosts)$")
    cron_expression: Optional[str] = Field(None, description="Cron表达式")
    description: Optional[str] = Field(None, description="任务描述")
    params: Optional[Dict[str, Any]] = Field(None, description="任务参数")
    active: Optional[bool] = Field(None, description="是否激活")
    
    class Config:
        extra = "forbid"

class ScheduleResponse(BaseModel):
    """调度任务响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    task_type: str
    cron_expression: str
    description: str
    params: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None
    active: bool
    next_run_time: Optional[datetime] = None
