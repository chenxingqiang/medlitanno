#!/bin/bash
# 医学文献自动标注系统 - 监控脚本
# Medical Literature Auto-Annotation System - Monitor Script

set -e

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 检查参数
ACTION=${1:-"monitor"}

case $ACTION in
    "monitor")
        echo "📊 启动实时监控..."
        python3 src/annotation/batch_monitor.py --monitor
        ;;
    "status")
        echo "📋 查看处理状态..."
        python3 src/annotation/batch_monitor.py --status
        ;;
    "restart")
        MODEL=${2:-"deepseek-reasoner"}
        echo "🔄 重启 $MODEL 模型处理..."
        python3 src/annotation/batch_monitor.py --restart $MODEL
        ;;
    *)
        echo "使用方法: $0 [monitor|status|restart] [model]"
        echo "Examples:"
        echo "  $0 monitor          # 实时监控"
        echo "  $0 status           # 查看状态"
        echo "  $0 restart deepseek # 重启DeepSeek模型"
        exit 1
        ;;
esac