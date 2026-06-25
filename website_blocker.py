# -*- coding: utf-8 -*-
"""
网站阻止核心功能模块
负责处理hosts文件操作、网站阻止/解除阻止等核心功能
"""

import os
import platform
import re
import shutil
import subprocess
import sys
from typing import List, Dict, Any, Optional
import logging
import ctypes

from logging_config import logger
from error_handler import ErrorHandler, ErrorType, ErrorInfo, error_handler
from data_exchange import data_exchange

class WebsiteBlocker:
    """网站阻止核心功能类"""
    
    def __init__(self):
        self.hosts_path = self._get_hosts_path()
        self.BLOCK_COMMENT_START = "# WEBSITE BLOCKER START"
        self.BLOCK_COMMENT_END = "# WEBSITE BLOCKER END"
        self.redirect_ip = "127.0.0.1"
        self.blocked_websites = []
        
        # 注册错误处理回调
        error_handler.register_error_callback(ErrorType.PERMISSION_ERROR, self._handle_permission_error)
    
    def _get_hosts_path(self) -> str:
        """获取hosts文件路径"""
        system = platform.system()
        if system == "Windows":
            return os.path.join(os.environ["SystemRoot"], "System32", "drivers", "etc", "hosts")
        elif system == "Darwin":  # macOS
            return "/private/etc/hosts"
        else:  # Linux 和其他 Unix 系统
            return "/etc/hosts"
    
    def _is_admin(self) -> bool:
        """检查是否以管理员/root权限运行"""
        try:
            if platform.system() == "Windows":
                # 使用更可靠的Windows管理员权限检查方法
                try:
                    import win32security
                    import win32api
                    
                    # 获取当前用户的SID
                    sid = win32security.CreateWellKnownSid(win32security.WinBuiltinAdministratorsSid, None)
                    
                    # 检查当前进程是否具有管理员权限
                    token = win32security.OpenProcessToken(
                        win32api.GetCurrentProcess(),
                        win32security.TOKEN_QUERY
                    )
                    
                    # 检查是否在管理员组中
                    is_admin = win32security.CheckTokenMembership(None, sid)
                    return is_admin
                except ImportError:
                    # 如果win32security不可用，回退到原始方法
                    try:
                        return ctypes.windll.shell32.IsUserAnAdmin()
                    except:
                        return False
            else:
                # 非Windows系统，检查是否为root用户
                return os.geteuid() == 0
        except Exception as e:
            logger.error(f"检查管理员权限失败: {str(e)}")
            return False
    
    def _run_as_admin(self) -> bool:
        """以管理员权限重新启动程序"""
        try:
            if platform.system() == "Windows":
                # 获取当前可执行文件路径
                script = os.path.abspath(sys.argv[0])
                
                # 使用ShellExecute重新启动程序，并请求管理员权限
                # "runas" 表示以管理员权限运行
                ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",
                    sys.executable,
                    f'"{script}"',
                    None,
                    1  # SW_SHOWNORMAL
                )
                return True
            return False
        except Exception as e:
            logger.error(f"请求管理员权限失败: {str(e)}")
            return False
    
    def _handle_permission_error(self, error_info: ErrorInfo):
        """处理权限错误"""
        logger.error("权限错误处理: 需要管理员权限")
        # 这里可以添加更多权限错误处理逻辑
    
    def backup_hosts(self, backup_path: str) -> bool:
        """备份hosts文件"""
        try:
            if not os.path.exists(self.hosts_path):
                logger.warning(f"hosts文件不存在，无法备份: {self.hosts_path}")
                return False
            
            # 确保备份目录存在
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            shutil.copy2(self.hosts_path, backup_path)
            logger.info(f"Hosts文件已备份到: {backup_path}")
            return True
            
        except Exception as e:
            error_info = ErrorInfo(
                ErrorType.FILE_OPERATION_ERROR,
                f"备份hosts文件失败",
                original_error=e,
                details={"hosts_path": self.hosts_path, "backup_path": backup_path}
            )
            error_handler.handle_error(error_info)
            return False
    
    def restore_hosts(self, backup_path: str) -> bool:
        """恢复hosts文件"""
        try:
            if not os.path.exists(backup_path):
                logger.warning(f"备份文件不存在，无法恢复: {backup_path}")
                return False
            
            shutil.copy2(backup_path, self.hosts_path)
            logger.info(f"Hosts文件已从备份恢复: {backup_path}")
            return True
            
        except Exception as e:
            error_info = ErrorInfo(
                ErrorType.FILE_OPERATION_ERROR,
                f"恢复hosts文件失败",
                original_error=e,
                details={"backup_path": backup_path, "hosts_path": self.hosts_path}
            )
            error_handler.handle_error(error_info)
            return False
    
    def load_blocked_websites(self) -> List[str]:
        """从hosts文件加载被阻止的网站列表"""
        try:
            self.blocked_websites = []
            if not os.path.exists(self.hosts_path):
                logger.warning(f"hosts文件不存在: {self.hosts_path}")
                return []
            
            in_block_section = False
            with open(self.hosts_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line == self.BLOCK_COMMENT_START:
                        in_block_section = True
                    elif line == self.BLOCK_COMMENT_END:
                        in_block_section = False
                    elif in_block_section and line.startswith(self.redirect_ip):
                        # 使用正则表达式分割，处理多个空格
                        parts = re.split(r'\s+', line)
                        if len(parts) > 1:
                            website = parts[1]
                            # 只添加主域名到内存列表，避免重复
                            if website.startswith('www.'):
                                domain = website[4:]
                            elif website.startswith('*.'):
                                domain = website[2:]
                            else:
                                domain = website
                            
                            if domain not in self.blocked_websites:
                                self.blocked_websites.append(domain)
            
            logger.info(f"从hosts文件解析到 {len(self.blocked_websites)} 个阻止网站: {self.blocked_websites}")
            return self.blocked_websites
            
        except Exception as e:
            error_info = ErrorInfo(
                ErrorType.FILE_OPERATION_ERROR,
                f"从hosts文件加载阻止网站失败",
                original_error=e,
                details={"hosts_path": self.hosts_path}
            )
            error_handler.handle_error(error_info)
            return []
    
    def save_blocked_websites(self, allow_empty: bool = False) -> bool:
        """保存被阻止的网站列表到hosts文件"""
        try:
            # 检查管理员权限
            if not self._is_admin():
                error_info = ErrorInfo(
                    ErrorType.PERMISSION_ERROR,
                    f"需要管理员权限才能修改hosts文件",
                    details={"hosts_path": self.hosts_path}
                )
                error_handler.handle_error(error_info)
                return False
            
            # 读取现有内容（排除阻止区域）
            lines = []
            in_block_section = False
            
            if os.path.exists(self.hosts_path):
                with open(self.hosts_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped == self.BLOCK_COMMENT_START:
                            in_block_section = True
                        elif stripped == self.BLOCK_COMMENT_END:
                            in_block_section = False
                        elif not in_block_section:
                            lines.append(line)
            
            # 添加阻止区域
            if self.blocked_websites or allow_empty:
                lines.append(f"\n{self.BLOCK_COMMENT_START}\n")
                
                if self.blocked_websites:
                    for website in self.blocked_websites:
                        # 添加主域名和www版本
                        lines.append(f"{self.redirect_ip} {website}\n")
                        lines.append(f"{self.redirect_ip} www.{website}\n")
                
                lines.append(f"{self.BLOCK_COMMENT_END}\n")
            
            # 写入新的hosts文件
            with open(self.hosts_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            # 刷新DNS缓存
            self._flush_dns_cache()
            
            logger.info(f"成功保存 {len(self.blocked_websites)} 个阻止网站到hosts文件")
            return True
            
        except Exception as e:
            error_info = ErrorInfo(
                ErrorType.FILE_OPERATION_ERROR,
                f"保存阻止网站到hosts文件失败",
                original_error=e,
                details={"hosts_path": self.hosts_path, "website_count": len(self.blocked_websites)}
            )
            error_handler.handle_error(error_info)
            return False
    
    def add_website(self, website: str) -> bool:
        """添加网站到阻止列表"""
        try:
            # 清理域名格式
            cleaned_website = data_exchange._clean_domain(website)
            
            if not cleaned_website:
                error_info = ErrorInfo(
                    ErrorType.VALIDATION_ERROR,
                    f"无效的网站格式: {website}",
                    details={"website": website}
                )
                error_handler.handle_error(error_info)
                return False
            
            if cleaned_website in self.blocked_websites:
                logger.warning(f"网站已在阻止列表中: {cleaned_website}")
                return True
            
            self.blocked_websites.append(cleaned_website)
            logger.info(f"添加网站到阻止列表: {cleaned_website}")
            return True
            
        except Exception as e:
            error_info = ErrorInfo(
                ErrorType.RUNTIME_ERROR,
                f"添加网站失败",
                original_error=e,
                details={"website": website}
            )
            error_handler.handle_error(error_info)
            return False
    
    def remove_website(self, website: str) -> bool:
        """从阻止列表中移除网站"""
        try:
            # 清理域名格式
            cleaned_website = data_exchange._clean_domain(website)
            
            if cleaned_website in self.blocked_websites:
                self.blocked_websites.remove(cleaned_website)
                logger.info(f"从阻止列表移除网站: {cleaned_website}")
                return True
            else:
                logger.warning(f"网站不在阻止列表中: {cleaned_website}")
                return False
                
        except Exception as e:
            error_info = ErrorInfo(
                ErrorType.RUNTIME_ERROR,
                f"移除网站失败",
                original_error=e,
                details={"website": website}
            )
            error_handler.handle_error(error_info)
            return False
    
    def clear_all_websites(self) -> bool:
        """清除所有阻止的网站"""
        try:
            self.blocked_websites = []
            logger.info("清除所有阻止的网站")
            return True
            
        except Exception as e:
            error_info = ErrorInfo(
                ErrorType.RUNTIME_ERROR,
                f"清除所有网站失败",
                original_error=e
            )
            error_handler.handle_error(error_info)
            return False
    
    def _flush_dns_cache(self) -> None:
        """刷新DNS缓存"""
        try:
            system = platform.system()
            if system == "Windows":
                subprocess.run(["ipconfig", "/flushdns"], check=True, shell=True)
            elif system == "Darwin":  # macOS
                subprocess.run(["dscacheutil", "-flushcache"], check=True)
                subprocess.run(["sudo", "killall", "-HUP", "mDNSResponder"], check=True)
            else:  # Linux
                # 不同的Linux发行版有不同的方法
                try:
                    subprocess.run(["systemctl", "restart", "systemd-resolved"], check=True)
                except:
                    try:
                        subprocess.run(["service", "dnsmasq", "restart"], check=True)
                    except:
                        logger.info("无法自动刷新Linux DNS缓存，请手动刷新或重启网络服务")
            
            logger.info("DNS缓存已刷新")
            
        except Exception as e:
            logger.warning(f"刷新DNS缓存失败: {str(e)}")

# 创建全局WebsiteBlocker实例
website_blocker = WebsiteBlocker()