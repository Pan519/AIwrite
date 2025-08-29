import requests
import json
import sys
import os

# 设置默认输出目录
DEFAULT_OUTPUT_DIR = r"C:\myproject\models"

def call_ollama_api(model, prompt, output_file=None):
    """
    调用Ollama API并保存结果到文件
    
    Args:
        model (str): 模型名称
        prompt (str): 提示词
        output_file (str): 输出文件路径，如果为None则使用默认路径
    
    Returns:
        str: API响应内容
    """
    # Ollama API端点
    url = "http://localhost:11434/api/generate"
    
    # 请求数据
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, json=payload)
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "No response found")
            
            # 如果指定了输出文件，则写入文件
            if output_file:
                # 确保输出文件的目录存在
                output_dir = os.path.dirname(output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(response_text)
                print(f"响应已保存到: {output_file}")
            else:
                # 使用默认目录和文件名
                if not os.path.exists(DEFAULT_OUTPUT_DIR):
                    os.makedirs(DEFAULT_OUTPUT_DIR)
                
                default_output = os.path.join(DEFAULT_OUTPUT_DIR, "ollama_response.txt")
                with open(default_output, 'w', encoding='utf-8') as f:
                    f.write(response_text)
                print(f"响应已保存到默认文件: {default_output}")
            
            return response_text
        else:
            error_msg = f"API请求失败，状态码: {response.status_code}"
            print(error_msg)
            if output_file:
                # 确保输出文件的目录存在
                output_dir = os.path.dirname(output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(error_msg)
            return error_msg
            
    except requests.exceptions.ConnectionError:
        error_msg = "无法连接到Ollama服务，请确保服务正在运行"
        print(error_msg)
        if output_file:
            # 确保输出文件的目录存在
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(error_msg)
        return error_msg
        
    except Exception as e:
        error_msg = f"发生错误: {str(e)}"
        print(error_msg)
        if output_file:
            # 确保输出文件的目录存在
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(error_msg)
        return error_msg

def get_installed_models():
    """
    获取已安装的模型列表
    
    Returns:
        list: 模型名称列表
    """
    url = "http://localhost:11434/api/tags"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            return models
        else:
            print(f"获取模型列表失败，状态码: {response.status_code}")
            return []
    except Exception as e:
        print(f"获取模型列表时发生错误: {str(e)}")
        return []

def main():
    """
    主函数，处理命令行参数
    """
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python ollama_api_client.py \"你的问题\" [模型名称] [输出文件]")
        print("示例: python ollama_api_client.py \"为什么天空是蓝色的?\" deepseek-r1:1.5b result.txt")
        print(f"\n默认输出目录: {DEFAULT_OUTPUT_DIR}")
        print("\n已安装的模型:")
        models = get_installed_models()
        for model in models:
            print(f"  - {model}")
        return
    
    # 获取提示词
    prompt = sys.argv[1]
    
    # 获取模型名称（默认为deepseek-r1:1.5b）
    model = sys.argv[2] if len(sys.argv) > 2 else "deepseek-r1:1.5b"
    
    # 获取输出文件路径（可选）
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    print(f"正在使用模型 '{model}' 处理问题: {prompt}")
    
    # 调用API
    response = call_ollama_api(model, prompt, output_file)
    
    # 同时打印到控制台
    print("\n模型响应:")
    print("-" * 50)
    print(response)
    print("-" * 50)

if __name__ == "__main__":
    main()