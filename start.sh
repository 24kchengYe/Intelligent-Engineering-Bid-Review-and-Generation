#!/bin/bash

echo "===================================="
echo "   智能标书审查系统"
echo "===================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装"
    exit 1
fi

echo "[1/3] 检查依赖..."
if ! pip show streamlit &> /dev/null; then
    echo "[提示] 首次运行，正在安装依赖包..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        exit 1
    fi
fi

echo "[2/3] 检查配置..."
if [ ! -f .env ]; then
    echo "[提示] 未找到 .env 配置文件，正在创建..."
    cp .env.example .env
    echo ""
    echo "[重要] 请编辑 .env 文件，填入你的 Claude API Key"
    echo "然后重新运行此脚本"
    echo ""
    exit 0
fi

echo "[3/3] 启动系统..."
echo ""
echo "系统将在浏览器中打开，默认地址: http://localhost:8501"
echo "按 Ctrl+C 可停止服务"
echo ""

streamlit run app.py
