from flask import Flask, render_template, request, send_file, jsonify
import os
import json
import threading
from werkzeug.utils import secure_filename
import tempfile

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大上传16MB

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {'md', 'docx', 'tex'}

# 初始化智能排版器
try:
    from smart_formatter import SmartFormatter, DocumentType, AIProvider, FormattingRule
    SMART_FORMATTER_AVAILABLE = True
    formatter = SmartFormatter()
except ImportError:
    SMART_FORMATTER_AVAILABLE = False
    formatter = None
    print("警告: smart_formatter模块未找到")

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
        
        # 处理文档
        result = formatter.process_document(
            input_path=input_path,
            output_path=output_path,
            doc_type=input_doc_type,
            ai_provider=AIProvider(ai_provider),
            api_key=api_key,
            optimize=optimize,
            custom_rules_name=template_name
        )
        
        return jsonify({'success': True, 'output_path': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)