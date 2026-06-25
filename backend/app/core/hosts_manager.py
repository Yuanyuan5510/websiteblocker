import os
import shutil
import subprocess
import platform
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.error_handler import WebsiteBlockerException, ErrorCode
from app.core.logger import logger
from app.models.blocked_domain import BlockedDomain
from app.models.whitelist import WhitelistDomain as Whitelist

class HostsManager:
    """Hosts文件管理核心服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.hosts_path = settings.hosts_file_path
        self.block_comment_start = settings.block_comment_start
        self.block_comment_end = settings.block_comment_end
        self.redirect_ip = settings.redirect_ip
    
    def _is_admin(self) -> bool:
        """
        检查是否以管理员/root权限运行
        
        Returns:
            bool: 是否具有管理员权限
        """
        try:
            if platform.system() == "Windows":
                # 使用ctypes检查Windows管理员权限
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                # 非Windows系统，检查是否为root用户
                return os.geteuid() == 0
        except Exception as e:
            logger.error(f"检查管理员权限失败: {str(e)}")
            return False
    
    def read_hosts(self) -> str:
        """
        读取Hosts文件内容
        
        Returns:
            str: Hosts文件内容
            
        Raises:
            WebsiteBlockerException: 文件读取失败
        """
        try:
            with open(self.hosts_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_NOT_FOUND,
                message=f"Hosts文件不存在: {self.hosts_path}",
                status_code=404
            )
        except PermissionError:
            raise WebsiteBlockerException(
                error_code=ErrorCode.PERMISSION_DENIED,
                message=f"没有权限读取Hosts文件: {self.hosts_path}",
                status_code=403
            )
        except Exception as e:
            logger.error(f"读取Hosts文件失败: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_OPERATION_FAILED,
                message=f"读取Hosts文件失败: {str(e)}",
                status_code=500
            )
    
    def write_hosts(self, content: str) -> None:
        """
        写入Hosts文件内容
        
        Args:
            content: 要写入的内容
            
        Raises:
            WebsiteBlockerException: 文件写入失败
        """
        try:
            with open(self.hosts_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Hosts文件写入成功: {self.hosts_path}")
        except PermissionError:
            raise WebsiteBlockerException(
                error_code=ErrorCode.PERMISSION_DENIED,
                message=f"没有权限写入Hosts文件: {self.hosts_path}",
                status_code=403
            )
        except Exception as e:
            logger.error(f"写入Hosts文件失败: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_OPERATION_FAILED,
                message=f"写入Hosts文件失败: {str(e)}",
                status_code=500
            )
    
    def backup_hosts(self, backup_path: Optional[str] = None) -> str:
        """
        备份Hosts文件
        
        Args:
            backup_path: 备份文件路径，默认为自动生成
            
        Returns:
            str: 备份文件路径
            
        Raises:
            WebsiteBlockerException: 备份失败
        """
        try:
            # 自动生成备份路径
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = os.path.join(os.path.dirname(self.hosts_path), "backups")
                os.makedirs(backup_dir, exist_ok=True)
                backup_path = os.path.join(backup_dir, f"hosts_{timestamp}.bak")
            
            # 执行备份
            shutil.copy2(self.hosts_path, backup_path)
            logger.info(f"Hosts文件备份成功: {backup_path}")
            return backup_path
        except FileNotFoundError:
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_NOT_FOUND,
                message=f"Hosts文件不存在: {self.hosts_path}",
                status_code=404
            )
        except PermissionError:
            raise WebsiteBlockerException(
                error_code=ErrorCode.PERMISSION_DENIED,
                message=f"没有权限备份Hosts文件",
                status_code=403
            )
        except Exception as e:
            logger.error(f"备份Hosts文件失败: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_OPERATION_FAILED,
                message=f"备份Hosts文件失败: {str(e)}",
                status_code=500
            )
    
    def restore_hosts(self, backup_path: str) -> None:
        """
        从备份恢复Hosts文件
        
        Args:
            backup_path: 备份文件路径
            
        Raises:
            WebsiteBlockerException: 恢复失败
        """
        try:
            # 检查备份文件是否存在
            if not os.path.exists(backup_path):
                raise WebsiteBlockerException(
                    error_code=ErrorCode.FILE_NOT_FOUND,
                    message=f"备份文件不存在: {backup_path}",
                    status_code=404
                )
            
            # 执行恢复
            shutil.copy2(backup_path, self.hosts_path)
            logger.info(f"Hosts文件从备份恢复成功: {backup_path}")
            
            # 刷新DNS缓存
            self.refresh_dns()
        except PermissionError:
            raise WebsiteBlockerException(
                error_code=ErrorCode.PERMISSION_DENIED,
                message=f"没有权限恢复Hosts文件",
                status_code=403
            )
        except Exception as e:
            logger.error(f"恢复Hosts文件失败: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_OPERATION_FAILED,
                message=f"恢复Hosts文件失败: {str(e)}",
                status_code=500
            )
    
    def update_hosts_from_database(self) -> None:
        """
        从数据库更新Hosts文件
        
        Raises:
            WebsiteBlockerException: 更新失败
        """
        try:
            # 1. 读取当前Hosts文件内容，排除我们添加的阻止区域
            current_content = self.read_hosts()
            lines = current_content.splitlines()
            
            # 2. 分离出非阻止区域的内容
            new_lines = []
            in_block_section = False
            
            for line in lines:
                line_stripped = line.strip()
                if line_stripped == self.block_comment_start:
                    in_block_section = True
                elif line_stripped == self.block_comment_end:
                    in_block_section = False
                elif not in_block_section:
                    new_lines.append(line)
            
            # 3. 获取所有激活的被阻止域名
            blocked_domains = self.db.query(BlockedDomain).filter(BlockedDomain.active == True).all()
            whitelist_domains = [w.domain for w in self.db.query(Whitelist).all()]
            
            # 4. 添加阻止区域
            if blocked_domains:
                new_lines.append("\n" + self.block_comment_start)
                
                for domain in blocked_domains:
                    # 检查是否在白名单中
                    if domain.domain not in whitelist_domains:
                        # 添加主域名和www版本
                        new_lines.append(f"{self.redirect_ip} {domain.domain}")
                        new_lines.append(f"{self.redirect_ip} www.{domain.domain}")
                
                new_lines.append(self.block_comment_end)
            
            # 5. 写入新的Hosts文件内容
            new_content = "\n".join(new_lines)
            self.write_hosts(new_content)
            
            # 6. 刷新DNS缓存
            self.refresh_dns()
            
            logger.info(f"Hosts文件从数据库更新成功，共阻止 {len(blocked_domains)} 个域名")
        except WebsiteBlockerException:
            raise
        except Exception as e:
            logger.error(f"从数据库更新Hosts文件失败: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_OPERATION_FAILED,
                message=f"从数据库更新Hosts文件失败: {str(e)}",
                status_code=500
            )
    
    def refresh_dns(self) -> None:
        """
        刷新DNS缓存
        
        Raises:
            WebsiteBlockerException: 刷新失败
        """
        try:
            system = platform.system()
            if system == "Windows":
                # Windows系统
                subprocess.run(["ipconfig", "/flushdns"], check=True, shell=True)
            elif system == "Darwin":  # macOS
                # macOS系统
                subprocess.run(["dscacheutil", "-flushcache"], check=True)
                subprocess.run(["sudo", "killall", "-HUP", "mDNSResponder"], check=True)
            else:  # Linux
                # Linux系统，根据不同的DNS服务刷新缓存
                try:
                    subprocess.run(["systemctl", "restart", "systemd-resolved"], check=True)
                except:
                    try:
                        subprocess.run(["service", "dnsmasq", "restart"], check=True)
                    except:
                        logger.warning("无法自动刷新Linux DNS缓存，请手动刷新或重启网络服务")
                        return
            
            logger.info("DNS缓存已刷新")
        except Exception as e:
            logger.warning(f"刷新DNS缓存失败: {str(e)}")
            # 不抛出异常，因为刷新DNS缓存失败不影响主要功能
    
    def get_all_domains_from_hosts(self) -> List[str]:
        """
        从Hosts文件获取所有域名
        
        Returns:
            List[str]: 域名列表
            
        Raises:
            WebsiteBlockerException: 读取文件失败
        """
        try:
            content = self.read_hosts()
            lines = content.splitlines()
            domains = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 提取域名
                parts = line.split()
                if len(parts) >= 2:
                    # 跳过我们添加的阻止区域中的域名
                    if not any(comment in line for comment in [self.block_comment_start, self.block_comment_end]):
                        domains.append(parts[1])
            
            return domains
        except WebsiteBlockerException:
            raise
        except Exception as e:
            logger.error(f"从Hosts文件提取域名失败: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_OPERATION_FAILED,
                message=f"从Hosts文件提取域名失败: {str(e)}",
                status_code=500
            )
    
    def disable_all_blocks(self) -> None:
        """
        禁用所有阻止规则
        
        Raises:
            WebsiteBlockerException: 操作失败
        """
        try:
            # 1. 读取当前Hosts文件内容
            current_content = self.read_hosts()
            lines = current_content.splitlines()
            
            # 2. 移除阻止区域
            new_lines = []
            in_block_section = False
            
            for line in lines:
                line_stripped = line.strip()
                if line_stripped == self.block_comment_start:
                    in_block_section = True
                elif line_stripped == self.block_comment_end:
                    in_block_section = False
                elif not in_block_section:
                    new_lines.append(line)
            
            # 3. 写入新的Hosts文件内容
            new_content = "\n".join(new_lines)
            self.write_hosts(new_content)
            
            # 4. 刷新DNS缓存
            self.refresh_dns()
            
            logger.info("所有阻止规则已禁用")
        except WebsiteBlockerException:
            raise
        except Exception as e:
            logger.error(f"禁用所有阻止规则失败: {str(e)}")
            raise WebsiteBlockerException(
                error_code=ErrorCode.FILE_OPERATION_FAILED,
                message=f"禁用所有阻止规则失败: {str(e)}",
                status_code=500
            )
    
    def enable_all_blocks(self) -> None:
        """
        启用所有阻止规则
        
        Raises:
            WebsiteBlockerException: 操作失败
        """
        # 实际上就是从数据库更新Hosts文件
        self.update_hosts_from_database()
        logger.info("所有阻止规则已启用")
