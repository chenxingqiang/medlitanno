#!/bin/bash
# 医学文献自动标注系统 - 运行脚本
# Medical Literature Auto-Annotation System - Run Script

set -e

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行 scripts/setup.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查环境变量
if [ -z "$DEEPSEEK_API_KEY" ] || [ -z "$QIANWEN_API_KEY" ]; then
    echo "⚠️ 环境变量未设置，尝试从 .env 文件加载..."
    if [ -f ".env" ]; then
        export $(cat .env | xargs)
        echo "✅ 从 .env 文件加载环境变量"
    else
        echo "❌ 请设置API密钥环境变量或创建 .env 文件"
        echo "   参考: config/env.example"
        exit 1
    fi
fi

# 创建日志目录
mkdir -p logs

# 运行标注系统
echo "🚀 启动医学文献自动标注系统..."
echo "🚀 Starting Medical Literature Auto-Annotation System..."

python3 src/annotation/run_annotation.py "$@" 