"""
智能文档排版软件
支持Word、Markdown、PDF和LaTeX文档格式
接入多种AI，根据内容和写作规范自动排版
支持用户自定义排版规范和模板
处理文字和图片的智能排版
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

class AIProvider(Enum):
    """AI提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    SILICONFLOW = "siliconflow"
    OLLAMA = "ollama"  # 新增Ollama支持

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
    output_format: str = "md"  # 新增输出格式字段
    
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
    
    @abstractmethod
    def apply_template(self, content: str, template: Template) -> str:
        """应用自定义模板"""
        pass