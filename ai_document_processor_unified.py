#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI文档处理器 - 统一版本
整合图形界面和命令行功能到一个可执行文件中
"""

import argparse
import sys
import os
import threading
import webbrowser
import time
from pathlib import Path
from datetime import datetime

# 尝试导入Flask相关模块（用于图形界面）
FLASK_AVAILABLE = False
try:
    from flask import Flask, request, jsonify, send_from_directory
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    pass

# 尝试导入Ollama模块
OLLAMA_AVAILABLE = False
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    pass

class AIDocumentProcessor:
    def __init__(self, model="qwen3:8b", host="http://127.0.0.1:11434"):
        """
        初始化AI文档处理器
        
        Args:
            model: 使用的模型名称
            host: Ollama服务地址
        """
        self.model = model
        if OLLAMA_AVAILABLE:
            self.client = ollama.Client(host=host)
        self.default_options = {
            'temperature': 0.7,
            'top_p': 0.9
        }
    
    def analyze_content_for_style(self, prompt):
        """
        让AI分析内容并推荐合适的文体
        
        Args:
            prompt: 文档主题或内容
            
        Returns:
            推荐的文体类型
        """
        if not OLLAMA_AVAILABLE:
            return "technical"
            
        analysis_prompt = f"""根据以下主题或内容，分析并推荐最适合的文档文体和排版风格：

主题或内容：{prompt}

请从以下选项中选择最合适的文体：
1. technical - 技术文档：适合技术说明、开发文档、API文档等
2. academic - 学术论文：适合学术研究、论文、研究报告等
3. business - 商务报告：适合商业计划、市场分析、企业报告等
4. creative - 创意写作：适合博客文章、故事、宣传文案等

请只回答一个词：technical、academic、business或creative，并简要说明理由（不超过20字）。
"""
        
        try:
            response = self.client.generate(
                model=self.model,
                prompt=analysis_prompt,
                options={'temperature': 0.3}
            )
            
            # 解析响应，提取文体类型
            content = response['response'].strip().lower()
            if 'technical' in content:
                return 'technical'
            elif 'academic' in content:
                return 'academic'
            elif 'business' in content:
                return 'business'
            elif 'creative' in content:
                return 'creative'
            else:
                return 'technical'  # 默认返回技术文档
        except Exception:
            return 'technical'  # 出错时默认返回技术文档
    
    def generate_prompt_by_style(self, topic, style):
        """
        根据推荐的文体生成更合适的提示词
        
        Args:
            topic: 文档主题
            style: 文体类型
            
        Returns:
            优化后的提示词
        """
        style_prompts = {
            "technical": f"请撰写一篇关于'{topic}'的技术文档，要求包含：1)技术背景 2)核心原理 3)实现方法 4)应用示例 5)技术细节，使用专业术语并保持逻辑清晰。",
            "academic": f"请撰写一篇关于'{topic}'的学术论文，要求包含：1)摘要 2)引言 3)文献综述 4)研究方法 5)分析与讨论 6)结论 7)参考文献，遵循学术写作规范。",
            "business": f"请撰写一份关于'{topic}'的商务报告，要求包含：1)执行摘要 2)市场背景 3)分析与发现 4)战略建议 5)实施计划 6)风险评估 7)财务预测，语言专业且具有说服力。",
            "creative": f"请以'{topic}'为主题创作一篇引人入胜的文章，要求：1)吸引人的开头 2)生动的内容展开 3)情感共鸣 4)有力的结尾，语言富有表现力和感染力。"
        }
        
        return style_prompts.get(style, style_prompts["technical"])
    
    def write_document(self, prompt, auto_style=False):
        """
        使用AI撰写文档
        
        Args:
            prompt: 写作提示
            auto_style: 是否自动分析文体
            
        Returns:
            生成的文档内容
        """
        if not OLLAMA_AVAILABLE:
            return "错误：未安装Ollama客户端，请先安装Ollama。"
            
        # 如果启用自动风格分析
        if auto_style:
            recommended_style = self.analyze_content_for_style(prompt)
            optimized_prompt = self.generate_prompt_by_style(prompt, recommended_style)
        else:
            # 使用用户提供的主题直接生成提示词
            optimized_prompt = f"""请根据以下主题撰写一篇结构完整、内容丰富的文档：

主题：{prompt}

要求：
1. 包含适当的标题和章节
2. 内容详细且有条理
3. 使用清晰的段落结构
4. 如果适用，包含实例或数据支持
"""
        
        try:
            response = self.client.generate(
                model=self.model,
                prompt=optimized_prompt if auto_style else optimized_prompt,
                options=self.default_options
            )
            
            return response['response']
        except Exception as e:
            return f"文档撰写失败: {str(e)}"
    
    def format_document(self, content, style="technical", output_file=None):
        """
        使用AI格式化文档
        
        Args:
            content: 原始文档内容
            style: 格式风格 (academic, business, technical, creative)
            output_file: 输出文件路径
            
        Returns:
            格式化后的文档内容
        """
        if not OLLAMA_AVAILABLE:
            return "错误：未安装Ollama客户端，请先安装Ollama。"
            
        # 根据风格定义提示词
        style_prompts = {
            "academic": "请将以下文档按照学术论文格式进行排版，包括标题、摘要、正文、参考文献等部分，要求格式规范、条理清晰：",
            "business": "请将以下文档按照商务报告格式进行排版，包括执行摘要、主要章节、结论和建议等部分，要求专业、简洁：",
            "technical": "请将以下文档按照技术文档格式进行排版，包括清晰的标题层级、代码块、图表说明等，要求准确、易读：",
            "creative": "请将以下文档按照创意写作格式进行排版，包括引人入胜的开头、流畅的段落过渡和有力的结尾，要求富有表现力："
        }
        
        prompt_prefix = style_prompts.get(style, style_prompts["technical"])
        prompt = f"{prompt_prefix}\n\n{content}"
        
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={'temperature': 0.5}  # 降低创造性以保持准确性
            )
            
            formatted_content = response['response']
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(formatted_content)
            
            return formatted_content
        except Exception as e:
            return f"文档格式化失败: {str(e)}"
    
    def export_document(self, content, format_type="markdown", output_file=None):
        """
        导出文档为指定格式
        
        Args:
            content: 文档内容
            format_type: 导出格式 (markdown, html, txt)
            output_file: 输出文件路径
        """
        # 如果没有指定输出文件，生成默认文件名
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extensions = {
                "markdown": ".md",
                "html": ".html",
                "txt": ".txt"
            }
            ext = extensions.get(format_type, f".{format_type}")
            output_file = f"document_{timestamp}{ext}"
        
        # 根据格式类型处理内容
        if format_type == "html":
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AI生成文档</title>
</head>
<body>
<pre>
{content}
</pre>
</body>
</html>"""
            final_content = html_content
        else:
            final_content = content
        
        # 保存文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        return output_file
    
    def process_document(self, prompt, style="auto", format_type="markdown", output_file=None):
        """
        完整的文档处理流程：撰写 -> 格式化 -> 导出
        
        Args:
            prompt: 写作提示
            style: 格式风格 (auto, academic, business, technical, creative)
            format_type: 导出格式
            output_file: 输出文件路径
        """
        if not OLLAMA_AVAILABLE:
            return "错误：未安装Ollama客户端，请先安装Ollama。"
            
        # 如果style为'auto'，则使用自动分析
        if style == "auto":
            style = self.analyze_content_for_style(prompt)
            auto_style = True
        else:
            auto_style = False
        
        # 步骤1: 撰写文档
        content = self.write_document(prompt, auto_style)
        
        # 步骤2: 格式化文档
        formatted_content = self.format_document(content, style)
        
        # 步骤3: 导出文档
        export_file = self.export_document(formatted_content, format_type, output_file)
        
        return export_file, style


def create_flask_app():
    """创建Flask应用"""
    if not FLASK_AVAILABLE:
        return None
        
    app = Flask(__name__)
    CORS(app)
    
    # 初始化文档处理器
    processor = AIDocumentProcessor()
    
    @app.route('/')
    def index():
        """提供HTML界面"""
        # 尝试从当前目录或资源中获取HTML文件
        html_file = Path(__file__).parent / "ai_document_webui.html"
        if html_file.exists():
            return send_from_directory(Path(__file__).parent, "ai_document_webui.html")
        else:
            return "错误：未找到HTML界面文件。"
    
    @app.route('/<path:filename>')
    def serve_static(filename):
        """提供静态文件"""
        return send_from_directory(Path(__file__).parent, filename)
    
    @app.route('/api/document/process', methods=['POST'])
    def process_document():
        """处理完整文档流程：撰写 -> 格式化"""
        try:
            data = request.get_json()
            prompt = data.get('prompt', '')
            model = data.get('model', 'qwen3:8b')
            style = data.get('style', 'auto')
            
            if not prompt:
                return jsonify({
                    'success': False,
                    'message': '提示词不能为空'
                }), 400
            
            # 设置模型
            processor.model = model
            
            # 如果style为'auto'，则使用自动分析
            if style == 'auto':
                style = processor.analyze_content_for_style(prompt)
                auto_style = True
            else:
                auto_style = False
            
            # 步骤1: 撰写文档
            content = processor.write_document(prompt, auto_style)
            
            # 步骤2: 格式化文档
            formatted_content = processor.format_document(content, style)
            
            return jsonify({
                'success': True,
                'message': '文档处理完成',
                'content': formatted_content,
                'style': style
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'处理失败: {str(e)}'
            }), 500
    
    @app.route('/api/document/write', methods=['POST'])
    def write_document():
        """仅撰写文档"""
        try:
            data = request.get_json()
            prompt = data.get('prompt', '')
            model = data.get('model', 'qwen3:8b')
            
            if not prompt:
                return jsonify({
                    'success': False,
                    'message': '提示词不能为空'
                }), 400
            
            # 设置模型
            processor.model = model
            
            # 撰写文档
            content = processor.write_document(prompt, False)
            
            return jsonify({
                'success': True,
                'message': '文档撰写完成',
                'content': content
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'撰写失败: {str(e)}'
            }), 500
    
    @app.route('/api/document/format', methods=['POST'])
    def format_document():
        """仅格式化文档"""
        try:
            data = request.get_json()
            content = data.get('content', '')
            style = data.get('style', 'technical')
            model = data.get('model', 'qwen3:8b')
            
            if not content:
                return jsonify({
                    'success': False,
                    'message': '内容不能为空'
                }), 400
            
            # 设置模型
            processor.model = model
            
            # 格式化文档
            formatted_content = processor.format_document(content, style)
            
            return jsonify({
                'success': True,
                'message': '文档格式化完成',
                'content': formatted_content
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'格式化失败: {str(e)}'
            }), 500
    
    @app.route('/api/document/export', methods=['POST'])
    def export_document():
        """导出文档"""
        try:
            data = request.get_json()
            content = data.get('content', '')
            format_type = data.get('format', 'markdown')
            
            if not content:
                return jsonify({
                    'success': False,
                    'message': '内容不能为空'
                }), 400
            
            # 导出文档
            output_file = processor.export_document(content, format_type)
            
            return jsonify({
                'success': True,
                'message': '文档导出完成',
                'file': output_file
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'导出失败: {str(e)}'
            }), 500
    
    @app.route('/api/document/models', methods=['GET'])
    def get_models():
        """获取可用模型列表"""
        # 这里应该调用Ollama API获取实际模型列表
        # 暂时返回预定义的模型列表
        models = ["qwen3:8b", "llama3:8b", "mistral:7b", "gemma:7b"]
        return jsonify({
            'success': True,
            'models': models
        })
    
    return app


def run_web_interface(port=8080):
    """运行Web界面"""
    app = create_flask_app()
    if app is None:
        print("错误：未安装Flask，无法启动Web界面。")
        print("请先安装Flask：pip install flask flask-cors")
        return
    
    print(f"AI文档处理器Web服务启动中...")
    print(f"访问地址: http://localhost:{port}")
    print("确保Ollama服务正在运行在 http://localhost:11434")
    app.run(host='0.0.0.0', port=port, debug=False)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI文档处理器 - 自动撰写、排版和导出文档")
    parser.add_argument("action", nargs="?", default="gui", 
                       choices=["gui", "write", "format", "export", "process", "web"],
                       help="操作类型: gui(图形界面), write(撰写), format(排版), export(导出), process(完整处理), web(启动Web服务)")
    parser.add_argument("input", nargs="?", help="输入内容或文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-m", "--model", default="qwen3:8b", help="使用的模型 (默认: qwen3:8b)")
    parser.add_argument("-s", "--style", default="auto", 
                       choices=["auto", "academic", "business", "technical", "creative"],
                       help="文档风格 (默认: auto)")
    parser.add_argument("-f", "--format", default="markdown",
                       choices=["markdown", "html", "txt"],
                       help="导出格式 (默认: markdown)")
    parser.add_argument("-p", "--port", type=int, default=8080, help="Web服务端口 (默认: 8080)")
    
    args = parser.parse_args()
    
    # 创建文档处理器
    processor = AIDocumentProcessor(model=args.model)
    
    # 根据操作类型执行相应功能
    if args.action == "gui" or args.action == "web":
        # 启动Web界面
        if args.action == "gui":
            # 尝试自动打开浏览器
            def open_browser():
                time.sleep(2)
                webbrowser.open(f"http://localhost:{args.port}")
            
            threading.Thread(target=open_browser).start()
        
        run_web_interface(args.port)
        
    elif args.action == "write":
        if not args.input:
            print("错误: 撰写文档需要提供提示词")
            return 1
        
        content = processor.write_document(args.input, args.style == "auto")
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"文档已保存到: {args.output}")
        else:
            print(content)
            
    elif args.action == "format":
        if not args.input:
            print("错误: 格式化文档需要提供文件路径")
            return 1
        
        # 读取文件内容
        if not os.path.exists(args.input):
            print(f"错误: 文件 {args.input} 不存在")
            return 1
            
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
        
        formatted_content = processor.format_document(content, args.style, args.output)
        if args.output:
            print(f"格式化文档已保存到: {args.output}")
        else:
            print(formatted_content)
            
    elif args.action == "export":
        if not args.input:
            print("错误: 导出文档需要提供文件路径")
            return 1
        
        # 读取文件内容
        if not os.path.exists(args.input):
            print(f"错误: 文件 {args.input} 不存在")
            return 1
            
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
        
        export_file = processor.export_document(content, args.format, args.output)
        print(f"文档已导出到: {export_file}")
            
    elif args.action == "process":
        if not args.input:
            print("错误: 处理文档需要提供提示词")
            return 1
        
        export_file, style = processor.process_document(args.input, args.style, args.format, args.output)
        print(f"文档处理完成!")
        print(f"最终文档已保存到: {export_file}")
        print(f"使用的文体: {style}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())