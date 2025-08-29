@echo off
chcp 65001 >nul
echo Ollama API 服务器启动脚本
echo =========================

REM 检查Python环境
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境
    echo 请确保已安装Python并添加到系统PATH中
    echo.
    pause
    exit /b 1
)

REM 检查并安装所需的库
echo 检查所需的Python库...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装Flask...
    pip install flask
    if %errorlevel% neq 0 (
        echo 错误: 无法安装Flask
        echo 请手动运行: pip install flask
        echo.
        pause
        exit /b 1
    )
)

python -c "import flask_cors" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装Flask-CORS...
    pip install flask-cors
    if %errorlevel% equ 0 (
        echo Flask-CORS 安装成功
    ) else (
        echo 错误: 无法安装Flask-CORS
        echo 请手动运行: pip install flask-cors
        echo.
        pause
        exit /b 1
    )
)

python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装requests...
    pip install requests
    if %errorlevel% neq 0 (
        echo 错误: 无法安装requests
        echo 请手动运行: pip install requests
        echo.
        pause
        exit /b 1
    )
)

REM 设置默认API密钥（如果环境变量未设置）
if "%OLLAMA_API_KEY%"=="" (
    set "OLLAMA_API_KEY=ollama-key-2023"
)

echo.
echo 启动 Ollama API 服务器...
echo 服务器地址: http://localhost:5000
echo API 密钥: %OLLAMA_API_KEY%
echo 按 Ctrl+C 停止服务器
echo.

REM 设置环境变量供Python脚本使用
set "OLLAMA_API_KEY=%OLLAMA_API_KEY%"
python "%~dp0ollama_api_server.py"

echo.
echo 服务器已停止
pause