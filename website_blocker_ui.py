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
from datetime import datetime
import atexit
import math
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('WebsiteBlocker')

# 设置中文字体
tk_font = ('SimHei', 10)

class WebsiteBlockerApp:
    def __init__(self, root):
        # 首先检查是否具有管理员权限，如果没有，自动请求
        if not self._is_admin():
            result = messagebox.askyesno(
                "权限不足", 
                "此程序需要管理员权限才能正常工作，是否以管理员身份重新启动程序？"
            )
            if result:
                # 以管理员权限重新启动程序
                if self._run_as_admin():
                    # 如果成功请求到管理员权限并重新启动，退出当前实例
                    root.destroy()
                    sys.exit(0)
                else:
                    # 如果无法请求管理员权限，显示警告
                    messagebox.showwarning("权限警告", "无法以管理员身份启动程序，部分功能可能无法使用")
            else:
                # 用户拒绝以管理员身份运行，显示警告
                messagebox.showwarning("权限警告", "部分功能需要管理员权限才能使用，请手动以管理员身份运行程序")
        
        self.root = root
        self.root.title("网站访问限制工具")
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
        
        # 初始化被阻止的网站列表
        self.blocked_websites = []
        
        # 获取用户配置目录，避免权限问题
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 优先使用用户目录存储配置文件（避免权限问题）
        self.user_config_dir = os.path.join(os.path.expanduser('~'), '.website_blocker')
        os.makedirs(self.user_config_dir, exist_ok=True)
        self.config_file = os.path.join(self.user_config_dir, "config.json")
        
        # 记录配置文件路径信息
        logger.info(f"程序目录: {self.app_dir}")
        logger.info(f"用户配置目录: {self.user_config_dir}")
        logger.info(f"配置文件路径: {self.config_file}")
        
        # 初始化配置
        self.config = {
            "blocked_websites": [],
            "auto_clear_on_exit": True,
            "external_storage_enabled": False  # 默认禁用外部存储
        }
        
        # 检查是否已获得管理员权限
        if self._is_admin():
            print("✓ 已获得管理员权限")
        else:
            print("⚠️  无管理员权限，部分功能可能无法使用")
        
        # 备份hosts文件
        if not os.path.exists(self.backup_path):
            self._backup_hosts()
        
        # 创建窗口图标（使用Python绘制）
        self._create_window_icon()
        
        # 初始化变量，先不创建UI（移到后面）
        
        # 加载配置（必须先加载配置）
        self._load_config()
        print(f"初始化后，加载配置完成，阻止网站数量: {len(self.blocked_websites)}")
        
        # 默认阻止bilibili
        self._ensure_default_block()
        print(f"确保默认阻止完成，阻止网站数量: {len(self.blocked_websites)}")
        
        # 创建UI（现在先创建UI，再保存配置）
        self._create_ui()
        print(f"UI创建完成，阻止网站数量: {len(self.blocked_websites)}")
        
        # 将配置应用到hosts文件
        # 创建一个备份，确保保存前不会丢失数据
        websites_backup = self.blocked_websites.copy()
        print(f"准备保存到hosts文件，备份的阻止网站数量: {len(websites_backup)}")
        self._save_blocked_websites()
        print(f"保存到hosts文件完成")
        
        # 设置退出处理
        self._setup_exit_handlers()
    
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
    
    def _load_blocked_websites(self):
        """从hosts文件加载被阻止的网站列表"""
        try:
            self.blocked_websites = []
            if not os.path.exists(self.hosts_path):
                return
            
            in_block_section = False
            with open(self.hosts_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line == self.BLOCK_COMMENT_START:
                        in_block_section = True
                    elif line == self.BLOCK_COMMENT_END:
                        in_block_section = False
                    elif in_block_section and line.startswith(self.redirect_ip):
                        parts = line.split()
                        if len(parts) > 1:
                            website = parts[1]
                            # 只添加主域名到内存列表，避免重复
                            domain = website[4:] if website.startswith('www.') else website
                            if domain not in self.blocked_websites:
                                self.blocked_websites.append(domain)
        except Exception as e:
            print(f"加载网站列表失败: {str(e)}")
            self.blocked_websites = []
    
    def _save_blocked_websites(self, allow_empty=False):
        """保存被阻止的网站列表到hosts文件
        
        Args:
            allow_empty: 是否允许保存空列表（用于解除所有限制的场景）
        """
        print(f"=== _save_blocked_websites 开始 ===")
        print(f"保存前内存中阻止网站数量: {len(self.blocked_websites)}, 列表: {self.blocked_websites}, allow_empty: {allow_empty}")
        
        # 添加防护：如果blocked_websites为空且不允许空列表，尝试从配置文件重新加载
        if len(self.blocked_websites) == 0 and not allow_empty:
            print("警告: blocked_websites为空，尝试从配置重新加载...")
            try:
                # 尝试从用户配置文件重新加载
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
        
        # 无论如何都先保存配置，这样即使hosts修改失败，配置也能保存
        # 创建配置副本，确保不会修改原始数据
        config_copy = self.config.copy()
        config_copy['blocked_websites'] = self.blocked_websites.copy()
        self.config = config_copy
        self._save_config()
        
        logger.info(f"开始保存阻止网站到hosts文件，当前内存中阻止网站数量: {len(self.blocked_websites)}")
        print(f"配置已更新，准备写入hosts文件")
        
        try:
            # 在写入前再次检查管理员权限
            if not self._is_admin():
                logger.error("无管理员权限，无法修改hosts文件")
                messagebox.showerror("权限不足", "需要管理员权限才能修改hosts文件\n请右键程序图标并选择'以管理员身份运行'")
                return False
            
            # 备份当前hosts文件（只在不存在备份时备份）
            if not os.path.exists(self.backup_path):
                try:
                    self._backup_hosts()
                    logger.info(f"成功备份hosts文件到: {self.backup_path}")
                except Exception as backup_error:
                    logger.error(f"备份hosts文件失败: {str(backup_error)}")
                    # 继续执行，备份失败不应该阻止主功能
            
            # 读取现有内容（排除阻止区域）
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
            
            # 写入新内容 - 使用更健壮的方式，特别是针对Windows权限问题
            temp_hosts = None
            try:
                # 在临时目录创建临时文件，而不是在系统目录
                if platform.system() == "Windows":
                    # 使用用户目录作为临时文件位置
                    temp_hosts = os.path.join(self.user_config_dir, "hosts.tmp")
                else:
                    # Linux/macOS使用标准临时文件
                    import tempfile
                    fd, temp_hosts = tempfile.mkstemp(suffix=".tmp")
                    os.close(fd)
                
                # 写入临时文件
                blocked_count = 0
                with open(temp_hosts, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                    if self.blocked_websites:
                        f.write(f"\n{self.BLOCK_COMMENT_START}\n")
                        f.write(f"# 此区域由网站访问限制工具自动生成，请勿手动修改\n")
                        f.write(f"# 阻止网站总数: {len(self.blocked_websites)}\n")
                        
                        # 对于每个域名，阻止主域名和所有子域名（包括www）
                        for domain in self.blocked_websites:
                            # 确保格式正确，移除http/https和路径
                            clean_domain = self._clean_domain(domain)
                            if clean_domain:
                                blocked_count += 1
                                # 阻止主域名
                                f.write(f"{self.redirect_ip} {clean_domain}\n")
                                # 阻止www子域名
                                f.write(f"{self.redirect_ip} www.{clean_domain}\n")
                                # 阻止所有子域名（使用通配符的方式，虽然hosts不支持真正的通配符，但这是最佳实践）
                                f.write(f"{self.redirect_ip} *.{clean_domain}\n")
                        f.write(f"{self.BLOCK_COMMENT_END}\n")
                
                logger.info(f"成功写入临时文件: {temp_hosts}，实际写入{blocked_count}个域名")
                
                # 使用不同的方法尝试复制文件，根据不同系统选择最佳方法
                if platform.system() == "Windows":
                    # 在Windows上，尝试多种方法写入hosts文件
                    success = False
                    retry_count = 3
                    
                    for attempt in range(retry_count):
                        try:
                            # 方法1: 使用shutil.copy2
                            shutil.copy2(temp_hosts, self.hosts_path)
                            success = True
                            break
                        except PermissionError:
                            logger.warning(f"尝试 {attempt+1}/{retry_count} 失败: 使用shutil.copy2时权限不足")
                            
                            # 方法2: 使用Windows API CopyFile函数
                            try:
                                import win32file
                                import win32con
                                win32file.CopyFile(temp_hosts, self.hosts_path, False)
                                success = True
                                break
                            except ImportError:
                                logger.warning("win32file模块不可用")
                            except Exception as win_error:
                                logger.warning(f"Windows API复制失败: {str(win_error)}")
                            
                            # 方法3: 使用命令行工具xcopy
                            try:
                                subprocess.run(
                                    ["xcopy", "/Y", temp_hosts, self.hosts_path],
                                    shell=True,
                                    check=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE
                                )
                                success = True
                                break
                            except Exception as xcopy_error:
                                logger.warning(f"xcopy命令失败: {str(xcopy_error)}")
                            
                            # 如果不是最后一次尝试，等待一段时间后重试
                            if attempt < retry_count - 1:
                                time.sleep(0.5)
                else:
                    # Linux/macOS使用标准方法
                    shutil.copy2(temp_hosts, self.hosts_path)
                    success = True
                
                if success:
                    logger.info(f"成功更新hosts文件，阻止了 {len(self.blocked_websites)} 个网站，实际写入{blocked_count}个域名")
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
            finally:
                # 清理临时文件
                if temp_hosts and os.path.exists(temp_hosts):
                    try:
                        os.remove(temp_hosts)
                    except Exception as cleanup_error:
                        logger.warning(f"清理临时文件失败: {str(cleanup_error)}")
        except Exception as e:
            logger.error(f"保存网站列表时发生未知错误: {str(e)}")
            messagebox.showerror("错误", f"操作失败: {str(e)}")
            return False
    
    def _ensure_default_block(self):
        """确保默认阻止bilibili"""
        print(f"_ensure_default_block调用前，当前阻止网站数量: {len(self.blocked_websites)}, 列表: {self.blocked_websites}")
        default_site = "bilibili.com"
        # 检查bilibili.com是否已经在阻止列表中（考虑www前缀）
        has_bilibili = False
        for site in self.blocked_websites:
            clean_site = site[4:] if site.startswith('www.') else site
            if clean_site == 'bilibili.com':
                has_bilibili = True
                break
        
        if not has_bilibili:
            print(f"添加默认阻止网站: {default_site}")
            self.blocked_websites.append(default_site)
            print(f"添加后阻止网站数量: {len(self.blocked_websites)}")
            # 保存配置，但不立即写入hosts，让初始化过程完成后统一处理
            self._save_config()
        else:
            print(f"bilibili.com 已在阻止列表中，无需重复添加")
        print(f"_ensure_default_block调用后，当前阻止网站数量: {len(self.blocked_websites)}")
    
    def _create_ui(self):
        """创建用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题标签
        title_label = ttk.Label(main_frame, text="网站访问限制工具", font=('SimHei', 14, 'bold'))
        title_label.pack(pady=10)
        
        # 当前阻止信息
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        status_text = f"当前阻止的网站数量: {len(self.blocked_websites)}"
        if self._is_admin():
            status_text += " (已获得管理员权限)"
        else:
            status_text += " (无管理员权限，无法修改)"
        
        status_label = ttk.Label(status_frame, text=status_text)
        status_label.pack(side=tk.LEFT)
        
        # 刷新按钮
        refresh_btn = ttk.Button(status_frame, text="刷新列表", command=self._refresh_list)
        refresh_btn.pack(side=tk.RIGHT)
        
        # 网站列表框架
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 网站列表
        self.website_tree = ttk.Treeview(list_frame, columns=("网站"), show="headings", yscrollcommand=scrollbar.set)
        self.website_tree.heading("网站", text="阻止的网站")
        self.website_tree.column("网站", width=500, anchor=tk.W)
        self.website_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.website_tree.yview)
        
        # 操作按钮框架
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        # 添加网站
        add_frame = ttk.Frame(action_frame)
        add_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(add_frame, text="网站地址:").pack(side=tk.LEFT, padx=5)
        self.add_entry = ttk.Entry(add_frame)
        self.add_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.add_entry.insert(0, "example.com")
        
        ttk.Button(add_frame, text="添加阻止", command=self._add_website_ui).pack(side=tk.LEFT, padx=5)
        
        # 其他操作按钮
        btn_frame = ttk.Frame(action_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="移除选中", command=self._remove_website_ui).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="解除所有限制", command=self._clear_all_blocks_ui).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="恢复hosts备份", command=self._restore_hosts_ui).pack(side=tk.LEFT, padx=5)
        
        # 底部信息
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(footer_frame, text="注意: 此工具通过修改hosts文件实现网站限制，请以管理员身份运行。").pack(side=tk.LEFT)
        
        # 填充初始列表
        self._refresh_list()
    
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
            
        # 域名基本格式检查：字母、数字、- 和 .
        # 更宽松的正则表达式，确保能匹配像kuaishou.com这样的合法域名
        pattern = r'^([a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.)*[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?$'
        if not re.match(pattern, domain):
            return False
            
        # 确保最后一部分至少有2个字符（顶级域名）
        parts = domain.split('.')
        if len(parts) < 2 or len(parts[-1]) < 2:
            return False
            
        # 确保没有连续的点或在错误位置使用连字符
        if '..' in domain or domain.startswith('-') or domain.endswith('-'):
            return False
            
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
        """设置程序退出处理函数，确保程序退出时自动解除限制"""
        # 使用atexit注册退出处理函数
        atexit.register(self._on_program_exit)
        
        # 为Tkinter窗口设置关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _on_window_close(self):
        """窗口关闭事件处理函数"""
        print(f"窗口关闭事件，当前阻止网站数量: {len(self.blocked_websites)}")
        
        # 询问用户是否解除限制
        should_clear = False
        if len(self.blocked_websites) > 0:
            response = messagebox.askyesno("退出确认", "程序即将退出，是否解除所有网站限制？")
            should_clear = response
        
        # 如果用户选择解除限制，先保存配置，再清空
        if should_clear:
            print("用户选择解除所有限制")
            # 先保存当前配置，以便稍后可以恢复
            temp_config = self.config.copy()
            temp_config['blocked_websites'] = self.blocked_websites.copy()
            
            # 解除所有限制
            self._clear_all_blocks()
            
            # 保存空列表配置
            self._save_config()
            print("已解除所有限制")
        else:
            print("用户选择保留限制")
            # 直接保存当前配置
            self._save_config()
            print("配置已保存")
        
        # 销毁窗口
        self.root.destroy()
    
    def _on_program_exit(self):
        """程序异常退出时的处理函数"""
        try:
            # 保存配置
            self._save_config()
            
            # 这里可以添加日志记录，但不显示UI
            print("程序退出，配置已保存")
        except Exception as e:
            print(f"程序退出处理错误: {e}")
    
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
        """加载配置文件，合并程序目录和用户目录的配置"""
        try:
            # 创建一个临时配置副本，避免直接修改原始配置
            temp_config = self.config.copy()
            
            # 尝试加载程序目录的配置文件（如果存在）
            program_config_file = os.path.join(self.app_dir, "config.json")
            program_websites = []
            if os.path.exists(program_config_file):
                try:
                    with open(program_config_file, 'r', encoding='utf-8') as f:
                        program_config = json.load(f)
                        program_websites = program_config.get('blocked_websites', [])
                    print(f"从程序目录配置文件加载到 {len(program_websites)} 个阻止网站: {program_websites}")
                except Exception as e:
                    print(f"加载程序目录配置文件失败: {str(e)}")
            
            # 尝试加载用户目录的配置文件
            user_websites = []
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        user_config = json.load(f)
                        # 保留其他配置项
                        for key, value in user_config.items():
                            if key != 'blocked_websites':
                                temp_config[key] = value
                        user_websites = user_config.get('blocked_websites', [])
                    print(f"从用户目录配置文件加载到 {len(user_websites)} 个阻止网站: {user_websites}")
                except Exception as e:
                    print(f"加载用户配置文件失败: {str(e)}")
            
            # 合并两个配置文件中的阻止网站，去重
            all_websites = list(set(program_websites + user_websites))
            print(f"合并后总共有 {len(all_websites)} 个阻止网站: {all_websites}")
            
            # 更新内存中的阻止网站列表
            self.blocked_websites = all_websites
            # 更新配置对象
            temp_config['blocked_websites'] = all_websites
            
            # 更新版本和最后运行时间
            temp_config['version'] = "3.7"
            temp_config['last_run'] = datetime.now().isoformat()
            
            # 保存更新后的配置
            self.config = temp_config
            
            # 立即保存配置到用户目录
            self._save_config()
            
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
            # 使用默认配置
            self.config = {
                'blocked_websites': [],
                'auto_clear_on_exit': True,
                'external_storage_enabled': False
            }
            self.blocked_websites = []
    
    def _save_config(self):
        """保存程序配置，确保blocked_websites正确更新"""
        try:
            # 确保配置目录存在
            if not os.path.exists(self.user_config_dir):
                try:
                    os.makedirs(self.user_config_dir, exist_ok=True)
                    logger.info(f"已创建配置目录: {self.user_config_dir}")
                except Exception as create_dir_error:
                    logger.error(f"无法创建配置目录: {str(create_dir_error)}")
                    return
            
            # 创建一个新的配置副本，确保包含当前的阻止网站列表
            config = {
                'blocked_websites': self.blocked_websites,  # 始终使用当前内存中的阻止列表
                'last_run': datetime.now().isoformat(),
                'version': '3.7',
                'auto_clear_on_exit': self.config.get('auto_clear_on_exit', True),
                'external_storage_enabled': self.config.get('external_storage_enabled', False)
            }
            
            logger.info(f"准备保存配置，阻止网站数量: {len(self.blocked_websites)}")
            
            # 保存为JSON格式 - 使用临时文件先写入再替换，避免写入失败损坏原文件
            temp_file = self.config_file + ".tmp"
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                
                # 原子性替换文件
                os.replace(temp_file, self.config_file)
                
                # 验证保存是否成功
                if os.path.exists(self.config_file):
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        saved_config = json.load(f)
                        saved_count = len(saved_config.get('blocked_websites', []))
                        logger.info(f"配置已保存到 {self.config_file}，阻止网站数量: {saved_count}")
                else:
                    logger.error(f"配置文件保存后不存在: {self.config_file}")
            except Exception as write_error:
                logger.error(f"写入配置文件失败: {str(write_error)}")
                # 清理临时文件
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")
    
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
                self._load_blocked_websites()
                messagebox.showinfo("成功", "hosts文件已恢复")
                self._refresh_list()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        # 设置窗口图标（如果有）
        # root.iconbitmap("app_icon.ico")
        app = WebsiteBlockerApp(root)
        root.mainloop()
    except Exception as e:
        print(f"程序发生错误: {str(e)}")
        # 确保在异常情况下也能恢复hosts
        try:
            hosts_path = os.path.join(os.environ["SystemRoot"], "System32", "drivers", "etc", "hosts")
            backup_path = hosts_path + ".backup"
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, hosts_path)
                print("程序异常退出，已自动恢复hosts文件")
        except:
            pass
        # 显示错误信息
        messagebox.showerror("错误", f"程序发生错误: {str(e)}")
        sys.exit(1)