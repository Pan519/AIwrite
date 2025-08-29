"""
图片处理模块
专门处理文档中的图片排版和格式化
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import base64
from PIL import Image
import io

class ImageAlignment(Enum):
    """图片对齐方式枚举"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"

class ImageFormat(Enum):
    """图片格式枚举"""
    JPEG = "JPEG"
    PNG = "PNG"
    GIF = "GIF"
    BMP = "BMP"

@dataclass
class ImageInfo:
    """图片信息数据类"""
    id: str
    path: Optional[str] = None
    data: Optional[bytes] = None
    width: int = 0
    height: int = 0
    format: str = "JPEG"
    caption: str = ""
    alignment: ImageAlignment = ImageAlignment.CENTER

@dataclass
class ImageFormattingRule:
    """图片排版规范"""
    alignment: ImageAlignment = ImageAlignment.CENTER
    max_width: int = 800
    max_height: int = 600
    caption_style: str = "below"  # below, above, none
    caption_prefix: str = "图"
    caption_font_family: str = "宋体"
    caption_font_size: int = 10
    allow_resize: bool = True
    preserve_aspect_ratio: bool = True

class ImageHandler:
    """图片处理器"""
    
    def __init__(self, formatting_rule: ImageFormattingRule = None):
        self.formatting_rule = formatting_rule or ImageFormattingRule()
    
    def analyze_image(self, image_path: str) -> ImageInfo:
        """
        分析图片信息
        
        Args:
            image_path: 图片路径
            
        Returns:
            ImageInfo: 图片信息对象
        """
        try:
            with Image.open(image_path) as img:
                image_info = ImageInfo(
                    id=self._generate_image_id(),
                    path=image_path,
                    width=img.width,
                    height=img.height,
                    format=img.format
                )
                return image_info
        except Exception as e:
            print(f"分析图片时出错: {e}")
            return ImageInfo(id=self._generate_image_id(), path=image_path)
    
    def analyze_image_from_data(self, image_data: bytes) -> ImageInfo:
        """
        从字节数据分析图片信息
        
        Args:
            image_data: 图片字节数据
            
        Returns:
            ImageInfo: 图片信息对象
        """
        try:
            img = Image.open(io.BytesIO(image_data))
            image_info = ImageInfo(
                id=self._generate_image_id(),
                data=image_data,
                width=img.width,
                height=img.height,
                format=img.format
            )
            return image_info
        except Exception as e:
            print(f"分析图片数据时出错: {e}")
            return ImageInfo(id=self._generate_image_id(), data=image_data)
    
    def resize_image(self, image_info: ImageInfo) -> ImageInfo:
        """
        根据排版规范调整图片大小
        
        Args:
            image_info: 图片信息对象
            
        Returns:
            ImageInfo: 调整后的图片信息对象
        """
        if not self.formatting_rule.allow_resize:
            return image_info
        
        # 如果图片尺寸在允许范围内，则不调整
        if (image_info.width <= self.formatting_rule.max_width and 
            image_info.height <= self.formatting_rule.max_height):
            return image_info
        
        # 计算缩放比例
        scale_x = self.formatting_rule.max_width / image_info.width
        scale_y = self.formatting_rule.max_height / image_info.height
        
        if self.formatting_rule.preserve_aspect_ratio:
            # 保持纵横比，选择较小的缩放比例
            scale = min(scale_x, scale_y)
            new_width = int(image_info.width * scale)
            new_height = int(image_info.height * scale)
        else:
            # 不保持纵横比，分别应用缩放
            new_width = self.formatting_rule.max_width
            new_height = self.formatting_rule.max_height
        
        # 更新图片信息
        resized_info = ImageInfo(
            id=image_info.id,
            path=image_info.path,
            data=image_info.data,
            width=new_width,
            height=new_height,
            format=image_info.format,
            caption=image_info.caption,
            alignment=image_info.alignment
        )
        
        return resized_info
    
    def apply_formatting(self, image_info: ImageInfo) -> ImageInfo:
        """
        应用排版规范到图片
        
        Args:
            image_info: 图片信息对象
            
        Returns:
            ImageInfo: 应用排版规范后的图片信息对象
        """
        # 设置对齐方式
        formatted_info = ImageInfo(
            id=image_info.id,
            path=image_info.path,
            data=image_info.data,
            width=image_info.width,
            height=image_info.height,
            format=image_info.format,
            caption=image_info.caption,
            alignment=self.formatting_rule.alignment
        )
        
        # 调整图片大小
        if self.formatting_rule.allow_resize:
            formatted_info = self.resize_image(formatted_info)
        
        return formatted_info
    
    def generate_caption(self, image_info: ImageInfo, index: int) -> str:
        """
        生成图片标题
        
        Args:
            image_info: 图片信息对象
            index: 图片索引
            
        Returns:
            str: 图片标题
        """
        if image_info.caption:
            return f"{self.formatting_rule.caption_prefix}{index}. {image_info.caption}"
        else:
            return f"{self.formatting_rule.caption_prefix}{index}"
    
    def to_markdown(self, image_info: ImageInfo, caption: str = None) -> str:
        """
        将图片信息转换为Markdown格式
        
        Args:
            image_info: 图片信息对象
            caption: 图片标题
            
        Returns:
            str: Markdown格式的图片
        """
        # 构建Markdown图片语法
        if image_info.path:
            md_image = f"![{caption or ''}]({image_info.path})"
        elif image_info.data:
            # 将图片数据转换为base64格式
            encoded_data = base64.b64encode(image_info.data).decode('utf-8')
            md_image = f"![{caption or ''}](data:image/{image_info.format.lower()};base64,{encoded_data})"
        else:
            md_image = f"![{caption or ''}](image_{image_info.id})"
        
        # 根据对齐方式添加HTML标签
        if image_info.alignment == ImageAlignment.CENTER:
            return f"<div align=\"center\">{md_image}</div>"
        elif image_info.alignment == ImageAlignment.RIGHT:
            return f"<div align=\"right\">{md_image}</div>"
        elif image_info.alignment == ImageAlignment.LEFT:
            return f"<div align=\"left\">{md_image}</div>"
        else:
            return md_image
    
    def to_html(self, image_info: ImageInfo, caption: str = None) -> str:
        """
        将图片信息转换为HTML格式
        
        Args:
            image_info: 图片信息对象
            caption: 图片标题
            
        Returns:
            str: HTML格式的图片
        """
        # 构建HTML图片标签
        style = f"text-align: {image_info.alignment.value};"
        
        if image_info.path:
            html_image = f"<img src=\"{image_info.path}\" alt=\"{caption or ''}\" "
        elif image_info.data:
            encoded_data = base64.b64encode(image_info.data).decode('utf-8')
            html_image = f"<img src=\"data:image/{image_info.format.lower()};base64,{encoded_data}\" alt=\"{caption or ''}\" "
        else:
            html_image = f"<img src=\"image_{image_info.id}\" alt=\"{caption or ''}\" "
        
        html_image += f"style=\"max-width: {self.formatting_rule.max_width}px; "
        
        if self.formatting_rule.preserve_aspect_ratio:
            html_image += "height: auto; "
        
        html_image += "\" />"
        
        # 添加标题
        if caption and self.formatting_rule.caption_style != "none":
            caption_style = f"font-family: {self.formatting_rule.caption_font_family}; "
            caption_style += f"font-size: {self.formatting_rule.caption_font_size}px; "
            caption_style += "margin-top: 5px; " if self.formatting_rule.caption_style == "below" else "margin-bottom: 5px; "
            
            html_caption = f"<div style=\"{caption_style}\">{caption}</div>"
            
            if self.formatting_rule.caption_style == "below":
                return f"<div style=\"{style}\">{html_image}{html_caption}</div>"
            else:
                return f"<div style=\"{style}\">{html_caption}{html_image}</div>"
        else:
            return f"<div style=\"{style}\">{html_image}</div>"
    
    def _generate_image_id(self) -> str:
        """
        生成图片ID
        
        Returns:
            str: 图片ID
        """
        import uuid
        return str(uuid.uuid4())[:8]

def main():
    """测试图片处理功能"""
    # 创建图片处理器
    image_handler = ImageHandler()
    
    # 示例：处理图片
    # image_info = image_handler.analyze_image("example.jpg")
    # formatted_image = image_handler.apply_formatting(image_info)
    # caption = image_handler.generate_caption(formatted_image, 1)
    # markdown_output = image_handler.to_markdown(formatted_image, caption)
    
    print("图片处理模块已加载")

if __name__ == "__main__":
    main()