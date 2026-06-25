from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class DomainBase(BaseModel):
    """域名基础模型"""
    domain: str = Field(..., description="域名", example="example.com")
    reason: Optional[str] = Field(default="", description="阻止/白名单原因", example="浪费时间")
    
    class Config:
        extra = "forbid"

class BlockedDomainCreate(DomainBase):
    """创建被阻止域名模型"""
    category: Optional[str] = Field(default="", description="域名分类", example="娱乐")

class WhitelistDomainCreate(DomainBase):
    """创建白名单域名模型"""
    pass

class BlockedDomainUpdate(BaseModel):
    """更新被阻止域名模型"""
    reason: Optional[str] = Field(None, description="阻止原因")
    category: Optional[str] = Field(None, description="域名分类")
    active: Optional[bool] = Field(None, description="是否激活")
    
    class Config:
        extra = "forbid"

class WhitelistDomainUpdate(BaseModel):
    """更新白名单域名模型"""
    reason: Optional[str] = Field(None, description="白名单原因")
    
    class Config:
        extra = "forbid"

class DomainResponse(BaseModel):
    """域名响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    domain: str
    reason: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class BlockedDomainResponse(DomainResponse):
    """被阻止域名响应模型"""
    category: str
    active: bool

class WhitelistDomainResponse(DomainResponse):
    """白名单域名响应模型"""
    pass

class BatchBlockedDomainCreate(BaseModel):
    """批量创建被阻止域名模型"""
    domains: List[str] = Field(..., description="域名列表", example=["example.com", "test.com"])
    reason: Optional[str] = Field(default="", description="阻止原因", example="模板应用")
    category: Optional[str] = Field(default="", description="域名分类", example="template")
    
    class Config:
        extra = "forbid"

class BatchDomainResult(BaseModel):
    """批量域名操作结果模型"""
    success_count: int = Field(..., description="成功数量")
    failure_count: int = Field(..., description="失败数量")
    failed_domains: List[str] = Field(..., description="失败的域名列表")
    message: str = Field(..., description="操作结果消息")
