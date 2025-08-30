# AI文档处理器

这是一个基于Ollama的AI文档处理工具，提供图形界面和命令行两种方式来实现文档的自动撰写、智能排版和多格式导出。

## 功能特性

1. **双模式操作** - 提供图形界面和命令行两种操作方式
2. **AI自动撰写** - 根据提示词自动生成结构完整的文档
3. **智能排版** - 支持多种文档风格（学术、商务、技术、创意）
4. **智能分析** - AI自动分析内容并推荐最佳文体和提示词
5. **多格式导出** - 支持Markdown、HTML、TXT等格式导出
6. **完整处理管道** - 一键完成撰写、排版和导出全过程
7. **图形界面** - 基于Web的用户友好界面，支持暗黑/明亮两种主题

## 系统要求

- Windows 7或更高版本
- Ollama服务（需要安装并运行相应的语言模型）

## 安装步骤

1. **安装Ollama**
   - 访问 https://ollama.com/ 下载并安装Ollama
   - 启动Ollama服务

2. **下载AI模型**
   ```bash
   ollama pull qwen3:8b
   ```

## 使用方法

### 图形界面模式

双击运行 `dist/AI文档处理器.exe` 文件，程序会自动打开浏览器并访问 http://localhost:8080

### 智能分析功能

本系统具有独特的智能分析功能：

1. **自动文体推荐** - AI会根据文档主题自动分析并推荐最适合的文体
2. **智能提示词优化** - 根据推荐的文体，AI会自动生成更精准的提示词
3. **自适应排版** - 根据内容类型自动选择最佳排版方案

在图形界面中，只需在文档风格中选择"自动分析"选项即可启用此功能。

### 命令行模式

```bash
# 完整处理流程（自动分析文体）
AI文档处理器.exe process "写一篇关于人工智能在医疗领域应用的文章" -s auto -f markdown -o ai_medical.md

# 指定特定文体
AI文档处理器.exe process "写一篇关于人工智能在医疗领域应用的文章" -s technical -f markdown -o ai_medical.md

# 单独撰写文档
AI文档处理器.exe write "提示词" -o document.md

# 格式化已有文档
AI文档处理器.exe format input.md -s academic -o formatted.md

# 导出文档
AI文档处理器.exe export formatted.md -f html -o document.html

# 启动Web服务
AI文档处理器.exe web -p 8080
```

## 打包为可执行文件

本项目支持打包为Windows可执行文件(.exe)，无需安装Python环境即可运行。

### 打包步骤

1. 确保已安装Python 3.7+
2. 双击运行 [build.bat](file://c:\myproject\AIwr\build.bat) 文件
3. 等待打包完成
4. 在 `dist` 目录中找到生成的可执行文件

### 打包生成的文件

- `AI文档处理器.exe` (约40MB) - 统一的可执行程序（图形界面+命令行）
- `使用说明.txt` - 使用说明

### 使用打包后的程序

1. 确保Ollama已安装并运行
2. 确保已下载所需模型 (如 `ollama pull qwen3:8b`)
3. 双击 `dist/AI文档处理器.exe` 启动图形界面服务
4. 在浏览器中访问 http://localhost:8080 使用

## 文件说明

- [ai_document_processor_unified.py](file://c:\myproject\AIwr\ai_document_processor_unified.py) - 统一版主程序源代码
- [ai_document_webui.html](file://c:\myproject\AIwr\ai_document_webui.html) - 图形界面HTML文件
- [build.bat](file://c:\myproject\AIwr\build.bat) - 打包批处理脚本
- [build_unified_exe.py](file://c:\myproject\AIwr\build_unified_exe.py) - 统一exe打包脚本
- [README.md](file://c:\myproject\AIwr\README.md) - 本说明文件

## 项目架构

```
AI文档处理器/
├── ai_document_processor_unified.py       # 统一版主程序源代码
├── ai_document_webui.html                 # 图形界面HTML文件
├── build.bat                             # 打包批处理脚本
├── build_unified_exe.py                  # 统一exe打包脚本
├── dist/                                 # 打包生成的可执行文件
│   ├── AI文档处理器.exe                    # 统一的可执行程序（图形界面+命令行）
│   └── 使用说明.txt                       # 使用说明
└── README.md                             # 项目说明文件
```

## 技术细节

### 图形界面模式工作流程

1. 用户通过浏览器访问Web界面
2. 前端通过AJAX请求与后端API通信
3. 后端API调用Ollama服务处理文档
4. 处理结果返回给前端显示

### 命令行模式工作流程

1. 用户通过命令行执行脚本
2. 脚本直接调用Ollama服务处理文档
3. 处理结果保存到文件或输出到控制台

## 故障排除

### 1. 启动服务时出现编码问题
如果在Windows系统上遇到中文显示乱码，请确保系统区域设置正确，或使用英文版启动脚本。

### 2. 无法连接到Ollama服务
确保：
1. Ollama已正确安装
2. Ollama服务正在运行（可以通过 `ollama serve` 启动）
3. 防火墙未阻止相关端口

### 3. 模型未找到
下载所需模型：
```bash
ollama pull qwen3:8b
ollama pull llama3:8b
```

## 许可证

本项目基于MIT许可证开源。