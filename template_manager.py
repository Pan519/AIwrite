"""
模板管理器用于管理自定义排版模板
支持用户创建、编辑和应用模板
"""

import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Optional
import os

try:
    from smart_formatter import Template, FormattingRule
    SMART_FORMATTER_AVAILABLE = True
except ImportError:
    SMART_FORMATTER_AVAILABLE = False
    print("警告: smart_formatter模块未找到")

class TemplateManager:
    """模板管理器类"""
    
    def __init__(self):
        self.templates: Dict[str, Template] = {}
        self.load_templates()
    
    def add_template(self, template: Template):
        """添加模板"""
        self.templates[template.name] = template
        self.save_templates()
    
    def remove_template(self, name: str):
        """删除模板"""
        if name in self.templates:
            del self.templates[name]
            self.save_templates()
    
    def get_template(self, name: str) -> Optional[Template]:
        """获取模板"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """列出所有模板"""
        return list(self.templates.keys())
    
    def save_templates(self):
        """保存模板到文件"""
        try:
            template_data = {name: template.to_dict() for name, template in self.templates.items()}
            with open("templates.json", "w", encoding="utf-8") as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存模板时出错: {e}")
    
    def load_templates(self):
        """从文件加载模板"""
        try:
            if os.path.exists("templates.json"):
                with open("templates.json", "r", encoding="utf-8") as f:
                    template_data = json.load(f)
                    self.templates = {name: Template.from_dict(data) for name, data in template_data.items()}
        except Exception as e:
            print(f"加载模板时出错: {e}")

class TemplateManagerUI:
    """模板管理器UI界面"""
    
    def __init__(self):
        self.manager = TemplateManager()
        self.root = tk.Tk()
        self.root.title("模板管理器")
        self.root.geometry("900x700")
        
        # 当前编辑的模板
        self.current_template = None
        self.current_template_name = tk.StringVar()
        self.current_template_desc = tk.StringVar()
        
        # 模板规则变量
        self.font_family = tk.StringVar(value="宋体")
        self.font_size = tk.IntVar(value=12)
        self.line_spacing = tk.DoubleVar(value=1.5)
        self.paragraph_spacing = tk.IntVar(value=10)
        self.indent_first_line = tk.BooleanVar(value=True)
        self.indent_size = tk.IntVar(value=2)
        self.heading_font_family = tk.StringVar(value="黑体")
        self.image_alignment = tk.StringVar(value="center")
        self.image_max_width = tk.IntVar(value=800)
        self.image_caption_style = tk.StringVar(value="below")
        
        # 内容结构
        self.content_structure = []
        
        self.create_widgets()
        self.refresh_template_list()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="模板管理器", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 主体区域
        body_frame = ttk.Frame(main_frame)
        body_frame.pack(fill=tk.BOTH, expand=True)
        body_frame.columnconfigure(1, weight=1)
        
        # 左侧：模板列表
        left_frame = ttk.Frame(body_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        ttk.Label(left_frame, text="现有模板", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")
        
        # 模板列表
        self.template_listbox = tk.Listbox(left_frame)
        template_listbox_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.template_listbox.yview)
        self.template_listbox.configure(yscrollcommand=template_listbox_scrollbar.set)
        
        self.template_listbox.grid(row=1, column=0, sticky="nsew", pady=(5, 10))
        template_listbox_scrollbar.grid(row=1, column=1, sticky="ns", pady=(5, 10))
        
        # 模板操作按钮
        template_button_frame = ttk.Frame(left_frame)
        template_button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        template_button_frame.columnconfigure((0,1,2), weight=1)
        
        ttk.Button(template_button_frame, text="新建", command=self.new_template).grid(row=0, column=0, padx=2, sticky="ew")
        ttk.Button(template_button_frame, text="编辑", command=self.edit_template).grid(row=0, column=1, padx=2, sticky="ew")
        ttk.Button(template_button_frame, text="删除", command=self.delete_template).grid(row=0, column=2, padx=2, sticky="ew")
        
        # 右侧：模板编辑区域
        right_frame = ttk.Frame(body_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(1, weight=1)
        
        # 模板基本信息
        info_frame = ttk.LabelFrame(right_frame, text="模板基本信息", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="模板名称:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(info_frame, textvariable=self.current_template_name).grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        ttk.Label(info_frame, text="模板描述:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(info_frame, textvariable=self.current_template_desc).grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        # 排版规则
        rules_frame = ttk.LabelFrame(right_frame, text="排版规则", padding="10")
        rules_frame.pack(fill=tk.X, pady=(0, 10))
        rules_frame.columnconfigure(1, weight=1)
        
        # 字体设置
        ttk.Label(rules_frame, text="正文字体:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(rules_frame, textvariable=self.font_family).grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        ttk.Label(rules_frame, text="正文字号:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Spinbox(rules_frame, from_=8, to=72, textvariable=self.font_size).grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        ttk.Label(rules_frame, text="行距:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Spinbox(rules_frame, from_=1.0, to=3.0, increment=0.1, textvariable=self.line_spacing).grid(row=2, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        ttk.Label(rules_frame, text="段落间距:").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Spinbox(rules_frame, from_=0, to=50, textvariable=self.paragraph_spacing).grid(row=3, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        ttk.Checkbutton(rules_frame, text="首行缩进", variable=self.indent_first_line).grid(row=4, column=0, columnspan=2, sticky="w", pady=2)
        
        ttk.Label(rules_frame, text="缩进字符:").grid(row=5, column=0, sticky="w", pady=2)
        ttk.Spinbox(rules_frame, from_=0, to=10, textvariable=self.indent_size).grid(row=5, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        ttk.Label(rules_frame, text="标题字体:").grid(row=6, column=0, sticky="w", pady=2)
        ttk.Entry(rules_frame, textvariable=self.heading_font_family).grid(row=6, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        # 图片设置
        image_frame = ttk.LabelFrame(right_frame, text="图片设置", padding="10")
        image_frame.pack(fill=tk.X, pady=(0, 10))
        image_frame.columnconfigure(1, weight=1)
        
        ttk.Label(image_frame, text="对齐方式:").grid(row=0, column=0, sticky="w", pady=2)
        image_alignment_combo = ttk.Combobox(image_frame, textvariable=self.image_alignment, values=["left", "center", "right"])
        image_alignment_combo.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        ttk.Label(image_frame, text="最大宽度:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Spinbox(image_frame, from_=100, to=2000, textvariable=self.image_max_width).grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        ttk.Label(image_frame, text="标题位置:").grid(row=2, column=0, sticky="w", pady=2)
        caption_style_combo = ttk.Combobox(image_frame, textvariable=self.image_caption_style, values=["above", "below", "none"])
        caption_style_combo.grid(row=2, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        # 内容结构
        structure_frame = ttk.LabelFrame(right_frame, text="内容结构", padding="10")
        structure_frame.pack(fill=tk.X, pady=(0, 10))
        structure_frame.columnconfigure(0, weight=1)
        structure_frame.rowconfigure(1, weight=1)
        
        ttk.Label(structure_frame, text="定义文档内容的结构元素（如标题、段落、列表等）:").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        self.structure_listbox = tk.Listbox(structure_frame, height=6)
        structure_listbox_scrollbar = ttk.Scrollbar(structure_frame, orient="vertical", command=self.structure_listbox.yview)
        self.structure_listbox.configure(yscrollcommand=structure_listbox_scrollbar.set)
        
        self.structure_listbox.grid(row=1, column=0, sticky="nsew", pady=(0, 5))
        structure_listbox_scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 5))
        
        # 结构操作按钮
        structure_button_frame = ttk.Frame(structure_frame)
        structure_button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        structure_button_frame.columnconfigure((0,1), weight=1)
        
        self.new_structure_entry = ttk.Entry(structure_button_frame)
        self.new_structure_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(structure_button_frame, text="添加", command=self.add_structure_item).grid(row=0, column=1)
        
        # 使用grid而不是pack来避免布局冲突
        ttk.Button(structure_frame, text="删除选中", command=self.remove_structure_item).grid(row=3, column=0, columnspan=2, pady=(5, 0))
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        button_frame.columnconfigure((0,1), weight=1)
        
        ttk.Button(button_frame, text="保存模板", command=self.save_template).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="取消", command=self.cancel_edit).pack(side=tk.LEFT, padx=(5, 0))
    
    def refresh_template_list(self):
        """刷新模板列表"""
        self.template_listbox.delete(0, tk.END)
        for template_name in self.manager.list_templates():
            self.template_listbox.insert(tk.END, template_name)
    
    def new_template(self):
        """新建模板"""
        self.current_template = None
        self.current_template_name.set("")
        self.current_template_desc.set("")
        
        # 重置规则
        self.font_family.set("宋体")
        self.font_size.set(12)
        self.line_spacing.set(1.5)
        self.paragraph_spacing.set(10)
        self.indent_first_line.set(True)
        self.indent_size.set(2)
        self.heading_font_family.set("黑体")
        self.image_alignment.set("center")
        self.image_max_width.set(800)
        self.image_caption_style.set("below")
        
        # 清空内容结构
        self.content_structure = []
        self.structure_listbox.delete(0, tk.END)
    
    def edit_template(self):
        """编辑模板"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个模板")
            return
        
        template_name = self.template_listbox.get(selection[0])
        template = self.manager.get_template(template_name)
        if not template:
            messagebox.showerror("错误", "无法找到选中的模板")
            return
        
        self.current_template = template
        self.current_template_name.set(template.name)
        self.current_template_desc.set(template.description)
        
        # 设置规则
        rules = template.rules
        self.font_family.set(rules.get("font_family", "宋体"))
        self.font_size.set(rules.get("font_size", 12))
        self.line_spacing.set(rules.get("line_spacing", 1.5))
        self.paragraph_spacing.set(rules.get("paragraph_spacing", 10))
        self.indent_first_line.set(rules.get("indent_first_line", True))
        self.indent_size.set(rules.get("indent_size", 2))
        self.heading_font_family.set(rules.get("heading_font_family", "黑体"))
        self.image_alignment.set(rules.get("image_alignment", "center"))
        self.image_max_width.set(rules.get("image_max_width", 800))
        self.image_caption_style.set(rules.get("image_caption_style", "below"))
        
        # 设置内容结构
        self.content_structure = template.content_structure.copy()
        self.structure_listbox.delete(0, tk.END)
        for item in self.content_structure:
            self.structure_listbox.insert(tk.END, item)
    
    def delete_template(self):
        """删除模板"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个模板")
            return
        
        template_name = self.template_listbox.get(selection[0])
        if messagebox.askyesno("确认", f"确定要删除模板 '{template_name}' 吗？"):
            self.manager.remove_template(template_name)
            self.refresh_template_list()
            messagebox.showinfo("成功", "模板已删除")
    
    def add_structure_item(self):
        """添加内容结构项"""
        item = self.new_structure_entry.get().strip()
        if item and item not in self.content_structure:
            self.content_structure.append(item)
            self.structure_listbox.insert(tk.END, item)
            self.new_structure_entry.delete(0, tk.END)
    
    def remove_structure_item(self):
        """删除内容结构项"""
        selection = self.structure_listbox.curselection()
        if selection:
            index = selection[0]
            self.content_structure.pop(index)
            self.structure_listbox.delete(index)
    
    def save_template(self):
        """保存模板"""
        name = self.current_template_name.get().strip()
        if not name:
            messagebox.showerror("错误", "请输入模板名称")
            return
        
        if not SMART_FORMATTER_AVAILABLE:
            messagebox.showerror("错误", "smart_formatter模块不可用")
            return
        
        # 构造规则字典
        rules = {
            "font_family": self.font_family.get(),
            "font_size": self.font_size.get(),
            "line_spacing": self.line_spacing.get(),
            "paragraph_spacing": self.paragraph_spacing.get(),
            "indent_first_line": self.indent_first_line.get(),
            "indent_size": self.indent_size.get(),
            "heading_font_family": self.heading_font_family.get(),
            "image_alignment": self.image_alignment.get(),
            "image_max_width": self.image_max_width.get(),
            "image_caption_style": self.image_caption_style.get()
        }
        
        # 创建模板对象
        template = Template(
            name=name,
            description=self.current_template_desc.get(),
            rules=rules,
            content_structure=self.content_structure.copy()
        )
        
        # 保存模板
        self.manager.add_template(template)
        self.refresh_template_list()
        messagebox.showinfo("成功", "模板已保存")
    
    def cancel_edit(self):
        """取消编辑"""
        self.new_template()
    
    def run(self):
        """运行UI"""
        self.root.mainloop()

def main():
    """主函数"""
    app = TemplateManagerUI()
    app.run()

if __name__ == "__main__":
    main()