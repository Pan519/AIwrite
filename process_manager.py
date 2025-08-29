"""
进程管理器用于管理前端和后端服务进程
确保前后端能够正常通信
"""

import subprocess
import threading
import time
import os
import signal
import psutil
from typing import Optional, Dict, List
import tkinter as tk
from tkinter import ttk, messagebox

class ProcessManager:
    """进程管理器类"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.logs: Dict[str, List[str]] = {
            "backend": [],
            "frontend": []
        }
        self.running = False
    
    def start_backend(self, script_path: str = "app.py") -> bool:
        """启动后端服务"""
        try:
            if "backend" in self.processes and self.processes["backend"].poll() is None:
                print("后端服务已在运行")
                return True
            
            # 启动后端服务
            backend_process = subprocess.Popen(
                ["python", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes["backend"] = backend_process
            self.running = True
            
            # 启动日志监控线程
            threading.Thread(target=self._monitor_logs, args=("backend", backend_process), daemon=True).start()
            
            print("后端服务启动成功")
            return True
        except Exception as e:
            print(f"启动后端服务时出错: {e}")
            return False
    
    def start_frontend(self) -> bool:
        """启动前端GUI"""
        try:
            if "frontend" in self.processes and self.processes["frontend"].poll() is None:
                print("前端GUI已在运行")
                return True
            
            # 启动前端GUI
            frontend_process = subprocess.Popen(
                ["python", "webui.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes["frontend"] = frontend_process
            
            # 启动日志监控线程
            threading.Thread(target=self._monitor_logs, args=("frontend", frontend_process), daemon=True).start()
            
            print("前端GUI启动成功")
            return True
        except Exception as e:
            print(f"启动前端GUI时出错: {e}")
            return False
    
    def stop_process(self, process_name: str):
        """停止指定进程"""
        if process_name in self.processes:
            process = self.processes[process_name]
            if process.poll() is None:  # 进程仍在运行
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                print(f"{process_name}进程已停止")
            else:
                print(f"{process_name}进程未在运行")
        else:
            print(f"未找到{process_name}进程")
    
    def stop_all(self):
        """停止所有进程"""
        for process_name in list(self.processes.keys()):
            self.stop_process(process_name)
        self.running = False
    
    def restart_process(self, process_name: str, script_path: str = None) -> bool:
        """重启指定进程"""
        self.stop_process(process_name)
        time.sleep(1)  # 等待进程完全停止
        
        if process_name == "backend":
            return self.start_backend(script_path or "app.py")
        elif process_name == "frontend":
            return self.start_frontend()
        else:
            return False
    
    def get_process_status(self, process_name: str) -> str:
        """获取进程状态"""
        if process_name not in self.processes:
            return "未启动"
        
        process = self.processes[process_name]
        if process.poll() is None:
            return "运行中"
        else:
            return "已停止"
    
    def get_logs(self, process_name: str, lines: int = 50) -> List[str]:
        """获取指定进程的日志"""
        if process_name in self.logs:
            return self.logs[process_name][-lines:]
        return []
    
    def _monitor_logs(self, process_name: str, process: subprocess.Popen):
        """监控进程日志"""
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.logs[process_name].append(line.strip())
                    # 限制日志数量
                    if len(self.logs[process_name]) > 1000:
                        self.logs[process_name] = self.logs[process_name][-500:]
            
            # 读取错误输出
            for line in iter(process.stderr.readline, ''):
                if line:
                    error_line = f"ERROR: {line.strip()}"
                    self.logs[process_name].append(error_line)
                    # 限制日志数量
                    if len(self.logs[process_name]) > 1000:
                        self.logs[process_name] = self.logs[process_name][-500:]
        except Exception as e:
            print(f"监控{process_name}日志时出错: {e}")

class ProcessManagerUI:
    """进程管理器UI界面"""
    
    def __init__(self):
        self.manager = ProcessManager()
        self.root = tk.Tk()
        self.root.title("智能文档排版软件 - 进程管理器")
        self.root.geometry("800x600")
        
        self.create_widgets()
        self.update_status()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="进程管理器", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 进程状态框架
        status_frame = ttk.LabelFrame(main_frame, text="进程状态", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 后端状态
        backend_frame = ttk.Frame(status_frame)
        backend_frame.pack(fill=tk.X, pady=5)
        
        self.backend_status = ttk.Label(backend_frame, text="后端服务: 未启动")
        self.backend_status.pack(side=tk.LEFT)
        
        backend_button_frame = ttk.Frame(backend_frame)
        backend_button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(backend_button_frame, text="启动", command=self.start_backend).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(backend_button_frame, text="停止", command=lambda: self.stop_process("backend")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(backend_button_frame, text="重启", command=lambda: self.restart_process("backend")).pack(side=tk.LEFT)
        
        # 前端状态
        frontend_frame = ttk.Frame(status_frame)
        frontend_frame.pack(fill=tk.X, pady=5)
        
        self.frontend_status = ttk.Label(frontend_frame, text="前端GUI: 未启动")
        self.frontend_status.pack(side=tk.LEFT)
        
        frontend_button_frame = ttk.Frame(frontend_frame)
        frontend_button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(frontend_button_frame, text="启动", command=self.start_frontend).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(frontend_button_frame, text="停止", command=lambda: self.stop_process("frontend")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(frontend_button_frame, text="重启", command=lambda: self.restart_process("frontend")).pack(side=tk.LEFT)
        
        # 控制按钮框架
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(control_frame, text="全部启动", command=self.start_all).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="全部停止", command=self.stop_all).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="全部重启", command=self.restart_all).pack(side=tk.LEFT)
        
        # 日志框架
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 日志选项卡
        tab_control = ttk.Notebook(log_frame)
        tab_control.pack(fill=tk.BOTH, expand=True)
        
        # 后端日志选项卡
        backend_log_frame = ttk.Frame(tab_control)
        tab_control.add(backend_log_frame, text="后端日志")
        backend_log_frame.columnconfigure(0, weight=1)
        backend_log_frame.rowconfigure(0, weight=1)
        
        self.backend_log_text = tk.Text(backend_log_frame, state="disabled")
        backend_log_scrollbar = ttk.Scrollbar(backend_log_frame, orient="vertical", command=self.backend_log_text.yview)
        self.backend_log_text.configure(yscrollcommand=backend_log_scrollbar.set)
        
        self.backend_log_text.grid(row=0, column=0, sticky="nsew")
        backend_log_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 前端日志选项卡
        frontend_log_frame = ttk.Frame(tab_control)
        tab_control.add(frontend_log_frame, text="前端日志")
        frontend_log_frame.columnconfigure(0, weight=1)
        frontend_log_frame.rowconfigure(0, weight=1)
        
        self.frontend_log_text = tk.Text(frontend_log_frame, state="disabled")
        frontend_log_scrollbar = ttk.Scrollbar(frontend_log_frame, orient="vertical", command=self.frontend_log_text.yview)
        self.frontend_log_text.configure(yscrollcommand=frontend_log_scrollbar.set)
        
        self.frontend_log_text.grid(row=0, column=0, sticky="nsew")
        frontend_log_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 定时更新日志
        self.update_logs()
    
    def start_backend(self):
        """启动后端服务"""
        if self.manager.start_backend():
            messagebox.showinfo("成功", "后端服务启动成功")
        else:
            messagebox.showerror("错误", "后端服务启动失败")
        self.update_status()
    
    def start_frontend(self):
        """启动前端GUI"""
        if self.manager.start_frontend():
            messagebox.showinfo("成功", "前端GUI启动成功")
        else:
            messagebox.showerror("错误", "前端GUI启动失败")
        self.update_status()
    
    def start_all(self):
        """启动所有服务"""
        backend_success = self.manager.start_backend()
        frontend_success = self.manager.start_frontend()
        
        if backend_success and frontend_success:
            messagebox.showinfo("成功", "所有服务启动成功")
        else:
            messagebox.showerror("错误", "部分服务启动失败")
        self.update_status()
    
    def stop_process(self, process_name: str):
        """停止指定进程"""
        self.manager.stop_process(process_name)
        self.update_status()
        messagebox.showinfo("提示", f"{process_name}进程已停止")
    
    def stop_all(self):
        """停止所有进程"""
        self.manager.stop_all()
        self.update_status()
        messagebox.showinfo("提示", "所有进程已停止")
    
    def restart_process(self, process_name: str):
        """重启指定进程"""
        if self.manager.restart_process(process_name):
            messagebox.showinfo("成功", f"{process_name}进程重启成功")
        else:
            messagebox.showerror("错误", f"{process_name}进程重启失败")
        self.update_status()
    
    def restart_all(self):
        """重启所有进程"""
        backend_success = self.manager.restart_process("backend")
        frontend_success = self.manager.restart_process("frontend")
        
        if backend_success and frontend_success:
            messagebox.showinfo("成功", "所有进程重启成功")
        else:
            messagebox.showerror("错误", "部分进程重启失败")
        self.update_status()
    
    def update_status(self):
        """更新进程状态显示"""
        backend_status = self.manager.get_process_status("backend")
        frontend_status = self.manager.get_process_status("frontend")
        
        self.backend_status.config(text=f"后端服务: {backend_status}")
        self.frontend_status.config(text=f"前端GUI: {frontend_status}")
    
    def update_logs(self):
        """更新日志显示"""
        # 更新后端日志
        backend_logs = self.manager.get_logs("backend")
        self.backend_log_text.config(state="normal")
        self.backend_log_text.delete(1.0, tk.END)
        for log in backend_logs:
            self.backend_log_text.insert(tk.END, log + "\n")
        self.backend_log_text.config(state="disabled")
        self.backend_log_text.see(tk.END)
        
        # 更新前端日志
        frontend_logs = self.manager.get_logs("frontend")
        self.frontend_log_text.config(state="normal")
        self.frontend_log_text.delete(1.0, tk.END)
        for log in frontend_logs:
            self.frontend_log_text.insert(tk.END, log + "\n")
        self.frontend_log_text.config(state="disabled")
        self.frontend_log_text.see(tk.END)
        
        # 每秒更新一次
        self.root.after(1000, self.update_logs)
    
    def run(self):
        """运行UI"""
        self.root.mainloop()

def main():
    """主函数"""
    app = ProcessManagerUI()
    app.run()

if __name__ == "__main__":
    main()