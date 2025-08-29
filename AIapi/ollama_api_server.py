import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import secrets

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 默认模型
DEFAULT_MODEL = "deepseek-r1:1.5b"

# Ollama API端点
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"

# API密钥配置
API_KEY = os.environ.get('OLLAMA_API_KEY') or 'your-api-key-here'  # 默认API密钥

def require_api_key(f):
    """
    装饰器函数，用于验证API密钥
    """
    def decorated_function(*args, **kwargs):
        # 从请求头中获取API密钥
        api_key = request.headers.get('X-API-Key')
        
        # 如果没有提供API密钥
        if not api_key:
            return jsonify({"error": "Missing API key"}), 401
        
        # 如果API密钥不正确
        if api_key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 403
        
        # API密钥正确，继续执行函数
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/api/models', methods=['GET'])
@require_api_key
def get_models():
    """
    获取已安装的模型列表
    """
    try:
        response = requests.get(OLLAMA_TAGS_URL)
        if response.status_code == 200:
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            return jsonify({"models": models}), 200
        else:
            return jsonify({"error": "Failed to fetch models", "status_code": response.status_code}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
@require_api_key
def generate_text():
    """
    调用Ollama生成文本
    请求体应包含:
    {
        "model": "模型名称", (可选，默认为deepseek-r1:1.5b)
        "prompt": "提示词",
        "stream": false (可选，默认为false)
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data or "prompt" not in data:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400
        
        # 准备请求数据
        payload = {
            "model": data.get("model", DEFAULT_MODEL),
            "prompt": data.get("prompt"),
            "stream": data.get("stream", False)
        }
        
        # 调用Ollama API
        response = requests.post(OLLAMA_API_URL, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify(result), 200
        else:
            return jsonify({"error": "Ollama API error", "status_code": response.status_code}), response.status_code
            
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Cannot connect to Ollama service. Please ensure Ollama is running."}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    健康检查端点
    """
    try:
        response = requests.get(OLLAMA_TAGS_URL)
        if response.status_code == 200:
            return jsonify({"status": "healthy", "ollama": "connected"}), 200
        else:
            return jsonify({"status": "unhealthy", "ollama": "disconnected"}), 503
    except:
        return jsonify({"status": "unhealthy", "ollama": "disconnected"}), 503

@app.route('/', methods=['GET'])
def home():
    """
    主页，提供API文档
    """
    return jsonify({
        "message": "Ollama API Server",
        "authentication": "All API endpoints require an API key in the X-API-Key header",
        "endpoints": {
            "GET /api/models": "获取已安装的模型列表",
            "POST /api/generate": "生成文本",
            "GET /api/health": "健康检查",
            "POST body for /api/generate": {
                "model": "模型名称 (可选，默认: deepseek-r1:1.5b)",
                "prompt": "提示词 (必需)",
                "stream": "是否流式输出 (可选，默认: false)"
            }
        },
        "example_usage": {
            "curl": "curl -X POST http://localhost:5000/api/generate -H 'Content-Type: application/json' -H 'X-API-Key: your-api-key-here' -d '{\"prompt\": \"为什么天空是蓝色的？\"}'"
        }
    }), 200

if __name__ == '__main__':
    # 确保使用的是环境变量中的API密钥或者默认值
    api_key = os.environ.get('OLLAMA_API_KEY') or API_KEY
    print("启动 Ollama API 服务器...")
    print("服务器地址: http://localhost:5000")
    print(f"API 密钥: {api_key}")
    print("按 Ctrl+C 停止服务器")
    app.run(host='0.0.0.0', port=5000, debug=False)
