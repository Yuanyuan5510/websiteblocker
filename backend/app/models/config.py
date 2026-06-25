from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Config(Base):
    """配置模型"""
    __tablename__ = "config"
    
    key = Column(String, primary_key=True, index=True)
    value = Column(JSON, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Config(key='{self.key}', value={self.value})>"
