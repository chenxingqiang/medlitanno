#!/bin/bash
# 医学文献自动标注系统 - 安装脚本
# Medical Literature Auto-Annotation System - Setup Script

set -e

echo "🚀 医学文献自动标注系统安装开始..."
echo "🚀 Starting Medical Literature Auto-Annotation System Setup..."

# 检查Python版本
echo "📋 检查Python环境..."
python3 --version || {
    echo "❌ Python 3 未安装，请先安装Python 3.7+"
    exit 1
}

# 创建虚拟环境
echo "🔧 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "ℹ️ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 安装Python依赖..."
pip install --upgrade pip
pip install -r config/requirements.txt

# 检查环境变量
echo "🔑 检查环境变量配置..."
if [ -z "$DEEPSEEK_API_KEY" ] || [ -z "$QIANWEN_API_KEY" ]; then
    echo "⚠️ 请设置API密钥环境变量："
    echo "   export DEEPSEEK_API_KEY=your_deepseek_api_key"
    echo "   export QIANWEN_API_KEY=your_qianwen_api_key"
    echo ""
    echo "或者复制配置文件："
    echo "   cp config/env.example .env"
    echo "   # 然后编辑 .env 文件"
else
    echo "✅ 环境变量已设置"
fi

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p {output,logs,temp}

echo ""
echo "🎉 安装完成！"
echo "🎉 Setup Complete!"
echo ""
echo "📖 下一步："
echo "   1. 设置API密钥（如果还未设置）"
echo "   2. 运行: python3 src/annotation/run_annotation.py"
echo "   3. 查看文档: docs/SETUP.md"
echo ""
echo "📖 Next Steps:"
echo "   1. Set API keys (if not already set)"
echo "   2. Run: python3 src/annotation/run_annotation.py"
echo "   3. Read docs: docs/SETUP.md" 