"""
Web UI界面用于智能文档排版软件
提供图形化操作界面，支持导出为MD/Word/PDF/LaTeX格式
支持自定义模板管理
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from typing import Dict, Optional
import webbrowser
import json

try:
    from smart_formatter import SmartFormatter, DocumentType, AIProvider, FormattingRule
    SMART_FORMATTER_AVAILABLE = True
except ImportError:
    SMART_FORMATTER_AVAILABLE = False
    print("警告: smart_formatter模块未找到")

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
        ai_providers = ["openai", "deepseek", "qwen", "siliconflow"]
        ttk.Combobox(ai_frame, textvariable=self.selected_ai_provider, values=ai_providers, state="readonly").grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # API密钥
        ttk.Label(ai_frame, text="API密钥:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(ai_frame, textvariable=self.api_key, show="*").grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # 输出格式
        ttk.Label(ai_frame, text="输出格式:").grid(row=2, column=0, sticky=tk.W, pady=5)
        output_formats = ["markdown", "word", "pdf", "latex"]
        ttk.Combobox(ai_frame, textvariable=self.document_type, values=output_formats, state="readonly").grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # 自定义规则
        ttk.Label(ai_frame, text="自定义规则:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(ai_frame, textvariable=self.custom_rules_name).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # 优化内容选项
        ttk.Checkbutton(ai_frame, text="优化内容", variable=self.optimize_content).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 模板设置区域
        template_frame = ttk.LabelFrame(main_frame, text="模板设置", padding="10")
        template_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        template_frame.columnconfigure(1, weight=1)
        
        # 自定义模板
        ttk.Label(template_frame, text="选择模板:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.template_combobox = ttk.Combobox(template_frame, textvariable=self.selected_template, state="readonly")
        self.template_combobox.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        ttk.Button(template_frame, text="管理模板", command=self.open_template_manager).grid(row=0, column=2, padx=(5, 0), pady=5)
        
        # 操作按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        # 开始处理按钮
        self.process_button = ttk.Button(button_frame, text="开始处理", command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 启动Web界面按钮
        ttk.Button(button_frame, text="启动Web界面", command=self.start_web_interface).pack(side=tk.LEFT, padx=(0, 10))
        
        # 启动进程管理器按钮
        ttk.Button(button_frame, text="进程管理器", command=self.start_process_manager).pack(side=tk.LEFT, padx=(0, 10))
        
        # 保存配置按钮
        ttk.Button(button_frame, text="保存配置", command=self.save_config).pack(side=tk.LEFT, padx=(0, 10))
        
        # 加载配置按钮
        ttk.Button(button_frame, text="加载配置", command=self.load_config).pack(side=tk.LEFT, padx=(0, 10))
        
        # 帮助按钮
        ttk.Button(button_frame, text="帮助", command=self.show_help).pack(side=tk.LEFT)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="10")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        self.log_text = tk.Text(log_frame, height=12, state="disabled")
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
    
    def refresh_template_list(self):
        """刷新模板列表"""
        if self.formatter and hasattr(self.formatter, 'list_templates'):
            templates = self.formatter.list_templates()
            self.template_combobox['values'] = [''] + templates  # 添加空选项
    
    def browse_input_file(self):
        """浏览输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择输入文件",
            filetypes=[
                ("Markdown文件", "*.md"),
                ("Word文件", "*.docx"),
                ("LaTeX文件", "*.tex"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.input_file_path.set(file_path)
            # 自动设置输出文件路径
            if not self.output_file_path.get():
                base_name = os.path.splitext(file_path)[0]
                output_ext = self._get_output_extension()
                output_path = f"{base_name}_formatted{output_ext}"
                self.output_file_path.set(output_path)
    
    def browse_output_file(self):
        """浏览输出文件"""
        output_ext = self._get_output_extension()
        file_path = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=output_ext,
            filetypes=[
                ("Markdown文件", "*.md"),
                ("Word文件", "*.docx"),
                ("PDF文件", "*.pdf"),
                ("LaTeX文件", "*.tex"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.output_file_path.set(file_path)
    
    def _get_output_extension(self):
        """获取输出文件扩展名"""
        doc_type = self.document_type.get()
        if doc_type == "word":
            return ".docx"
        elif doc_type == "pdf":
            return ".pdf"
        elif doc_type == "latex":
            return ".tex"
        else:
            return ".md"
    
    def start_processing(self):
        """开始处理文档"""
        # 验证输入
        if not self.input_file_path.get():
            messagebox.showerror("错误", "请选择输入文件")
            return
        
        if not self.output_file_path.get():
            messagebox.showerror("错误", "请选择输出文件")
            return
        
        if not self.api_key.get():
            messagebox.showerror("错误", "请输入API密钥")
            return
        
        # 禁用处理按钮，显示进度条
        self.process_button.config(state="disabled")
        self.progress.start()
        
        # 在后台线程中处理文档
        thread = threading.Thread(target=self.process_document)
        thread.daemon = True
        thread.start()
    
    def process_document(self):
        """处理文档"""
        try:
            # 记录日志
            self.log("开始处理文档...")
            
            # 确定文档类型
            input_path = self.input_file_path.get()
            output_path = self.output_file_path.get()
            
            # 确定输入文档类型
            if input_path.endswith(".docx"):
                input_doc_type = DocumentType.WORD
            elif input_path.endswith(".tex"):
                input_doc_type = DocumentType.LATEX
            else:
                input_doc_type = DocumentType.MARKDOWN
            
            # 确定输出文档类型
            if output_path.endswith(".docx"):
                output_doc_type = DocumentType.WORD
            elif output_path.endswith(".pdf"):
                output_doc_type = DocumentType.PDF
            elif output_path.endswith(".tex"):
                output_doc_type = DocumentType.LATEX
            else:
                output_doc_type = DocumentType.MARKDOWN
            
            # 确定AI提供商
            provider_map = {
                "openai": AIProvider.OPENAI,
                "deepseek": AIProvider.DEEPSEEK,
                "qwen": AIProvider.QWEN,
                "siliconflow": AIProvider.SILICONFLOW
            }
            ai_provider = provider_map.get(self.selected_ai_provider.get(), AIProvider.OPENAI)
            
            # 处理文档
            if self.formatter:
                self.formatter.process_document(
                    input_path=input_path,
                    output_path=output_path,
                    doc_type=input_doc_type,
                    ai_provider=ai_provider,
                    api_key=self.api_key.get(),
                    custom_rules_name=self.custom_rules_name.get() or None,
                    optimize=self.optimize_content.get()
                )
                
                # 刷新模板列表，如果支持模板功能
                if hasattr(self.formatter, 'list_templates'):
                    self.refresh_template_list()
                
                self.log(f"文档处理完成: {output_path}")
                messagebox.showinfo("成功", "文档处理完成!")
            else:
                self.log("错误: smart_formatter模块不可用")
                messagebox.showerror("错误", "smart_formatter模块不可用")
        
        except Exception as e:
            self.log(f"处理文档时出错: {str(e)}")
            messagebox.showerror("错误", f"处理文档时出错: {str(e)}")
        
        finally:
            # 恢复UI状态
            self.progress.stop()
            self.process_button.config(state="normal")
    
    def start_web_interface(self):
        """启动Web界面"""
        try:
            # 在新线程中启动Web服务
            def start_flask():
                try:
                    from app import app
                    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
                except ImportError:
                    messagebox.showerror("错误", "无法导入app模块，请确保app.py文件存在")
                except Exception as e:
                    messagebox.showerror("错误", f"启动Web服务时出错: {str(e)}")
            
            thread = threading.Thread(target=start_flask)
            thread.daemon = True
            thread.start()
            
            # 等待一下让服务启动
            self.root.after(2000, lambda: webbrowser.open("http://127.0.0.1:5000"))
            messagebox.showinfo("提示", "Web界面正在启动，请稍后在浏览器中访问 http://127.0.0.1:5000")
        except Exception as e:
            messagebox.showerror("错误", f"启动Web界面时出错: {str(e)}")
    
    def start_process_manager(self):
        """启动进程管理器"""
        try:
            def start_manager():
                try:
                    from process_manager import ProcessManagerUI
                    manager_ui = ProcessManagerUI()
                    manager_ui.run()
                except ImportError:
                    messagebox.showerror("错误", "无法导入process_manager模块")
                except Exception as e:
                    messagebox.showerror("错误", f"启动进程管理器时出错: {str(e)}")
            
            thread = threading.Thread(target=start_manager)
            thread.daemon = True
            thread.start()
        except Exception as e:
            messagebox.showerror("错误", f"启动进程管理器时出错: {str(e)}")
    
    def open_template_manager(self):
        """打开模板管理器"""
        messagebox.showinfo("提示", "模板管理功能将在后续版本中实现")
    
    def save_config(self):
        """保存配置"""
        config = {
            "ai_provider": self.selected_ai_provider.get(),
            "api_key": self.api_key.get(),
            "document_type": self.document_type.get(),
            "custom_rules_name": self.custom_rules_name.get(),
            "optimize_content": self.optimize_content.get()
        }
        
        file_path = filedialog.asksaveasfilename(
            title="保存配置",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("成功", "配置保存成功!")
            except Exception as e:
                messagebox.showerror("错误", f"保存配置时出错: {str(e)}")
    
    def load_config(self):
        """加载配置"""
        file_path = filedialog.askopenfilename(
            title="加载配置",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                self.selected_ai_provider.set(config.get("ai_provider", "openai"))
                self.api_key.set(config.get("api_key", ""))
                self.document_type.set(config.get("document_type", "markdown"))
                self.custom_rules_name.set(config.get("custom_rules_name", ""))
                self.optimize_content.set(config.get("optimize_content", False))
                
                messagebox.showinfo("成功", "配置加载成功!")
            except Exception as e:
                messagebox.showerror("错误", f"加载配置时出错: {str(e)}")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
智能文档排版软件使用说明：

1. 选择输入文件：
   - 支持Markdown(.md)、Word(.docx)和LaTeX(.tex)格式
   
2. 选择输出文件：
   - 可导出为Markdown(.md)、Word(.docx)、PDF(.pdf)和LaTeX(.tex)格式
   
3. 配置AI参数：
   - 选择AI提供商（OpenAI、DeepSeek、通义千问等）
   - 输入对应的API密钥
   - 可选择自定义排版规则和模板
   
4. 处理文档：
   - 点击"开始处理"按钮启动排版流程
   - 可选启用内容优化功能

5. 其他功能：
   - 启动Web界面：在浏览器中使用Web版本
   - 进程管理器：管理前后端服务进程
   - 模板管理器：创建和管理自定义模板
   - 保存/加载配置：保存和复用常用设置

注意事项：
- 确保网络连接正常
- 确保API密钥有效
- 大文件处理可能需要较长时间
- PDF导出需要安装weasyprint库
- LaTeX支持为基本功能，复杂文档可能需要手动调整
        """
        
        # 创建帮助窗口
        help_window = tk.Toplevel(self.root)
        help_window.title("帮助")
        help_window.geometry("550x450")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(help_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def log(self, message: str):
        """记录日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
    
    def run(self):
        """运行UI"""
        self.root.mainloop()

def main():
    """主函数"""
    app = WebUI()
    app.run()

if __name__ == "__main__":
    main()