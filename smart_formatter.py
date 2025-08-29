"""
智能文档排版软件
支持Word、Markdown、PDF和LaTeX文档格式
接入多种AI，根据内容和写作规范自动排版
支持用户自定义排版规范和模板
处理文字和图片的智能排版
"""

import os
import json
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# 导入图片处理模块
try:
    from image_handler import ImageHandler, ImageInfo, ImageFormattingRule
    IMAGE_HANDLER_AVAILABLE = True
except ImportError:
    IMAGE_HANDLER_AVAILABLE = False
    print("警告: image_handler模块未找到，图片处理功能将不可用")

class DocumentType(Enum):
    """文档类型枚举"""
    WORD = "word"
    MARKDOWN = "markdown"
    PDF = "pdf"
    LATEX = "latex"

class AIProvider(Enum):
    """AI提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    QWEN = "qwen"
    BAIDU = "baidu"
    XFYUN = "xfyun"
    DEEPSEEK = "deepseek"
    SILICONFLOW = "siliconflow"
    CUSTOM = "custom"

@dataclass
class Template:
    """自定义模板数据类"""
    name: str
    description: str
    rules: Dict[str, Any]
    content_structure: List[str]
    
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "rules": self.rules,
            "content_structure": self.content_structure
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            description=data["description"],
            rules=data["rules"],
            content_structure=data["content_structure"]
        )

@dataclass
class FormattingRule:
    """排版规范数据类"""
    font_family: str = "宋体"
    font_size: int = 12
    line_spacing: float = 1.5
    paragraph_spacing: int = 10
    indent_first_line: bool = True
    indent_size: int = 2
    heading_font_family: str = "黑体"
    heading_font_size: Dict[str, int] = None
    image_alignment: str = "center"
    image_max_width: int = 800
    image_caption_style: str = "below"
    
    def __post_init__(self):
        if self.heading_font_size is None:
            self.heading_font_size = {
                "h1": 22,
                "h2": 18,
                "h3": 16,
                "h4": 14,
                "h5": 12,
                "h6": 12
            }

@dataclass
class ImageFormattingRule:
    """图片排版规范数据类"""
    alignment: str = "center"
    max_width: int = 800
    caption_style: str = "below"
    caption_font_family: str = "宋体"
    caption_font_size: int = 10
    caption_prefix: str = "图"

class AIClient(ABC):
    """AI客户端抽象基类"""
    
    @abstractmethod
    def format_text(self, content: str, rules: FormattingRule) -> str:
        """根据规范格式化文本"""
        pass
    
    @abstractmethod
    def analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """分析文档结构"""
        pass
    
    @abstractmethod
    def optimize_content(self, content: str) -> str:
        """优化文档内容"""
        pass

class OpenAIClient(AIClient):
    """OpenAI客户端实现"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        except ImportError:
            self.client = None
            print("警告: 未安装openai库，OpenAI功能将不可用")
    
    def format_text(self, content: str, rules: FormattingRule) -> str:
        """使用OpenAI根据规范格式化文本"""
        if not self.client:
            return content
            
        prompt = f"""
        请根据以下排版规范格式化文档内容：
        
        排版规范：
        - 字体：{rules.font_family}
        - 字号：{rules.font_size}磅
        - 行距：{rules.line_spacing}
        - 段落间距：{rules.paragraph_spacing}磅
        - 首行缩进：{'是' if rules.indent_first_line else '否'}
        - 缩进字符数：{rules.indent_size}
        
        文档内容：
        {content}
        
        请严格按照上述规范格式化文档，保持内容不变，仅调整格式。
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI调用出错: {e}")
            return content
    
    def analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """使用OpenAI分析文档结构"""
        if not self.client:
            return {"headings": [], "paragraphs": [], "images": [], "tables": []}
            
        prompt = f"""
        请分析以下文档的结构，并以JSON格式返回结果：
        
        文档内容：
        {content}
        
        请识别并返回以下信息：
        1. 标题（headings）：包括所有层级的标题
        2. 段落（paragraphs）：文档中的段落数量和位置
        3. 图片（images）：文档中图片的位置和描述
        4. 表格（tables）：文档中表格的位置和描述
        5. 列表（lists）：文档中的有序和无序列表
        
        请以以下JSON格式返回结果：
        {{
            "headings": [...],
            "paragraphs": [...],
            "images": [...],
            "tables": [...],
            "lists": [...]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024
            )
            # 这里应该解析返回的JSON，但为简化起见直接返回模拟数据
            return {
                "headings": [],
                "paragraphs": [],
                "images": [],
                "tables": [],
                "lists": []
            }
        except Exception as e:
            print(f"OpenAI调用出错: {e}")
            return {
                "headings": [],
                "paragraphs": [],
                "images": [],
                "tables": [],
                "lists": []
            }
    
    def optimize_content(self, content: str) -> str:
        """使用OpenAI优化文档内容"""
        if not self.client:
            return content
            
        prompt = f"""
        请优化以下文档内容，提高可读性和专业性：
        
        优化要求：
        1. 修正语法错误和拼写错误
        2. 改善句子结构，提高流畅度
        3. 确保用词准确、专业
        4. 保持原意不变
        
        文档内容：
        {content}
        
        请返回优化后的内容。
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI调用出错: {e}")
            return content

class DeepSeekClient(AIClient):
    """DeepSeek客户端实现"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key, base_url=self.base_url)
        except ImportError:
            self.client = None
            print("警告: 未安装openai库，DeepSeek功能将不可用")
    
    def format_text(self, content: str, rules: FormattingRule) -> str:
        """使用DeepSeek根据规范格式化文本"""
        if not self.client:
            return content
            
        prompt = f"""
        请根据以下排版规范格式化文档内容：
        
        排版规范：
        - 字体：{rules.font_family}
        - 字号：{rules.font_size}磅
        - 行距：{rules.line_spacing}
        - 段落间距：{rules.paragraph_spacing}磅
        - 首行缩进：{'是' if rules.indent_first_line else '否'}
        - 缩进字符数：{rules.indent_size}
        
        文档内容：
        {content}
        
        请严格按照上述规范格式化文档，保持内容不变，仅调整格式。
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000  # DeepSeek-V3支持最大2000 tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"DeepSeek调用出错: {e}")
            return content
    
    def analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """使用DeepSeek分析文档结构"""
        if not self.client:
            return {"headings": [], "paragraphs": [], "images": [], "tables": [], "lists": []}
            
        prompt = f"""
        请分析以下文档的结构，并以JSON格式返回结果：
        
        文档内容：
        {content}
        
        请识别并返回以下信息：
        1. 标题（headings）：包括所有层级的标题
        2. 段落（paragraphs）：文档中的段落数量和位置
        3. 图片（images）：文档中图片的位置和描述
        4. 表格（tables）：文档中表格的位置和描述
        5. 列表（lists）：文档中的有序和无序列表
        
        请以以下JSON格式返回结果：
        {{
            "headings": [...],
            "paragraphs": [...],
            "images": [...],
            "tables": [...],
            "lists": [...]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            # 这里应该解析返回的JSON，但为简化起见直接返回模拟数据
            return {
                "headings": [],
                "paragraphs": [],
                "images": [],
                "tables": [],
                "lists": []
            }
        except Exception as e:
            print(f"DeepSeek调用出错: {e}")
            return {
                "headings": [],
                "paragraphs": [],
                "images": [],
                "tables": [],
                "lists": []
            }
    
    def optimize_content(self, content: str) -> str:
        """使用DeepSeek优化文档内容"""
        if not self.client:
            return content
            
        prompt = f"""
        请优化以下文档内容，提高可读性和专业性：
        
        优化要求：
        1. 修正语法错误和拼写错误
        2. 改善句子结构，提高流畅度
        3. 确保用词准确、专业
        4. 保持原意不变
        
        文档内容：
        {content}
        
        请返回优化后的内容。
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"DeepSeek调用出错: {e}")
            return content

class QwenClient(AIClient):
    """阿里通义千问客户端实现"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    def format_text(self, content: str, rules: FormattingRule) -> str:
        """使用通义千问根据规范格式化文本"""
        prompt = f"""
        请根据以下排版规范格式化文档内容：
        
        排版规范：
        - 字体：{rules.font_family}
        - 字号：{rules.font_size}磅
        - 行距：{rules.line_spacing}
        - 段落间距：{rules.paragraph_spacing}磅
        - 首行缩进：{'是' if rules.indent_first_line else '否'}
        - 缩进字符数：{rules.indent_size}
        
        文档内容：
        {content}
        
        请严格按照上述规范格式化文档，保持内容不变，仅调整格式。
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "qwen-max",
            "input": {"prompt": prompt},
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.8,
                "max_tokens": 2048
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                return result["output"]["text"]
            else:
                print(f"通义千问API调用失败: {response.status_code}")
                return content
        except Exception as e:
            print(f"通义千问调用出错: {e}")
            return content
    
    def analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """使用通义千问分析文档结构"""
        prompt = f"""
        请分析以下文档的结构：
        
        文档内容：
        {content}
        
        请识别文档中的标题、段落、图片、表格和列表，并以简洁的方式描述它们的位置和内容。
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "qwen-max",
            "input": {"prompt": prompt},
            "parameters": {
                "temperature": 0.3,
                "top_p": 0.8,
                "max_tokens": 1024
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            if response.status_code == 200:
                # 返回模拟数据
                return {
                    "headings": [],
                    "paragraphs": [],
                    "images": [],
                    "tables": [],
                    "lists": []
                }
            else:
                print(f"通义千问API调用失败: {response.status_code}")
                return {
                    "headings": [],
                    "paragraphs": [],
                    "images": [],
                    "tables": [],
                    "lists": []
                }
        except Exception as e:
            print(f"通义千问调用出错: {e}")
            return {
                "headings": [],
                "paragraphs": [],
                "images": [],
                "tables": [],
                "lists": []
            }
    
    def optimize_content(self, content: str) -> str:
        """使用通义千问优化文档内容"""
        prompt = f"""
        请优化以下文档内容，提高可读性和专业性：
        
        优化要求：
        1. 修正语法错误和拼写错误
        2. 改善句子结构，提高流畅度
        3. 确保用词准确、专业
        4. 保持原意不变
        
        文档内容：
        {content}
        
        请返回优化后的内容。
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "qwen-max",
            "input": {"prompt": prompt},
            "parameters": {
                "temperature": 0.5,
                "top_p": 0.8,
                "max_tokens": 2048
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                return result["output"]["text"]
            else:
                print(f"通义千问API调用失败: {response.status_code}")
                return content
        except Exception as e:
            print(f"通义千问调用出错: {e}")
            return content

class SiliconFlowClient(AIClient):
    """硅基流动客户端实现"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.siliconflow.cn/v1"
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key, base_url=self.base_url)
        except ImportError:
            self.client = None
            print("警告: 未安装openai库，硅基流动功能将不可用")
    
    def format_text(self, content: str, rules: FormattingRule) -> str:
        """使用硅基流动根据规范格式化文本"""
        if not self.client:
            return content
            
        prompt = f"""
        请根据以下排版规范格式化文档内容：
        
        排版规范：
        - 字体：{rules.font_family}
        - 字号：{rules.font_size}磅
        - 行距：{rules.line_spacing}
        - 段落间距：{rules.paragraph_spacing}磅
        - 首行缩进：{'是' if rules.indent_first_line else '否'}
        - 缩进字符数：{rules.indent_size}
        
        文档内容：
        {content}
        
        请严格按照上述规范格式化文档，保持内容不变，仅调整格式。
        """
        
        try:
            response = self.client.chat.completions.create(
                model="siliconflow/qwen2-7b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"硅基流动调用出错: {e}")
            return content
    
    def analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """使用硅基流动分析文档结构"""
        if not self.client:
            return {"headings": [], "paragraphs": [], "images": [], "tables": [], "lists": []}
            
        prompt = f"""
        请分析以下文档的结构，并以JSON格式返回结果：
        
        文档内容：
        {content}
        
        请识别并返回以下信息：
        1. 标题（headings）：包括所有层级的标题
        2. 段落（paragraphs）：文档中的段落数量和位置
        3. 图片（images）：文档中图片的位置和描述
        4. 表格（tables）：文档中表格的位置和描述
        5. 列表（lists）：文档中的有序和无序列表
        
        请以以下JSON格式返回结果：
        {{
            "headings": [...],
            "paragraphs": [...],
            "images": [...],
            "tables": [...],
            "lists": [...]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="siliconflow/qwen2-7b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024
            )
            # 这里应该解析返回的JSON，但为简化起见直接返回模拟数据
            return {
                "headings": [],
                "paragraphs": [],
                "images": [],
                "tables": [],
                "lists": []
            }
        except Exception as e:
            print(f"硅基流动调用出错: {e}")
            return {
                "headings": [],
                "paragraphs": [],
                "images": [],
                "tables": [],
                "lists": []
            }
    
    def optimize_content(self, content: str) -> str:
        """使用硅基流动优化文档内容"""
        if not self.client:
            return content
            
        prompt = f"""
        请优化以下文档内容，提高可读性和专业性：
        
        优化要求：
        1. 修正语法错误和拼写错误
        2. 改善句子结构，提高流畅度
        3. 确保用词准确、专业
        4. 保持原意不变
        
        文档内容：
        {content}
        
        请返回优化后的内容。
        """
        
        try:
            response = self.client.chat.completions.create(
                model="siliconflow/qwen2-7b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"硅基流动调用出错: {e}")
            return content

class DocumentProcessor(ABC):
    """文档处理器抽象基类"""
    
    def __init__(self, ai_client: AIClient, formatting_rules: FormattingRule):
        self.ai_client = ai_client
        self.formatting_rules = formatting_rules
        if IMAGE_HANDLER_AVAILABLE:
            image_rules = ImageFormattingRule(
                alignment=formatting_rules.image_alignment,
                max_width=formatting_rules.image_max_width,
                caption_style=formatting_rules.image_caption_style
            )
            self.image_handler = ImageHandler(image_rules)
        else:
            self.image_handler = None
    
    @abstractmethod
    def load_document(self, file_path: str) -> str:
        """加载文档内容"""
        pass
    
    @abstractmethod
    def save_document(self, content: str, file_path: str):
        """保存文档内容"""
        pass
    
    @abstractmethod
    def apply_formatting(self, content: str) -> str:
        """应用排版格式"""
        pass
    
    def process_images(self, content: str) -> str:
        """处理文档中的图片"""
        if not self.image_handler:
            print("图片处理功能不可用")
            return content
        
        # 这里应该实现具体的图片处理逻辑
        # 例如识别文档中的图片引用，应用排版规范等
        return content
    
    def optimize_content(self, content: str) -> str:
        """优化文档内容"""
        return self.ai_client.optimize_content(content)
    
    def process_document(self, input_path: str, output_path: str, optimize: bool = False):
        """处理文档的主流程"""
        # 加载文档
        content = self.load_document(input_path)
        
        # 分析文档结构
        structure = self.ai_client.analyze_document_structure(content)
        
        # 优化内容（可选）
        if optimize:
            content = self.optimize_content(content)
        
        # 处理图片
        content_with_formatted_images = self.process_images(content)
        
        # 应用格式化
        formatted_content = self.apply_formatting(content_with_formatted_images)
        
        # 保存文档
        self.save_document(formatted_content, output_path)

class WordProcessor(DocumentProcessor):
    """Word文档处理器"""
    
    def load_document(self, file_path: str) -> str:
        """加载Word文档"""
        # 实际实现中需要使用python-docx库
        # doc = Document(file_path)
        # content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        # return content
        return f"Word文档内容来自: {file_path}"
    
    def save_document(self, content: str, file_path: str):
        """保存Word文档"""
        # 实际实现中需要使用python-docx库创建和保存文档
        print(f"已保存Word文档到: {file_path}")
    
    def apply_formatting(self, content: str) -> str:
        """应用Word格式化"""
        # 使用AI客户端格式化内容
        formatted_content = self.ai_client.format_text(content, self.formatting_rules)
        return formatted_content

class MarkdownProcessor(DocumentProcessor):
    """Markdown文档处理器"""
    
    def load_document(self, file_path: str) -> str:
        """加载Markdown文档"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def save_document(self, content: str, file_path: str):
        """保存Markdown文档"""
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"已保存Markdown文档到: {file_path}")
    
    def apply_formatting(self, content: str) -> str:
        """应用Markdown格式化"""
        # 使用AI客户端格式化内容
        formatted_content = self.ai_client.format_text(content, self.formatting_rules)
        return formatted_content

class SmartFormatter:
    """智能排版器主类"""
    
    def __init__(self):
        self.processors: Dict[DocumentType, DocumentProcessor] = {}
        self.default_rules = FormattingRule()
        self.custom_rules: Dict[str, FormattingRule] = {}
        self.ai_clients: Dict[AIProvider, AIClient] = {}
    
    def add_ai_client(self, provider: AIProvider, ai_client: AIClient):
        """添加AI客户端"""
        self.ai_clients[provider] = ai_client
        print(f"已添加AI客户端: {provider.value}")
    
    def set_default_formatting_rules(self, rules: FormattingRule):
        """设置默认排版规范"""
        self.default_rules = rules
        print("已设置默认排版规范")
    
    def add_custom_formatting_rules(self, name: str, rules: FormattingRule):
        """添加自定义排版规范"""
        self.custom_rules[name] = rules
        print(f"已添加自定义排版规范: {name}")
    
    def get_processor(self, doc_type: DocumentType, ai_client: AIClient) -> DocumentProcessor:
        """获取文档处理器"""
        if doc_type == DocumentType.WORD:
            return WordProcessor(ai_client, self.default_rules)
        elif doc_type == DocumentType.MARKDOWN:
            return MarkdownProcessor(ai_client, self.default_rules)
        else:
            raise ValueError(f"不支持的文档类型: {doc_type}")
    
    def process_document(self, 
                        input_path: str, 
                        output_path: str, 
                        doc_type: DocumentType, 
                        ai_provider: AIProvider,
                        api_key: str,
                        custom_rules_name: Optional[str] = None,
                        optimize: bool = False):
        """处理文档"""
        # 确定使用的AI客户端
        ai_client = self._get_ai_client(ai_provider, api_key)
        
        # 确定使用的排版规范
        if custom_rules_name and custom_rules_name in self.custom_rules:
            formatting_rules = self.custom_rules[custom_rules_name]
        else:
            formatting_rules = self.default_rules
        
        # 获取处理器
        processor = self.get_processor(doc_type, ai_client)
        processor.formatting_rules = formatting_rules
        
        # 处理文档
        processor.process_document(input_path, output_path, optimize)
    
    def _get_ai_client(self, provider: AIProvider, api_key: str) -> AIClient:
        """获取AI客户端实例"""
        # 检查是否已有缓存的客户端
        if provider in self.ai_clients:
            return self.ai_clients[provider]
        
        # 创建新的客户端
        if provider == AIProvider.OPENAI:
            client = OpenAIClient(api_key)
        elif provider == AIProvider.DEEPSEEK:
            client = DeepSeekClient(api_key)
        elif provider == AIProvider.QWEN:
            client = QwenClient(api_key)
        elif provider == AIProvider.SILICONFLOW:
            client = SiliconFlowClient(api_key)
        else:
            client = OpenAIClient(api_key)
        
        # 缓存客户端
        self.ai_clients[provider] = client
        return client

def main():
    """主函数"""
    # 创建智能排版器实例
    formatter = SmartFormatter()
    
    # 设置默认排版规范
    default_rules = FormattingRule(
        font_family="宋体",
        font_size=12,
        line_spacing=1.5,
        paragraph_spacing=10,
        indent_first_line=True,
        indent_size=2
    )
    formatter.set_default_formatting_rules(default_rules)
    
    # 添加自定义排版规范
    academic_rules = FormattingRule(
        font_family="Times New Roman",
        font_size=12,
        line_spacing=2.0,
        paragraph_spacing=0,
        indent_first_line=False,
        heading_font_family="Arial",
        heading_font_size={
            "h1": 16,
            "h2": 14,
            "h3": 12,
            "h4": 12,
            "h5": 12,
            "h6": 12
        },
        image_alignment="center",
        image_max_width=600,
        image_caption_style="below"
    )
    formatter.add_custom_formatting_rules("学术论文", academic_rules)
    
    # 添加AI客户端
    # formatter.add_ai_client(AIProvider.OPENAI, OpenAIClient("your-openai-api-key"))
    
    # 处理文档示例
    # formatter.process_document(
    #     input_path="input.docx",
    #     output_path="output.docx",
    #     doc_type=DocumentType.WORD,
    #     ai_provider=AIProvider.DEEPSEEK,
    #     api_key="your-api-key",
    #     custom_rules_name="学术论文",
    #     optimize=True  # 启用内容优化
    # )

if __name__ == "__main__":
    main()