from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class WhitelistDomain(Base):
    """白名单域名模型"""
    __tablename__ = "whitelist"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True, nullable=False)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Whitelist(domain='{self.domain}')>"
