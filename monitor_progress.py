#!/usr/bin/env python3
"""
批量处理进度监控脚本
Batch processing progress monitor
"""

import os
import json
import time
from datetime import datetime
from collections import defaultdict

def monitor_progress():
    """监控批量处理进度"""
    
    data_dir = "datatrain"
    
    print("=== DeepSeek批量标注进度监控 ===")
    print(f"数据目录: {data_dir}")
    print("结果保存在各目录的 annotation/ 子目录下")
    print()
    
    # 统计总文件数
    total_files = 0
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.xlsx'):
                total_files += 1
    
    while True:
        try:
            # 统计已处理文件
            processed_files = 0
            total_articles = 0
            total_entities = 0
            total_relations = 0
            relation_types = defaultdict(int)
            processed_paths = []
            
            # 遍历所有annotation目录
            for root, dirs, files in os.walk(data_dir):
                if 'annotation' in dirs:
                    annotation_dir = os.path.join(root, 'annotation')
                    for file in os.listdir(annotation_dir):
                        if file.endswith('_annotated_deepseek.json'):
                            processed_files += 1
                            processed_paths.append(os.path.join(annotation_dir, file))
                            
                            # 读取统计信息
                            file_path = os.path.join(annotation_dir, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                
                                total_articles += len(data)
                                for article in data:
                                    total_entities += len(article.get('entities', []))
                                    total_relations += len(article.get('relations', []))
                                    
                                    for relation in article.get('relations', []):
                                        rel_type = relation.get('relation_type', 'unknown')
                                        relation_types[rel_type] += 1
                                        
                            except Exception as e:
                                print(f"读取文件出错 {file_path}: {e}")
            
            # 计算进度
            progress_percent = (processed_files / total_files * 100) if total_files > 0 else 0
            
            # 清屏并显示进度
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("=== DeepSeek批量标注进度监控 ===")
            print(f"⏰ 监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            print("📊 处理进度:")
            print(f"  总文件数: {total_files}")
            print(f"  已处理: {processed_files}")
            print(f"  剩余: {total_files - processed_files}")
            print(f"  完成率: {progress_percent:.1f}%")
            
            # 进度条
            bar_length = 50
            filled_length = int(bar_length * processed_files // total_files) if total_files > 0 else 0
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            print(f"  进度条: |{bar}| {progress_percent:.1f}%")
            print()
            
            print("📈 标注统计:")
            print(f"  总文章数: {total_articles}")
            print(f"  总实体数: {total_entities}")
            print(f"  总关系数: {total_relations}")
            
            if relation_types:
                print("  关系类型分布:")
                for rel_type, count in relation_types.items():
                    print(f"    - {rel_type}: {count}")
            print()
            
            # 显示最近处理的文件
            if processed_paths:
                print("📁 最近处理的文件:")
                recent_files = sorted(processed_paths, key=lambda x: os.path.getmtime(x), reverse=True)[:5]
                for file_path in recent_files:
                    rel_path = os.path.relpath(file_path, data_dir)
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    print(f"  - {rel_path} ({mtime.strftime('%H:%M:%S')})")
                print()
            
            # 估算剩余时间
            if processed_files > 0:
                avg_time_per_file = 60  # 假设每个文件1分钟
                remaining_files = total_files - processed_files
                estimated_minutes = remaining_files * avg_time_per_file / 60
                
                if estimated_minutes < 60:
                    print(f"⏱️  预计剩余时间: {estimated_minutes:.0f} 分钟")
                else:
                    hours = estimated_minutes / 60
                    print(f"⏱️  预计剩余时间: {hours:.1f} 小时")
            
            print()
            print("💡 提示: 按 Ctrl+C 退出监控")
            print("📁 结果保存在: datatrain/*/annotation/ 目录下")
            
            # 检查是否完成
            if processed_files >= total_files:
                print()
                print("🎉 批量处理已完成!")
                
                # 显示完整统计
                print("\n📊 最终统计:")
                print(f"  处理文件: {processed_files}/{total_files}")
                print(f"  标注文章: {total_articles}")
                print(f"  识别实体: {total_entities}")
                print(f"  提取关系: {total_relations}")
                
                if relation_types:
                    print("  关系类型:")
                    for rel_type, count in sorted(relation_types.items()):
                        print(f"    - {rel_type}: {count}")
                
                break
            
            # 等待30秒后刷新
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n👋 监控已退出")
            print(f"\n📊 当前进度: {processed_files}/{total_files} ({progress_percent:.1f}%)")
            break
        except Exception as e:
            print(f"\n❌ 监控出错: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_progress() 