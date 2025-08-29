"""
Ollama客户端实现
支持本地运行的Ollama大模型
"""

import requests
import json
import sys
from typing import Dict, Any

# 尝试从当前目录导入
try:
    from smart_formatter import AIClient
except ImportError:
    try:
        # 尝试从上级目录导入
        from ..smart_formatter import AIClient
    except ImportError:
        # 如果都失败了，打印错误信息并退出
        print("警告: smart_formatter模块未找到，可能需要调整路径")
        print("无法导入smart_formatter模块，请检查项目结构")
        # sys.exit(1)  # 注释掉这行避免程序退出

class OllamaClient(AIClient):
    """Ollama客户端实现"""
    
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
    
    def format_text(self, content: str, rules) -> str:
        """使用Ollama根据规范格式化文本"""
        prompt = f"""
        请根据以下排版规范格式化文档内容：
        
        排版规范：
        - 字体：{rules.font_family}
        - 字号：{rules.font_size}磅
        - 行距：{rules.line_spacing}
        - 段落间距：{rules.paragraph_spacing}磅
        - 首行缩进：{'是' if rules.indent_first_line else '否'}
        - 标题字体：{rules.heading_font_family}
        - 图片对齐方式：{rules.image_alignment}
        - 图片最大宽度：{rules.image_max_width}px
        - 图片标题位置：{rules.image_caption_style}
        
        文档内容：
        {content}
        
        请返回格式化后的文档内容。
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", content)
            else:
                print(f"Ollama请求失败: {response.status_code}")
                return content
                
        except Exception as e:
            print(f"调用Ollama时出错: {e}")
            return content
    
    def analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """分析文档结构"""
        prompt = f"""
        请分析以下文档的结构，并返回JSON格式的结果：
        
        文档内容：
        {content}
        
        分析要求：
        - 识别标题层级（h1, h2, h3等）
        - 识别段落、列表、引用等元素
        - 识别图片和表格位置
        - 返回结构化的文档信息
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return json.loads(result.get("response", "{}"))
            else:
                print(f"Ollama请求失败: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"调用Ollama时出错: {e}")
            return {}
    
    def optimize_content(self, content: str) -> str:
        """优化文档内容"""
        prompt = f"""
        请优化以下文档内容，提高可读性和专业性：
        
        文档内容：
        {content}
        
        优化要求：
        - 改善句子结构，使表达更清晰
        - 修正语法错误
        - 提高语言的专业性
        - 保持原意不变
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", content)
            else:
                print(f"Ollama请求失败: {response.status_code}")
                return content
                
        except Exception as e:
            print(f"调用Ollama时出错: {e}")
            return content
    
    def apply_template(self, content: str, template) -> str:
        """应用自定义模板"""
        prompt = f"""
        请根据以下模板格式化文档内容：
        
        模板规则：
        {json.dumps(template.rules, ensure_ascii=False)}
        
        文档内容：
        {content}
        
        请返回应用模板后的文档内容。
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", content)
            else:
                print(f"Ollama请求失败: {response.status_code}")
                return content
                
        except Exception as e:
            print(f"调用Ollama时出错: {e}")
            return content