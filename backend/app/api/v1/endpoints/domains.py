from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.domain import (
    BlockedDomainCreate,
    WhitelistDomainCreate,
    BlockedDomainResponse,
    WhitelistDomainResponse,
    BatchBlockedDomainCreate,
    BatchDomainResult
)
from app.core.domain_manager import DomainManager

router = APIRouter()

@router.get("/blocked", response_model=List[BlockedDomainResponse])
async def get_blocked_domains(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    db: Session = Depends(get_db)
):
    """获取所有被阻止的域名"""
    domain_manager = DomainManager(db)
    return domain_manager.get_blocked_domains(skip=skip, limit=limit)

@router.post("/blocked", response_model=BlockedDomainResponse)
async def add_blocked_domain(
    domain_data: BlockedDomainCreate,
    db: Session = Depends(get_db)
):
    """添加被阻止的域名"""
    domain_manager = DomainManager(db)
    return domain_manager.create_blocked_domain(domain_data)

@router.post("/blocked/batch", response_model=BatchDomainResult)
async def add_blocked_domains_batch(
    batch_data: BatchBlockedDomainCreate,
    db: Session = Depends(get_db)
):
    """批量添加被阻止的域名"""
    domain_manager = DomainManager(db)
    result = domain_manager.batch_create_blocked_domains(
        domains=batch_data.domains,
        reason=batch_data.reason,
        category=batch_data.category
    )
    
    return BatchDomainResult(
        success_count=result["success_count"],
        failure_count=result["failure_count"],
        failed_domains=result["failed_domains"],
        message=f"成功阻止 {result['success_count']} 个域名，失败 {result['failure_count']} 个域名"
    )

@router.delete("/blocked/{domain_id}")
async def remove_blocked_domain(
    domain_id: int,
    db: Session = Depends(get_db)
):
    """删除被阻止的域名"""
    domain_manager = DomainManager(db)
    domain = domain_manager.delete_blocked_domain(domain_id)
    return {"success": True, "message": f"Domain {domain} unblocked successfully", "domain": domain}

@router.put("/blocked/{domain_id}/toggle", response_model=BlockedDomainResponse)
async def toggle_blocked_domain(
    domain_id: int,
    db: Session = Depends(get_db)
):
    """切换域名阻止状态"""
    domain_manager = DomainManager(db)
    return domain_manager.toggle_blocked_domain(domain_id)

@router.get("/whitelist", response_model=List[WhitelistDomainResponse])
async def get_whitelist_domains(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    db: Session = Depends(get_db)
):
    """获取所有白名单域名"""
    domain_manager = DomainManager(db)
    return domain_manager.get_whitelist_domains(skip=skip, limit=limit)

@router.post("/whitelist", response_model=WhitelistDomainResponse)
async def add_whitelist_domain(
    domain_data: WhitelistDomainCreate,
    db: Session = Depends(get_db)
):
    """添加白名单域名"""
    domain_manager = DomainManager(db)
    return domain_manager.create_whitelist_domain(domain_data)

@router.delete("/whitelist/{domain_id}")
async def remove_whitelist_domain(
    domain_id: int,
    db: Session = Depends(get_db)
):
    """删除白名单域名"""
    domain_manager = DomainManager(db)
    domain = domain_manager.delete_whitelist_domain(domain_id)
    return {"success": True, "message": f"Domain {domain} removed from whitelist successfully", "domain": domain}
