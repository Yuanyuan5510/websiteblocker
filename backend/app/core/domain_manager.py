import re
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.blocked_domain import BlockedDomain
from app.models.whitelist import WhitelistDomain as Whitelist
from app.schemas.domain import BlockedDomainCreate, WhitelistDomainCreate, BlockedDomainUpdate, WhitelistDomainUpdate
from app.core.error_handler import WebsiteBlockerException, ErrorCode
from app.core.logger import logger

class DomainManager:
    """域名管理核心服务"""
    
    def __init__(self, db: Session):
        self.db = db
        from app.core.hosts_manager import HostsManager
        self.hosts_manager = HostsManager(db)
    
    @staticmethod
    def validate_domain(domain: str) -> str:
        """
        验证域名格式
        
        Args:
            domain: 域名字符串
            
        Returns:
            验证后的域名
            
        Raises:
            WebsiteBlockerException: 域名格式无效
        """
        # 移除前后空格
        domain = domain.strip()
        
        # 简单的域名格式验证
        domain_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        if not re.match(domain_pattern, domain):
            raise WebsiteBlockerException(
                error_code=ErrorCode.INVALID_DOMAIN,
                message=f"无效的域名格式: {domain}",
                status_code=400
            )
        
        # 转换为小写
        domain = domain.lower()
        
        # 移除www前缀
        if domain.startswith("www."):
            domain = domain[4:]
        
        return domain
    
    # 被阻止域名相关方法
    def get_blocked_domains(self, skip: int = 0, limit: int = 100) -> List[BlockedDomain]:
        """
        获取被阻止的域名列表
        
        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            
        Returns:
            被阻止域名列表
        """
        return self.db.query(BlockedDomain).order_by(BlockedDomain.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_blocked_domain_by_id(self, domain_id: int) -> Optional[BlockedDomain]:
        """
        根据ID获取被阻止的域名
        
        Args:
            domain_id: 域名ID
            
        Returns:
            被阻止域名对象，不存在则返回None
        """
        return self.db.query(BlockedDomain).filter(BlockedDomain.id == domain_id).first()
    
    def get_blocked_domain_by_name(self, domain: str) -> Optional[BlockedDomain]:
        """
        根据域名获取被阻止的域名
        
        Args:
            domain: 域名
            
        Returns:
            被阻止域名对象，不存在则返回None
        """
        domain = self.validate_domain(domain)
        return self.db.query(BlockedDomain).filter(BlockedDomain.domain == domain).first()
    
    def create_blocked_domain(self, domain_data: BlockedDomainCreate) -> BlockedDomain:
        """
        创建被阻止域名
        
        Args:
            domain_data: 被阻止域名数据
            
        Returns:
            创建的被阻止域名对象
            
        Raises:
            WebsiteBlockerException: 域名已被阻止或格式无效
        """
        # 验证域名格式
        domain = self.validate_domain(domain_data.domain)
        
        # 检查域名是否已在白名单中
        if self.db.query(Whitelist).filter(Whitelist.domain == domain).first():
            raise WebsiteBlockerException(
                error_code=ErrorCode.DOMAIN_ALREADY_BLOCKED,
                message=f"域名 {domain} 已在白名单中，无法阻止",
                status_code=400
            )
        
        # 创建被阻止域名对象
        db_domain = BlockedDomain(
            domain=domain,
            reason=domain_data.reason or "",
            category=domain_data.category or ""
        )
        
        try:
            self.db.add(db_domain)
            self.db.commit()
            self.db.refresh(db_domain)
            logger.info(f"Domain {domain} blocked successfully")
            # 自动更新Hosts文件
            self.hosts_manager.update_hosts_from_database()
            
            # 广播WebSocket消息
            try:
                from app.core.websocket_manager import websocket_manager
                import asyncio
                asyncio.create_task(websocket_manager.broadcast({
                    "type": "domain_updated",
                    "action": "add",
                    "domain_type": "blocked",
                    "domain": db_domain.domain,
                    "timestamp": "2026-01-04"
                }))
            except Exception as e:
                logger.error(f"Failed to broadcast WebSocket message: {str(e)}")
                
            return db_domain
        except IntegrityError:
            self.db.rollback()
            raise WebsiteBlockerException(
                error_code=ErrorCode.DOMAIN_ALREADY_BLOCKED,
                message=f"域名 {domain} 已被阻止",
                status_code=400
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to block domain {domain}: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_OPERATION_FAILED,
                message=f"阻止域名失败: {str(e)}",
                status_code=500
            )
    
    def update_blocked_domain(self, domain_id: int, domain_data: BlockedDomainUpdate) -> BlockedDomain:
        """
        更新被阻止域名
        
        Args:
            domain_id: 域名ID
            domain_data: 更新数据
            
        Returns:
            更新后的被阻止域名对象
            
        Raises:
            WebsiteBlockerException: 域名不存在或更新失败
        """
        # 获取域名
        db_domain = self.get_blocked_domain_by_id(domain_id)
        if not db_domain:
            raise WebsiteBlockerException(
                error_code=ErrorCode.RESOURCE_NOT_FOUND,
                message=f"被阻止的域名不存在，ID: {domain_id}",
                status_code=404
            )
        
        # 更新域名信息
        update_data = domain_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_domain, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(db_domain)
            logger.info(f"Blocked domain {db_domain.domain} updated successfully")
            return db_domain
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update blocked domain {db_domain.domain}: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_OPERATION_FAILED,
                message=f"更新被阻止域名失败: {str(e)}",
                status_code=500
            )
    
    def batch_create_blocked_domains(self, domains: List[str], reason: str = "", category: str = "template") -> Dict[str, Any]:
        """
        批量创建被阻止域名
        
        Args:
            domains: 域名列表
            reason: 阻止原因
            category: 域名分类
            
        Returns:
            批量操作结果，包含成功数量、失败数量和失败的域名列表
        """
        success_count = 0
        failure_count = 0
        failed_domains = []
        
        try:
            # 开启事务
            for domain_str in domains:
                try:
                    # 验证域名格式
                    domain = self.validate_domain(domain_str)
                    
                    # 检查域名是否已被阻止
                    if self.db.query(BlockedDomain).filter(BlockedDomain.domain == domain).first():
                        failure_count += 1
                        failed_domains.append(domain_str)
                        continue
                    
                    # 检查域名是否已在白名单中
                    if self.db.query(Whitelist).filter(Whitelist.domain == domain).first():
                        failure_count += 1
                        failed_domains.append(domain_str)
                        continue
                    
                    # 创建被阻止域名对象
                    db_domain = BlockedDomain(
                        domain=domain,
                        reason=reason,
                        category=category
                    )
                    
                    self.db.add(db_domain)
                    success_count += 1
                    logger.info(f"Domain {domain} blocked successfully")
                except Exception as e:
                    failure_count += 1
                    failed_domains.append(domain_str)
                    logger.error(f"Failed to block domain {domain_str}: {str(e)}")
            
            # 提交事务
            self.db.commit()
            
            # 统一更新Hosts文件，提高效率
            self.hosts_manager.update_hosts_from_database()
            
            # 广播WebSocket消息
            try:
                from app.core.websocket_manager import websocket_manager
                import asyncio
                asyncio.create_task(websocket_manager.broadcast({
                    "type": "batch_domains_updated",
                    "action": "add",
                    "domain_type": "blocked",
                    "success_count": success_count,
                    "failure_count": failure_count,
                    "timestamp": datetime.now().isoformat()
                }))
            except Exception as e:
                logger.error(f"Failed to broadcast WebSocket message: {str(e)}")
            
            return {
                "success_count": success_count,
                "failure_count": failure_count,
                "failed_domains": failed_domains
            }
        except Exception as e:
            # 回滚事务
            self.db.rollback()
            logger.error(f"Batch create blocked domains failed: {str(e)}")
            return {
                "success_count": 0,
                "failure_count": len(domains),
                "failed_domains": domains
            }
    
    def delete_blocked_domain(self, domain_id: int) -> str:
        """
        删除被阻止域名
        
        Args:
            domain_id: 域名ID
            
        Returns:
            删除的域名
            
        Raises:
            WebsiteBlockerException: 域名不存在或删除失败
        """
        # 获取域名
        db_domain = self.get_blocked_domain_by_id(domain_id)
        if not db_domain:
            raise WebsiteBlockerException(
                error_code=ErrorCode.RESOURCE_NOT_FOUND,
                message=f"被阻止的域名不存在，ID: {domain_id}",
                status_code=404
            )
        
        domain = db_domain.domain
        
        try:
            self.db.delete(db_domain)
            self.db.commit()
            logger.info(f"Blocked domain {domain} deleted successfully")
            # 自动更新Hosts文件
            self.hosts_manager.update_hosts_from_database()
            
            # 广播WebSocket消息
            try:
                from app.core.websocket_manager import websocket_manager
                import asyncio
                asyncio.create_task(websocket_manager.broadcast({
                    "type": "domain_updated",
                    "action": "delete",
                    "domain_type": "blocked",
                    "domain": domain,
                    "timestamp": "2026-01-04"
                }))
            except Exception as e:
                logger.error(f"Failed to broadcast WebSocket message: {str(e)}")
                
            return domain
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete blocked domain {domain}: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_OPERATION_FAILED,
                message=f"删除被阻止域名失败: {str(e)}",
                status_code=500
            )
    
    def toggle_blocked_domain(self, domain_id: int) -> BlockedDomain:
        """
        切换被阻止域名的激活状态
        
        Args:
            domain_id: 域名ID
            
        Returns:
            更新后的被阻止域名对象
            
        Raises:
            WebsiteBlockerException: 域名不存在或操作失败
        """
        # 获取域名
        db_domain = self.get_blocked_domain_by_id(domain_id)
        if not db_domain:
            raise WebsiteBlockerException(
                error_code=ErrorCode.RESOURCE_NOT_FOUND,
                message=f"被阻止的域名不存在，ID: {domain_id}",
                status_code=404
            )
        
        # 切换激活状态
        db_domain.active = not db_domain.active
        
        try:
            self.db.commit()
            self.db.refresh(db_domain)
            logger.info(f"Blocked domain {db_domain.domain} toggled to {db_domain.active}")
            # 自动更新Hosts文件
            self.hosts_manager.update_hosts_from_database()
            
            # 广播WebSocket消息
            try:
                from app.core.websocket_manager import websocket_manager
                import asyncio
                asyncio.create_task(websocket_manager.broadcast({
                    "type": "domain_updated",
                    "action": "toggle",
                    "domain_type": "blocked",
                    "domain": db_domain.domain,
                    "active": db_domain.active,
                    "timestamp": "2026-01-04"
                }))
            except Exception as e:
                logger.error(f"Failed to broadcast WebSocket message: {str(e)}")
                
            return db_domain
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to toggle blocked domain {db_domain.domain}: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_OPERATION_FAILED,
                message=f"切换被阻止域名状态失败: {str(e)}",
                status_code=500
            )
    
    # 白名单域名相关方法
    def get_whitelist_domains(self, skip: int = 0, limit: int = 100) -> List[Whitelist]:
        """
        获取白名单域名列表
        
        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            
        Returns:
            白名单域名列表
        """
        return self.db.query(Whitelist).order_by(Whitelist.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_whitelist_domain_by_id(self, domain_id: int) -> Optional[Whitelist]:
        """
        根据ID获取白名单域名
        
        Args:
            domain_id: 域名ID
            
        Returns:
            白名单域名对象，不存在则返回None
        """
        return self.db.query(Whitelist).filter(Whitelist.id == domain_id).first()
    
    def get_whitelist_domain_by_name(self, domain: str) -> Optional[Whitelist]:
        """
        根据域名获取白名单域名
        
        Args:
            domain: 域名
            
        Returns:
            白名单域名对象，不存在则返回None
        """
        domain = self.validate_domain(domain)
        return self.db.query(Whitelist).filter(Whitelist.domain == domain).first()
    
    def create_whitelist_domain(self, domain_data: WhitelistDomainCreate) -> Whitelist:
        """
        创建白名单域名
        
        Args:
            domain_data: 白名单域名数据
            
        Returns:
            创建的白名单域名对象
            
        Raises:
            WebsiteBlockerException: 域名已在白名单中或格式无效
        """
        # 验证域名格式
        domain = self.validate_domain(domain_data.domain)
        
        # 检查域名是否已被阻止
        if self.db.query(BlockedDomain).filter(BlockedDomain.domain == domain).first():
            raise WebsiteBlockerException(
                error_code=ErrorCode.RESOURCE_EXISTS,
                message=f"域名 {domain} 已被阻止，无法添加到白名单",
                status_code=400
            )
        
        # 创建白名单域名对象
        db_domain = Whitelist(
            domain=domain,
            reason=domain_data.reason or ""
        )
        
        try:
            self.db.add(db_domain)
            self.db.commit()
            self.db.refresh(db_domain)
            logger.info(f"Domain {domain} added to whitelist successfully")
            # 自动更新Hosts文件
            self.hosts_manager.update_hosts_from_database()
            
            # 广播WebSocket消息
            try:
                from app.core.websocket_manager import websocket_manager
                import asyncio
                asyncio.create_task(websocket_manager.broadcast({
                    "type": "domain_updated",
                    "action": "add",
                    "domain_type": "whitelist",
                    "domain": db_domain.domain,
                    "timestamp": "2026-01-04"
                }))
            except Exception as e:
                logger.error(f"Failed to broadcast WebSocket message: {str(e)}")
                
            return db_domain
        except IntegrityError:
            self.db.rollback()
            raise WebsiteBlockerException(
                error_code=ErrorCode.RESOURCE_EXISTS,
                message=f"域名 {domain} 已在白名单中",
                status_code=400
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add domain {domain} to whitelist: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_OPERATION_FAILED,
                message=f"添加域名到白名单失败: {str(e)}",
                status_code=500
            )
    
    def update_whitelist_domain(self, domain_id: int, domain_data: WhitelistDomainUpdate) -> Whitelist:
        """
        更新白名单域名
        
        Args:
            domain_id: 域名ID
            domain_data: 更新数据
            
        Returns:
            更新后的白名单域名对象
            
        Raises:
            WebsiteBlockerException: 域名不存在或更新失败
        """
        # 获取域名
        db_domain = self.get_whitelist_domain_by_id(domain_id)
        if not db_domain:
            raise WebsiteBlockerException(
                error_code=ErrorCode.RESOURCE_NOT_FOUND,
                message=f"白名单域名不存在，ID: {domain_id}",
                status_code=404
            )
        
        # 更新域名信息
        update_data = domain_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_domain, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(db_domain)
            logger.info(f"Whitelist domain {db_domain.domain} updated successfully")
            return db_domain
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update whitelist domain {db_domain.domain}: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_OPERATION_FAILED,
                message=f"更新白名单域名失败: {str(e)}",
                status_code=500
            )
    
    def delete_whitelist_domain(self, domain_id: int) -> str:
        """
        删除白名单域名
        
        Args:
            domain_id: 域名ID
            
        Returns:
            删除的域名
            
        Raises:
            WebsiteBlockerException: 域名不存在或删除失败
        """
        # 获取域名
        db_domain = self.get_whitelist_domain_by_id(domain_id)
        if not db_domain:
            raise WebsiteBlockerException(
                error_code=ErrorCode.RESOURCE_NOT_FOUND,
                message=f"白名单域名不存在，ID: {domain_id}",
                status_code=404
            )
        
        domain = db_domain.domain
        
        try:
            self.db.delete(db_domain)
            self.db.commit()
            logger.info(f"Whitelist domain {domain} deleted successfully")
            # 自动更新Hosts文件
            self.hosts_manager.update_hosts_from_database()
            
            # 广播WebSocket消息
            try:
                from app.core.websocket_manager import websocket_manager
                import asyncio
                asyncio.create_task(websocket_manager.broadcast({
                    "type": "domain_updated",
                    "action": "delete",
                    "domain_type": "whitelist",
                    "domain": domain,
                    "timestamp": "2026-01-04"
                }))
            except Exception as e:
                logger.error(f"Failed to broadcast WebSocket message: {str(e)}")
                
            return domain
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete whitelist domain {domain}: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_OPERATION_FAILED,
                message=f"删除白名单域名失败: {str(e)}",
                status_code=500
            )
