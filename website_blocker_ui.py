import os
import sys
import json
import shutil
import re
import ctypes
import logging
import platform
import time
import subprocess
import socket
import signal
import webbrowser
from datetime import datetime
import atexit
import math
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Version Info
APP_VERSION = "2.9"
UPDATE_URL = "https://websiteblocker.wangstation.dpdns.org/download.html"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('WebsiteBlocker')

# Set font
tk_font = ('SimHei', 10)

class WebsiteBlockerApp:
    def __init__(self, root):
        # Check admin privileges first
        if not self._is_admin():
            result = messagebox.askyesno(
                "权限不足", 
                "此程序需要管理员权限才能正常工作，是否以管理员身份重新启动程序？"
            )
            if result:
                if self._run_as_admin():
                    root.destroy()
                    sys.exit(0)
                else:
                    # 如果无法请求管理员权限，显示警告
                    messagebox.showwarning("权限警告", "无法以管理员身份启动程序，部分功能可能无法使用")
            else:
                # 用户拒绝以管理员身份运行，显示警告
                messagebox.showwarning("权限警告", "部分功能需要管理员权限才能使用，请手动以管理员身份运行程序")
        
        self.root = root
        self.root.title(f"Website Blocker V{APP_VERSION}")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=tk_font)
        self.style.configure("TLabel", font=tk_font)
        self.style.configure("TEntry", font=tk_font)
        self.style.configure("Treeview", font=tk_font)
        
        # 确保hosts文件路径正确
        self.hosts_path = self._get_hosts_path()
        self.backup_path = self.hosts_path + ".backup"
        self.BLOCK_COMMENT_START = "# WEBSITE BLOCKER START"
        self.BLOCK_COMMENT_END = "# WEBSITE BLOCKER END"
        self.redirect_ip = "127.0.0.1"
        print(f"V2.9 - 重定向IP设置为: {self.redirect_ip}")
        # Cloudflare WARP等服务检测绕过机制
        self.force_dns_priority = True
        
        # 初始化被阻止的网站列表
        self.blocked_websites = []
        
        # 获取用户配置目录，避免权限问题
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 使用统一配置路径: %APPDATA%\WebsiteBlocker
        self.user_config_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'WebsiteBlocker')
        os.makedirs(self.user_config_dir, exist_ok=True)
        self.config_file = os.path.join(self.user_config_dir, "config.json")
        
        # 记录配置文件路径信息
        logger.info(f"程序目录: {self.app_dir}")
        logger.info(f"用户配置目录: {self.user_config_dir}")
        logger.info(f"配置文件路径: {self.config_file}")
        print(f"V2.9 - hosts文件路径: {self.hosts_path}")
        
        # 初始化配置
        self.config = {
            "blocked_websites": [],
            "auto_clear_on_exit": False,  # V2.9默认不自动清除
            "external_storage_enabled": False  # 默认禁用外部存储
        }
        
        # 检查是否已获得管理员权限
        if self._is_admin():
            print("✓ 已获得管理员权限")
        else:
            print("⚠️  无管理员权限，部分功能可能无法使用")
        
        # 备份hosts文件（只在首次运行时备份）
        if not os.path.exists(self.backup_path):
            self._backup_hosts()
        
        # 创建窗口图标（使用Python绘制）
        self._create_window_icon()
        
        # V2.9核心改进：优先从hosts文件读取现有阻止规则
        self._load_blocked_websites_from_hosts()
        print(f"从hosts文件加载阻止规则，当前阻止网站数量: {len(self.blocked_websites)}")
        print(f"当前阻止的网站列表: {self.blocked_websites}")
        
        # 加载配置文件（用于保存程序设置，不影响hosts规则）
        self._load_config()
        print(f"加载配置完成")
        
        # V2.9：取消默认限制设置，不再自动添加任何网站
        
        # 创建UI
        self._create_ui()
        print(f"UI创建完成")
        
        # 如果从hosts读取到规则，同步到配置文件
        if self.blocked_websites:
            self._save_config()
            print(f"已将hosts中的阻止规则同步到配置文件")
        
        # 设置退出处理
        self._setup_exit_handlers()
        
        # Show deprecation warning
        messagebox.showwarning(
            "版本不再支持", 
            "警告: Version 2.9 已不再支持。请考虑升级到最新版本。"
        )
        self._show_deprecation_warning()
    
    def _get_hosts_path(self):
        """获取hosts文件路径"""
        system = platform.system()
        if system == "Windows":
            return os.path.join(os.environ["SystemRoot"], "System32", "drivers", "etc", "hosts")
        elif system == "Darwin":  # macOS
            return "/private/etc/hosts"
        else:  # Linux 和其他 Unix 系统
            return "/etc/hosts"
    
    def _is_admin(self):
        """检查是否以管理员/root权限运行"""
        try:
            if platform.system() == "Windows":
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except:
            return False
            
    def _run_as_admin(self):
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
            print(f"请求管理员权限失败: {e}")
            return False
    
    def _backup_hosts(self):
        """备份hosts文件"""
        try:
            if os.path.exists(self.hosts_path):
                shutil.copy2(self.hosts_path, self.backup_path)
                print(f"Hosts文件已备份到: {self.backup_path}")
                return True
            return False
        except Exception as e:
            print(f"备份hosts失败: {str(e)}")
            messagebox.showerror("备份失败", f"无法备份hosts文件: {str(e)}")
            return False
    
    def _restore_hosts(self):
        """恢复hosts文件"""
        try:
            if os.path.exists(self.backup_path):
                shutil.copy2(self.backup_path, self.hosts_path)
                print("Hosts文件已恢复")
                return True
            return False
        except Exception as e:
            print(f"恢复hosts失败: {str(e)}")
            messagebox.showerror("恢复失败", f"无法恢复hosts文件: {str(e)}")
            return False
    
    def _load_blocked_websites_from_hosts(self):
        """V2.9核心功能：从hosts文件加载被阻止的网站列表"""
        try:
            self.blocked_websites = []
            if not os.path.exists(self.hosts_path):
                print("V2.9 - hosts文件不存在")
                return
            
            print(f"V2.9 - 开始读取hosts文件: {self.hosts_path}")
            
            # 读取整个hosts文件内容用于调试
            with open(self.hosts_path, 'r', encoding='utf-8') as f:
                hosts_content = f.read()
            
            print(f"V2.9 - hosts文件内容长度: {len(hosts_content)} 字符")
            print(f"V2.9 - 是否包含阻止区域标记: {self.BLOCK_COMMENT_START in hosts_content}")
            
            # 重新逐行读取并解析
            in_block_section = False
            with open(self.hosts_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    stripped_line = line.strip()
                    
                    if stripped_line == self.BLOCK_COMMENT_START:
                        in_block_section = True
                        print(f"V2.9 - 第{line_num}行: 找到阻止区域开始标记")
                    elif stripped_line == self.BLOCK_COMMENT_END:
                        in_block_section = False
                        print(f"V2.9 - 第{line_num}行: 找到阻止区域结束标记")
                    elif in_block_section and stripped_line and not stripped_line.startswith('#'):
                        print(f"V2.9 - 第{line_num}行: 解析阻止规则: {stripped_line}")
                        if stripped_line.startswith(self.redirect_ip):
                            parts = stripped_line.split()
                            if len(parts) > 1:
                                website = parts[1]
                                # 只添加主域名到内存列表，避免重复
                                domain = website[4:] if website.startswith('www.') else website
                                # 忽略通配符域名，只保留实际的主域名
                                if not domain.startswith('*.'):
                                    if domain not in self.blocked_websites:
                                        self.blocked_websites.append(domain)
                                        print(f"V2.9 - 成功添加阻止域名: {domain}")
            
            print(f"V2.9 - 成功从hosts文件加载了 {len(self.blocked_websites)} 个被阻止的网站")
            print(f"V2.9 - 最终阻止列表: {self.blocked_websites}")
            
        except Exception as e:
            print(f"V2.9 - 加载网站列表失败: {str(e)}")
            import traceback
            traceback.print_exc()
            self.blocked_websites = []
    
    def _save_blocked_websites(self, allow_empty=False):
        """保存被阻止的网站列表到hosts文件（增强版）
        
        Args:
            allow_empty: 是否允许保存空列表（用于解除所有限制的场景）
        
        Returns:
            bool: 保存是否成功
        """
        print(f"=== _save_blocked_websites 开始 ===")
        print(f"保存前内存中阻止网站数量: {len(self.blocked_websites)}, allow_empty: {allow_empty}")
        
        # 确保blocked_websites不为空（除非允许）
        self._ensure_websites_list(allow_empty)
        
        # 保存配置（即使hosts修改失败，配置也能保存）
        config_copy = self.config.copy()
        config_copy['blocked_websites'] = self.blocked_websites.copy()
        self.config = config_copy
        self._save_config()
        
        logger.info(f"开始保存阻止网站到hosts文件，当前内存中阻止网站数量: {len(self.blocked_websites)}")
        print(f"配置已更新，准备写入hosts文件")
        
        try:
            # 检查管理员权限
            if not self._is_admin():
                logger.error("无管理员权限，无法修改hosts文件")
                messagebox.showerror("权限不足", "需要管理员权限才能修改hosts文件\n请右键程序图标并选择'以管理员身份运行'")
                return False
            
            # 备份hosts文件
            self._backup_hosts_if_needed()
            
            # 读取现有hosts内容（排除阻止区域）
            existing_content = self._read_existing_hosts_content()
            
            # 生成阻止规则内容
            blocked_content = self._generate_blocked_content()
            
            # 创建临时文件
            temp_file = self._create_temp_hosts_file(existing_content, blocked_content)
            
            # 写入hosts文件
            success = self._write_to_hosts_file(temp_file)
            
            if success:
                # 清理缓存
                self._clear_caches()
                
                # 验证DNS解析
                self._verify_dns_resolution()
                
                # 更新UI显示
                if hasattr(self, '_update_status'):
                    self._update_status(f"已阻止 {len(self.blocked_websites)} 个网站")
                
                return True
            else:
                logger.error("所有尝试写入hosts文件的方法都失败了")
                messagebox.showerror("保存失败", "无法修改hosts文件，请确认您有管理员权限\n并检查文件是否被其他程序占用")
                return False
            
        except Exception as write_error:
            logger.error(f"写入hosts文件失败: {str(write_error)}")
            messagebox.showerror("保存失败", f"无法修改hosts文件: {str(write_error)}")
            return False
        except Exception as e:
            logger.error(f"保存网站列表时发生未知错误: {str(e)}")
            messagebox.showerror("错误", f"操作失败: {str(e)}")
            return False
    
    def _ensure_websites_list(self, allow_empty: bool) -> None:
        """确保阻止网站列表不为空（除非允许）
        
        Args:
            allow_empty: 是否允许空列表
        """
        if len(self.blocked_websites) == 0 and not allow_empty:
            print("警告: blocked_websites为空，尝试从配置重新加载...")
            try:
                if os.path.exists(self.config_file):
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        user_config = json.load(f)
                        saved_websites = user_config.get('blocked_websites', [])
                        if saved_websites:
                            print(f"从配置文件恢复 {len(saved_websites)} 个阻止网站")
                            self.blocked_websites = saved_websites
                        else:
                            print("配置文件中也没有保存的阻止网站")
            except Exception as e:
                print(f"尝试从配置文件恢复失败: {str(e)}")
    
    def _backup_hosts_if_needed(self) -> None:
        """必要时备份hosts文件"""
        if not os.path.exists(self.backup_path):
            try:
                self._backup_hosts()
                logger.info(f"成功备份hosts文件到: {self.backup_path}")
            except Exception as backup_error:
                logger.error(f"备份hosts文件失败: {str(backup_error)}")
                # 继续执行，备份失败不应该阻止主功能
    
    def _read_existing_hosts_content(self) -> list:
        """读取现有hosts内容（排除阻止区域）
        
        Returns:
            list: 现有hosts内容列表
        """
        lines = []
        in_block_section = False
        
        try:
            if os.path.exists(self.hosts_path):
                with open(self.hosts_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped == self.BLOCK_COMMENT_START:
                            in_block_section = True
                            continue
                        elif stripped == self.BLOCK_COMMENT_END:
                            in_block_section = False
                            continue
                        if not in_block_section:
                            lines.append(line)
                logger.info(f"成功读取hosts文件，保留非阻止区域内容")
        except Exception as read_error:
            logger.error(f"读取hosts文件失败: {str(read_error)}")
            # 如果读取失败，使用空文件作为基础
            lines = []
        
        return lines
    
    def _generate_blocked_content(self) -> str:
        """生成阻止规则内容
        
        Returns:
            str: 阻止规则内容
        """
        if not self.blocked_websites:
            return ""
        
        content = []
        content.append(f"\n{self.BLOCK_COMMENT_START}\n")
        content.append(f"# 此区域由Website Blocker自动生成，请勿手动修改\n")
        content.append(f"# 阻止网站总数: {len(self.blocked_websites)}\n")
        
        # 添加DNS优先级规则
        if self.force_dns_priority:
            content.append("# 强制DNS优先级规则\n")
            content.append(f"{self.redirect_ip}    connectivity-check.warp-svc\n")
            content.append(f"{self.redirect_ip}    1.1.1.1\n")
            content.append(f"{self.redirect_ip}    1.0.0.1\n")
            content.append(f"{self.redirect_ip}    8.8.8.8\n")
            content.append(f"{self.redirect_ip}    8.8.4.4\n")
            content.append("\n")
        
        # 生成每个域名的阻止规则
        blocked_count = 0
        for domain in self.blocked_websites:
            clean_domain = self._clean_domain(domain)
            if clean_domain:
                print(f"正在阻止域名: {clean_domain}")
                domain_rules = self._generate_domain_rules(clean_domain)
                content.extend(domain_rules)
                blocked_count += len(domain_rules)
        
        content.append(f"{self.BLOCK_COMMENT_END}\n")
        logger.info(f"生成{blocked_count}个域名规则")
        
        return ''.join(content)
    
    def _generate_domain_rules(self, domain: str) -> list:
        """为单个域名生成阻止规则
        
        Args:
            domain: 域名
            
        Returns:
            list: 阻止规则列表
        """
        rules = []
        # 阻止主域名
        rules.append(f"{self.redirect_ip}    {domain}\n")
        # 阻止www子域名
        rules.append(f"{self.redirect_ip}    www.{domain}\n")
        # 阻止所有子域名（通配符方式）
        rules.append(f"{self.redirect_ip}    *.{domain}\n")
        # 添加可能的CNAME和别名
        rules.append(f"{self.redirect_ip}    {domain}.queniusz.com\n")
        rules.append(f"{self.redirect_ip}    {domain}.w.cdngslb.com\n")
        
        return rules
    
    def _create_temp_hosts_file(self, existing_content: list, blocked_content: str) -> str:
        """创建临时hosts文件
        
        Args:
            existing_content: 现有hosts内容
            blocked_content: 阻止规则内容
            
        Returns:
            str: 临时文件路径
        """
        # 确定临时文件位置
        if platform.system() == "Windows":
            temp_file = os.path.join(self.user_config_dir, "hosts.tmp")
        else:
            import tempfile
            fd, temp_file = tempfile.mkstemp(suffix=".tmp")
            os.close(fd)
        
        # 写入内容
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.writelines(existing_content)
            if blocked_content:
                f.write(blocked_content)
        
        logger.info(f"成功写入临时文件: {temp_file}")
        return temp_file
    
    def _write_to_hosts_file(self, temp_file: str) -> bool:
        """将临时文件写入hosts文件
        
        Args:
            temp_file: 临时文件路径
            
        Returns:
            bool: 是否成功
        """
        success = False
        
        if platform.system() == "Windows":
            # 在Windows上尝试多种方法
            retry_count = 3
            methods = [
                ("shutil.copy2", self._copy_with_shutil),
                ("Windows API CopyFile", self._copy_with_windows_api),
                ("xcopy命令", self._copy_with_xcopy)
            ]
            
            for attempt in range(retry_count):
                for method_name, method_func in methods:
                    try:
                        if method_func(temp_file, self.hosts_path):
                            print(f"✓ 使用{method_name}成功写入hosts文件")
                            success = True
                            break
                    except Exception as e:
                        logger.warning(f"尝试 {attempt+1}/{retry_count}, {method_name} 失败: {str(e)}")
                
                if success:
                    break
                
                # 如果不是最后一次尝试，等待后重试
                if attempt < retry_count - 1:
                    time.sleep(0.5)
        else:
            # Linux/macOS使用标准方法
            try:
                shutil.copy2(temp_file, self.hosts_path)
                success = True
            except Exception as e:
                logger.error(f"Linux/macOS写入hosts失败: {str(e)}")
        
        # 清理临时文件
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as cleanup_error:
                logger.warning(f"清理临时文件失败: {str(cleanup_error)}")
        
        return success
    
    def _copy_with_shutil(self, src: str, dst: str) -> bool:
        """使用shutil.copy2复制文件
        
        Args:
            src: 源文件
            dst: 目标文件
            
        Returns:
            bool: 是否成功
        """
        shutil.copy2(src, dst)
        return True
    
    def _copy_with_windows_api(self, src: str, dst: str) -> bool:
        """使用Windows API CopyFile复制文件
        
        Args:
            src: 源文件
            dst: 目标文件
            
        Returns:
            bool: 是否成功
        """
        try:
            import win32file
            import win32con
            win32file.CopyFile(src, dst, False)
            return True
        except ImportError:
            logger.warning("win32file模块不可用")
            return False
    
    def _copy_with_xcopy(self, src: str, dst: str) -> bool:
        """使用xcopy命令复制文件
        
        Args:
            src: 源文件
            dst: 目标文件
            
        Returns:
            bool: 是否成功
        """
        subprocess.run(
            ["xcopy", "/Y", src, dst],
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    
    def _clear_caches(self) -> None:
        """清理缓存"""
        if platform.system() != "Windows":
            return
        
        try:
            print("正在执行缓存清理...")
            
            # 刷新DNS缓存和重置网络栈
            reset_commands = "ipconfig /flushdns & ipconfig /registerdns & ipconfig /release & ipconfig /renew & netsh winsock reset"
            dns_process = subprocess.Popen(
                ["powershell", "-Command", f"Start-Process cmd -ArgumentList '/c {reset_commands}' -Verb RunAs -WindowStyle Hidden"]
            )
            # 增加等待时间
            try:
                dns_process.wait(30)  # 最多等待30秒
            except subprocess.TimeoutExpired:
                print("网络重置命令超时，但已继续执行后续步骤")
            print("DNS缓存刷新和网络重置命令已执行")
            
            # 显示浏览器缓存清理提示
            browser_info = (
                "为确保阻止立即生效，请执行以下操作：\n\n"
                "1. 关闭所有浏览器窗口\n"
                "2. 禁用浏览器的DNS over HTTPS (DoH)功能：\n"
                "   - Chrome: 设置 > 隐私和安全 > 安全 > 使用安全DNS > 关闭\n"
                "   - Firefox: 设置 > 常规 > 网络设置 > DNS over HTTPS > 关闭\n"
                "3. 重新打开浏览器后再尝试访问被阻止的网站\n"
                "4. 如仍能访问，请清除浏览器缓存和Cookie\n\n"
                "注意：如使用Cloudflare WARP或其他VPN代理服务，请暂时禁用它们。"
            )
            messagebox.showinfo("缓存清理提示", browser_info)
            
        except Exception as dns_error:
            logger.warning(f"缓存清理过程中出错: {str(dns_error)}")
            print(f"缓存清理过程中出错: {str(dns_error)}")
            
            # 显示手动操作提示
            messagebox.showwarning(
                "手动操作提示", 
                "请手动执行以下操作确保阻止生效：\n\n"
                "1. 以管理员身份打开命令提示符\n"
                "2. 执行命令: ipconfig /flushdns\n"
                "3. 关闭并重新打开所有浏览器\n"
                "4. 清除浏览器缓存和Cookie"
            )
    
    def _verify_dns_resolution(self) -> None:
        """验证DNS解析结果"""
        print("验证DNS解析结果...")
        
        try:
            import socket
            # 强制重置DNS缓存
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM).connect(("8.8.8.8", 53))
            
            for domain in self.blocked_websites:
                # 清除Python的DNS缓存
                if hasattr(socket, 'gethostbyname_ex'):
                    socket.gethostbyname_ex(domain)  # 刷新缓存
                
                try:
                    # 获取解析结果
                    ip = socket.gethostbyname(domain)
                    print(f"域名 {domain} 解析到IP: {ip}")
                    
                    if ip == self.redirect_ip:
                        print(f"✓ 域名 {domain} 成功被重定向到 {self.redirect_ip}")
                    else:
                        print(f"✗ 域名 {domain} 未被正确重定向，解析到 {ip}")
                        print(f"警告: 可能存在DNS缓存或浏览器缓存问题")
                        
                except socket.gaierror as e:
                    print(f"域名 {domain} 解析失败: {str(e)} - 这可能是阻止生效的迹象")
                    print(f"✓ 域名 {domain} 可能已被成功阻止（无法解析）")
        
        except Exception as check_error:
            print(f"验证DNS解析时出错: {str(check_error)}")
        
        # 显示hosts文件内容确认
        try:
            with open(self.hosts_path, 'r', encoding='utf-8') as f:
                hosts_content = f.read()
                if self.BLOCK_COMMENT_START in hosts_content:
                    start = hosts_content.find(self.BLOCK_COMMENT_START)
                    end = hosts_content.find(self.BLOCK_COMMENT_END) + len(self.BLOCK_COMMENT_END)
                    blocked_content = hosts_content[start:end]
                    print(f"hosts文件阻止区域内容:\n{blocked_content}")
        except Exception as read_error:
            print(f"读取hosts文件失败: {str(read_error)}")


    def _create_ui(self):
        """Create user interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label with version
        title_label = ttk.Label(main_frame, text=f"Website Blocker V{APP_VERSION}", font=('SimHei', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Current block status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        status_text = f"Blocked websites: {len(self.blocked_websites)}"
        if self._is_admin():
            status_text += " (已获得管理员权限)"
        else:
            status_text += " (无管理员权限，无法修改)"
        
        status_label = ttk.Label(status_frame, text=status_text)
        status_label.pack(side=tk.LEFT)
        
        # 刷新按钮
        refresh_btn = ttk.Button(status_frame, text="刷新列表", command=self._refresh_list)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Website list frame
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 网站列表
        self.website_tree = ttk.Treeview(list_frame, columns=("网站"), show="headings", yscrollcommand=scrollbar.set)
        self.website_tree.heading("网站", text="阻止的网站")
        self.website_tree.column("网站", width=500, anchor=tk.W)
        self.website_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.website_tree.yview)
        
        # Action button frame
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        # Add website
        add_frame = ttk.Frame(action_frame)
        add_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(add_frame, text="网站地址:").pack(side=tk.LEFT, padx=5)
        self.add_entry = ttk.Entry(add_frame)
        self.add_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.add_entry.insert(0, "example.com")
        
        ttk.Button(add_frame, text="添加阻止", command=self._add_website_ui).pack(side=tk.LEFT, padx=5)
        
        # Other action buttons
        btn_frame = ttk.Frame(action_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="移除选中", command=self._remove_website_ui).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="解除所有限制", command=self._clear_all_blocks_ui).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="恢复hosts备份", command=self._restore_hosts_ui).pack(side=tk.LEFT, padx=5)
        
        # Footer info
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=10)
        
        # 添加示例配置提示
        example_text = "V2.9 提示: 退出程序后将保持当前限制状态"
        example_label = ttk.Label(footer_frame, text=example_text, font=('SimHei', 10, 'italic'))
        example_label.pack(side=tk.LEFT)
        
        # Version info
        version_label = ttk.Label(footer_frame, text=f"Version {APP_VERSION}", font=('SimHei', 10))
        version_label.pack(side=tk.RIGHT)
        
        # Fill initial list
        self._refresh_list()
    
    def _check_update(self):
        """Check for updates"""
        result = messagebox.askyesno(
            "Check Update", 
            f"Current Version: V{APP_VERSION}\n\nDo you want to visit the download page to check for latest version?",
            icon='question'
        )
        if result:
            try:
                webbrowser.open(UPDATE_URL)
                logger.info(f"Opened update page: {UPDATE_URL}")
            except Exception as e:
                logger.error(f"Failed to open update page: {e}")
                messagebox.showerror("Error", f"Cannot open update page: {e}")
    
    def _refresh_list(self):
        """刷新网站列表"""
        # 清空当前列表
        for item in self.website_tree.get_children():
            self.website_tree.delete(item)
        
        # 重新加载配置（包括程序目录和用户目录）
        self._load_config()
        
        # 添加到Treeview
        for website in self.blocked_websites:
            self.website_tree.insert('', tk.END, values=(website,))
        
        # 更新状态显示
        status_text = f"当前阻止的网站数量: {len(self.blocked_websites)}"
        if hasattr(self, 'status_label'):
            self.status_label.config(text=status_text)
        
        print(f"刷新列表后，当前阻止网站数量: {len(self.blocked_websites)}")
    
    def _clean_domain(self, domain):
        """清理域名格式，移除不必要的部分"""
        if not domain:
            return ""
            
        # 转换为小写
        domain = domain.lower()
            
        # 移除协议部分
        for protocol in ['http://', 'https://', 'ftp://', 'ftps://']:
            if domain.startswith(protocol):
                domain = domain[len(protocol):]
        
        # 可选地移除www前缀
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # 移除路径和端口部分
        if '/' in domain:
            domain = domain.split('/', 1)[0]
        if ':' in domain and '/' not in domain:
            domain = domain.split(':', 1)[0]
        
        # 移除尾部的点
        domain = domain.rstrip('.')
        
        # 确保格式正确
        if re.match(r'^[a-zA-Z0-9.-]+$', domain):
            return domain
        return None
    
    def _is_valid_domain(self, domain):
        """验证域名格式是否正确"""
        if not domain:
            return False
            
        # 确保域名字符长度合理（最长253个字符）
        if len(domain) > 253:
            return False
            
        # 简化的域名验证，确保能正确处理juejin.cn等常见域名
        # 只检查基本格式：字母、数字、- 和 .
        pattern = r'^[a-zA-Z0-9.-]+$'
        if not re.match(pattern, domain):
            return False
            
        # 确保最后一部分至少有2个字符（顶级域名）
        parts = domain.split('.')
        if len(parts) < 2 or len(parts[-1]) < 2:
            return False
            
        # 确保没有连续的点或在错误位置使用连字符
        if '..' in domain or domain.startswith('-') or domain.endswith('-'):
            return False
            
        print(f"域名验证通过: {domain}")
        return True
    
    def _add_website_ui(self):
        """添加网站的UI处理"""
        if not self._is_admin():
            messagebox.showerror("权限不足", "需要管理员权限才能添加网站限制")
            return
        
        website = self.add_entry.get().strip()
        if not website:
            messagebox.showwarning("输入错误", "请输入网站地址")
            return
        
        # 清理和标准化域名
        clean_domain = self._clean_domain(website)
        if not clean_domain or not self._is_valid_domain(clean_domain):
            messagebox.showwarning("格式错误", "网站地址格式不正确，请输入有效的域名，如 example.com 或 https://www.example.com/page")
            return
        
        # 检查是否已存在
        if clean_domain in self.blocked_websites:
            messagebox.showinfo("提示", f"该网站 {clean_domain} 已在阻止列表中")
            return
        
        # 添加网站（只添加清理后的主域名）
        self.blocked_websites.append(clean_domain)
        if self._save_blocked_websites():
            messagebox.showinfo("成功", f"已成功阻止 {clean_domain} 及其所有子域名")
            self.add_entry.delete(0, tk.END)
            self.add_entry.insert(0, "example.com")
            self._refresh_list()
    
    def _remove_website_ui(self):
        """移除网站的UI处理"""
        if not self._is_admin():
            messagebox.showerror("权限不足", "需要管理员权限才能移除网站限制")
            return
        
        selected = self.website_tree.selection()
        if not selected:
            messagebox.showwarning("选择错误", "请先选择要移除的网站")
            return
        
        for item in selected:
            website = self.website_tree.item(item, "values")[0]
            # 从列表中移除
            if website in self.blocked_websites:
                self.blocked_websites.remove(website)
        
        if self._save_blocked_websites():
            messagebox.showinfo("成功", "已成功移除选中的网站限制")
            self._refresh_list()
    
    def _clear_all_blocks_ui(self):
        """解除所有限制的UI处理"""
        if not self._is_admin():
            messagebox.showerror("权限不足", "需要管理员权限才能解除限制")
            return
        
        if messagebox.askyesno("确认", "确定要解除所有网站的访问限制吗？"):
            self.blocked_websites = []
            if self._save_blocked_websites():
                messagebox.showinfo("成功", "已解除所有网站的访问限制")
                self._refresh_list()
    
    def _create_window_icon(self):
        """创建窗口图标（使用Python绘制）"""
        try:
            # 创建32x32像素的图标（更大更清晰）
            icon = tk.PhotoImage(width=32, height=32)
            
            # 绘制红色背景（盾牌形状）
            # 使用更简单的方式确保图标正确显示
            # 1. 先绘制一个红色矩形背景
            for x in range(32):
                for y in range(32):
                    icon.put("#FF0000", (x, y))
            
            # 2. 绘制白色叉号（更明显的线条）
            # 左上到右下的线（加粗）
            for i in range(20):
                x = 6 + i
                y = 6 + i
                if 0 <= x < 32 and 0 <= y < 32:
                    # 绘制3像素宽的线
                    for offset in range(-1, 2):
                        if 0 <= x + offset < 32 and 0 <= y < 32:
                            icon.put("#FFFFFF", (x + offset, y))
                        if 0 <= x < 32 and 0 <= y + offset < 32:
                            icon.put("#FFFFFF", (x, y + offset))
            
            # 右上到左下的线（加粗）
            for i in range(20):
                x = 25 - i
                y = 6 + i
                if 0 <= x < 32 and 0 <= y < 32:
                    # 绘制3像素宽的线
                    for offset in range(-1, 2):
                        if 0 <= x + offset < 32 and 0 <= y < 32:
                            icon.put("#FFFFFF", (x + offset, y))
                        if 0 <= x < 32 and 0 <= y + offset < 32:
                            icon.put("#FFFFFF", (x, y + offset))
            
            # 确保图标正确设置到窗口
            # 使用iconphoto方法并设置为True表示将图标设置为应用程序图标
            self.root.iconphoto(True, icon)
            
            # 保存图标引用防止被垃圾回收
            self.window_icon = icon
            print("✓ 窗口图标已创建并设置成功")
            
        except Exception as e:
            print(f"创建图标失败: {e}")
            # 降级方案：使用更简单的备用图标
            try:
                # 创建一个简单的红色方块图标
                temp_icon = tk.PhotoImage(width=16, height=16)
                for x in range(16):
                    for y in range(16):
                        # 创建简单的红色方块
                        temp_icon.put("#FF0000", (x, y))
                        # 在中心添加一个白点
                        if 6 <= x <= 9 and 6 <= y <= 9:
                            temp_icon.put("#FFFFFF", (x, y))
                
                self.root.iconphoto(True, temp_icon)
                self.window_icon = temp_icon
                print("✓ 使用备用图标")
            except Exception as fallback_e:
                print(f"创建备用图标失败: {fallback_e}")
    
    def _setup_exit_handlers(self):
        """V2.9 - 设置程序退出处理器"""
        # 窗口关闭时的处理
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # 捕获Ctrl+C等退出信号
        def signal_handler(sig, frame):
            print("V2.9 - 接收到退出信号，保存设置...")
            self._on_program_exit()
            self.root.destroy()
            sys.exit(0)
        
        # 注册信号处理器（如果在Windows上可能不工作）
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except Exception as e:
            print(f"V2.9 - 无法注册信号处理器: {str(e)}")
    
    def _on_window_close(self):
        """V2.9 - 窗口关闭时的处理"""
        # 保存当前配置和设置
        self._save_config()
        
        # V2.9核心功能：默认不恢复hosts文件内容
        # 询问用户是否要清除所有阻止（即使auto_clear_on_exit设置为False）
        result = messagebox.askyesno(
            "确认退出", 
            "是否在退出前解除所有网站访问限制？\nV2.9提示：不解除将保持当前限制状态（推荐）"
        )
        if result:
            self._clear_all_blocks()
        
        # 退出程序
        self.root.destroy()
        sys.exit(0)
    
    def _on_program_exit(self):
        """V2.9 - 程序异常退出时的处理"""
        try:
            # 保存配置
            self._save_config()
            
            # V2.9：无论退出方式如何，都询问用户是否解除限制
            print("V2.9 - 程序退出，询问用户是否解除限制...")
            try:
                # 尝试弹出确认对话框（如果GUI线程仍然可用）
                result = messagebox.askyesno(
                    "确认退出", 
                    "是否在退出前解除所有网站访问限制？\nV2.9提示：不解除将保持当前限制状态（推荐）"
                )
                if result:
                    self._clear_all_blocks()
            except Exception as e:
                # 如果GUI线程不可用，根据配置决定
                print(f"V2.9 - GUI不可用，使用配置决定是否解除限制: {str(e)}")
                if self.config.get('auto_clear_on_exit', False):
                    print("V2.9 - 程序异常退出，根据设置自动解除所有网站访问限制...")
                    self._clear_all_blocks()
        except Exception as e:
            print(f"V2.9 - 退出处理时出错: {str(e)}")
    
    def _clear_all_blocks(self):
        """内部方法：解除所有限制，不显示UI提示"""
        try:
            print("执行解除所有限制操作")
            self.blocked_websites = []
            # 调用_save_blocked_websites时设置allow_empty=True，允许保存空列表
            result = self._save_blocked_websites(allow_empty=True)
            print(f"解除所有限制操作结果: {result}")
            return result
        except Exception as e:
            print(f"解除所有限制失败: {str(e)}")
            return False
    
    def _load_config(self):
        """V2.9 - 从配置文件加载程序设置"""
        try:
            print(f"V2.9 - 尝试从配置文件加载程序设置: {self.config_file}")
            
            # 首先确保配置目录存在
            os.makedirs(self.user_config_dir, exist_ok=True)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    
                # 使用字典解包来合并配置，保留默认值
                self.config.update(loaded_config)
                
                # 从配置中获取程序设置
                if 'auto_clear_on_exit' in loaded_config:
                    self.config['auto_clear_on_exit'] = loaded_config['auto_clear_on_exit']
                    print(f"V2.9 - 自动清除设置: {self.config['auto_clear_on_exit']}")
                
                if 'external_storage_enabled' in loaded_config:
                    self.config['external_storage_enabled'] = loaded_config['external_storage_enabled']
                    print(f"V2.9 - 外部存储设置: {self.config['external_storage_enabled']}")
                
                # 检查配置版本
                config_version = loaded_config.get('version', '1.0')
                print(f"V2.9 - 加载的配置版本: {config_version}")
                
                print("V2.9 - 程序设置加载成功")
            else:
                print("V2.9 - 配置文件不存在，使用默认设置")
                # 保存默认配置
                self._save_config()
        except json.JSONDecodeError as e:
            print(f"V2.9 - 配置文件格式错误: {str(e)}")
            messagebox.showerror("配置错误", f"配置文件格式错误，使用默认设置: {str(e)}")
            # 使用默认配置并保存
            self.config = {
                "auto_clear_on_exit": False,  # V2.9默认不自动清除
                "external_storage_enabled": False
            }
            self._save_config()
        except Exception as e:
            print(f"V2.9 - 加载配置时出错: {str(e)}")
            messagebox.showerror("错误", f"加载配置失败: {str(e)}")
    
    def _save_config(self):
        """V2.9 - 保存程序设置到配置文件"""
        try:
            print(f"V2.9 - 开始保存程序设置到: {self.config_file}")
            
            # 确保配置目录存在
            os.makedirs(self.user_config_dir, exist_ok=True)
            
            # 准备要保存的配置（只保存程序设置，不依赖于阻止列表）
            config_to_save = {
                "blocked_websites": self.blocked_websites.copy(),  # 保留同步，但不依赖它来控制hosts
                "auto_clear_on_exit": self.config.get("auto_clear_on_exit", False),  # V2.9默认不自动清除
                "external_storage_enabled": self.config.get("external_storage_enabled", False),
                "version": "2.9",  # V2.9版本号
                "last_update": datetime.now().isoformat()
            }
            
            # 使用临时文件写入，然后原子替换，避免配置文件损坏
            temp_config_file = self.config_file + ".tmp"
            with open(temp_config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, ensure_ascii=False, indent=2)
            
            # 原子替换
            os.replace(temp_config_file, self.config_file)
            
            print(f"V2.9 - 程序设置保存成功，文件路径: {self.config_file}")
        except Exception as e:
            print(f"V2.9 - 保存配置时出错: {str(e)}")
            # 尝试使用备用方式保存
            try:
                # 创建一个备用配置文件路径
                backup_config_file = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'WebsiteBlocker', 'config_backup.json')
                with open(backup_config_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "blocked_websites": self.blocked_websites.copy(),
                        "last_update": datetime.now().isoformat()
                    }, f, ensure_ascii=False, indent=2)
                print(f"V2.9 - 配置已保存到备用位置: {backup_config_file}")
                messagebox.showinfo("配置保存", f"配置已保存到备用位置: {backup_config_file}")
            except Exception as fallback_error:
                print(f"V2.9 - 备用保存方式也失败: {str(fallback_error)}")
                messagebox.showerror("保存失败", f"无法保存配置: {str(e)}")
    
    def _restore_hosts_ui(self):
        """恢复hosts备份的UI处理"""
        if not self._is_admin():
            messagebox.showerror("权限不足", "需要管理员权限才能恢复hosts文件")
            return
        
        if not os.path.exists(self.backup_path):
            messagebox.showinfo("提示", "未找到hosts备份文件")
            return
        
        if messagebox.askyesno("确认", "确定要恢复hosts文件吗？这将解除所有当前的限制。"):
            if self._restore_hosts():
                self.blocked_websites = []
                self._load_blocked_websites_from_hosts()
                messagebox.showinfo("成功", "hosts文件已恢复")
                self._refresh_list()
    
    def _show_deprecation_warning(self):
        """Show version deprecation warning"""
        deprecation_msg = (
            "⚠️ 重要通知 ⚠️\n\n"
            "Website Blocker V2.9 已停止支持。\n\n"
            "该版本不再接收安全更新和功能改进。\n"
            "建议您升级到最新版本以获得更好的体验和安全保障。\n\n"
            "感谢您的理解与支持！"
        )
        messagebox.showwarning("版本停止支持", deprecation_msg)

def main():
    """主函数"""
    # 设置日志记录
    setup_logging()
    
    # 创建Tkinter主窗口
    root = tk.Tk()
    
    # V2.9 - 移除自动恢复hosts的逻辑，允许限制在程序退出后保持
    try:
        # 创建应用实例
        app = WebsiteBlockerApp(root)
        
        # 启动主事件循环
        root.mainloop()
    except Exception as e:
        print(f"V2.9 - 程序发生异常: {str(e)}")
        logger.error(f"V2.9 - 程序崩溃: {str(e)}", exc_info=True)
        
        # 显示错误对话框
        tk_no_ui = tk.Tk()
        tk_no_ui.withdraw()  # 隐藏主窗口
        messagebox.showerror("程序错误", f"V2.9 - 程序发生错误: {str(e)}")
        tk_no_ui.destroy()
    finally:
        # 确保程序完全退出
        sys.exit(0)

if __name__ == "__main__":
    main()

