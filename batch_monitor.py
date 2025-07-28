#!/usr/bin/env python3
"""
批量处理监控和管理脚本
Batch processing monitoring and management script
"""

import os
import json
import time
import argparse
from datetime import datetime
from collections import defaultdict

def monitor_progress(data_dir="datatrain", refresh_interval=30):
    """
    实时监控批量处理进度
    
    Args:
        data_dir: 数据目录
        refresh_interval: 刷新间隔(秒)
    """
    print("=== 批量标注进度监控 ===")
    print("按 Ctrl+C 退出监控")
    print()
    
    try:
        while True:
            # 统计总文件数
            total_files = 0
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if file.endswith('.xlsx'):
                        total_files += 1
            
            # 统计各模型的处理进度
            model_stats = {
                "deepseek": {"processed": 0, "total_articles": 0, "total_relations": 0},
                "deepseek-reasoner": {"processed": 0, "total_articles": 0, "total_relations": 0},
                "qianwen": {"processed": 0, "total_articles": 0, "total_relations": 0}
            }
            
            recent_files = []
            
            # 遍历所有annotation目录
            for root, dirs, files in os.walk(data_dir):
                if 'annotation' in dirs:
                    annotation_dir = os.path.join(root, 'annotation')
                    for file in os.listdir(annotation_dir):
                        for model in model_stats.keys():
                            if file.endswith(f'_annotated_{model}.json'):
                                model_stats[model]["processed"] += 1
                                file_path = os.path.join(annotation_dir, file)
                                recent_files.append((file_path, os.path.getmtime(file_path)))
                                
                                # 读取文件统计信息
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        data = json.load(f)
                                    model_stats[model]["total_articles"] += len(data)
                                    for article in data:
                                        model_stats[model]["total_relations"] += len(article.get('relations', []))
                                except:
                                    pass
            
            # 清屏并显示进度
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("=== 批量标注进度监控 ===")
            print(f"⏰ 监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📁 总文件数: {total_files}")
            print()
            
            # 显示各模型进度
            for model, stats in model_stats.items():
                processed = stats["processed"]
                progress_percent = (processed / total_files * 100) if total_files > 0 else 0
                
                print(f"🤖 {model.upper()}:")
                print(f"  已处理: {processed}/{total_files} ({progress_percent:.1f}%)")
                
                # 进度条
                bar_length = 40
                filled_length = int(bar_length * processed // total_files) if total_files > 0 else 0
                bar = '█' * filled_length + '-' * (bar_length - filled_length)
                print(f"  进度条: |{bar}| {progress_percent:.1f}%")
                
                if stats["total_articles"] > 0:
                    print(f"  标注文章: {stats['total_articles']}")
                    print(f"  提取关系: {stats['total_relations']}")
                
                print()
            
            # 显示最近处理的文件
            if recent_files:
                recent_files.sort(key=lambda x: x[1], reverse=True)
                print("📁 最近处理的文件:")
                for file_path, mtime in recent_files[:5]:
                    rel_path = os.path.relpath(file_path, data_dir)
                    time_str = datetime.fromtimestamp(mtime).strftime('%H:%M:%S')
                    print(f"  - {rel_path} ({time_str})")
                print()
            
            # 检查失败文件
            failed_logs = []
            for model in model_stats.keys():
                log_file = f"failed_files_{model}.json"
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            failed_count = len(json.load(f))
                        failed_logs.append((model, failed_count))
                    except:
                        pass
            
            if failed_logs:
                print("❌ 失败文件:")
                for model, count in failed_logs:
                    print(f"  {model}: {count} 个文件")
                print()
            
            print("💡 提示:")
            print("  - 按 Ctrl+C 退出监控")
            print("  - 结果保存在各目录的 annotation/ 子目录下")
            print("  - 支持断点续传，可随时中断和重启")
            
            # 等待刷新
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n👋 监控已退出")

def check_status(data_dir="datatrain"):
    """
    检查处理状态
    
    Args:
        data_dir: 数据目录
    """
    print("📊 检查处理状态...")
    print(f"数据目录: {data_dir}")
    print()
    
    # 统计文件数量
    total_files = 0
    processed_files = {"deepseek": 0, "deepseek-reasoner": 0, "qianwen": 0}
    model_stats = {"deepseek": {}, "deepseek-reasoner": {}, "qianwen": {}}
    
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.xlsx'):
                total_files += 1
                
                # 检查annotation目录
                annotation_dir = os.path.join(root, 'annotation')
                if os.path.exists(annotation_dir):
                    base_name = os.path.splitext(file)[0]
                    for model in processed_files.keys():
                        result_file = os.path.join(annotation_dir, f"{base_name}_annotated_{model}.json")
                        stats_file = os.path.join(annotation_dir, f"{base_name}_stats_{model}.json")
                        
                        if os.path.exists(result_file):
                            processed_files[model] += 1
                            
                            # 读取统计信息
                            if os.path.exists(stats_file):
                                try:
                                    with open(stats_file, 'r', encoding='utf-8') as f:
                                        stats = json.load(f)
                                    
                                    if 'total_articles' not in model_stats[model]:
                                        model_stats[model] = {
                                            'total_articles': 0,
                                            'total_bacteria': 0,
                                            'total_diseases': 0,
                                            'total_relations': 0,
                                            'relation_types': defaultdict(int)
                                        }
                                    
                                    model_stats[model]['total_articles'] += stats.get('total_articles', 0)
                                    model_stats[model]['total_bacteria'] += stats.get('total_bacteria', 0)
                                    model_stats[model]['total_diseases'] += stats.get('total_diseases', 0)
                                    model_stats[model]['total_relations'] += stats.get('total_relations', 0)
                                    
                                    for rel_type, count in stats.get('relation_types', {}).items():
                                        model_stats[model]['relation_types'][rel_type] += count
                                        
                                except:
                                    pass
    
    print(f"📁 总文件数: {total_files}")
    print()
    
    for model, count in processed_files.items():
        percentage = (count / total_files * 100) if total_files > 0 else 0
        print(f"🤖 {model.upper()}:")
        print(f"  处理进度: {count}/{total_files} ({percentage:.1f}%)")
        
        if model in model_stats and model_stats[model]:
            stats = model_stats[model]
            print(f"  标注文章: {stats['total_articles']}")
            print(f"  细菌实体: {stats['total_bacteria']}")
            print(f"  疾病实体: {stats['total_diseases']}")
            print(f"  关系总数: {stats['total_relations']}")
            
            if stats['relation_types']:
                print(f"  关系类型:")
                for rel_type, rel_count in sorted(stats['relation_types'].items()):
                    print(f"    - {rel_type}: {rel_count}")
        
        print()
    
    # 检查失败文件日志
    failed_logs = []
    for model in processed_files.keys():
        log_file = f"failed_files_{model}.json"
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    failed_items = json.load(f)
                failed_logs.append((log_file, len(failed_items)))
                print(f"❌ {model} 失败文件: {len(failed_items)} (日志: {log_file})")
            except:
                pass
    
    if failed_logs:
        print("\n💡 重新处理失败文件的命令:")
        for log_file, count in failed_logs:
            print(f"  python3 batch_monitor.py --retry-failed {log_file}")
    
    print(f"\n📈 总体进度:")
    total_processed = sum(processed_files.values())
    max_possible = total_files * len(processed_files)
    overall_percentage = (total_processed / max_possible * 100) if max_possible > 0 else 0
    print(f"  已处理: {total_processed}/{max_possible} ({overall_percentage:.1f}%)")

def restart_processing(model="deepseek-reasoner", data_dir="datatrain"):
    """
    重新启动批量处理
    
    Args:
        model: 模型类型
        data_dir: 数据目录
    """
    print(f"🚀 重新启动 {model} 模型的批量处理...")
    print(f"📁 数据目录: {data_dir}")
    print("💡 支持断点续传，已处理的文件将被跳过")
    print()
    
    # 配置API密钥
    api_keys = {
        "deepseek": "sk-d02fca54e07f4bdfb1778aeb62ae7671",
        "deepseek-reasoner": "sk-d02fca54e07f4bdfb1778aeb62ae7671",
        "qianwen": "sk-296434b603504719b9f5aca8286f5166"
    }
    
    model_names = {
        "deepseek": "deepseek-chat",
        "deepseek-reasoner": "deepseek-reasoner",
        "qianwen": "qwen-plus"
    }
    
    if model not in api_keys:
        print(f"❌ 不支持的模型类型: {model}")
        return
    
    try:
        from auto_annotation_system import batch_process_directory
        
        batch_process_directory(
            data_dir=data_dir,
            api_key=api_keys[model],
            model=model_names[model],
            model_type=model,
            max_retries=5,
            retry_delay=10
        )
        
    except KeyboardInterrupt:
        print("\n⚠️ 处理被中断")
        print("💡 可以稍后重新运行继续处理")
    except Exception as e:
        print(f"❌ 处理出现错误: {e}")

def main():
    parser = argparse.ArgumentParser(description="批量处理监控和管理脚本")
    parser.add_argument("--monitor", action="store_true", help="实时监控处理进度")
    parser.add_argument("--status", action="store_true", help="检查处理状态")
    parser.add_argument("--restart", type=str, choices=["deepseek", "deepseek-reasoner", "qianwen"],
                       help="重新启动指定模型的批量处理")
    parser.add_argument("--data-dir", type=str, default="datatrain", help="数据目录 (默认: datatrain)")
    parser.add_argument("--refresh", type=int, default=30, help="监控刷新间隔(秒) (默认: 30)")
    
    args = parser.parse_args()
    
    if args.monitor:
        monitor_progress(args.data_dir, args.refresh)
    elif args.status:
        check_status(args.data_dir)
    elif args.restart:
        restart_processing(args.restart, args.data_dir)
    else:
        print("批量处理监控和管理脚本")
        print()
        print("可用操作:")
        print("  --monitor: 实时监控处理进度")
        print("  --status: 检查处理状态")
        print("  --restart <模型>: 重新启动批量处理")
        print()
        print("示例:")
        print("  python3 batch_monitor.py --monitor")
        print("  python3 batch_monitor.py --status")
        print("  python3 batch_monitor.py --restart deepseek-reasoner")

if __name__ == "__main__":
    main() 