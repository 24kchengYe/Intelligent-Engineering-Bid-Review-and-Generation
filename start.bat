@echo off
chcp 65001 >nul
echo ====================================
echo   智能标书审查系统
echo ====================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.9 或更高版本
    pause
    exit /b 1
)

echo [1/3] 检查依赖...
pip show streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 首次运行，正在安装依赖包...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [2/3] 检查配置...
if not exist .env (
    echo [提示] 未找到 .env 配置文件，正在创建...
    copy .env.example .env
    echo.
    echo [重要] 请编辑 .env 文件，填入你的 Claude API Key
    echo 然后重新运行此脚本
    echo.
    pause
    exit /b 0
)

echo [3/3] 启动系统...
echo.
echo 系统将在浏览器中打开，默认地址: http://localhost:8501
echo 按 Ctrl+C 可停止服务
echo.

streamlit run app.py

pause
