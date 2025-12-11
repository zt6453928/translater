#!/bin/bash

echo "================================"
echo "  PDF翻译器 - 启动脚本"
echo "================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python"
    exit 1
fi

echo "✓ Python3 已安装"

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo ""
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo "✓ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo ""
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "检查并安装依赖..."
pip install -r requirements.txt

# 启动应用
echo ""
echo "================================"
echo "  启动应用..."
echo "================================"
echo ""
echo "访问地址: http://localhost:8000"
echo "按 Ctrl+C 停止服务器"
echo ""

python app.py


