import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ConfigManager')

# 设置中文字体
tk_font = ('SimHei', 10)

class ConfigManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("网站限制配置管理器")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
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
        
        # 定义模板数据
        self.templates = {
            "视频模板": [
                "youtube.com", "youku.com", "iqiyi.com", "tencent.com", "bilibili.com",
                "douyin.com", "kuaishou.com", "mgtv.com", "sohu.com", "1905.com",
                "pptv.com", "acfun.cn", "le.com", "letv.com", "huashu.com"
            ],
            "文体类模板": [
                "zhihu.com", "tieba.baidu.com", "wenku.baidu.com", "xiaoshuo.com",
                "qidian.com", "readnovel.com", "xs8.cn", "zongheng.com", "jjwxc.net",
                "duokan.com", "m.17k.com", "m.qidian.com", "m.readnovel.com", "wenxuecity.com"
            ],
            "搜索引擎模板": [
                "baidu.com", "sogou.com", "bing.com", "google.com", "360.cn",
                "so.com", "sm.cn", "yandex.com", "yahoo.com", "ask.com",
                "duckduckgo.com", "baidu.cn", "m.baidu.com", "wap.baidu.com"
            ],
            "全部限制模板": [
                # 视频网站
                "youtube.com", "youku.com", "iqiyi.com", "tencent.com", "bilibili.com",
                "douyin.com", "kuaishou.com", "mgtv.com", "sohu.com", "1905.com",
                # 社交网站
                "weibo.com", "weixin.qq.com", "qq.com", "renren.com", "kaixin001.com",
                # 搜索引擎
                "baidu.com", "sogou.com", "bing.com", "google.com", "360.cn",
                # 小说阅读
                "qidian.com", "readnovel.com", "xiaoshuo.com", "zongheng.com", "jjwxc.net",
                # 新闻资讯
                "sina.com.cn", "163.com", "ifeng.com", "toutiao.com", "thepaper.cn",
                # 购物网站
                "taobao.com", "jd.com", "tmall.com", "pinduoduo.com", "suning.com",
                # 其他娱乐网站
                "zhihu.com", "tieba.baidu.com", "douban.com", "acfun.cn"
            ]
        }
        
        # 默认配置
        self.default_config = {
            "blocked_websites": [],
            "auto_clear_on_exit": True,
            "external_storage_enabled": False
        }
        
        # 当前配置
        self.config = self.default_config.copy()
        
        # 创建窗口图标（使用Python绘制）
        self._create_window_icon()
        
        # 创建UI
        self._create_ui()
        
        # 加载配置
        self._load_config()
    
    def _create_ui(self):
        """创建用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题标签
        title_label = ttk.Label(main_frame, text="网站限制配置管理", font=('SimHei', 14, 'bold'))
        title_label.pack(pady=10)
        
        # 配置信息框架
        info_frame = ttk.LabelFrame(main_frame, text="配置信息", padding="10")
        info_frame.pack(fill=tk.X, pady=5)
        
        # 配置文件路径
        path_frame = ttk.Frame(info_frame)
        path_frame.pack(fill=tk.X, pady=5)
        ttk.Label(path_frame, text="配置文件:", width=15).pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value=self.config_file)
        ttk.Label(path_frame, textvariable=self.path_var, font=('SimHei', 9)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 网站列表框架
        list_frame = ttk.LabelFrame(main_frame, text="默认阻止网站列表", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 网站列表
        self.website_tree = ttk.Treeview(list_frame, columns=("网站"), show="headings", yscrollcommand=scrollbar.set)
        self.website_tree.heading("网站", text="阻止的网站")
        self.website_tree.column("网站", width=400, anchor=tk.W)
        self.website_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.website_tree.yview)
        
        # 网站操作框架
        website_action_frame = ttk.Frame(main_frame)
        website_action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(website_action_frame, text="添加网站:").pack(side=tk.LEFT, padx=5)
        self.add_entry = ttk.Entry(website_action_frame)
        self.add_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.add_entry.insert(0, "example.com")
        
        ttk.Button(website_action_frame, text="添加", command=self._add_website).pack(side=tk.LEFT, padx=5)
        ttk.Button(website_action_frame, text="移除选中", command=self._remove_website).pack(side=tk.LEFT, padx=5)
        
        # 设置选项框架
        settings_frame = ttk.LabelFrame(main_frame, text="程序设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)
        
        # 退出时自动清除
        self.auto_clear_var = tk.BooleanVar(value=True)
        auto_clear_check = ttk.Checkbutton(settings_frame, text="退出时自动清除所有限制", 
                                          variable=self.auto_clear_var)
        auto_clear_check.pack(anchor=tk.W, pady=2)
        
        # 启用外部存储
        self.external_storage_var = tk.BooleanVar(value=False)
        external_storage_check = ttk.Checkbutton(settings_frame, text="启用外部存储", 
                                               variable=self.external_storage_var)
        external_storage_check.pack(anchor=tk.W, pady=2)
        
        # 模板框架
        template_frame = ttk.LabelFrame(main_frame, text="网站限制模板", padding="10")
        template_frame.pack(fill=tk.X, pady=5)
        
        # 模板选择和应用按钮
        template_select_frame = ttk.Frame(template_frame)
        template_select_frame.pack(fill=tk.X, pady=5)
        
        self.template_var = tk.StringVar()
        template_label = ttk.Label(template_select_frame, text="选择模板:", width=15)
        template_label.pack(side=tk.LEFT, padx=5)
        
        template_combo = ttk.Combobox(template_select_frame, textvariable=self.template_var, width=20)
        template_combo['values'] = list(self.templates.keys())
        template_combo.pack(side=tk.LEFT, padx=5)
        template_combo.current(0)
        
        ttk.Button(template_select_frame, text="应用模板", command=self._apply_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(template_select_frame, text="添加到现有列表", command=self._add_template_to_existing).pack(side=tk.LEFT, padx=5)
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="保存配置", command=self._save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="重置为默认值", command=self._reset_to_default).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="刷新", command=self._refresh).pack(side=tk.LEFT, padx=5)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=('SimHei', 9))
        status_label.pack(side=tk.LEFT, pady=5)
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        loaded_config = json.load(f)
                        
                        # 更新当前配置
                        self.config = {
                            "blocked_websites": loaded_config.get("blocked_websites", []),
                            "auto_clear_on_exit": loaded_config.get("auto_clear_on_exit", True),
                            "external_storage_enabled": loaded_config.get("external_storage_enabled", False)
                        }
                        
                        # 更新UI
                        self._update_ui_from_config()
                        logger.info(f"已从 {self.config_file} 加载配置")
                        self.status_var.set(f"已加载配置文件")
                except json.JSONDecodeError:
                    logger.error(f"配置文件格式错误: {self.config_file}")
                    self.status_var.set("配置文件格式错误，使用默认配置")
                    messagebox.showwarning("配置错误", "配置文件格式错误，将使用默认配置")
                except PermissionError:
                    logger.error(f"权限不足，无法读取配置文件: {self.config_file}")
                    self.status_var.set("读取配置失败: 权限不足")
                    messagebox.showerror("权限错误", f"权限不足，无法读取配置文件: {self.config_file}")
            else:
                # 检查是否存在旧位置的配置文件
                old_config_file = os.path.join(self.app_dir, "config.json")
                if os.path.exists(old_config_file):
                    try:
                        logger.info(f"发现旧位置的配置文件: {old_config_file}，尝试迁移")
                        # 读取旧配置
                        with open(old_config_file, 'r', encoding='utf-8') as f:
                            old_config = json.load(f)
                        # 迁移到新位置
                        self.config = {
                            "blocked_websites": old_config.get("blocked_websites", []),
                            "auto_clear_on_exit": old_config.get("auto_clear_on_exit", True),
                            "external_storage_enabled": old_config.get("external_storage_enabled", False)
                        }
                        self._update_ui_from_config()
                        logger.info("配置文件迁移成功")
                        self.status_var.set("已迁移配置文件")
                        messagebox.showinfo("配置迁移", "已从旧位置迁移配置文件")
                        # 尝试保存到新位置
                        self._save_config()
                    except Exception as migrate_error:
                        logger.error(f"迁移配置失败: {str(migrate_error)}")
                        self.status_var.set("配置文件不存在，使用默认配置")
                else:
                    logger.info(f"配置文件不存在: {self.config_file}，使用默认配置")
                    self.status_var.set("配置文件不存在，使用默认配置")
        except Exception as e:
            error_msg = f"加载配置时发生未知错误: {str(e)}"
            logger.error(error_msg)
            self.status_var.set(f"加载配置失败")
            messagebox.showerror("加载失败", error_msg)
    
    def _update_ui_from_config(self):
        """从配置更新UI"""
        # 更新网站列表
        self.website_tree.delete(*self.website_tree.get_children())
        for website in self.config["blocked_websites"]:
            self.website_tree.insert("", tk.END, values=(website,))
        
        # 更新设置选项
        self.auto_clear_var.set(self.config["auto_clear_on_exit"])
        self.external_storage_var.set(self.config["external_storage_enabled"])
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            # 验证配置
            if not self._validate_config():
                return
            
            # 确保配置目录存在
            if not os.path.exists(self.user_config_dir):
                try:
                    os.makedirs(self.user_config_dir, exist_ok=True)
                    logger.info(f"已创建配置目录: {self.user_config_dir}")
                except Exception as create_dir_error:
                    error_msg = f"无法创建配置目录: {str(create_dir_error)}"
                    logger.error(error_msg)
                    self.status_var.set(error_msg)
                    messagebox.showerror("目录创建失败", error_msg)
                    return
            
            # 读取现有配置（如果存在）以保留额外字段
            existing_config = {}
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        existing_config = json.load(f)
                    logger.info("成功读取现有配置")
                except Exception as read_error:
                    logger.warning(f"读取现有配置失败: {str(read_error)}，将使用新配置")
            
            # 更新配置数据
            config = {
                **existing_config,  # 保留现有配置中的其他字段
                "last_run": datetime.now().isoformat(),
                "version": "3.7",
                "blocked_websites": self.config["blocked_websites"],
                "auto_clear_on_exit": self.config["auto_clear_on_exit"],
                "external_storage_enabled": self.config["external_storage_enabled"]
            }
            
            # 保存为JSON格式 - 使用临时文件先写入再替换，避免写入失败损坏原文件
            temp_file = self.config_file + ".tmp"
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                
                # 原子性替换文件
                os.replace(temp_file, self.config_file)
                
                logger.info(f"配置已成功保存到 {self.config_file}")
                self.status_var.set(f"配置已成功保存")
                messagebox.showinfo("保存成功", f"配置已成功保存到:\n{self.config_file}")
            except Exception as write_error:
                logger.error(f"写入配置文件失败: {str(write_error)}")
                # 清理临时文件
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                raise write_error
        except PermissionError:
            error_msg = f"权限不足，无法写入配置文件: {self.config_file}\n请尝试以管理员身份运行程序或检查用户权限"
            logger.error(error_msg)
            self.status_var.set("保存配置失败: 权限不足")
            messagebox.showerror("权限错误", error_msg)
        except OSError as e:
            error_msg = f"操作系统错误，无法写入配置文件: {str(e)}"
            logger.error(error_msg)
            self.status_var.set(f"保存配置失败: 系统错误")
            messagebox.showerror("系统错误", error_msg)
        except Exception as e:
            error_msg = f"保存配置时发生未知错误: {str(e)}"
            logger.error(error_msg)
            self.status_var.set(f"保存配置失败")
            messagebox.showerror("保存失败", error_msg)
    
    def _validate_config(self):
        """验证配置的有效性"""
        # 验证网站列表中的域名格式
        import re
        for website in self.config["blocked_websites"]:
            # 使用与主程序相同的验证逻辑
            pattern = r'^([a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.)*[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?$'
            if not re.match(pattern, website):
                messagebox.showwarning("验证失败", f"域名格式无效: {website}")
                return False
            
            # 确保最后一部分至少有2个字符
            parts = website.split('.')
            if len(parts) < 2 or len(parts[-1]) < 2:
                messagebox.showwarning("验证失败", f"域名格式无效: {website} (顶级域名过短)")
                return False
            
            # 确保没有连续的点或在错误位置使用连字符
            if '..' in website or website.startswith('-') or website.endswith('-'):
                messagebox.showwarning("验证失败", f"域名格式无效: {website} (包含连续的点或不适当的连字符)")
                return False
        
        return True
    
    def _reset_to_default(self):
        """重置为默认配置"""
        if messagebox.askyesno("确认重置", "确定要将配置重置为默认值吗？这将清除所有自定义设置。"):
            self.config = self.default_config.copy()
            self._update_ui_from_config()
            self.status_var.set("已重置为默认配置")
            print("✓ 已重置为默认配置")
    
    def _refresh(self):
        """刷新配置"""
        self._load_config()
    
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
    
    def _add_website(self):
        """添加网站到列表"""
        website = self.add_entry.get().strip()
        if not website:
            messagebox.showwarning("输入错误", "请输入网站地址")
            return
        
        # 改进的域名验证，使用更宽松的规则以支持'kuaishou.com'等域名
            import re
            pattern = r'^([a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.)*[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?$'
            if not re.match(pattern, website):
                messagebox.showwarning("格式错误", "网站地址格式不正确，请输入有效的域名，如 example.com")
                return
        
        # 确保最后一部分至少有2个字符
        parts = website.split('.')
        if len(parts) < 2 or len(parts[-1]) < 2:
            messagebox.showwarning("格式错误", "域名格式不正确，顶级域名部分过短")
            return
            
        # 确保没有连续的点或在错误位置使用连字符
        if '..' in website or website.startswith('-') or website.endswith('-'):
            messagebox.showwarning("格式错误", "域名不能包含连续的点或在开头/结尾使用连字符")
            return
        
        # 检查是否已存在
        if website in self.config["blocked_websites"]:
            messagebox.showinfo("提示", f"该网站 {website} 已在列表中")
            return
        
        # 添加到配置
        self.config["blocked_websites"].append(website)
        # 更新UI
        self.website_tree.insert("", tk.END, values=(website,))
        
        self.add_entry.delete(0, tk.END)
        self.add_entry.insert(0, "example.com")
        self.status_var.set(f"已添加网站: {website}")
    
    def _remove_website(self):
        """从列表中移除网站"""
        selected = self.website_tree.selection()
        if not selected:
            messagebox.showwarning("选择错误", "请先选择要移除的网站")
            return
        
        removed_count = 0
        for item in selected:
            website = self.website_tree.item(item, "values")[0]
            # 从配置中移除
            if website in self.config["blocked_websites"]:
                self.config["blocked_websites"].remove(website)
                # 从UI中移除
                self.website_tree.delete(item)
                removed_count += 1
        
        self.status_var.set(f"已移除 {removed_count} 个网站")
    
    def _apply_template(self):
        """应用选定的模板，替换当前列表"""
        template_name = self.template_var.get()
        if not template_name:
            messagebox.showwarning("选择错误", "请选择一个模板")
            return
        
        if messagebox.askyesno("确认应用模板", f"确定要应用'{template_name}'吗？这将替换当前的阻止列表。"):
            # 应用模板
            self.config["blocked_websites"] = self.templates[template_name].copy()
            # 更新UI
            self._update_ui_from_config()
            self.status_var.set(f"已应用模板: {template_name}")
            logger.info(f"已应用模板: {template_name}")
    
    def _add_template_to_existing(self):
        """将选定模板的网站添加到现有列表"""
        template_name = self.template_var.get()
        if not template_name:
            messagebox.showwarning("选择错误", "请选择一个模板")
            return
        
        # 获取模板中的网站
        template_websites = self.templates[template_name]
        
        # 计算新增的网站数量
        original_count = len(self.config["blocked_websites"])
        
        # 添加新网站，避免重复
        for website in template_websites:
            if website not in self.config["blocked_websites"]:
                self.config["blocked_websites"].append(website)
        
        # 计算新增数量
        added_count = len(self.config["blocked_websites"]) - original_count
        
        # 更新UI
        self._update_ui_from_config()
        self.status_var.set(f"已将{added_count}个网站添加到现有列表")
        logger.info(f"已将{added_count}个网站从模板'{template_name}'添加到现有列表")
        messagebox.showinfo("添加成功", f"已将{added_count}个网站从模板'{template_name}'添加到现有列表")


# 命令行接口函数
def cli_mode(args=None):
    """命令行接口"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="网站限制配置管理工具")
    parser.add_argument("--add", help="添加网站到阻止列表")
    parser.add_argument("--remove", help="从阻止列表移除网站")
    parser.add_argument("--list", action="store_true", help="列出当前阻止的网站")
    parser.add_argument("--set-auto-clear", choices=["true", "false"], help="设置退出时是否自动清除限制")
    parser.add_argument("--set-external-storage", choices=["true", "false"], help="设置是否启用外部存储")
    parser.add_argument("--reset", action="store_true", help="重置配置为默认值")
    parser.add_argument("--gui", action="store_true", help="启动图形界面")
    
    args = parser.parse_args(args)
    
    # 获取配置文件路径
    app_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(app_dir, "config.json")
    
    # 加载配置
    config = {
        "blocked_websites": [],
        "auto_clear_on_exit": True,
        "external_storage_enabled": False
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                config["blocked_websites"] = loaded_config.get("blocked_websites", [])
                config["auto_clear_on_exit"] = loaded_config.get("auto_clear_on_exit", True)
                config["external_storage_enabled"] = loaded_config.get("external_storage_enabled", False)
        except Exception as e:
            print(f"错误: 无法加载配置文件: {str(e)}")
            return 1
    
    # 执行操作
    save_needed = False
    
    if args.gui:
        # 启动图形界面
        root = tk.Tk()
        app = ConfigManagerApp(root)
        root.mainloop()
        return 0
    
    if args.add:
        website = args.add.strip()
        # 改进的域名验证，使用更宽松的规则以支持'kuaishou.com'等域名
        import re
        pattern = r'^([a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.)*[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?$'
        if not re.match(pattern, website):
            print(f"错误: 无效的域名格式: {website}")
            return 1
        
        parts = website.split('.')
        if len(parts) < 2 or len(parts[-1]) < 2:
            print(f"错误: 无效的域名格式: {website}")
            return 1
            
        if '..' in website or website.startswith('-') or website.endswith('-'):
            print(f"错误: 无效的域名格式: {website}")
            return 1
        
        if website in config["blocked_websites"]:
            print(f"网站 {website} 已在阻止列表中")
        else:
            config["blocked_websites"].append(website)
            save_needed = True
            print(f"已添加网站到阻止列表: {website}")
    
    if args.remove:
        website = args.remove.strip()
        if website in config["blocked_websites"]:
            config["blocked_websites"].remove(website)
            save_needed = True
            print(f"已从阻止列表移除网站: {website}")
        else:
            print(f"网站 {website} 不在阻止列表中")
    
    if args.list:
        print("当前阻止的网站列表:")
        if config["blocked_websites"]:
            for i, website in enumerate(config["blocked_websites"], 1):
                print(f"  {i}. {website}")
        else:
            print("  (空)")
        
        print(f"\n设置:")
        print(f"  退出时自动清除: {config['auto_clear_on_exit']}")
        print(f"  启用外部存储: {config['external_storage_enabled']}")
    
    if args.set_auto_clear is not None:
        config["auto_clear_on_exit"] = (args.set_auto_clear.lower() == "true")
        save_needed = True
        print(f"已设置 '退出时自动清除' 为: {config['auto_clear_on_exit']}")
    
    if args.set_external_storage is not None:
        config["external_storage_enabled"] = (args.set_external_storage.lower() == "true")
        save_needed = True
        print(f"已设置 '启用外部存储' 为: {config['external_storage_enabled']}")
    
    if args.reset:
        config = {
            "blocked_websites": [],
            "auto_clear_on_exit": True,
            "external_storage_enabled": False
        }
        save_needed = True
        print("已重置配置为默认值")
    
    # 保存配置
    if save_needed:
        try:
            # 读取现有配置以保留额外字段
            existing_config = {}
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
            
            # 更新配置
            save_config = {
                **existing_config,
                "last_run": datetime.now().isoformat(),
                "version": "3.7",
                "blocked_websites": config["blocked_websites"],
                "auto_clear_on_exit": config["auto_clear_on_exit"],
                "external_storage_enabled": config["external_storage_enabled"]
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(save_config, f, indent=4, ensure_ascii=False)
            print(f"配置已保存到: {config_file}")
        except Exception as e:
            print(f"错误: 无法保存配置文件: {str(e)}")
            return 1
    
    # 如果没有提供任何参数，显示帮助
    if not any([args.add, args.remove, args.list, args.set_auto_clear, args.set_external_storage, args.reset, args.gui]):
        parser.print_help()
    
    return 0

def main():
    """主函数"""
    import sys
    
    # 如果没有命令行参数，启动GUI
    if len(sys.argv) == 1:
        root = tk.Tk()
        app = ConfigManagerApp(root)
        root.mainloop()
    else:
        # 否则，使用命令行模式
        sys.exit(cli_mode())

if __name__ == "__main__":
    main()