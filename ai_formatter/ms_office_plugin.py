"""
MS Office插件实现
将智能文档排版功能集成到MS Office中
"""

import os
import sys
from pathlib import Path
import threading
from tkinter import messagebox

class MSOfficePlugin:
    """MS Office插件类"""
    
    def __init__(self):
        self.office_app = None
        self.current_document = None
        self.formatter = None
        
        # 初始化Office应用
        self.init_office()
        
        # 初始化智能排版器
        self.init_formatter()
    
    def init_office(self):
        """初始化Office应用"""
        try:
            import win32com.client
        except ImportError:
            messagebox.showerror("错误", "请安装pywin32模块: pip install pywin32")
            sys.exit(1)

        try:
            # 尝试连接Word
            self.office_app = win32com.client.Dispatch("Word.Application")
            self.office_app.Visible = True
        except Exception as e:
            try:
                # 如果Word不可用，尝试连接Excel
                self.office_app = win32com.client.Dispatch("Excel.Application")
                self.office_app.Visible = True
            except Exception as e:
                messagebox.showerror("错误", f"无法启动Office: {e}")
                self.office_app = None
    
    def init_formatter(self):
        """初始化智能排版器"""
        try:
            from smart_formatter import SmartFormatter
            self.formatter = SmartFormatter()
        except Exception as e:
            messagebox.showerror("错误", f"无法初始化智能排版器: {e}")
            self.formatter = None
    
    def get_current_document(self):
        """获取当前文档"""
        if self.office_app and self.office_app.ActiveDocument:
            self.current_document = self.office_app.ActiveDocument
            return self.current_document
        return None
    
    def save_document_as_temp(self, doc):
        """将文档保存为临时文件"""
        temp_dir = Path(os.getenv("TEMP"))
        temp_file = temp_dir / "office_plugin_temp.docx"
        
        try:
            doc.SaveAs(temp_file)
            return str(temp_file)
        except Exception as e:
            messagebox.showerror("错误", f"保存文档失败: {e}")
            return None
    
    def load_document_from_temp(self, temp_file, doc):
        """从临时文件加载文档"""
        try:
            doc.Close(SaveChanges=False)
            doc = self.office_app.Documents.Open(temp_file)
            return doc
        except Exception as e:
            messagebox.showerror("错误", f"加载文档失败: {e}")
            return None
    
    def process_document(self, ai_provider="openai", api_key=None, optimize=False, template_name=""):
        """处理文档"""
        if not self.formatter:
            messagebox.showerror("错误", "智能排版器未初始化")
            return
        
        doc = self.get_current_document()
        if not doc:
            messagebox.showerror("错误", "没有打开的文档")
            return
        
        # 保存为临时文件
        temp_file = self.save_document_as_temp(doc)
        if not temp_file:
            return
        
        # 处理文档
        try:
            # 调用智能排版器处理
            output_path = self.formatter.process_document(
                input_path=temp_file,
                output_path=temp_file,
                doc_type="word",
                ai_provider=ai_provider,
                api_key=api_key,
                optimize=optimize,
                custom_rules_name=template_name
            )
            
            # 重新加载文档
            doc = self.load_document_from_temp(temp_file, doc)
            
            # 显示成功消息
            messagebox.showinfo("成功", "文档排版完成！")
            
        except Exception as e:
            messagebox.showerror("错误", f"处理文档时出错: {e}")
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def add_menu_item(self):
        """添加菜单项到Office"""
        if not self.office_app:
            return
        
        try:
            # 添加菜单项
            menu_bar = self.office_app.CommandBars("Menu Bar")
            menu = menu_bar.Controls.Add(Type=1, Before=1)
            menu.Caption = "智能排版"
            
            # 添加子菜单项
            submenu = menu.Controls.Add(Type=1)
            submenu.Caption = "AI自动排版"
            submenu.OnAction = self.process_document
            
            # 添加其他功能
            submenu = menu.Controls.Add(Type=1)
            submenu.Caption = "设置"
            submenu.OnAction = self.open_settings
            
        except Exception as e:
            messagebox.showerror("错误", f"添加菜单项失败: {e}")
    
    def open_settings(self):
        """打开设置对话框"""
        # 这里可以实现设置对话框
        messagebox.showinfo("设置", "设置功能正在开发中...")
    
    def run(self):
        """运行插件"""
        self.add_menu_item()
        messagebox.showinfo("提示", "智能排版插件已安装成功！")

# 启动插件
if __name__ == "__main__":
    plugin = MSOfficePlugin()
    plugin.run()