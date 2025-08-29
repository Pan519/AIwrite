class WebUI:
    """Web UI界面类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("智能文档排版软件")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # 初始化变量
        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.selected_ai_provider = tk.StringVar(value="openai")
        self.api_key = tk.StringVar()
        self.document_type = tk.StringVar(value="markdown")
        self.custom_rules_name = tk.StringVar()
        self.optimize_content = tk.BooleanVar(value=False)
        self.selected_template = tk.StringVar()
        
        # 创建界面
        self.create_widgets()
        
        # 初始化智能排版器
        if SMART_FORMATTER_AVAILABLE:
            self.formatter = SmartFormatter()
            self.refresh_template_list()
        else:
            self.formatter = None
            messagebox.showwarning("警告", "smart_formatter模块未找到，部分功能可能不可用")
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="智能文档排版软件", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # 输入文件
        ttk.Label(file_frame, text="输入文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.input_file_path, state="readonly").grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        ttk.Button(file_frame, text="浏览", command=self.browse_input_file).grid(row=0, column=2, pady=5)
        
        # 输出文件
        ttk.Label(file_frame, text="输出文件:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_file_path, state="readonly").grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        ttk.Button(file_frame, text="浏览", command=self.browse_output_file).grid(row=1, column=2, pady=5)
        
        # AI设置区域
        ai_frame = ttk.LabelFrame(main_frame, text="AI设置", padding="10")
        ai_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        ai_frame.columnconfigure(1, weight=1)
        
        # AI提供商
        ttk.Label(ai_frame, text="AI提供商:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ai_provider_combo = ttk.Combobox(ai_frame, textvariable=self.selected_ai_provider, values=[
            "openai", "anthropic", "deepseek", "qwen", "siliconflow", "ollama"
        ])
        ai_provider_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        
        # API密钥
        ttk.Label(ai_frame, text="API密钥:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(ai_frame, textvariable=self.api_key, show="*").grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        
        # 输出格式
        ttk.Label(ai_frame, text="输出格式:").grid(row=2, column=0, sticky=tk.W, pady=5)
        output_format_combo = ttk.Combobox(ai_frame, textvariable=self.document_type, values=[
            "markdown", "word", "pdf", "latex"
        ])
        output_format_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        
        # 模板选择
        ttk.Label(ai_frame, text="模板:").grid(row=3, column=0, sticky=tk.W, pady=5)
        template_combo = ttk.Combobox(ai_frame, textvariable=self.selected_template, values=[""])
        template_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        
        # 优化选项
        ttk.Checkbutton(ai_frame, text="优化内容", variable=self.optimize_content).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 20))
        
        ttk.Button(button_frame, text="开始处理", command=self.process_document).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="清空", command=self.clear_all).pack(side=tk.LEFT)
        
        # 状态显示
        self.status_label = ttk.Label(main_frame, text="", foreground="blue")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        # 绑定事件
        self.selected_ai_provider.trace_add("write", self.on_ai_provider_change)
        self.selected_template.trace_add("write", self.on_template_change)
        
        # 设置默认值
        self.on_ai_provider_change()
        
    def on_ai_provider_change(self, *args):
        """AI提供商改变时的处理"""
        provider = self.selected_ai_provider.get()
        if provider == "ollama":
            # Ollama不需要API密钥
            self.api_key.set("")
            self.api_key.setvar("disabled")
        else:
            # 其他提供商需要API密钥
            self.api_key.setvar("normal")
    
    def on_template_change(self, *args):
        """模板改变时的处理"""
        template_name = self.selected_template.get()
        if template_name:
            # 加载模板配置
            pass