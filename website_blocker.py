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
    
    def _is_packaged(self) -> bool:
        """检测是否在打包环境中运行"""
        # 方法1: sys.frozen (cx_Freeze, py2exe)
        if getattr(sys, 'frozen', False):
            return True

        # 方法2: sys._MEIPASS (PyInstaller)
        if hasattr(sys, '_MEIPASS'):
            return True

        # 方法3: 检查可执行文件扩展名 (Nuitka)
        if sys.executable:
            exe_path = sys.executable
            exe_name = os.path.basename(exe_path).lower()

            # 如果可执行文件名不是Python解释器，则是打包环境
            python_interpreters = ('python.exe', 'pythonw.exe', 'python3.exe', 'python3w.exe',
                                   'python3.8.exe', 'python3.9.exe', 'python3.10.exe',
                                   'python3.11.exe', 'python3.12.exe', 'python3.13.exe')

            if exe_name not in python_interpreters:
                return True

        # 方法4: Nuitka 特定检测
        # Nuitka 会创建 .dist 目录
        if hasattr(sys, 'executable'):
            exe_dir = os.path.dirname(sys.executable)
            if exe_dir.endswith('.dist') or '.dist' in exe_dir:
                return True

        return False

    def _get_executable_path(self) -> str:
        """获取正确的可执行文件路径"""
        exe_path = sys.executable
        logger.debug(f"_get_executable_path: sys.executable={exe_path}")

        # 检查sys.argv[0]是否是编译后的exe文件（优先检查）
        if len(sys.argv) > 0:
            argv_path = os.path.abspath(sys.argv[0])
            logger.debug(f"_get_executable_path: sys.argv[0]={argv_path}")

            if argv_path.endswith('.exe'):
                # 检查是否是Python解释器
                exe_name = os.path.basename(argv_path).lower()
                python_interpreters = ('python.exe', 'pythonw.exe', 'python3.exe', 'python3w.exe')

                if exe_name not in python_interpreters:
                    # sys.argv[0]是编译后的可执行文件
                    if os.path.isfile(argv_path):
                        logger.info(f"检测到编译后的可执行文件 (sys.argv[0]): {argv_path}")
                        return argv_path

        # 尝试规范化路径（处理DOS短路径）
        try:
            import ctypes
            buffer = ctypes.create_unicode_buffer(260)
            ctypes.windll.kernel32.GetLongPathNameW(exe_path, buffer, 260)
            normalized_path = buffer.value if buffer.value else exe_path
            logger.debug(f"_get_executable_path: 规范化路径={normalized_path}")
        except Exception:
            normalized_path = exe_path

        # 检查sys.executable是否存在且是有效文件
        if os.path.isfile(normalized_path):
            exe_name = os.path.basename(normalized_path).lower()
            python_interpreters = ('python.exe', 'pythonw.exe', 'python3.exe', 'python3w.exe')

            if exe_name not in python_interpreters:
                # sys.executable是编译后的可执行文件
                logger.info(f"使用sys.executable: {normalized_path}")
                return normalized_path

        # 回退：检查是否在.dist目录中
        if exe_path:
            exe_dir = os.path.dirname(exe_path)
            if '.dist' in exe_dir.lower() or exe_dir.endswith('.dist'):
                if os.path.exists(exe_dir):
                    for file in os.listdir(exe_dir):
                        if file.endswith('.exe') and not file.lower().startswith('python'):
                            potential_exe = os.path.join(exe_dir, file)
                            logger.info(f"在.dist目录中找到可执行文件: {potential_exe}")
                            return potential_exe

        logger.warning(f"无法确定正确的可执行文件路径，使用默认: {exe_path}")
        return exe_path

    def _run_as_admin(self) -> bool:
        """以管理员权限重新启动程序"""
        try:
            if platform.system() == "Windows":
                # 获取正确的可执行文件路径
                exe_path = self._get_executable_path()
                working_dir = os.path.dirname(exe_path)

                logger.info(f"检测打包环境: frozen={getattr(sys, 'frozen', False)}")
                logger.info(f"sys.executable: {sys.executable}")
                logger.info(f"实际使用路径: {exe_path}")
                logger.info(f"工作目录: {working_dir}")
                logger.info(f"文件存在: {os.path.exists(exe_path)}")

                if self._is_packaged():
                    # 打包环境：直接运行可执行文件，参数为None
                    params = None
                    logger.info(f"打包环境 - 请求管理员权限重启")
                else:
                    # 开发环境：使用Python解释器和脚本路径
                    script = os.path.abspath(sys.argv[0])
                    params = f'"{script}"'
                    logger.info(f"开发环境 - 请求管理员权限重启: {exe_path} {params}")

                # 确保文件存在
                if not os.path.exists(exe_path):
                    logger.error(f"可执行文件不存在: {exe_path}")
                    return False

                # 使用ShellExecute重新启动程序，并请求管理员权限
                # "runas" 表示以管理员权限运行
                result = ctypes.windll.shell32.ShellExecuteW(
                    None,           # hwnd
                    "runas",        # 操作：请求管理员权限
                    exe_path,       # 可执行文件路径
                    params,         # 参数（打包环境为None）
                    working_dir,    # 工作目录
                    1               # SW_SHOWNORMAL
                )

                # ShellExecuteW返回值说明
                # > 32: 成功
                # 0: 内存不足
                # 2: 文件未找到
                # 3: 路径未找到
                # 5: 访问被拒绝
                # 31: 无应用程序关联
                # 32: DLL未找到

                if result > 32:
                    logger.info(f"管理员权限请求成功，返回值: {result}")
                    return True
                else:
                    error_messages = {
                        0: "内存不足",
                        2: "文件未找到",
                        3: "路径未找到",
                        5: "访问被拒绝",
                        31: "无应用程序关联",
                        32: "DLL未找到"
                    }
                    error_msg = error_messages.get(result, f"未知错误")
                    logger.error(f"管理员权限请求失败，错误码: {result} ({error_msg})")
                    return False
            return False
        except Exception as e:
            logger.error(f"请求管理员权限失败: {str(e)}")
            import traceback
            logger.debug(f"详细错误: {traceback.format_exc()}")
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