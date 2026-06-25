from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class BlockedDomain(Base):
    """被阻止域名模型"""
    __tablename__ = "blocked_domains"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True, nullable=False)
    reason = Column(String, nullable=True)
    category = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<BlockedDomain(domain='{self.domain}', active={self.active})>"
