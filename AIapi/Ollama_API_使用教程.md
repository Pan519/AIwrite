# Ollama API 服务器使用教程

## 1. 启动 API 服务器

### 1.1 启动步骤
1. 双击运行项目目录下的 [start_api_server.bat](file://c:\myproject\models\start_api_server.bat) 文件
2. 或右键点击 [start_api_server.bat](file://c:\myproject\models\start_api_server.bat) 并选择"以管理员身份运行"
3. 等待脚本自动检查并安装所需依赖

### 1.2 启动成功标识
当看到以下信息时，表示服务器已成功启动：
```
启动 Ollama API 服务器...
服务器地址: http://localhost:5000
API 密钥: ollama-key-2023
按 Ctrl+C 停止服务器
 * Serving Flask app 'ollama_api_server'
 * Debug mode: off
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://你的局域网IP:5000
```

## 2. API 端点说明

### 2.1 健康检查
- **URL**: `/api/health`
- **方法**: GET
- **用途**: 检查服务器和 Ollama 服务是否正常运行
- **示例响应**:
  ```json
  {
    "status": "healthy",
    "ollama": "connected"
  }
  ```

### 2.2 获取模型列表
- **URL**: `/api/models`
- **方法**: GET
- **用途**: 获取已安装的 Ollama 模型列表
- **示例响应**:
  ```json
  {
    "models": [
      "deepseek-r1:1.5b",
      "llama3:8b",
      "phi3:3.8b"
    ]
  }
  ```

### 2.3 文本生成
- **URL**: `/api/generate`
- **方法**: POST
- **用途**: 使用模型生成文本
- **请求参数**:
  ```json
  {
    "model": "模型名称 (可选，默认: deepseek-r1:1.5b)",
    "prompt": "提示词 (必需)",
    "stream": "是否流式输出 (可选，默认: false)"
  }
  ```
- **示例响应**:
  ```json
  {
    "model": "deepseek-r1:1.5b",
    "response": "生成的文本内容",
    "done": true
  }
  ```

## 3. 局域网内访问 API

### 3.1 查找服务器 IP 地址
启动成功后，控制台会显示类似以下信息：
```
 * Running on http://192.168.199.234:5000
```
其中 `192.168.199.234` 就是你的服务器 IP 地址。

### 3.2 局域网内其他设备访问
局域网内的其他设备可以通过以下地址访问 API：
```
http://服务器IP地址:5000
```

例如，如果服务器 IP 是 `192.168.199.234`，则访问地址为：
```
http://192.168.199.234:5000
```

## 4. API 调用示例

### 4.1 认证方式
所有 API 调用都需要在请求头中包含 API 密钥：
```
X-API-Key: ollama-key-2023
```

### 4.2 使用 curl 调用

#### 健康检查
```bash
curl -X GET http://localhost:5000/api/health
```

#### 获取模型列表
```bash
curl -X GET http://localhost:5000/api/models \
  -H "X-API-Key: ollama-key-2023"
```

#### 文本生成
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ollama-key-2023" \
  -d '{"prompt": "你好，世界！"}'
```

#### 指定模型生成文本
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ollama-key-2023" \
  -d '{"model": "llama3:8b", "prompt": "写一首关于春天的诗"}'
```

### 4.3 使用 Python 调用

#### 基本调用示例
```python
import requests

# 服务器地址（本地或局域网IP）
BASE_URL = "http://localhost:5000"  # 或 "http://192.168.199.234:5000"
API_KEY = "ollama-key-2023"

# 设置请求头
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# 获取模型列表
response = requests.get(f"{BASE_URL}/api/models", headers=headers)
print("模型列表:", response.json())

# 文本生成
payload = {
    "prompt": "写一首关于春天的诗",
    "model": "deepseek-r1:1.5b"  # 可选，默认使用此模型
}

response = requests.post(
    f"{BASE_URL}/api/generate",
    headers=headers,
    json=payload
)

if response.status_code == 200:
    result = response.json()
    print("生成结果:", result.get("response", "无响应内容"))
else:
    print("请求失败:", response.status_code, response.text)
```

### 4.4 使用 JavaScript (Node.js) 调用
```javascript
const axios = require('axios');

const API_URL = 'http://localhost:5000';
const API_KEY = 'ollama-key-2023';

async function generateText(prompt) {
  try {
    const response = await axios.post(`${API_URL}/api/generate`, {
      prompt: prompt
    }, {
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      }
    });
    
    console.log('生成结果:', response.data.response);
  } catch (error) {
    console.error('请求失败:', error.response?.data || error.message);
  }
}

// 使用示例
generateText('你好，世界！');
```

### 4.5 使用 JavaScript (浏览器) 调用
```javascript
const API_URL = 'http://192.168.199.234:5000'; // 服务器IP地址
const API_KEY = 'ollama-key-2023';

async function generateText(prompt) {
  try {
    const response = await fetch(`${API_URL}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify({ prompt })
    });
    
    const data = await response.json();
    console.log('生成结果:', data.response);
  } catch (error) {
    console.error('请求失败:', error);
  }
}

// 使用示例
generateText('你好，世界！');
```

## 5. 局域网访问配置说明

### 5.1 防火墙设置
确保 Windows 防火墙允许 Python 或端口 5000 通过：
1. 打开"Windows 安全中心"
2. 点击"防火墙和网络保护"
3. 点击"允许应用通过防火墙"
4. 确保 Python 或 [start_api_server.bat](file://c:\myproject\models\start_api_server.bat) 在允许列表中

### 5.2 网络连接检查
确保所有设备在同一局域网内：
1. 服务器和其他设备连接到同一个路由器或网络
2. 可以通过 `ping 服务器IP` 测试网络连通性

## 6. 后台运行配置

[start_api_server.bat](file://c:\myproject\models\start_api_server.bat) 可以配置为后台运行，无需保持窗口打开：

### 6.1 最小化窗口运行
运行 [start_api_server.bat](file://c:\myproject\models\start_api_server.bat) 后，可以将窗口最小化，服务器会继续在后台运行。

### 6.2 使用 Windows 服务（推荐）
可以将 API 服务器安装为 Windows 服务，这样就可以在后台运行而不需要保持窗口打开。

#### 安装步骤：
1. 下载并安装 [NSSM](https://nssm.cc/download) (Non-Sucking Service Manager)
2. 使用管理员权限打开命令提示符
3. 运行以下命令创建服务：
   ```cmd
   nssm install OllamaAPIService "C:\myproject\models\start_api_server.bat"
   ```
4. 启动服务：
   ```cmd
   nssm start OllamaAPIService
   ```

### 6.3 使用 PowerShell 后台运行
可以通过 PowerShell 命令以后台方式运行：
```powershell
Start-Process -FilePath "C:\myproject\models\start_api_server.bat" -WindowStyle Hidden
```

### 6.4 使用任务计划程序
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器为"计算机启动时"
4. 设置操作为启动 [start_api_server.bat](file://c:\myproject\models\start_api_server.bat) 文件

### 6.5 停止后台服务
如果使用了后台运行方式，要停止服务可以：

1. **通过任务管理器**：
   - 按 `Ctrl+Shift+Esc` 打开任务管理器
   - 找到 Python 进程并结束任务

2. **通过命令行**：
   ```cmd
   taskkill /f /im python.exe
   ```

3. **如果安装为服务**：
   ```cmd
   nssm stop OllamaAPIService
   ```

## 7. 常见问题解决

### 7.1 连接被拒绝
- 确保服务器正在运行
- 检查防火墙设置
- 确认 IP 地址和端口号正确
- 检查是否在同一局域网内

### 7.2 API 密钥错误
- 确保在请求头中正确添加 `X-API-Key: ollama-key-2023`
- 检查是否有拼写错误
- 确认密钥是否已更改

### 7.3 无法获取模型列表
- 确保 Ollama 服务正在运行
- 检查 Ollama 是否已安装至少一个模型
- 确认 Ollama 服务是否正常工作

### 7.4 生成响应很慢
- 检查所选模型的大小，大模型需要更多时间
- 确认服务器硬件配置是否足够
- 检查是否有其他程序占用大量资源

### 7.5 服务器启动失败
- 检查 Python 环境是否正确安装
- 确认所有依赖库是否已安装
- 查看错误信息并针对性解决

## 8. 自定义 API 密钥（可选）

### 8.1 临时设置
在运行 [start_api_server.bat](file://c:\myproject\models\start_api_server.bat) 前执行：
```cmd
set OLLAMA_API_KEY=你的自定义密钥
start_api_server.bat
```

### 8.2 永久设置
1. 右键"此电脑" -> "属性"
2. 点击"高级系统设置"
3. 点击"环境变量"
4. 新建系统变量：
   - 变量名: `OLLAMA_API_KEY`
   - 变量值: 你的自定义密钥
5. 重启系统使设置生效

### 8.3 生成安全密钥
可以使用以下 Python 代码生成安全的 API 密钥：
```python
import secrets
print(secrets.token_urlsafe(32))
```

## 9. 客户端工具使用

### 9.1 命令行客户端
项目包含 [ollama_api_client.py](file://c:\myproject\models\ollama_api_client.py) 命令行客户端工具：

#### 基本使用：
```cmd
python ollama_api_client.py "你的问题"
```

#### 指定模型：
```cmd
python ollama_api_client.py "你的问题" "模型名称"
```

#### 获取模型列表：
```cmd
python ollama_api_client.py list-models
```

### 9.2 客户端参数说明
- 第一个参数：问题或命令（必需）
- 第二个参数：模型名称（可选）
- 第三个参数：输出文件路径（可选）

## 10. 安全建议

### 10.1 API 密钥安全
- 定期更换 API 密钥
- 不要在代码中硬编码密钥
- 使用环境变量存储密钥
- 限制对 API 服务器的网络访问

### 10.2 网络安全
- 仅在受信任的网络环境中运行
- 使用防火墙限制访问
- 考虑使用 HTTPS（需要额外配置）
- 定期更新依赖库

### 10.3 系统安全
- 使用非管理员账户运行服务
- 定期备份重要数据
- 监控系统资源使用情况
- 及时应用系统安全更新

## 11. 性能优化建议

### 11.1 硬件要求
- CPU: 至少双核处理器
- 内存: 推荐 8GB 或以上
- 存储: 足够的磁盘空间存储模型文件

### 11.2 模型选择
- 根据硬件配置选择合适的模型
- 小模型响应速度快，大模型质量高
- 可以同时安装多个模型按需使用

### 11.3 并发处理
- 当前版本为单线程处理
- 避免同时发送大量请求
- 考虑使用队列机制处理请求

## 12. 故障排除

### 12.1 查看日志信息
启动服务器后，控制台会显示详细的日志信息，包括：
- 启动过程中的依赖检查
- API 请求处理情况
- 错误信息和警告

### 12.2 常见错误及解决方案

#### ModuleNotFoundError
- 错误信息：`ModuleNotFoundError: No module named 'flask_cors'`
- 解决方案：运行 [start_api_server.bat](file://c:\myproject\models\start_api_server.bat) 会自动安装依赖

#### ConnectionError
- 错误信息：`Cannot connect to Ollama service`
- 解决方案：确保 Ollama 服务正在运行

#### PermissionError
- 错误信息：`Permission denied`
- 解决方案：以管理员身份运行 [start_api_server.bat](file://c:\myproject\models\start_api_server.bat)

## 13. 更新和维护

### 13.1 更新依赖库
定期更新 Python 依赖库以获得最新功能和安全修复：
```cmd
pip install --upgrade flask flask-cors requests
```

### 13.2 更新 Ollama
定期更新 Ollama 以获得最新模型和功能：
```cmd
ollama upgrade
```

### 13.3 备份配置
定期备份重要配置和数据：
- API 密钥设置
- 自定义模型配置
- 重要日志文件