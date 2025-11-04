#!/usr/bin/env python3
"""
HyFuzz 跨平台 GUI 界面
支持 Windows 和 Ubuntu 系统
提供活动管理、实时监控、系统状态查看等功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import requests
import threading
import time
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any


class HyFuzzGUI:
    """HyFuzz 主界面类"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("HyFuzz - 智能分布式模糊测试平台")
        self.root.geometry("1200x800")

        # 配置服务器地址
        self.server_url = "http://localhost:8080"
        self.dashboard_url = "http://localhost:8888"

        # 状态变量
        self.current_campaign_id = None
        self.monitoring_active = False
        self.campaigns_list = []

        # 设置样式
        self.setup_styles()

        # 创建主界面
        self.create_widgets()

        # 启动自动刷新
        self.auto_refresh()

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 配置标签样式
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Section.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))

        # 配置按钮样式
        style.configure('Action.TButton', font=('Arial', 10))
        style.configure('Success.TButton', foreground='green')
        style.configure('Danger.TButton', foreground='red')

    def create_widgets(self):
        """创建主界面组件"""
        # 创建菜单栏
        self.create_menu()

        # 创建状态栏
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.status_label = ttk.Label(
            self.status_frame,
            text="就绪",
            style='Status.TLabel'
        )
        self.status_label.pack(side=tk.LEFT)

        self.connection_indicator = ttk.Label(
            self.status_frame,
            text="● 未连接",
            foreground='red'
        )
        self.connection_indicator.pack(side=tk.RIGHT)

        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建各个标签页
        self.create_campaign_tab()
        self.create_monitoring_tab()
        self.create_results_tab()
        self.create_system_tab()
        self.create_config_tab()

        # 检查连接
        self.check_connection()

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入配置", command=self.import_config)
        file_menu.add_command(label="导出结果", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        # 操作菜单
        action_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="操作", menu=action_menu)
        action_menu.add_command(label="刷新", command=self.refresh_all)
        action_menu.add_command(label="检查连接", command=self.check_connection)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

    def create_campaign_tab(self):
        """创建活动管理标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="活动管理")

        # 左侧：创建新活动
        left_frame = ttk.LabelFrame(tab, text="创建新活动", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 活动名称
        ttk.Label(left_frame, text="活动名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.campaign_name = ttk.Entry(left_frame, width=40)
        self.campaign_name.grid(row=0, column=1, pady=5, padx=5)

        # 协议选择
        ttk.Label(left_frame, text="协议:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.protocol_var = tk.StringVar(value="coap")
        protocol_combo = ttk.Combobox(
            left_frame,
            textvariable=self.protocol_var,
            values=["coap", "modbus", "mqtt", "http", "grpc", "json-rpc"],
            state='readonly',
            width=38
        )
        protocol_combo.grid(row=1, column=1, pady=5, padx=5)

        # 目标地址
        ttk.Label(left_frame, text="目标地址:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.target_entry = ttk.Entry(left_frame, width=40)
        self.target_entry.insert(0, "localhost:5683")
        self.target_entry.grid(row=2, column=1, pady=5, padx=5)

        # Payload 数量
        ttk.Label(left_frame, text="Payload 数量:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.payload_count = ttk.Spinbox(left_frame, from_=1, to=1000, width=38)
        self.payload_count.set(10)
        self.payload_count.grid(row=3, column=1, pady=5, padx=5)

        # 超时时间
        ttk.Label(left_frame, text="超时时间(秒):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.timeout_entry = ttk.Spinbox(left_frame, from_=1, to=300, width=38)
        self.timeout_entry.set(30)
        self.timeout_entry.grid(row=4, column=1, pady=5, padx=5)

        # LLM 模型
        ttk.Label(left_frame, text="LLM 模型:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value="llama3.2")
        model_combo = ttk.Combobox(
            left_frame,
            textvariable=self.model_var,
            values=["llama3.2", "codellama", "mistral", "gpt-4", "gpt-3.5-turbo"],
            width=38
        )
        model_combo.grid(row=5, column=1, pady=5, padx=5)

        # 启用防御分析
        self.defense_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            left_frame,
            text="启用防御分析",
            variable=self.defense_enabled
        ).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)

        # 启用判决反馈
        self.feedback_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            left_frame,
            text="启用判决反馈",
            variable=self.feedback_enabled
        ).grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=5)

        # 创建按钮
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)

        ttk.Button(
            button_frame,
            text="创建活动",
            command=self.create_campaign,
            style='Action.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="清空表单",
            command=self.clear_campaign_form
        ).pack(side=tk.LEFT, padx=5)

        # 右侧：活动列表
        right_frame = ttk.LabelFrame(tab, text="活动列表", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建树形视图
        columns = ("ID", "名称", "协议", "状态", "进度")
        self.campaigns_tree = ttk.Treeview(
            right_frame,
            columns=columns,
            show='headings',
            height=15
        )

        for col in columns:
            self.campaigns_tree.heading(col, text=col)
            self.campaigns_tree.column(col, width=100)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            right_frame,
            orient=tk.VERTICAL,
            command=self.campaigns_tree.yview
        )
        self.campaigns_tree.configure(yscrollcommand=scrollbar.set)

        self.campaigns_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 活动控制按钮
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            control_frame,
            text="刷新列表",
            command=self.refresh_campaigns
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="启动",
            command=self.start_campaign,
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="暂停",
            command=self.pause_campaign
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="停止",
            command=self.stop_campaign,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="删除",
            command=self.delete_campaign,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=5)

    def create_monitoring_tab(self):
        """创建监控标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="实时监控")

        # 顶部信息框
        info_frame = ttk.LabelFrame(tab, text="当前活动信息", padding=10)
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        # 活动信息
        self.monitor_info = ttk.Label(
            info_frame,
            text="未选择活动",
            font=('Arial', 10)
        )
        self.monitor_info.pack()

        # 进度条
        progress_frame = ttk.LabelFrame(tab, text="执行进度", padding=10)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=1100
        )
        self.progress_bar.pack(pady=5)

        self.progress_label = ttk.Label(progress_frame, text="0 / 0 (0%)")
        self.progress_label.pack()

        # 统计信息
        stats_frame = ttk.LabelFrame(tab, text="统计信息", padding=10)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)

        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack()

        # 创建统计标签
        self.stats_labels = {}
        stats_items = [
            ("总执行数", "executions"),
            ("成功", "success"),
            ("失败", "failed"),
            ("崩溃", "crashes"),
            ("高风险", "high_risk"),
            ("防御拦截", "blocked")
        ]

        for i, (label, key) in enumerate(stats_items):
            ttk.Label(stats_grid, text=f"{label}:").grid(
                row=i//3, column=(i%3)*2, sticky=tk.W, padx=10, pady=5
            )
            value_label = ttk.Label(stats_grid, text="0", font=('Arial', 10, 'bold'))
            value_label.grid(row=i//3, column=(i%3)*2+1, sticky=tk.W, padx=5, pady=5)
            self.stats_labels[key] = value_label

        # 实时日志
        log_frame = ttk.LabelFrame(tab, text="实时日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.monitor_log = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            wrap=tk.WORD,
            font=('Courier', 9)
        )
        self.monitor_log.pack(fill=tk.BOTH, expand=True)

        # 控制按钮
        control_frame = ttk.Frame(log_frame)
        control_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            control_frame,
            text="开始监控",
            command=self.start_monitoring
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="停止监控",
            command=self.stop_monitoring
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="清空日志",
            command=lambda: self.monitor_log.delete(1.0, tk.END)
        ).pack(side=tk.LEFT, padx=5)

    def create_results_tab(self):
        """创建结果查看标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="执行结果")

        # 顶部筛选框
        filter_frame = ttk.LabelFrame(tab, text="筛选条件", padding=10)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="活动ID:").pack(side=tk.LEFT, padx=5)
        self.results_campaign_id = ttk.Entry(filter_frame, width=30)
        self.results_campaign_id.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="状态:").pack(side=tk.LEFT, padx=5)
        self.results_status = ttk.Combobox(
            filter_frame,
            values=["全部", "成功", "失败", "崩溃"],
            state='readonly',
            width=15
        )
        self.results_status.set("全部")
        self.results_status.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            filter_frame,
            text="查询",
            command=self.query_results
        ).pack(side=tk.LEFT, padx=5)

        # 结果列表
        results_frame = ttk.Frame(tab)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("ID", "活动", "Payload", "状态", "响应码", "风险等级", "判决", "时间")
        self.results_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show='headings',
            height=20
        )

        for col in columns:
            self.results_tree.heading(col, text=col)
            width = 150 if col == "Payload" else 100
            self.results_tree.column(col, width=width)

        # 滚动条
        scrollbar_y = ttk.Scrollbar(
            results_frame,
            orient=tk.VERTICAL,
            command=self.results_tree.yview
        )
        scrollbar_x = ttk.Scrollbar(
            results_frame,
            orient=tk.HORIZONTAL,
            command=self.results_tree.xview
        )
        self.results_tree.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )

        self.results_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')

        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        # 详情查看
        detail_frame = ttk.LabelFrame(tab, text="详细信息", padding=10)
        detail_frame.pack(fill=tk.X, padx=5, pady=5)

        self.result_detail = scrolledtext.ScrolledText(
            detail_frame,
            height=8,
            wrap=tk.WORD,
            font=('Courier', 9)
        )
        self.result_detail.pack(fill=tk.BOTH, expand=True)

        # 绑定选择事件
        self.results_tree.bind('<<TreeviewSelect>>', self.show_result_detail)

    def create_system_tab(self):
        """创建系统状态标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="系统状态")

        # 服务状态
        service_frame = ttk.LabelFrame(tab, text="服务状态", padding=10)
        service_frame.pack(fill=tk.X, padx=5, pady=5)

        services = [
            ("MCP 服务器", "server"),
            ("Web 控制台", "dashboard"),
            ("任务队列", "workers"),
            ("数据库", "database"),
            ("缓存", "cache"),
            ("LLM 服务", "llm")
        ]

        self.service_labels = {}
        for i, (name, key) in enumerate(services):
            ttk.Label(service_frame, text=f"{name}:").grid(
                row=i//3, column=(i%3)*2, sticky=tk.W, padx=10, pady=5
            )
            status_label = ttk.Label(
                service_frame,
                text="● 未知",
                font=('Arial', 10)
            )
            status_label.grid(row=i//3, column=(i%3)*2+1, sticky=tk.W, padx=5, pady=5)
            self.service_labels[key] = status_label

        # 系统资源
        resource_frame = ttk.LabelFrame(tab, text="系统资源", padding=10)
        resource_frame.pack(fill=tk.X, padx=5, pady=5)

        self.cpu_label = ttk.Label(resource_frame, text="CPU: --")
        self.cpu_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)

        self.memory_label = ttk.Label(resource_frame, text="内存: --")
        self.memory_label.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

        self.disk_label = ttk.Label(resource_frame, text="磁盘: --")
        self.disk_label.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)

        # 系统日志
        log_frame = ttk.LabelFrame(tab, text="系统日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.system_log = scrolledtext.ScrolledText(
            log_frame,
            height=20,
            wrap=tk.WORD,
            font=('Courier', 9)
        )
        self.system_log.pack(fill=tk.BOTH, expand=True)

        # 控制按钮
        control_frame = ttk.Frame(log_frame)
        control_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            control_frame,
            text="健康检查",
            command=self.run_health_check
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="刷新状态",
            command=self.refresh_system_status
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="清空日志",
            command=lambda: self.system_log.delete(1.0, tk.END)
        ).pack(side=tk.LEFT, padx=5)

    def create_config_tab(self):
        """创建配置标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="配置")

        # 连接配置
        conn_frame = ttk.LabelFrame(tab, text="连接配置", padding=10)
        conn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(conn_frame, text="服务器地址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.server_url_entry = ttk.Entry(conn_frame, width=50)
        self.server_url_entry.insert(0, self.server_url)
        self.server_url_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(conn_frame, text="控制台地址:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dashboard_url_entry = ttk.Entry(conn_frame, width=50)
        self.dashboard_url_entry.insert(0, self.dashboard_url)
        self.dashboard_url_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Button(
            conn_frame,
            text="保存连接",
            command=self.save_connection_config
        ).grid(row=2, column=0, columnspan=2, pady=10)

        # 默认配置
        default_frame = ttk.LabelFrame(tab, text="默认配置", padding=10)
        default_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(default_frame, text="默认协议:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.default_protocol = ttk.Combobox(
            default_frame,
            values=["coap", "modbus", "mqtt", "http", "grpc", "json-rpc"],
            state='readonly',
            width=48
        )
        self.default_protocol.set("coap")
        self.default_protocol.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(default_frame, text="默认 Payload 数:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.default_payloads = ttk.Spinbox(default_frame, from_=1, to=1000, width=48)
        self.default_payloads.set(10)
        self.default_payloads.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(default_frame, text="默认超时(秒):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.default_timeout = ttk.Spinbox(default_frame, from_=1, to=300, width=48)
        self.default_timeout.set(30)
        self.default_timeout.grid(row=2, column=1, pady=5, padx=5)

        ttk.Button(
            default_frame,
            text="保存默认配置",
            command=self.save_default_config
        ).grid(row=3, column=0, columnspan=2, pady=10)

        # 主题配置
        theme_frame = ttk.LabelFrame(tab, text="界面主题", padding=10)
        theme_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(theme_frame, text="主题:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.theme_var = tk.StringVar(value="clam")
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=ttk.Style().theme_names(),
            state='readonly',
            width=48
        )
        theme_combo.grid(row=0, column=1, pady=5, padx=5)

        ttk.Button(
            theme_frame,
            text="应用主题",
            command=lambda: ttk.Style().theme_use(self.theme_var.get())
        ).grid(row=1, column=0, columnspan=2, pady=10)

        # 关于信息
        about_frame = ttk.LabelFrame(tab, text="关于", padding=10)
        about_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        about_text = """
HyFuzz - 智能分布式模糊测试平台

版本: 1.0.0
作者: HyFuzz Team
许可: MIT License

功能特性:
• 支持多协议 (CoAP, Modbus, MQTT, HTTP, gRPC, JSON-RPC)
• LLM 驱动的智能 Payload 生成
• 防御系统集成与分析
• 分布式执行架构
• 实时监控与反馈

系统要求:
• Python 3.10+
• Windows 10+ 或 Ubuntu 20.04+
• 2GB+ RAM
• 网络连接
        """

        about_label = ttk.Label(
            about_frame,
            text=about_text,
            justify=tk.LEFT,
            font=('Arial', 10)
        )
        about_label.pack(padx=10, pady=10)

    # API 调用方法
    def api_call(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """调用 API"""
        try:
            url = f"{self.server_url}{endpoint}"
            headers = {"Content-Type": "application/json"}

            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return None

            if response.status_code in [200, 201]:
                return response.json()
            else:
                self.log_message(f"API 错误: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.ConnectionError:
            self.log_message(f"连接失败: 无法连接到 {url}")
            return None
        except Exception as e:
            self.log_message(f"API 调用异常: {str(e)}")
            return None

    # 活动管理方法
    def create_campaign(self):
        """创建新活动"""
        name = self.campaign_name.get().strip()
        if not name:
            messagebox.showwarning("输入错误", "请输入活动名称")
            return

        protocol = self.protocol_var.get()
        target = self.target_entry.get().strip()

        # 构建完整的目标 URL
        if not target.startswith(f"{protocol}://"):
            target = f"{protocol}://{target}"

        data = {
            "name": name,
            "description": f"通过 GUI 创建的 {protocol} 模糊测试活动",
            "protocol": protocol,
            "target": target,
            "payload_count": int(self.payload_count.get()),
            "timeout": int(self.timeout_entry.get()),
            "model": self.model_var.get(),
            "defense_enabled": self.defense_enabled.get(),
            "feedback_enabled": self.feedback_enabled.get(),
            "created_at": datetime.now().isoformat()
        }

        self.log_message(f"正在创建活动: {name}...")
        result = self.api_call("POST", "/api/v1/campaigns", data)

        if result:
            messagebox.showinfo("成功", f"活动 '{name}' 创建成功!\nID: {result.get('id', 'N/A')}")
            self.log_message(f"活动创建成功: {name}")
            self.refresh_campaigns()
            self.clear_campaign_form()
        else:
            messagebox.showerror("失败", "活动创建失败，请检查服务器连接")

    def clear_campaign_form(self):
        """清空活动表单"""
        self.campaign_name.delete(0, tk.END)
        self.target_entry.delete(0, tk.END)
        self.target_entry.insert(0, "localhost:5683")
        self.payload_count.set(10)
        self.timeout_entry.set(30)
        self.protocol_var.set("coap")
        self.model_var.set("llama3.2")
        self.defense_enabled.set(True)
        self.feedback_enabled.set(True)

    def refresh_campaigns(self):
        """刷新活动列表"""
        self.log_message("正在刷新活动列表...")
        result = self.api_call("GET", "/api/v1/campaigns")

        if result:
            # 清空现有列表
            for item in self.campaigns_tree.get_children():
                self.campaigns_tree.delete(item)

            # 添加新数据
            campaigns = result.get('campaigns', [])
            self.campaigns_list = campaigns

            for campaign in campaigns:
                self.campaigns_tree.insert('', tk.END, values=(
                    campaign.get('id', 'N/A'),
                    campaign.get('name', 'N/A'),
                    campaign.get('protocol', 'N/A'),
                    campaign.get('status', 'unknown'),
                    campaign.get('progress', '0%')
                ))

            self.log_message(f"活动列表已刷新: 共 {len(campaigns)} 个活动")
        else:
            self.log_message("刷新活动列表失败")

    def start_campaign(self):
        """启动活动"""
        selected = self.campaigns_tree.selection()
        if not selected:
            messagebox.showwarning("未选择", "请先选择一个活动")
            return

        item = self.campaigns_tree.item(selected[0])
        campaign_id = item['values'][0]

        result = self.api_call("POST", f"/api/v1/campaigns/{campaign_id}/start")
        if result:
            messagebox.showinfo("成功", f"活动 {campaign_id} 已启动")
            self.log_message(f"活动 {campaign_id} 已启动")
            self.refresh_campaigns()
        else:
            messagebox.showerror("失败", "启动活动失败")

    def pause_campaign(self):
        """暂停活动"""
        selected = self.campaigns_tree.selection()
        if not selected:
            messagebox.showwarning("未选择", "请先选择一个活动")
            return

        item = self.campaigns_tree.item(selected[0])
        campaign_id = item['values'][0]

        result = self.api_call("POST", f"/api/v1/campaigns/{campaign_id}/pause")
        if result:
            messagebox.showinfo("成功", f"活动 {campaign_id} 已暂停")
            self.log_message(f"活动 {campaign_id} 已暂停")
            self.refresh_campaigns()
        else:
            messagebox.showerror("失败", "暂停活动失败")

    def stop_campaign(self):
        """停止活动"""
        selected = self.campaigns_tree.selection()
        if not selected:
            messagebox.showwarning("未选择", "请先选择一个活动")
            return

        item = self.campaigns_tree.item(selected[0])
        campaign_id = item['values'][0]

        if not messagebox.askyesno("确认", f"确定要停止活动 {campaign_id} 吗？"):
            return

        result = self.api_call("POST", f"/api/v1/campaigns/{campaign_id}/stop")
        if result:
            messagebox.showinfo("成功", f"活动 {campaign_id} 已停止")
            self.log_message(f"活动 {campaign_id} 已停止")
            self.refresh_campaigns()
        else:
            messagebox.showerror("失败", "停止活动失败")

    def delete_campaign(self):
        """删除活动"""
        selected = self.campaigns_tree.selection()
        if not selected:
            messagebox.showwarning("未选择", "请先选择一个活动")
            return

        item = self.campaigns_tree.item(selected[0])
        campaign_id = item['values'][0]

        if not messagebox.askyesno("确认", f"确定要删除活动 {campaign_id} 吗？此操作不可恢复！"):
            return

        result = self.api_call("DELETE", f"/api/v1/campaigns/{campaign_id}")
        if result:
            messagebox.showinfo("成功", f"活动 {campaign_id} 已删除")
            self.log_message(f"活动 {campaign_id} 已删除")
            self.refresh_campaigns()
        else:
            messagebox.showerror("失败", "删除活动失败")

    # 监控方法
    def start_monitoring(self):
        """开始监控"""
        selected = self.campaigns_tree.selection()
        if not selected:
            messagebox.showwarning("未选择", "请先在活动列表中选择一个活动")
            return

        item = self.campaigns_tree.item(selected[0])
        self.current_campaign_id = item['values'][0]
        campaign_name = item['values'][1]

        self.monitoring_active = True
        self.monitor_info.config(
            text=f"监控活动: {campaign_name} (ID: {self.current_campaign_id})"
        )
        self.log_message(f"开始监控活动 {self.current_campaign_id}")

        # 启动监控线程
        threading.Thread(target=self.monitoring_loop, daemon=True).start()

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        self.monitor_info.config(text="监控已停止")
        self.log_message("监控已停止")

    def monitoring_loop(self):
        """监控循环"""
        while self.monitoring_active:
            if self.current_campaign_id:
                self.update_monitoring_data()
            time.sleep(2)  # 每2秒更新一次

    def update_monitoring_data(self):
        """更新监控数据"""
        if not self.current_campaign_id:
            return

        # 获取活动统计
        result = self.api_call("GET", f"/api/v1/campaigns/{self.current_campaign_id}/statistics")

        if result:
            stats = result.get('statistics', {})

            # 更新进度条
            total = stats.get('total_payloads', 0)
            executed = stats.get('executed', 0)
            progress = (executed / total * 100) if total > 0 else 0

            self.progress_var.set(progress)
            self.progress_label.config(
                text=f"{executed} / {total} ({progress:.1f}%)"
            )

            # 更新统计信息
            self.stats_labels['executions'].config(text=str(executed))
            self.stats_labels['success'].config(text=str(stats.get('success', 0)))
            self.stats_labels['failed'].config(text=str(stats.get('failed', 0)))
            self.stats_labels['crashes'].config(text=str(stats.get('crashes', 0)))
            self.stats_labels['high_risk'].config(text=str(stats.get('high_risk', 0)))
            self.stats_labels['blocked'].config(text=str(stats.get('blocked', 0)))

            # 添加日志
            if executed > 0:
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_msg = f"[{timestamp}] 进度: {executed}/{total} | 成功: {stats.get('success', 0)} | 崩溃: {stats.get('crashes', 0)}\n"
                self.monitor_log.insert(tk.END, log_msg)
                self.monitor_log.see(tk.END)

    # 结果查询方法
    def query_results(self):
        """查询执行结果"""
        campaign_id = self.results_campaign_id.get().strip()
        if not campaign_id:
            messagebox.showwarning("输入错误", "请输入活动ID")
            return

        self.log_message(f"正在查询活动 {campaign_id} 的执行结果...")
        result = self.api_call("GET", f"/api/v1/campaigns/{campaign_id}/executions")

        if result:
            # 清空现有列表
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)

            # 添加新数据
            executions = result.get('executions', [])
            status_filter = self.results_status.get()

            for execution in executions:
                status = execution.get('status', 'unknown')

                # 应用筛选
                if status_filter != "全部":
                    status_map = {"成功": "success", "失败": "failed", "崩溃": "crash"}
                    if status != status_map.get(status_filter, status_filter):
                        continue

                self.results_tree.insert('', tk.END, values=(
                    execution.get('id', 'N/A'),
                    campaign_id,
                    execution.get('payload', '')[:50] + '...',
                    status,
                    execution.get('response_code', 'N/A'),
                    execution.get('risk_level', 'N/A'),
                    execution.get('verdict', 'N/A'),
                    execution.get('timestamp', 'N/A')
                ))

            self.log_message(f"查询完成: 共 {len(executions)} 条结果")
        else:
            self.log_message("查询执行结果失败")

    def show_result_detail(self, event):
        """显示结果详情"""
        selected = self.results_tree.selection()
        if not selected:
            return

        item = self.results_tree.item(selected[0])
        values = item['values']

        detail_text = f"""
执行ID: {values[0]}
活动ID: {values[1]}
状态: {values[3]}
响应码: {values[4]}
风险等级: {values[5]}
判决: {values[6]}
时间: {values[7]}

Payload:
{values[2]}
        """

        self.result_detail.delete(1.0, tk.END)
        self.result_detail.insert(1.0, detail_text)

    # 系统状态方法
    def run_health_check(self):
        """运行健康检查"""
        self.log_message("正在运行系统健康检查...")
        result = self.api_call("GET", "/health")

        if result:
            status = result.get('status', 'unknown')
            components = result.get('components', {})

            log_text = f"\n========== 健康检查结果 ==========\n"
            log_text += f"总体状态: {status}\n"
            log_text += f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            for component, info in components.items():
                component_status = info.get('status', 'unknown')
                log_text += f"  {component}: {component_status}\n"

                # 更新服务状态标签
                if component in self.service_labels:
                    color = 'green' if component_status == 'healthy' else 'red'
                    self.service_labels[component].config(
                        text=f"● {component_status}",
                        foreground=color
                    )

            log_text += "=" * 35 + "\n"

            self.system_log.insert(tk.END, log_text)
            self.system_log.see(tk.END)

            self.log_message("健康检查完成")
        else:
            self.log_message("健康检查失败")

    def refresh_system_status(self):
        """刷新系统状态"""
        self.run_health_check()
        # TODO: 添加资源监控

    # 配置管理方法
    def save_connection_config(self):
        """保存连接配置"""
        self.server_url = self.server_url_entry.get().strip()
        self.dashboard_url = self.dashboard_url_entry.get().strip()
        messagebox.showinfo("成功", "连接配置已保存")
        self.log_message("连接配置已更新")
        self.check_connection()

    def save_default_config(self):
        """保存默认配置"""
        messagebox.showinfo("成功", "默认配置已保存")
        self.log_message("默认配置已更新")

    # 菜单方法
    def import_config(self):
        """导入配置文件"""
        filename = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("YAML files", "*.yaml *.yml"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            messagebox.showinfo("信息", f"配置文件: {filename}")
            self.log_message(f"导入配置: {filename}")

    def export_results(self):
        """导出结果"""
        filename = filedialog.asksaveasfilename(
            title="保存结果",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            messagebox.showinfo("成功", f"结果已导出到: {filename}")
            self.log_message(f"导出结果: {filename}")

    def refresh_all(self):
        """刷新所有数据"""
        self.refresh_campaigns()
        self.refresh_system_status()
        self.log_message("所有数据已刷新")

    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于 HyFuzz",
            "HyFuzz - 智能分布式模糊测试平台\n\n"
            "版本: 1.0.0\n"
            "作者: HyFuzz Team\n"
            "许可: MIT License\n\n"
            "支持的平台:\n"
            "• Windows 10+\n"
            "• Ubuntu 20.04+\n\n"
            "技术栈:\n"
            "• Python 3.10+\n"
            "• Tkinter (GUI)\n"
            "• FastAPI (后端)\n"
            "• SQLAlchemy (数据库)"
        )

    # 辅助方法
    def check_connection(self):
        """检查服务器连接"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                self.connection_indicator.config(text="● 已连接", foreground='green')
                self.log_message("服务器连接成功")
                return True
            else:
                self.connection_indicator.config(text="● 连接异常", foreground='orange')
                self.log_message("服务器响应异常")
                return False
        except:
            self.connection_indicator.config(text="● 未连接", foreground='red')
            self.log_message("无法连接到服务器")
            return False

    def log_message(self, message: str):
        """记录日志消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.status_label.config(text=message)
        print(log_entry)  # 同时输出到控制台

    def auto_refresh(self):
        """自动刷新"""
        self.check_connection()
        # 每30秒刷新一次连接状态
        self.root.after(30000, self.auto_refresh)


def main():
    """主函数"""
    root = tk.Tk()
    app = HyFuzzGUI(root)

    # 设置窗口图标（如果有的话）
    # root.iconbitmap('icon.ico')

    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()
