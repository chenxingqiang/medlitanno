#!/usr/bin/env python3
"""
运行自动标注系统的实用脚本
Practical script for running the automated annotation system
"""

import os
import sys
from auto_annotation_system import MedicalAnnotationLLM, batch_process_directory

def main():
    """主函数"""
    
    # 配置参数 - 从环境变量获取API密钥
    CONFIG = {
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
        "QIANWEN_API_KEY": os.getenv("QIANWEN_API_KEY"), 
        "DATA_DIR": "datatrain",                # 数据目录
        "OUTPUT_DIR": "annotated_results",      # 输出目录
    }
    
    # 检查API密钥
    if not CONFIG["DEEPSEEK_API_KEY"]:
        print("❌ 请设置环境变量 DEEPSEEK_API_KEY")
        print("Please set environment variable DEEPSEEK_API_KEY")
        print("例如: export DEEPSEEK_API_KEY=your_api_key")
        return
    
    if not CONFIG["QIANWEN_API_KEY"]:
        print("❌ 请设置环境变量 QIANWEN_API_KEY")
        print("Please set environment variable QIANWEN_API_KEY")
        print("例如: export QIANWEN_API_KEY=your_api_key")
        return
    
    print("=== 医学文献自动标注系统 ===")
    print("Medical Literature Auto-Annotation System")
    print("支持模型: DeepSeek, Qianwen")
    print()
    
    # 检查数据目录
    if not os.path.exists(CONFIG["DATA_DIR"]):
        print(f"❌ 数据目录不存在: {CONFIG['DATA_DIR']}")
        print(f"Data directory not found: {CONFIG['DATA_DIR']}")
        return
    
    print(f"📁 数据目录: {CONFIG['DATA_DIR']}")
    print(f"💾 输出目录: {CONFIG['OUTPUT_DIR']}")
    print()
    
    # 统计数据文件
    total_files = 0
    for root, dirs, files in os.walk(CONFIG["DATA_DIR"]):
        for file in files:
            if file.endswith('.xlsx'):
                total_files += 1
    
    print(f"📊 发现 {total_files} 个Excel文件待处理")
    print(f"Found {total_files} Excel files to process")
    print()
    
    # 选择模型
    print("请选择要使用的模型:")
    print("1. DeepSeek (deepseek-chat)")
    print("2. DeepSeek Reasoner (deepseek-reasoner) - 推理增强版")
    print("3. Qianwen (qwen-plus)")
    print("4. 所有模型都使用")
    print()
    
    choice = input("请输入选择 (1/2/3/4): ").strip()
    
    if choice == "1":
        models_to_use = [("deepseek", "deepseek-chat", CONFIG["DEEPSEEK_API_KEY"])]
    elif choice == "2":
        models_to_use = [("deepseek-reasoner", "deepseek-reasoner", CONFIG["DEEPSEEK_API_KEY"])]
    elif choice == "3":
        models_to_use = [("qianwen", "qwen-plus", CONFIG["QIANWEN_API_KEY"])]
    elif choice == "4":
        models_to_use = [
            ("deepseek", "deepseek-chat", CONFIG["DEEPSEEK_API_KEY"]),
            ("deepseek-reasoner", "deepseek-reasoner", CONFIG["DEEPSEEK_API_KEY"]),
            ("qianwen", "qwen-plus", CONFIG["QIANWEN_API_KEY"])
        ]
    else:
        print("❌ 无效选择")
        return
    
    # 确认开始处理
    print(f"\n将使用以下模型进行处理:")
    for model_type, model_name, _ in models_to_use:
        print(f"  - {model_type.upper()}: {model_name}")
    print()
    
    response = input("是否开始处理? (y/N): ").strip().lower()
    if response not in ['y', 'yes', '是']:
        print("处理已取消")
        return
    
    print("\n🚀 开始批量处理...")
    print("Starting batch processing...")
    
    # 处理每个模型
    for model_type, model_name, api_key in models_to_use:
        print(f"\n=== 使用 {model_type.upper()} 模型处理 ===")
        
        try:
            # 执行批量处理
            batch_process_directory(
                data_dir=CONFIG["DATA_DIR"],
                api_key=api_key,
                model=model_name,
                model_type=model_type
            )
            
            print(f"✅ {model_type.upper()} 模型处理完成!")
            print(f"{model_type.upper()} model processing completed!")
            print(f"结果保存在各目录的 annotation/ 子目录下")
            print(f"Results saved in annotation/ subdirectories")
            
        except Exception as e:
            print(f"❌ {model_type.upper()} 模型处理过程中出现错误: {e}")
            print(f"Error during {model_type.upper()} processing: {e}")
    
    print("\n🎉 所有处理完成!")
    print("All processing completed!")


def test_single_file():
    """测试单个文件的标注功能"""
    
    # 配置 - 从环境变量获取API密钥
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    QIANWEN_API_KEY = os.getenv("QIANWEN_API_KEY")
    
    # 检查API密钥
    if not DEEPSEEK_API_KEY or not QIANWEN_API_KEY:
        print("❌ 请设置环境变量 DEEPSEEK_API_KEY 和 QIANWEN_API_KEY")
        print("Please set environment variables DEEPSEEK_API_KEY and QIANWEN_API_KEY")
        return
    TEST_FILE = "datatrain/bacteria-ids-4937/A/Acute motor axonal neuropathy.xlsx"
    
    if not os.path.exists(TEST_FILE):
        print(f"❌ 测试文件不存在: {TEST_FILE}")
        return
    
    print("🧪 测试单个文件标注...")
    print(f"文件: {TEST_FILE}")
    print()
    
    # 选择测试模型
    print("选择测试模型:")
    print("1. DeepSeek")
    print("2. DeepSeek Reasoner (推理增强版)")
    print("3. Qianwen")
    print("4. 所有模型都测试")
    
    choice = input("请输入选择 (1/2/3/4): ").strip()
    
    if choice == "1":
        test_configs = [("deepseek", "deepseek-chat", DEEPSEEK_API_KEY)]
    elif choice == "2":
        test_configs = [("deepseek-reasoner", "deepseek-reasoner", DEEPSEEK_API_KEY)]
    elif choice == "3":
        test_configs = [("qianwen", "qwen-plus", QIANWEN_API_KEY)]
    elif choice == "4":
        test_configs = [
            ("deepseek", "deepseek-chat", DEEPSEEK_API_KEY),
            ("deepseek-reasoner", "deepseek-reasoner", DEEPSEEK_API_KEY),
            ("qianwen", "qwen-plus", QIANWEN_API_KEY)
        ]
    else:
        print("❌ 无效选择")
        return
    
    # 测试每个模型
    for model_type, model_name, api_key in test_configs:
        print(f"\n=== 测试 {model_type.upper()} 模型 ===")
        
        try:
            # 创建标注器
            annotator = MedicalAnnotationLLM(
                api_key=api_key, 
                model=model_name, 
                model_type=model_type
            )
            
            # 处理文件
            output_file = f"test_annotation_result_{model_type}.json"
            results = annotator.annotate_excel_file(TEST_FILE, output_file)
            
            # 生成统计
            stats = annotator.generate_statistics(results)
            
            print(f"\n📊 {model_type.upper()} 标注统计:")
            print(f"模型: {stats['model_info']['model_name']}")
            print(f"总文章数: {stats['total_articles']}")
            print(f"有实体的文章: {stats['articles_with_entities']}")
            print(f"有关系的文章: {stats['articles_with_relations']}")
            print(f"总细菌实体: {stats['total_bacteria']}")
            print(f"总疾病实体: {stats['total_diseases']}")
            print(f"总关系数: {stats['total_relations']}")
            print(f"关系类型分布: {stats['relation_types']}")
            
            print(f"\n✅ {model_type.upper()} 测试完成! 结果保存在: {output_file}")
            
            # 显示第一个有关系的结果示例
            for result in results:
                if result.relations:
                    print(f"\n📝 {model_type.upper()} 示例结果 (PMID: {result.pmid}):")
                    print(f"标题: {result.title[:100]}...")
                    for relation in result.relations[:2]:  # 只显示前2个关系
                        print(f"  - {relation.subject.text} -> {relation.object.text}")
                        print(f"    关系类型: {relation.relation_type}")
                        print(f"    证据: {relation.evidence.text[:100]}...")
                    break
            
        except Exception as e:
            print(f"❌ {model_type.upper()} 测试失败: {e}")


def compare_models():
    """比较不同模型的标注结果"""
    print("🔍 模型比较功能")
    print("此功能需要先运行测试或批量处理生成结果文件")
    print()
    
    # 查找结果文件
    deepseek_file = "test_annotation_result_deepseek.json"
    qianwen_file = "test_annotation_result_qianwen.json"
    
    if not (os.path.exists(deepseek_file) and os.path.exists(qianwen_file)):
        print("❌ 未找到比较所需的结果文件")
        print("请先运行: python run_annotation.py --test")
        return
    
    try:
        import json
        
        # 读取结果
        with open(deepseek_file, 'r', encoding='utf-8') as f:
            deepseek_results = json.load(f)
        
        with open(qianwen_file, 'r', encoding='utf-8') as f:
            qianwen_results = json.load(f)
        
        print("📊 模型比较结果:")
        print(f"{'指标':<20} {'DeepSeek':<15} {'Qianwen':<15}")
        print("-" * 50)
        
        # 计算基本统计
        for model_name, results in [("DeepSeek", deepseek_results), ("Qianwen", qianwen_results)]:
            total_entities = sum(len(r.get('entities', [])) for r in results)
            total_relations = sum(len(r.get('relations', [])) for r in results)
            articles_with_relations = sum(1 for r in results if r.get('relations', []))
            
            if model_name == "DeepSeek":
                ds_entities, ds_relations, ds_articles = total_entities, total_relations, articles_with_relations
            else:
                qw_entities, qw_relations, qw_articles = total_entities, total_relations, articles_with_relations
        
        print(f"{'总实体数':<20} {ds_entities:<15} {qw_entities:<15}")
        print(f"{'总关系数':<20} {ds_relations:<15} {qw_relations:<15}")
        print(f"{'有关系的文章数':<20} {ds_articles:<15} {qw_articles:<15}")
        
        print(f"\n💡 建议: 可以根据实际需求选择表现更好的模型")
        
    except Exception as e:
        print(f"❌ 比较过程中出现错误: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="医学文献自动标注系统")
    parser.add_argument("--test", action="store_true", help="运行单文件测试")
    parser.add_argument("--batch", action="store_true", help="批量处理所有文件")
    parser.add_argument("--compare", action="store_true", help="比较不同模型结果")
    
    args = parser.parse_args()
    
    if args.test:
        test_single_file()
    elif args.batch:
        main()
    elif args.compare:
        compare_models()
    else:
        print("使用方法:")
        print("  python run_annotation.py --test     # 测试单个文件")
        print("  python run_annotation.py --batch    # 批量处理所有文件")
        print("  python run_annotation.py --compare  # 比较模型结果")
        print()
        print("Usage:")
        print("  python run_annotation.py --test     # Test single file")
        print("  python run_annotation.py --batch    # Batch process all files")
        print("  python run_annotation.py --compare  # Compare model results") 