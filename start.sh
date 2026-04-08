#!/bin/bash

# 启动AI服务中转代理系统

# 进入项目目录
cd "$(dirname "$0")"

# 检查并创建虚拟环境
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "Activating virtual environment..."
source venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt

# 启动服务
echo "Starting AI service proxy server..."
python app_proxy.py