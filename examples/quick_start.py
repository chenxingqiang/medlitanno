#!/usr/bin/env python3
"""
医学文献自动标注系统 - 快速开始示例
Medical Literature Auto-Annotation System - Quick Start Example

这个示例展示如何使用系统进行基本的标注任务。
This example shows how to use the system for basic annotation tasks.
"""

import os
import sys
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from annotation.auto_annotation_system import MedicalAnnotationLLM

def main():
    print("🚀 医学文献自动标注系统 - 快速开始")
    print("🚀 Medical Literature Auto-Annotation System - Quick Start")
    print()
    
    # 检查环境变量
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 请设置环境变量 DEEPSEEK_API_KEY")
        print("❌ Please set environment variable DEEPSEEK_API_KEY")
        return
    
    # 示例文本
    sample_title = "Association between Helicobacter pylori infection and autoimmune gastritis"
    sample_abstract = """
    Background: Helicobacter pylori infection has been associated with various autoimmune diseases.
    This study investigates the relationship between H. pylori and autoimmune gastritis.
    
    Methods: We analyzed 200 patients with autoimmune gastritis and 200 healthy controls.
    H. pylori infection was detected using serology and histology.
    
    Results: H. pylori infection was found in 65% of patients with autoimmune gastritis 
    compared to 35% in controls (p<0.001). The bacteria showed a significant correlation 
    with disease severity and contributed to inflammatory responses.
    
    Conclusion: H. pylori infection contributes to the development of autoimmune gastritis 
    and may serve as a biomarker for disease progression.
    """
    
    print("📝 示例文本:")
    print(f"标题: {sample_title}")
    print(f"摘要: {sample_abstract[:200]}...")
    print()
    
    # 创建标注器
    print("🔧 初始化标注器...")
    annotator = MedicalAnnotationLLM(
        api_key=api_key,
        model="deepseek-chat",
        model_type="deepseek"
    )
    
    # 执行标注
    print("🧠 开始标注...")
    try:
        result = annotator.annotate_text(
            title=sample_title,
            abstract=sample_abstract,
            pmid="example_001"
        )
        
        print("✅ 标注完成!")
        print()
        
        # 显示结果
        print("📊 标注结果:")
        print(f"实体数量: {len(result.entities)}")
        print(f"关系数量: {len(result.relations)}")
        print(f"证据数量: {len(result.evidences)}")
        print()
        
        print("🦠 识别的实体:")
        for entity in result.entities:
            print(f"  - {entity.text} ({entity.label})")
        print()
        
        print("🔗 识别的关系:")
        for relation in result.relations:
            print(f"  - {relation.subject} --{relation.relation_type}--> {relation.object}")
        print()
        
        print("📝 支持证据:")
        for evidence in result.evidences:
            print(f"  - {evidence.text[:100]}...")
        print()
        
        # 保存结果
        output_file = "examples/quick_start_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"💾 结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"❌ 标注失败: {e}")
        return
    
    print()
    print("🎉 快速开始示例完成!")
    print("🎉 Quick start example completed!")
    print()
    print("📖 下一步:")
    print("  - 查看完整文档: docs/SETUP.md")
    print("  - 运行批量处理: python3 src/annotation/run_annotation.py")
    print("  - 监控处理进度: scripts/monitor.sh")

if __name__ == "__main__":
    main() 