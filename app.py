"""
Flask Web应用用于智能文档排版软件
提供Web界面操作，支持导出为MD/Word/PDF/LaTeX格式
支持自定义模板
"""

from flask import Flask, render_template, request, send_file, jsonify
import os
import json
import threading
from werkzeug.utils import secure_filename
import tempfile

try:
    from smart_formatter import SmartFormatter, DocumentType, AIProvider, FormattingRule, Template
    from webui import WebUI
    SMART_FORMATTER_AVAILABLE = True
except ImportError:
    SMART_FORMATTER_AVAILABLE = False
    print("警告: smart_formatter或webui模块未找到")

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大上传16MB

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {'md', 'docx', 'tex'}

# 初始化智能排版器
if SMART_FORMATTER_AVAILABLE:
    formatter = SmartFormatter()
else:
    formatter = None

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """主页"""
    # 获取模板列表
    templates = []
    if formatter:
        templates = formatter.list_templates()
    return render_template('index.html', templates=templates)

@app.route('/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'success': True, 'filepath': file_path, 'filename': filename})
    
    return jsonify({'error': '不支持的文件格式'}), 400

@app.route('/process', methods=['POST'])
def process_document():
    """处理文档"""
    if not SMART_FORMATTER_AVAILABLE:
        return jsonify({'error': 'smart_formatter模块不可用'}), 500
    
    try:
        # 获取参数
        data = request.get_json()
        input_path = data.get('input_path')
        output_format = data.get('output_format', 'md')
        ai_provider = data.get('ai_provider', 'openai')
        api_key = data.get('api_key')
        optimize = data.get('optimize', False)
        template_name = data.get('template_name', '')
        
        if not input_path or not api_key:
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 确定输入文档类型
        if input_path.endswith('.docx'):
            input_doc_type = DocumentType.WORD
        elif input_path.endswith('.tex'):
            input_doc_type = DocumentType.LATEX
        else:
            input_doc_type = DocumentType.MARKDOWN
        
        # 确定输出文件路径
        base_name = os.path.splitext(input_path)[0]
        if output_format == 'docx':
            output_path = f"{base_name}_formatted.docx"
            output_doc_type = DocumentType.WORD
        elif output_format == 'pdf':
            output_path = f"{base_name}_formatted.pdf"
            output_doc_type = DocumentType.PDF
        elif output_format == 'latex':
            output_path = f"{base_name}_formatted.tex"
            output_doc_type = DocumentType.LATEX
        else:
            output_path = f"{base_name}_formatted.md"
            output_doc_type = DocumentType.MARKDOWN
        
        # 确定AI提供商
        provider_map = {
            "openai": AIProvider.OPENAI,
            "deepseek": AIProvider.DEEPSEEK,
            "qwen": AIProvider.QWEN,
            "siliconflow": AIProvider.SILICONFLOW
        }
        ai_provider_enum = provider_map.get(ai_provider, AIProvider.OPENAI)
        
        # 处理文档
        formatter.process_document(
            input_path=input_path,
            output_path=output_path,
            doc_type=input_doc_type,
            ai_provider=ai_provider_enum,
            api_key=api_key,
            optimize=optimize
        )
        
        return jsonify({
            'success': True, 
            'output_path': output_path,
            'output_format': output_format
        })
    
    except Exception as e:
        return jsonify({'error': f'处理文档时出错: {str(e)}'}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    """下载文件"""
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'下载文件时出错: {str(e)}'}), 500

@app.route('/templates')
def get_templates():
    """获取模板列表"""
    if not SMART_FORMATTER_AVAILABLE:
        return jsonify({'error': 'smart_formatter模块不可用'}), 500
    
    try:
        templates = formatter.list_templates()
        return jsonify({'success': True, 'templates': templates})
    except Exception as e:
        return jsonify({'error': f'获取模板时出错: {str(e)}'}), 500

@app.route('/template/<name>')
def get_template(name):
    """获取模板详情"""
    if not SMART_FORMATTER_AVAILABLE:
        return jsonify({'error': 'smart_formatter模块不可用'}), 500
    
    try:
        template = formatter.get_template(name)
        if template:
            return jsonify({'success': True, 'template': template.to_dict()})
        else:
            return jsonify({'error': '模板未找到'}), 404
    except Exception as e:
        return jsonify({'error': f'获取模板时出错: {str(e)}'}), 500

@app.route('/gui')
def run_gui():
    """运行GUI界面"""
    try:
        # 在新线程中运行GUI
        def start_gui():
            gui = WebUI()
            gui.run()
        
        thread = threading.Thread(target=start_gui)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'GUI已在后台启动'})
    except Exception as e:
        return jsonify({'error': f'启动GUI时出错: {str(e)}'}), 500

def main():
    """主函数"""
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()