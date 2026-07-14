# -*- coding: utf-8 -*-
"""
网站阻止工具用户界面模块
使用PyQt6实现直观美观的用户界面
"""

import sys
import os
import platform
from typing import List, Dict, Any, Optional
import logging
import urllib.request
import urllib.error

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTreeWidget, QTreeWidgetItem, QLabel, QLineEdit, QPushButton, 
    QGroupBox, QRadioButton, QCheckBox, QTextEdit, QMessageBox,
    QSplitter, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressDialog, QFileDialog, QMenu, QToolBar, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QFont, QIcon, QCursor, QPixmap, QActionGroup, QAction

from logging_config import logger
from error_handler import ErrorHandler, ErrorType, ErrorInfo, error_handler
from website_blocker import website_blocker
from config_manager import config_manager


def is_nuitka():
    """检测是否在Nuitka打包环境中运行"""
    return "__compiled__" in globals() or hasattr(sys, 'frozen')


def get_app_dir():
    """获取应用程序目录（兼容Nuitka打包环境）"""
    if is_nuitka():
        # Nuitka打包环境：使用可执行文件目录
        return os.path.dirname(sys.executable)
    else:
        # 开发环境：使用脚本所在目录
        return os.path.dirname(os.path.abspath(__file__))


def get_resource_path(relative_path):
    """获取资源文件路径（兼容Nuitka打包环境）"""
    # 尝试多个可能的路径
    base_dir = get_app_dir()

    paths_to_try = [
        os.path.join(base_dir, relative_path),  # 可执行文件同级目录
        os.path.join(base_dir, 'lib', relative_path),  # lib目录下（某些打包工具）
        os.path.join(base_dir, 'resources', relative_path),  # resources目录下
    ]

    # 开发环境下，尝试脚本所在目录
    if not is_nuitka():
        script_dir = os.path.dirname(os.path.abspath(__file__))
        paths_to_try.insert(0, os.path.join(script_dir, relative_path))

    for path in paths_to_try:
        if os.path.exists(path):
            return path

    return None

class VersionCheckThread(QThread):
    """版本检查线程类，在后台执行版本检查"""
    version_checked = pyqtSignal(str, bool)  # 参数：最新版本号，是否有错误

    def __init__(self):
        super().__init__()
        self._is_running = False

    def run(self):
        """执行版本检查，包含重试机制"""
        # 防止重复运行
        if self._is_running:
            return

        self._is_running = True
        try:
            url = "https://websiteblocker.wangstation.dpdns.org/version.txt"
            max_retries = 2
            retry_count = 0

            # 创建请求对象，添加User-Agent模拟正常浏览器
            request = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                }
            )

            while retry_count <= max_retries:
                try:
                    logger.info(f"正在检查版本，尝试第 {retry_count + 1} 次，URL: {url}")

                    # 发送HTTP请求获取最新版本
                    with urllib.request.urlopen(request, timeout=10) as response:
                        # 检查响应状态码
                        if response.getcode() == 200:
                            # 读取并处理版本号
                            latest_version = response.read().decode('utf-8').strip()
                            logger.info(f"成功获取到最新版本: {latest_version}")

                            # 验证版本号格式（至少包含数字）
                            if any(char.isdigit() for char in latest_version):
                                self.version_checked.emit(latest_version, False)
                                return
                            else:
                                logger.warning(f"获取到的版本号格式无效: '{latest_version}'")
                                retry_count += 1
                        else:
                            logger.warning(f"版本检查请求失败，状态码: {response.getcode()}")
                            retry_count += 1

                except urllib.error.URLError as e:
                    logger.error(f"版本检查网络错误 (尝试 {retry_count + 1}/{max_retries + 1}): {str(e)}")
                    retry_count += 1
                except Exception as e:
                    logger.error(f"版本检查发生未知错误 (尝试 {retry_count + 1}/{max_retries + 1}): {str(e)}")
                    import traceback
                    logger.debug(f"详细错误信息: {traceback.format_exc()}")
                    retry_count += 1

            # 所有重试都失败
            logger.error("版本检查失败，已尝试最大次数")
            self.version_checked.emit("", True)
        finally:
            self._is_running = False


class WebsiteBlockerApp(QMainWindow):
    """网站阻止工具主应用类"""

    update_log_signal = pyqtSignal(str)
    update_status_signal = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()

        # 初始化关闭标志
        self._is_restarting = False

        # 模板缓存（优化启动速度）
        self._template_cache = None
        self._templates_loaded = False

        # 设置基本属性
        self.setWindowTitle("Website Blocker v3.9")
        self.setGeometry(100, 100, 900, 700)

        # 设置窗口图标（优化：减少路径检查）
        self._load_icon_fast()

        # 初始化UI（优化：延迟加载模板）
        self._init_ui()

        # 加载配置
        self._load_config()

        # 刷新列表
        self._refresh_list()

        # 注册错误处理回调
        error_handler.register_error_callback(ErrorType.UI_ERROR, self._handle_ui_error)

        # 初始化定时器
        self._init_timers()

        # 延迟启动版本检查（优化启动速度）
        QTimer.singleShot(2000, self._start_version_check)

    def _load_icon_fast(self):
        """快速加载图标（兼容Nuitka打包环境）"""
        icon_path = get_resource_path("app_icon.ico")

        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
            logger.debug(f"使用图标文件: {icon_path}")
        else:
            logger.warning("未找到图标文件")
    

    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建工具栏
        self._create_toolbar()
        
        # 创建拆分器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 创建左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 创建网站输入区域
        self._create_input_section(left_layout)
        
        # 创建模板选择区域
        self._create_template_section(left_layout)
        
        # 创建右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 创建标签页
        self._create_tabs(right_layout)
        
        # 将面板添加到拆分器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # 设置拆分器比例
        splitter.setSizes([300, 600])
        
        # 创建状态栏
        self._create_status_bar()
        
        # 显示欢迎信息
        self._show_welcome_message()
    
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = self.addToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        
        # 添加阻止按钮
        block_action = QAction("阻止网站", self)
        block_action.setToolTip("阻止当前输入的网站")
        block_action.triggered.connect(self._add_website)
        toolbar.addAction(block_action)
        
        # 添加解除阻止按钮
        unblock_action = QAction("解除阻止", self)
        unblock_action.setToolTip("解除选中网站的阻止")
        unblock_action.triggered.connect(self._remove_website)
        toolbar.addAction(unblock_action)
        
        toolbar.addSeparator()
        
        # 添加刷新按钮
        refresh_action = QAction("刷新列表", self)
        refresh_action.setToolTip("刷新网站列表")
        refresh_action.triggered.connect(self._refresh_list)
        toolbar.addAction(refresh_action)
        
        # 添加保存按钮
        save_action = QAction("保存配置", self)
        save_action.setToolTip("保存当前配置")
        save_action.triggered.connect(self._save_config)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 添加版本检查按钮
        version_check_action = QAction("检查更新", self)
        version_check_action.setToolTip("立即检查版本更新")
        version_check_action.triggered.connect(self._start_version_check)
        toolbar.addAction(version_check_action)
    
    def _create_input_section(self, parent_layout):
        """创建网站输入区域"""
        group_box = QGroupBox("网站管理")
        layout = QVBoxLayout(group_box)
        
        # 网站输入框
        input_layout = QHBoxLayout()
        self.website_input = QLineEdit()
        self.website_input.setPlaceholderText("输入要阻止的网站，例如: example.com")
        self.website_input.returnPressed.connect(self._add_website)
        input_layout.addWidget(self.website_input)
        
        # 添加按钮
        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self._add_website)
        input_layout.addWidget(self.add_button)
        
        layout.addLayout(input_layout)
        
        # 快捷操作按钮
        quick_layout = QHBoxLayout()
        self.clear_button = QPushButton("清除所有")
        self.clear_button.clicked.connect(self._clear_all)
        quick_layout.addWidget(self.clear_button)
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self._refresh_list)
        quick_layout.addWidget(self.refresh_button)
        
        layout.addLayout(quick_layout)
        
        parent_layout.addWidget(group_box)
    
    def _create_template_section(self, parent_layout):
        """创建模板选择区域"""
        group_box = QGroupBox("网站模板")
        layout = QVBoxLayout(group_box)
        
        # 创建模板列表
        self.template_tree = QTreeWidget()
        self.template_tree.setHeaderLabels(["模板类别"])
        self.template_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.template_tree.itemDoubleClicked.connect(self._add_template_websites)
        
        # 加载模板数据
        self._load_templates()
        
        layout.addWidget(self.template_tree)
        
        # 添加模板按钮
        template_button = QPushButton("添加选中模板")
        template_button.clicked.connect(self._add_template_websites)
        layout.addWidget(template_button)
        
        parent_layout.addWidget(group_box)
    
    def _create_tabs(self, parent_layout):
        """创建标签页"""
        self.tab_widget = QTabWidget()
        
        # 创建网站列表标签
        self._create_website_list_tab()
        
        # 创建日志标签
        self._create_log_tab()
        
        # 创建配置标签
        self._create_config_tab()
        
        # 创建帮助标签
        self._create_help_tab()
        
        parent_layout.addWidget(self.tab_widget)
    
    def _create_website_list_tab(self):
        """创建网站列表标签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 创建网站列表树
        self.website_tree = QTreeWidget()
        self.website_tree.setHeaderLabels(["网站", "状态", "添加时间"])
        self.website_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.website_tree.customContextMenuRequested.connect(self._show_context_menu)
        self.website_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        
        # 设置列宽
        header = self.website_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.website_tree)
        
        # 添加批量操作按钮
        batch_layout = QHBoxLayout()
        self.batch_remove_button = QPushButton("批量解除阻止")
        self.batch_remove_button.clicked.connect(self._batch_remove_websites)
        batch_layout.addWidget(self.batch_remove_button)
        
        batch_layout.addStretch()
        layout.addLayout(batch_layout)
        
        self.tab_widget.addTab(tab, "阻止列表")
    
    def _create_log_tab(self):
        """创建日志标签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.log_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.log_text)
        
        # 日志操作按钮
        log_layout = QHBoxLayout()
        self.clear_log_button = QPushButton("清除日志")
        self.clear_log_button.clicked.connect(self._clear_log)
        log_layout.addWidget(self.clear_log_button)
        
        self.export_log_button = QPushButton("导出日志")
        self.export_log_button.clicked.connect(self._export_log)
        log_layout.addWidget(self.export_log_button)
        
        log_layout.addStretch()
        layout.addLayout(log_layout)
        
        self.tab_widget.addTab(tab, "操作日志")
    
    def _create_config_tab(self):
        """创建配置标签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 创建配置表格
        self.config_table = QTableWidget()
        self.config_table.setColumnCount(2)
        self.config_table.setHorizontalHeaderLabels(["配置项", "值"])
        self.config_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.config_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # 加载配置数据
        self._load_config_to_table()
        
        layout.addWidget(self.config_table)
        
        # 配置操作按钮
        config_layout = QHBoxLayout()
        self.save_config_button = QPushButton("保存配置")
        self.save_config_button.clicked.connect(self._save_config_table)
        config_layout.addWidget(self.save_config_button)
        
        self.reset_config_button = QPushButton("重置默认")
        self.reset_config_button.clicked.connect(self._reset_config)
        config_layout.addWidget(self.reset_config_button)
        
        self.import_config_button = QPushButton("导入配置")
        self.import_config_button.clicked.connect(self._import_config)
        config_layout.addWidget(self.import_config_button)
        
        self.export_config_button = QPushButton("导出配置")
        self.export_config_button.clicked.connect(self._export_config)
        config_layout.addWidget(self.export_config_button)
        
        config_layout.addStretch()
        layout.addLayout(config_layout)
        
        self.tab_widget.addTab(tab, "配置管理")
    
    def _create_help_tab(self):
        """创建帮助标签"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>Website Blocker使用说明</h2>
        <h3>基本功能</h3>
        <p>1. 在左侧输入框中输入要阻止的网站，点击"添加"按钮</p>
        <p>2. 网站将被添加到阻止列表中并立即生效</p>
        <p>3. 从列表中选择网站，点击"解除阻止"按钮可解除限制</p>
        <h3>模板使用</h3>
        <p>1. 选择左侧的网站模板类别</p>
        <p>2. 点击"添加选中模板"按钮可批量添加模板中的网站</p>
        <h3>注意事项</h3>
        <p>1. 程序需要管理员权限才能正常工作</p>
        <p>2. 修改后会自动刷新DNS缓存</p>
        <p>3. 所有修改都会自动保存到配置文件</p>
        <h3>版本信息</h3>
        <p>当前版本: 3.9</p>
        <p>软件开发日期: 2025-12-13</p>
        """)
        
        layout.addWidget(help_text)
        self.tab_widget.addTab(tab, "帮助")
    
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")
        
        # 添加状态标签
        self.blocked_count_label = QLabel("已阻止: 0")
        self.status_bar.addPermanentWidget(self.blocked_count_label)
        
        self.version_label = QLabel("v3.9")
        self.status_bar.addPermanentWidget(self.version_label)
    
    def _init_timers(self):
        """初始化定时器"""
        # 设置定时器定期保存配置
        self.save_timer = QTimer(self)
        self.save_timer.timeout.connect(self._save_config)
        self.save_timer.start(30000)  # 每30秒保存一次配置
        
        # 设置定时器更新状态
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(5000)  # 每5秒更新一次状态
        
        # 设置定时器定期检查版本
        self.version_check_timer = QTimer(self)
        self.version_check_timer.timeout.connect(self._check_version_periodically)
        self.version_check_timer.start(3600000)  # 每小时检查一次是否需要更新
    
    def _load_templates(self):
        """加载网站模板数据"""
        # 获取模板数据（使用缓存）
        if self._template_cache is None:
            self._template_cache = config_manager.get_website_templates()

        templates = self._template_cache

        if not templates:
            logger.warning("模板数据为空")
            return

        # 使用批量添加优化性能
        self.template_tree.setUpdatesEnabled(False)
        try:
            for category, websites in templates.items():
                category_item = QTreeWidgetItem(self.template_tree)
                category_item.setText(0, category)
                category_item.setFlags(category_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                category_item.setCheckState(0, Qt.CheckState.Unchecked)

                for website in websites:
                    website_item = QTreeWidgetItem(category_item)
                    website_item.setText(0, website)
                    website_item.setFlags(website_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    website_item.setCheckState(0, Qt.CheckState.Unchecked)

            self.template_tree.expandAll()
        finally:
            self.template_tree.setUpdatesEnabled(True)

        self._templates_loaded = True
        logger.info(f"已加载 {len(templates)} 个模板类别")
    
    def _add_website(self):
        """添加网站到阻止列表"""
        website = self.website_input.text().strip()
        
        if not website:
            QMessageBox.warning(self, "警告", "请输入要阻止的网站")
            return
        
        if website_blocker.add_website(website):
            if website_blocker.save_blocked_websites():
                self.website_input.clear()
                self._refresh_list()
                self._log_message(f"已阻止网站: {website}")
                QMessageBox.information(self, "成功", f"网站 {website} 已被阻止")
            else:
                QMessageBox.error(self, "错误", "保存阻止列表失败")
        else:
            QMessageBox.error(self, "错误", f"添加网站 {website} 失败")
    
    def _remove_website(self):
        """从阻止列表中移除网站"""
        selected_items = self.website_tree.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "警告", "请选择要解除阻止的网站")
            return
        
        # 确认操作
        reply = QMessageBox.question(
            self, "确认", f"确定要解除阻止选中的 {len(selected_items)} 个网站吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        success_count = 0
        
        for item in selected_items:
            website = item.text(0)
            if website_blocker.remove_website(website):
                success_count += 1
                self._log_message(f"已解除阻止: {website}")
        
        if success_count > 0:
            if website_blocker.save_blocked_websites():
                self._refresh_list()
                QMessageBox.information(self, "成功", f"已解除阻止 {success_count} 个网站")
            else:
                QMessageBox.error(self, "错误", "保存阻止列表失败")
        else:
            QMessageBox.warning(self, "警告", "没有成功解除阻止任何网站")
    
    def _batch_remove_websites(self):
        """批量解除阻止网站"""
        self._remove_website()
    
    def _add_template_websites(self):
        """添加模板中的网站"""
        selected_items = self.template_tree.selectedItems()
        check_items = []
        
        # 检查是否有选中项
        if selected_items:
            for item in selected_items:
                if item.childCount() > 0:  # 是类别
                    for i in range(item.childCount()):
                        check_items.append(item.child(i))
                else:  # 是单个网站
                    check_items.append(item)
        else:
            # 检查是否有勾选的项目
            def collect_checked_items(tree_item):
                if tree_item.checkState(0) == Qt.CheckState.Checked:
                    check_items.append(tree_item)
                for i in range(tree_item.childCount()):
                    collect_checked_items(tree_item.child(i))
            
            for i in range(self.template_tree.topLevelItemCount()):
                collect_checked_items(self.template_tree.topLevelItem(i))
        
        if not check_items:
            QMessageBox.warning(self, "警告", "请选择或勾选要添加的网站模板")
            return
        
        # 收集要添加的网站
        websites_to_add = []
        for item in check_items:
            if item.childCount() == 0:  # 只添加单个网站
                websites_to_add.append(item.text(0))
        
        if not websites_to_add:
            QMessageBox.warning(self, "警告", "没有选中任何可添加的网站")
            return
        
        # 确认操作
        reply = QMessageBox.question(
            self, "确认", f"确定要添加 {len(websites_to_add)} 个模板网站吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # 添加网站
        success_count = 0
        for website in websites_to_add:
            if website_blocker.add_website(website):
                success_count += 1
        
        if success_count > 0:
            if website_blocker.save_blocked_websites():
                self._refresh_list()
                self._log_message(f"已从模板添加 {success_count} 个网站")
                QMessageBox.information(self, "成功", f"已添加 {success_count} 个模板网站")
            else:
                QMessageBox.error(self, "错误", "保存阻止列表失败")
        else:
            QMessageBox.warning(self, "警告", "没有成功添加任何网站")
    
    def _clear_all(self):
        """清除所有阻止的网站"""
        if not website_blocker.blocked_websites:
            QMessageBox.information(self, "提示", "没有被阻止的网站")
            return
        
        # 确认操作
        reply = QMessageBox.question(
            self, "确认", f"确定要解除所有 {len(website_blocker.blocked_websites)} 个网站的阻止吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        if website_blocker.clear_all_websites():
            if website_blocker.save_blocked_websites():
                self._refresh_list()
                self._log_message("已清除所有阻止的网站")
                QMessageBox.information(self, "成功", "所有网站的阻止已解除")
            else:
                QMessageBox.error(self, "错误", "保存阻止列表失败")
        else:
            QMessageBox.error(self, "错误", "清除阻止列表失败")
    
    def _refresh_list(self):
        """刷新网站列表显示"""
        # 检查website_tree是否存在
        if not hasattr(self, 'website_tree'):
            logger.debug("website_tree尚未创建，跳过列表刷新")
            return
        
        # 清空列表
        self.website_tree.clear()
        
        # 重新加载被阻止的网站
        blocked_websites = website_blocker.load_blocked_websites()
        
        # 添加到树状列表
        for website in blocked_websites:
            item = QTreeWidgetItem(self.website_tree)
            item.setText(0, website)
            item.setText(1, "已阻止")
            item.setText(2, "-" if platform.system() != "Windows" else "自动")  # 简化的时间显示
        
        # 更新状态栏计数
        self.blocked_count_label.setText(f"已阻止: {len(blocked_websites)}")
    
    def _load_config(self):
        """加载配置"""
        config = config_manager.load_config()
        # 这里可以根据需要加载特定的配置到UI
    
    def _save_config(self):
        """保存配置"""
        try:
            config_manager.save_config()
            logger.info("配置已保存")
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")
    
    def _show_context_menu(self, position):
        """显示上下文菜单"""
        menu = QMenu()
        
        remove_action = QAction("解除阻止")
        remove_action.triggered.connect(self._remove_website)
        menu.addAction(remove_action)
        
        menu.exec(QCursor.pos())
    
    def _log_message(self, message):
        """记录消息到日志标签"""
        import datetime
        import re
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 移除HTML标签，只保留纯文本
        plain_text = re.sub(r'<[^>]+>', '', message)
        log_entry = f"[{timestamp}] {plain_text}\n"
        
        # 使用insertPlainText确保只显示纯文本
        self.log_text.insertPlainText(log_entry)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def _clear_log(self):
        """清除日志"""
        self.log_text.clear()
    
    def _export_log(self):
        """导出日志"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出日志", "website_blocker_log.txt", "文本文件 (*.txt)"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.toPlainText())
            QMessageBox.information(self, "成功", "日志已导出")
    
    def _update_status(self):
        """更新状态栏"""
        blocked_count = len(website_blocker.blocked_websites)
        self.status_bar.showMessage(f"就绪，已阻止 {blocked_count} 个网站")
    
    def _load_config_to_table(self):
        """加载配置到表格"""
        config = config_manager.config
        self.config_table.setRowCount(0)
        
        self._add_config_items(config, "")
    
    def _add_config_items(self, config_dict, parent_key):
        """递归添加配置项到表格"""
        for key, value in config_dict.items():
            current_key = f"{parent_key}.{key}" if parent_key else key
            
            if isinstance(value, dict):
                # 添加类别行
                row = self.config_table.rowCount()
                self.config_table.insertRow(row)
                self.config_table.setItem(row, 0, QTableWidgetItem(current_key))
                self.config_table.setItem(row, 1, QTableWidgetItem("(类别)"))
                
                # 递归添加子项
                self._add_config_items(value, current_key)
            else:
                # 添加配置项行
                row = self.config_table.rowCount()
                self.config_table.insertRow(row)
                self.config_table.setItem(row, 0, QTableWidgetItem(current_key))
                self.config_table.setItem(row, 1, QTableWidgetItem(str(value)))
    
    def _save_config_table(self):
        """保存配置表格中的修改"""
        for row in range(self.config_table.rowCount()):
            key_item = self.config_table.item(row, 0)
            value_item = self.config_table.item(row, 1)
            
            if key_item and value_item:
                key = key_item.text()
                value = value_item.text()
                
                # 跳过类别行
                if value != "(类别)":
                    # 尝试解析值类型
                    try:
                        if value.lower() == "true":
                            parsed_value = True
                        elif value.lower() == "false":
                            parsed_value = False
                        elif value.isdigit():
                            parsed_value = int(value)
                        elif value.replace('.', '', 1).isdigit():
                            parsed_value = float(value)
                        else:
                            parsed_value = value
                        
                        config_manager.set(key, parsed_value)
                    except Exception as e:
                        logger.error(f"设置配置项失败: {key} = {value}, 错误: {str(e)}")
        
        QMessageBox.information(self, "成功", "配置已保存")
    
    def _reset_config(self):
        """重置配置为默认值"""
        reply = QMessageBox.question(
            self, "确认", "确定要重置所有配置为默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if config_manager.reset_config():
                self._load_config_to_table()
                QMessageBox.information(self, "成功", "配置已重置为默认值")
            else:
                QMessageBox.error(self, "错误", "重置配置失败")
    
    def _import_config(self):
        """导入配置"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "导入配置", "", "配置文件 (*.json)"
        )
        
        if filename:
            import json
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    imported_config = json.load(f)
                    
                # 这里可以添加配置验证逻辑
                config_manager.config = imported_config
                config_manager.save_config()
                self._load_config_to_table()
                QMessageBox.information(self, "成功", "配置已导入")
                
            except Exception as e:
                QMessageBox.error(self, "错误", f"导入配置失败: {str(e)}")
    
    def _export_config(self):
        """导出配置"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出配置", "website_blocker_config.json", "配置文件 (*.json)"
        )
        
        if filename:
            import json
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config_manager.config, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "成功", "配置已导出")
            except Exception as e:
                QMessageBox.error(self, "错误", f"导出配置失败: {str(e)}")
    
    def _show_welcome_message(self):
        """显示欢迎信息"""
        welcome_text = """
Welcome to Website Blocker v3.9
这是一个功能强大的网站阻止工具，可以帮助您控制网站访问权限。

主要功能：
- 阻止单个网站
- 批量阻止模板网站
- 实时查看阻止列表
- 灵活的配置管理
- 完整的操作日志

使用前请确保以管理员权限运行！
        """
        
        self._log_message(welcome_text)
    
    def _start_version_check(self):
        """启动版本检查线程"""
        self.version_thread = VersionCheckThread()
        self.version_thread.version_checked.connect(self._handle_version_check)
        self.version_thread.start()
    
    def _simulate_version_check(self, mock_version: str = "4.0"):
        """模拟版本检查，用于测试
        
        Args:
            mock_version: 模拟的最新版本号
        """
        logger.info(f"开始模拟版本检查，模拟版本: {mock_version}")
        # 直接调用处理函数，模拟版本检查结果
        self._handle_version_check(mock_version, False)
    
    def _on_simulate_version_check(self):
        """处理模拟版本检查按钮点击事件"""
        from PyQt6.QtWidgets import QInputDialog
        
        # 显示输入对话框，让用户输入模拟版本号
        mock_version, ok = QInputDialog.getText(
            self, 
            "模拟版本检查", 
            "请输入要测试的版本号:",
            text="4.0"
        )
        
        if ok and mock_version:
            # 调用模拟版本检查方法
            self._simulate_version_check(mock_version.strip())
    
    def _check_version_periodically(self):
        """定期检查版本更新"""
        try:
            # 检查是否启用了版本检查
            version_check_enabled = config_manager.get("version_check.enabled", True)
            if not version_check_enabled:
                return
            
            # 获取配置的检查间隔（小时）
            check_interval_hours = config_manager.get("version_check.check_interval_hours", 24)
            
            # 获取最后检查时间
            last_check_time = config_manager.get("version_check.last_check_time", 0)
            
            # 当前时间（Unix时间戳，秒）
            import time
            current_time = int(time.time())
            
            # 检查是否需要更新
            if current_time - last_check_time >= check_interval_hours * 3600:
                # 启动版本检查
                self._start_version_check()
                logger.info("执行了定期版本检查")
                # 注意：最后检查时间将在成功获取版本号后更新
                
        except Exception as e:
            logger.error(f"定期版本检查失败: {str(e)}")
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """比较两个版本号，支持多种格式（如 "3.9"、"39"、"3.9.1"）
        
        Args:
            version1: 第一个版本号
            version2: 第二个版本号
            
        Returns:
            0: 版本相同
            1: version1 > version2
            -1: version1 < version2
        """
        try:
            # 确保版本号为字符串
            version1 = str(version1).strip()
            version2 = str(version2).strip()
            
            # 特殊处理：如果两个版本号完全相同，直接返回
            if version1 == version2:
                return 0
            
            # 处理纯数字版本号（如 "39"）
            if version1.isdigit() and version2.isdigit():
                v1 = int(version1)
                v2 = int(version2)
                return 1 if v1 > v2 else -1
            
            # 处理包含点号的版本号（如 "3.9"、"3.9.1"）
            if "." in version1 or "." in version2:
                # 将版本号拆分为数字列表
                def parse_version(v):
                    try:
                        # 如果是纯数字，转换为整数并作为单元素列表
                        if v.isdigit():
                            return [int(v)]
                        # 否则按点号拆分
                        return list(map(int, v.split(".")))
                    except:
                        # 如果解析失败，返回 [0]
                        return [0]
                
                v1_parts = parse_version(version1)
                v2_parts = parse_version(version2)
                
                # 补全较短的版本号，使它们长度相同
                max_length = max(len(v1_parts), len(v2_parts))
                v1_parts += [0] * (max_length - len(v1_parts))
                v2_parts += [0] * (max_length - len(v2_parts))
                
                # 逐位比较
                for v1, v2 in zip(v1_parts, v2_parts):
                    if v1 > v2:
                        return 1
                    elif v1 < v2:
                        return -1
                
                # 所有位都相同
                return 0
            
            # 最后的回退方案：字符串比较
            logger.warning(f"使用字符串比较版本号: {version1} vs {version2}")
            return 1 if version1 > version2 else -1
            
        except Exception as e:
            logger.error(f"版本比较失败: {str(e)}")
            # 安全回退：直接比较字符串
            return 1 if version1 > version2 else (-1 if version1 < version2 else 0)
    
    def _get_current_version(self):
        """获取当前应用版本号"""
        # 从配置中获取版本号，如果没有则使用默认值
        current_version = config_manager.get("version", "3.9")
        return current_version
    
    def _handle_version_check(self, latest_version: str, error: bool):
        """处理版本检查结果"""
        # 动态获取当前版本号
        current_version = self._get_current_version()
        
        if error or not latest_version:
            # 发生错误或未获取到版本号，记录日志但不显示提示
            logger.info(f"版本检查失败或未获取到有效版本号，error: {error}, latest_version: '{latest_version}'")
            return
        
        try:
            # 确保版本号有效
            if not any(char.isdigit() for char in latest_version):
                logger.warning(f"获取到的版本号无效，不包含数字: '{latest_version}'")
                return
            
            logger.info(f"正在比较版本，当前版本: {current_version}，最新版本: {latest_version}")
            
            # 使用改进的版本比较函数
            comparison_result = self._compare_versions(latest_version, current_version)
            
            logger.info(f"版本比较结果: {comparison_result} (0: 相同, 1: 有新版本, -1: 旧版本)")
            
            # 更新最后检查时间（无论版本结果如何，只要成功获取到版本号就更新）
            import time
            config_manager.set("version_check.last_check_time", int(time.time()))
            logger.info("已更新版本检查时间")
            
            if comparison_result == 0:
                logger.info(f"当前版本 {current_version} 是最新版本")
                # 可以选择显示提示，或者只记录日志
                # QMessageBox.information(self, "版本信息", f"当前版本 {current_version} 是最新版本")
            elif comparison_result > 0:
                # 有新版本可用，显示通知窗口
                logger.info(f"发现新版本 {latest_version}，当前版本 {current_version}")
                
                reply = QMessageBox.question(
                    self, 
                    "版本更新", 
                    f"🎉 发现新版本 {latest_version}！\n\n"+
                    f"当前版本: {current_version}\n"+
                    f"最新版本: {latest_version}\n\n"+
                    f"新版本可能包含新功能、优化和bug修复。\n\n"+
                    f"是否立即前往更新网页？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # 打开更新网页
                    update_url = "https://websiteblocker.wangstation.dpdns.org/download.html"
                    logger.info(f"用户选择前往更新网页: {update_url}")
                    import webbrowser
                    webbrowser.open(update_url)
                else:
                    logger.info("用户选择暂不更新")
            else:
                # 版本号比当前版本低，可能是测试版本或服务器问题
                logger.info(f"检测到版本 {latest_version}，当前版本 {current_version} 更高级")
                # 可以选择显示提示，也可以只记录日志
                
        except Exception as e:
            # 版本比较或显示提示时发生错误，记录详细日志
            logger.error(f"版本检查处理错误: {str(e)}")
            import traceback
            logger.debug(f"详细错误信息: {traceback.format_exc()}")
            
            # 显示错误提示，帮助用户了解情况
            QMessageBox.warning(
                self, 
                "版本检查错误", 
                f"版本检查过程中发生错误: {str(e)}\n\n"+
                f"当前版本: {current_version}\n"+
                f"获取到的版本: {latest_version}\n\n"+
                f"请稍后重试或手动检查更新。"
            )
    
    def _handle_ui_error(self, error_info: ErrorInfo):
        """处理UI相关错误"""
        QMessageBox.error(
            self,
            "UI错误",
            f"发生UI错误: {error_info.message}\n\n详细信息: {str(error_info.original_error)}"
        )
    
    def closeEvent(self, event):
        """窗口关闭事件（优化：添加资源清理）"""
        # 保存配置
        self._save_config()

        # 停止所有定时器
        if hasattr(self, 'save_timer'):
            self.save_timer.stop()
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        if hasattr(self, 'version_check_timer'):
            self.version_check_timer.stop()

        # 清理版本检查线程
        if hasattr(self, 'version_thread') and self.version_thread.isRunning():
            self.version_thread.quit()
            self.version_thread.wait(1000)

        # 如果是因为重启而关闭，则不显示确认对话框
        if self._is_restarting:
            event.accept()
        else:
            # 确认关闭
            reply = QMessageBox.question(
                self, "确认", "确定要退出程序吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()

def main():
    """程序入口函数（优化启动速度，兼容Nuitka）"""
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("Website Blocker")

    # 实现窗口唯一性校验机制
    from PyQt6.QtCore import QSharedMemory
    shared_memory = QSharedMemory("WebsiteBlocker_Instance_Key")
    if shared_memory.attach():
        # 已有实例在运行，显示已存在的窗口并退出
        QMessageBox.information(None, "提示", "程序已经在运行中。")
        sys.exit()

    if not shared_memory.create(1):
        # 创建共享内存失败，可能是权限问题
        logger.warning("无法确保程序只运行一个实例。")

    # 设置应用图标（兼容Nuitka）
    icon_path = get_resource_path("app_icon.ico")
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))

    # 在创建主窗口之前，先检查管理员权限（后台检查，不阻塞UI）
    has_admin = website_blocker._is_admin()
    if not has_admin:
        reply = QMessageBox.warning(
            None,
            "权限请求",
            "程序需要管理员权限才能正常工作。\n\n是否立即申请管理员权限？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if website_blocker._run_as_admin():
                sys.exit()
            else:
                QMessageBox.critical(
                    None,
                    "错误",
                    "申请管理员权限失败。\n程序将以普通用户权限运行，部分功能可能无法使用。",
                    QMessageBox.StandardButton.Ok
                )
        else:
            QMessageBox.warning(
                None,
                "权限警告",
                "程序将以普通用户权限运行，部分功能可能无法使用。",
                QMessageBox.StandardButton.Ok
            )

    # 创建主窗口
    window = WebsiteBlockerApp()
    window.show()

    # 运行应用
    exit_code = app.exec()

    # 清理共享内存
    shared_memory.detach()

    sys.exit(exit_code)

if __name__ == "__main__":
    main()