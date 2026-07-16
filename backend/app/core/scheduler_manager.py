import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from app.core.config import settings
from app.core.logger import logger
from app.core.error_handler import WebsiteBlockerException, ErrorCode
from app.core.hosts_manager import HostsManager
from app.models.schedule import Schedule as ScheduleModel
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from app.db.session import SessionLocal

class SchedulerManager:
    """调度器核心服务"""
    
    def __init__(self):
        self.jobstores = {
            'default': SQLAlchemyJobStore(url=settings.database_url)
        }
        self.executors = {
            'default': ThreadPoolExecutor(20)
        }
        self.job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=self.jobstores,
            executors=self.executors,
            job_defaults=self.job_defaults,
            timezone='Asia/Shanghai'
        )
        
        self.is_running = False
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取调度器状态
        
        Returns:
            Dict[str, Any]: 调度器状态信息
        """
        return {
            "isRunning": self.is_running,
            "jobstores": list(self.jobstores.keys()),
            "executors": list(self.executors.keys()),
            "jobsCount": len(self.scheduler.get_jobs())
        }
    
    def start(self) -> None:
        """
        启动调度器
        
        Raises:
            WebsiteBlockerException: 调度器启动失败
        """
        if self.is_running:
            logger.warning("调度器已经在运行中")
            return
        
        try:
            # 启动调度器
            self.scheduler.start()
            self.is_running = True
            
            # 添加系统内置的报告任务
            # 每日报告任务（每天0点执行）
            if not self.scheduler.get_job("daily_report"):
                self.scheduler.add_job(
                    func=self._execute_task,
                    trigger="cron",
                    id="daily_report",
                    name="每日报告",
                    args=["daily_report", {}],
                    replace_existing=True,
                    misfire_grace_time=60,
                    hour=0,
                    minute=0
                )
            
            # 每周报告任务（每周一0点执行）
            if not self.scheduler.get_job("weekly_report"):
                self.scheduler.add_job(
                    func=self._execute_task,
                    trigger="cron",
                    id="weekly_report",
                    name="每周报告",
                    args=["weekly_report", {}],
                    replace_existing=True,
                    misfire_grace_time=60,
                    day_of_week=0,
                    hour=0,
                    minute=0
                )
            
            # 从数据库加载所有激活的任务
            self._load_jobs_from_database()
            
            logger.info("调度器已启动")
        except Exception as e:
            logger.error(f"启动调度器失败: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.SCHEDULER_ERROR,
                message=f"启动调度器失败: {str(e)}",
                status_code=500
            )
    
    def stop(self) -> None:
        """
        停止调度器
        
        Raises:
            WebsiteBlockerException: 调度器停止失败
        """
        if not self.is_running:
            logger.warning("调度器已经停止")
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("调度器已停止")
        except Exception as e:
            logger.error(f"停止调度器失败: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.SCHEDULER_ERROR,
                message=f"停止调度器失败: {str(e)}",
                status_code=500
            )
    
    def restart(self) -> None:
        """
        重启调度器
        
        Raises:
            WebsiteBlockerException: 调度器重启失败
        """
        try:
            self.stop()
            self.start()
            logger.info("调度器已重启")
        except Exception as e:
            logger.error(f"重启调度器失败: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.SCHEDULER_ERROR,
                message=f"重启调度器失败: {str(e)}",
                status_code=500
            )
    
    def get_all_jobs(self) -> List[ScheduleModel]:
        """
        获取所有调度任务
        
        Returns:
            List[ScheduleModel]: 调度任务列表
        """
        db = SessionLocal()
        try:
            return db.query(ScheduleModel).all()
        finally:
            db.close()
    
    def get_job(self, job_id: str) -> Optional[ScheduleModel]:
        """
        获取单个调度任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            Optional[ScheduleModel]: 调度任务，不存在则返回None
        """
        db = SessionLocal()
        try:
            return db.query(ScheduleModel).filter(ScheduleModel.id == job_id).first()
        finally:
            db.close()
    
    def toggle_job(self, job_id: str) -> ScheduleModel:
        """
        切换调度任务的激活状态
        
        Args:
            job_id: 任务ID
            
        Returns:
            ScheduleModel: 更新后的调度任务
            
        Raises:
            WebsiteBlockerException: 任务不存在或操作失败
        """
        db = SessionLocal()
        try:
            db_schedule = db.query(ScheduleModel).filter(ScheduleModel.id == job_id).first()
            if not db_schedule:
                raise WebsiteBlockerException(
                    error_code=ErrorCode.RESOURCE_NOT_FOUND,
                    message=f"调度任务不存在: {job_id}",
                    status_code=404
                )
            
            # 切换状态
            new_active = not db_schedule.active
            db_schedule.active = new_active
            
            if new_active:
                # 激活任务：添加到调度器
                trigger = CronTrigger.from_crontab(db_schedule.cron_expression)
                job = self.scheduler.add_job(
                    func=self._execute_task,
                    trigger=trigger,
                    id=job_id,
                    name=db_schedule.name,
                    args=[db_schedule.task_type, db_schedule.params],
                    replace_existing=True,
                    misfire_grace_time=60
                )
                db_schedule.next_run_time = job.next_run_time
            else:
                # 停用任务：从调度器移除
                try:
                    self.scheduler.remove_job(job_id)
                except Exception:
                    pass  # 任务可能不在调度器中
                db_schedule.next_run_time = None
            
            db.commit()
            db.refresh(db_schedule)
            
            logger.info(f"切换调度任务状态: {job_id} -> {'激活' if new_active else '停用'}")
            return db_schedule
        except WebsiteBlockerException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"切换调度任务状态失败: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.SCHEDULER_ERROR,
                message=f"切换调度任务状态失败: {str(e)}",
                status_code=500
            )
        finally:
            db.close()
    
    def add_job(self, schedule_data: ScheduleCreate) -> str:
        """
        添加调度任务
        
        Args:
            schedule_data: 调度任务数据
            
        Returns:
            str: 任务ID
            
        Raises:
            WebsiteBlockerException: 添加任务失败
        """
        try:
            # 生成任务ID
            job_id = str(uuid.uuid4())
            
            # 创建触发器
            trigger = CronTrigger.from_crontab(schedule_data.cron_expression)
            
            # 添加任务到调度器
            job = self.scheduler.add_job(
                func=self._execute_task,
                trigger=trigger,
                id=job_id,
                name=schedule_data.name,
                args=[schedule_data.task_type, schedule_data.params],
                replace_existing=False,
                misfire_grace_time=60
            )
            
            # 保存到数据库
            db = SessionLocal()
            try:
                # 获取下一次运行时间（兼容不同APScheduler版本）
                next_run = None
                if hasattr(job, 'next_run_time'):
                    next_run = job.next_run_time
                elif hasattr(job, 'next_run'):
                    next_run = job.next_run
                
                db_schedule = ScheduleModel(
                    id=job_id,
                    name=schedule_data.name,
                    task_type=schedule_data.task_type,
                    cron_expression=schedule_data.cron_expression,
                    description=schedule_data.description,
                    params=schedule_data.params,
                    active=schedule_data.active,
                    next_run_time=next_run
                )
                db.add(db_schedule)
                db.commit()
                db.refresh(db_schedule)
            finally:
                db.close()
            
            logger.info(f"添加调度任务成功: {schedule_data.name} (ID: {job_id})")
            return job_id
        except Exception as e:
            logger.error(f"添加调度任务失败: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.SCHEDULER_ERROR,
                message=f"添加调度任务失败: {str(e)}",
                status_code=500
            )
    
    def update_job(self, job_id: str, schedule_data: ScheduleUpdate) -> None:
        """
        更新调度任务
        
        Args:
            job_id: 任务ID
            schedule_data: 更新后的任务数据
            
        Raises:
            WebsiteBlockerException: 更新任务失败
        """
        try:
            # 获取现有任务
            db = SessionLocal()
            try:
                db_schedule = db.query(ScheduleModel).filter(ScheduleModel.id == job_id).first()
                if not db_schedule:
                    raise WebsiteBlockerException(
                        error_code=ErrorCode.RESOURCE_NOT_FOUND,
                        message=f"调度任务不存在: {job_id}",
                        status_code=404
                    )
                
                # 更新数据库记录
                update_data = schedule_data.model_dump(exclude_unset=True)
                for field, value in update_data.items():
                    setattr(db_schedule, field, value)
                
                # 从调度器中移除现有任务
                self.scheduler.remove_job(job_id)
                
                # 如果任务是激活的，重新添加到调度器
                if db_schedule.active:
                    trigger = CronTrigger.from_crontab(db_schedule.cron_expression)
                    job = self.scheduler.add_job(
                        func=self._execute_task,
                        trigger=trigger,
                        id=job_id,
                        name=db_schedule.name,
                        args=[db_schedule.task_type, db_schedule.params],
                        replace_existing=False,
                        misfire_grace_time=60
                    )
                    db_schedule.next_run_time = job.next_run_time
                else:
                    db_schedule.next_run_time = None
                
                db.commit()
            finally:
                db.close()
            
            logger.info(f"更新调度任务成功: {job_id}")
        except WebsiteBlockerException:
            raise
        except Exception as e:
            logger.error(f"更新调度任务失败: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.SCHEDULER_ERROR,
                message=f"更新调度任务失败: {str(e)}",
                status_code=500
            )
    
    def remove_job(self, job_id: str) -> None:
        """
        删除调度任务
        
        Args:
            job_id: 任务ID
            
        Raises:
            WebsiteBlockerException: 删除任务失败
        """
        try:
            # 从调度器中移除任务
            self.scheduler.remove_job(job_id)
            
            # 从数据库中删除记录
            db = SessionLocal()
            try:
                db_schedule = db.query(ScheduleModel).filter(ScheduleModel.id == job_id).first()
                if db_schedule:
                    db.delete(db_schedule)
                    db.commit()
            finally:
                db.close()
            
            logger.info(f"删除调度任务成功: {job_id}")
        except Exception as e:
            logger.error(f"删除调度任务失败: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.SCHEDULER_ERROR,
                message=f"删除调度任务失败: {str(e)}",
                status_code=500
            )
    
    def _load_jobs_from_database(self) -> None:
        """
        从数据库加载调度任务
        """
        try:
            db = SessionLocal()
            try:
                # 获取所有激活的调度任务
                schedules = db.query(ScheduleModel).filter(ScheduleModel.active == True).all()
                
                for schedule in schedules:
                    try:
                        # 创建触发器
                        trigger = CronTrigger.from_crontab(schedule.cron_expression)
                        
                        # 添加任务到调度器
                        job = self.scheduler.add_job(
                            func=self._execute_task,
                            trigger=trigger,
                            id=schedule.id,
                            name=schedule.name,
                            args=[schedule.task_type, schedule.params],
                            replace_existing=True,
                            misfire_grace_time=60
                        )
                        
                        # 更新下次运行时间
                        schedule.next_run_time = job.next_run_time
                        db.commit()
                        
                        logger.info(f"从数据库加载调度任务: {schedule.name} (ID: {schedule.id})")
                    except Exception as e:
                        logger.error(f"加载调度任务失败: {schedule.name} (ID: {schedule.id}): {str(e)}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"从数据库加载调度任务失败: {str(e)}")
    
    def _execute_task(self, task_type: str, params: Dict[str, Any] = None) -> None:
        """
        执行调度任务
        
        Args:
            task_type: 任务类型
            params: 任务参数
        """
        logger.info(f"开始执行调度任务: {task_type}, 参数: {params}")
        
        try:
            from app.core.notification_manager import notification_manager
            
            if task_type == "block":
                self._block_domains(params)
                # 发送实时通知（如果用户设置为立即通知）
                if notification_manager.enabled and notification_manager.notification_frequency == "immediate":
                    if params and "domains" in params:
                        domains = params["domains"]
                        if domains:
                            domain_list = ", ".join(domains[:3]) + ("等" if len(domains) > 3 else "")
                            notification_manager.send_notification(
                                title="调度任务执行成功",
                                message=f"已自动阻止 {domain_list} 共 {len(domains)} 个域名"
                            )
            elif task_type == "unblock":
                self._unblock_domains(params)
                # 发送实时通知（如果用户设置为立即通知）
                if notification_manager.enabled and notification_manager.notification_frequency == "immediate":
                    if params and "domains" in params:
                        domains = params["domains"]
                        if domains:
                            domain_list = ", ".join(domains[:3]) + ("等" if len(domains) > 3 else "")
                            notification_manager.send_notification(
                                title="调度任务执行成功",
                                message=f"已自动解除阻止 {domain_list} 共 {len(domains)} 个域名"
                            )
            elif task_type == "update_hosts":
                self._update_hosts()
                # 发送实时通知（如果用户设置为立即通知）
                if notification_manager.enabled and notification_manager.notification_frequency == "immediate":
                    notification_manager.send_notification(
                        title="调度任务执行成功",
                        message="已自动更新Hosts文件"
                    )
            elif task_type == "daily_report":
                # 发送每日报告
                notification_manager.send_daily_report()
            elif task_type == "weekly_report":
                # 发送每周报告
                notification_manager.send_weekly_report()
            else:
                logger.error(f"未知的任务类型: {task_type}")
                return
            
            logger.info(f"调度任务执行成功: {task_type}")
        except Exception as e:
            logger.error(f"调度任务执行失败: {task_type}: {str(e)}")
            # 发送执行失败通知（如果用户设置为立即通知）
            from app.core.notification_manager import notification_manager
            if notification_manager.enabled and notification_manager.notification_frequency == "immediate":
                notification_manager.send_notification(
                    title="调度任务执行失败",
                    message=f"调度任务 {task_type} 执行失败，请检查日志"
                )
    
    def _block_domains(self, params: Dict[str, Any] = None):
        """
        执行阻止域名任务
        
        Args:
            params: 任务参数，包含要阻止的域名列表
        """
        logger.info(f"执行阻止域名任务，参数: {params}")
        
        if not params or "domains" not in params:
            logger.error("阻止域名任务缺少必要参数: domains")
            return
        
        domains = params["domains"]
        if not isinstance(domains, list) or len(domains) == 0:
            logger.error("阻止域名任务的域名列表无效")
            return
        
        try:
            from app.core.domain_manager import DomainManager
            from app.schemas.domain import BlockedDomainCreate
            
            db = SessionLocal()
            try:
                domain_manager = DomainManager(db)
                
                for domain in domains:
                    try:
                        domain_data = BlockedDomainCreate(
                            domain=domain,
                            reason="自动阻止: 调度任务",
                            category="scheduled"
                        )
                        domain_manager.create_blocked_domain(domain_data)
                        logger.info(f"成功阻止域名: {domain}")
                    except Exception as e:
                        logger.error(f"阻止域名失败: {domain}, 错误: {str(e)}")
            finally:
                db.close()
            
            logger.info(f"阻止域名任务执行完成，共处理 {len(domains)} 个域名")
        except Exception as e:
            logger.error(f"执行阻止域名任务失败: {str(e)}")
    
    def _unblock_domains(self, params: Dict[str, Any] = None):
        """
        执行解除阻止域名任务
        
        Args:
            params: 任务参数，包含要解除阻止的域名列表
        """
        logger.info(f"执行解除阻止域名任务，参数: {params}")
        
        if not params or "domains" not in params:
            logger.error("解除阻止域名任务缺少必要参数: domains")
            return
        
        domains = params["domains"]
        if not isinstance(domains, list) or len(domains) == 0:
            logger.error("解除阻止域名任务的域名列表无效")
            return
        
        try:
            from app.core.domain_manager import DomainManager
            
            db = SessionLocal()
            try:
                domain_manager = DomainManager(db)
                
                for domain in domains:
                    try:
                        # 查找域名ID
                        blocked_domain = domain_manager.get_blocked_domain_by_name(domain)
                        if blocked_domain:
                            domain_manager.delete_blocked_domain(blocked_domain.id)
                            logger.info(f"成功解除阻止域名: {domain}")
                        else:
                            logger.warning(f"域名 {domain} 未被阻止，跳过")
                    except Exception as e:
                        logger.error(f"解除阻止域名失败: {domain}, 错误: {str(e)}")
            finally:
                db.close()
            
            logger.info(f"解除阻止域名任务执行完成，共处理 {len(domains)} 个域名")
        except Exception as e:
            logger.error(f"执行解除阻止域名任务失败: {str(e)}")
    
    def _update_hosts(self):
        """
        执行更新Hosts文件任务
        """
        logger.info("执行更新Hosts文件任务")
        
        # 创建数据库会话
        db = SessionLocal()
        try:
            # 创建HostsManager实例
            hosts_manager = HostsManager(db)
            
            # 更新Hosts文件
            hosts_manager.update_hosts_from_database()
            
            logger.info("Hosts文件更新成功")
        finally:
            db.close()

# 创建全局调度器实例
scheduler_manager = SchedulerManager()
