import platform
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.core.logger import logger
from app.core.error_handler import WebsiteBlockerException, ErrorCode

class NotificationManager:
    """通知系统核心服务"""
    
    def __init__(self):
        self.enabled = settings.notifications_enabled
        self.notification_frequency = settings.notification_frequency
        self._notification_backend = None
        self._initialize_backend()
    
    def _initialize_backend(self):
        """
        初始化通知后端
        """
        try:
            system = platform.system()
            if system == "Windows":
                # Windows平台
                from plyer import notification
                self._notification_backend = notification
                logger.info("初始化Windows通知后端")
            elif system == "Darwin":
                # macOS平台
                from plyer import notification
                self._notification_backend = notification
                logger.info("初始化macOS通知后端")
            elif system == "Linux":
                # Linux平台
                from plyer import notification
                self._notification_backend = notification
                logger.info("初始化Linux通知后端")
            else:
                logger.warning(f"不支持的平台: {system}")
                self._notification_backend = None
        except Exception as e:
            logger.error(f"初始化通知后端失败: {str(e)}")
            self._notification_backend = None
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取通知配置
        
        Returns:
            Dict[str, Any]: 通知配置信息
        """
        return {
            "enabled": self.enabled,
            "notification_frequency": self.notification_frequency,
            "backend": "plyer" if self._notification_backend else "none",
            "platform": platform.system()
        }
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        更新通知配置
        
        Args:
            config: 新的通知配置
        """
        if "enabled" in config:
            self.enabled = config["enabled"]
        if "notification_frequency" in config:
            self.notification_frequency = config["notification_frequency"]
        logger.info(f"更新通知配置: {config}")
    
    def toggle(self) -> bool:
        """
        切换通知开关
        
        Returns:
            bool: 切换后的状态
        """
        self.enabled = not self.enabled
        logger.info(f"切换通知状态: {self.enabled}")
        return self.enabled
    
    def send_notification(self, title: str, message: str, app_name: str = "Website Blocker") -> bool:
        """
        发送通知
        
        Args:
            title: 通知标题
            message: 通知内容
            app_name: 应用名称
            
        Returns:
            bool: 是否发送成功
        """
        if not self.enabled:
            logger.debug(f"通知已禁用，跳过发送: {title}")
            return False
        
        if not self._notification_backend:
            logger.warning("通知后端未初始化，跳过发送通知")
            return False
        
        try:
            # 使用plyer发送通知
            self._notification_backend.notify(
                title=title,
                message=message,
                app_name=app_name,
                timeout=10  # 通知显示10秒
            )
            logger.info(f"发送通知成功: {title}")
            return True
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}")
            return False
    
    def send_scheduled_notification(self, title: str, message: str) -> bool:
        """
        发送计划通知
        
        Args:
            title: 通知标题
            message: 通知内容
            
        Returns:
            bool: 是否发送成功
        """
        if not self.enabled:
            logger.debug(f"通知已禁用，跳过发送计划通知: {title}")
            return False
        
        return self.send_notification(title, message)
    
    def generate_statistics_report(self) -> Dict[str, Any]:
        """
        生成统计报告
        
        Returns:
            Dict[str, Any]: 统计报告数据
        """
        from app.db.session import SessionLocal
        from app.models.blocked_domain import BlockedDomain
        
        db = SessionLocal()
        try:
            # 统计被阻止的域名数量
            total_blocked_domains = db.query(BlockedDomain).count()
            active_blocked_domains = db.query(BlockedDomain).filter(BlockedDomain.active == True).count()
            
            return {
                "total_blocked_domains": total_blocked_domains,
                "active_blocked_domains": active_blocked_domains,
                "report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        finally:
            db.close()
    
    def send_daily_report(self) -> bool:
        """
        发送每日报告
        
        Returns:
            bool: 是否发送成功
        """
        if self.notification_frequency != "daily":
            return False
        
        stats = self.generate_statistics_report()
        title = "每日网站访问限制报告"
        message = f"""网站访问限制工具每日报告\n\n"\
                  f"报告时间: {stats['report_time']}\n"\
                  f"累计拦截网站数量: {stats['total_blocked_domains']}\n"\
                  f"当前激活拦截: {stats['active_blocked_domains']}\n"\
                  f"""
        
        return self.send_scheduled_notification(title, message)
    
    def send_weekly_report(self) -> bool:
        """
        发送每周报告
        
        Returns:
            bool: 是否发送成功
        """
        if self.notification_frequency != "weekly":
            return False
        
        stats = self.generate_statistics_report()
        title = "每周网站访问限制报告"
        message = f"""网站访问限制工具每周报告\n\n"\
                  f"报告时间: {stats['report_time']}\n"\
                  f"累计拦截网站数量: {stats['total_blocked_domains']}\n"\
                  f"当前激活拦截: {stats['active_blocked_domains']}\n"\
                  f"""
        
        return self.send_scheduled_notification(title, message)
    
    def send_block_notification(self, domain: str) -> bool:
        """
        发送域名被阻止的通知
        
        Args:
            domain: 被阻止的域名
            
        Returns:
            bool: 是否发送成功
        """
        return self.send_notification(
            title="网站已被阻止",
            message=f"网站 {domain} 已被阻止访问",
            app_name="Website Blocker"
        )
    
    def send_unblock_notification(self, domain: str) -> bool:
        """
        发送域名被解除阻止的通知
        
        Args:
            domain: 被解除阻止的域名
            
        Returns:
            bool: 是否发送成功
        """
        return self.send_notification(
            title="网站已解除阻止",
            message=f"网站 {domain} 已解除阻止",
            app_name="Website Blocker"
        )
    
    def send_hosts_update_notification(self, domain_count: int) -> bool:
        """
        发送Hosts文件更新的通知
        
        Args:
            domain_count: 更新的域名数量
            
        Returns:
            bool: 是否发送成功
        """
        return self.send_notification(
            title="Hosts文件已更新",
            message=f"Hosts文件已更新，共处理 {domain_count} 个域名",
            app_name="Website Blocker"
        )
    
    def send_schedule_notification(self, schedule_name: str, status: str) -> bool:
        """
        发送调度任务执行结果的通知
        
        Args:
            schedule_name: 调度任务名称
            status: 执行状态 (success, failed)
            
        Returns:
            bool: 是否发送成功
        """
        if status == "success":
            title = "调度任务执行成功"
            message = f"调度任务 {schedule_name} 执行成功"
        else:
            title = "调度任务执行失败"
            message = f"调度任务 {schedule_name} 执行失败"
        
        return self.send_notification(
            title=title,
            message=message,
            app_name="Website Blocker"
        )

# 创建全局通知管理器实例
notification_manager = NotificationManager()
