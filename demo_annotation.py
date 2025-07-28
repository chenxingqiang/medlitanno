#!/usr/bin/env python3
"""
医学文献标注系统演示脚本
Demo script for medical literature annotation system
"""

from auto_annotation_system import MedicalAnnotationLLM
import os
import json

def demo_annotation():
    """演示标注功能"""

    print("=== 医学文献自动标注系统演示 ===")
    print("Medical Literature Auto-Annotation System Demo")
    print("使用模型: DeepSeek & Qianwen")
    print()

    # 配置 - 使用您提供的API密钥
    DEEPSEEK_API_KEY = "sk-d02fca54e07f4bdfb1778aeb62ae7671"
    QIANWEN_API_KEY = "sk-296434b603504719b9f5aca8286f5166"

    # 测试文件路径
    test_file = "datatrain/bacteria-ids-4937/A/Acute motor axonal neuropathy.xlsx"

    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return

    print(f"📁 测试文件: {test_file}")
    print()

    # 选择演示模型
    print("选择演示模型:")
    print("1. DeepSeek")
    print("2. Qianwen")
    print("3. 两个模型都演示")

    choice = input("请输入选择 (1/2/3): ").strip()

    if choice == "1":
        demo_configs = [("deepseek", "deepseek-chat", DEEPSEEK_API_KEY)]
    elif choice == "2":
        demo_configs = [("qianwen", "qwen-plus", QIANWEN_API_KEY)]
    elif choice == "3":
        demo_configs = [
            ("deepseek", "deepseek-chat", DEEPSEEK_API_KEY),
            ("qianwen", "qwen-plus", QIANWEN_API_KEY)
        ]
    else:
        print("❌ 无效选择")
        return

    # 演示每个模型
    for model_type, model_name, api_key in demo_configs:
        print(f"\n=== 使用 {model_type.upper()} 模型演示 ===")

        try:
            # 创建标注器
            print(f"🚀 初始化 {model_type.upper()} 标注器...")
            annotator = MedicalAnnotationLLM(
                api_key=api_key,
                model=model_name,
                model_type=model_type
            )

            # 进行标注
            print("📝 开始标注...")
            output_file = f"demo_output_{model_type}.json"
            results = annotator.annotate_excel_file(test_file, output_file)

            # 生成统计
            stats = annotator.generate_statistics(results)

            print(f"\n📊 {model_type.upper()} 标注结果统计:")
            print(f"  模型: {stats['model_info']['model_name']}")
            print(f"  总文章数: {stats['total_articles']}")
            print(f"  有实体的文章: {stats['articles_with_entities']}")
            print(f"  有关系的文章: {stats['articles_with_relations']}")
            print(f"  总细菌实体: {stats['total_bacteria']}")
            print(f"  总疾病实体: {stats['total_diseases']}")
            print(f"  总关系数: {stats['total_relations']}")
            print(f"  关系类型分布:")
            for rel_type, count in stats['relation_types'].items():
                print(f"    - {rel_type}: {count}")

            # 显示示例结果
            print(f"\n📋 {model_type.upper()} 标注示例:")
            example_count = 0
            for result in results:
                if result.relations and example_count < 2:  # 显示前2个有关系的例子
                    print(f"\n  📄 文章 {example_count + 1} (PMID: {result.pmid}):")
                    print(f"     标题: {result.title[:80]}...")

                    for i, relation in enumerate(result.relations[:2]):  # 每篇文章显示前2个关系
                        print(f"     关系 {i+1}:")
                        print(f"       病原体: {relation.subject.text}")
                        print(f"       疾病: {relation.object.text}")
                        print(f"       关系类型: {relation.relation_type}")
                        print(f"       证据: {relation.evidence.text[:100]}...")

                    example_count += 1

            print(f"\n✅ {model_type.upper()} 演示完成!")
            print(f"完整结果已保存到: {output_file}")

        except Exception as e:
            print(f"❌ {model_type.upper()} 演示过程中出现错误: {e}")
            print("请检查:")
            print("1. API密钥是否正确")
            print("2. 网络连接是否正常")
            print("3. 账户余额是否充足")

    # 显示转换提示
    print(f"\n💡 提示: 可以使用以下命令转换为Label Studio格式:")
    print(f"python convert_to_label_studio.py -i . -o label_studio_demo")


def demo_with_sample_text():
    """使用示例文本演示标注功能"""

    print("\n=== 示例文本标注演示 ===")

    # 示例医学文本
    sample_title = "Campylobacter jejuni infection and Guillain-Barré syndrome"
    sample_abstract = """
    Campylobacter jejuni is a major cause of bacterial gastroenteritis worldwide and is strongly
    associated with the development of Guillain-Barré syndrome (GBS), an acute inflammatory
    demyelinating polyneuropathy. The pathogenesis involves molecular mimicry between
    C. jejuni lipooligosaccharides and human gangliosides, leading to cross-reactive
    antibodies that target peripheral nerve components. Studies have shown that patients
    with GBS often have elevated antibodies against GM1 ganglioside following C. jejuni
    infection. This bacterial infection triggers an autoimmune response that results in
    peripheral nerve damage and the characteristic clinical features of GBS.
    """

    DEEPSEEK_API_KEY = "sk-d02fca54e07f4bdfb1778aeb62ae7671"
    QIANWEN_API_KEY = "sk-296434b603504719b9f5aca8286f5166"

    # 选择模型
    print("选择测试模型:")
    print("1. DeepSeek")
    print("2. Qianwen")
    print("3. 两个都测试")

    choice = input("请输入选择 (1/2/3): ").strip()

    if choice == "1":
        test_configs = [("deepseek", "deepseek-chat", DEEPSEEK_API_KEY)]
    elif choice == "2":
        test_configs = [("qianwen", "qwen-plus", QIANWEN_API_KEY)]
    elif choice == "3":
        test_configs = [
            ("deepseek", "deepseek-chat", DEEPSEEK_API_KEY),
            ("qianwen", "qwen-plus", QIANWEN_API_KEY)
        ]
    else:
        print("❌ 无效选择")
        return

    # 测试每个模型
    for model_type, model_name, api_key in test_configs:
        print(f"\n=== {model_type.upper()} 文本标注演示 ===")

        try:
            print(f"📝 使用 {model_type.upper()} 标注示例文本...")
            annotator = MedicalAnnotationLLM(
                api_key=api_key,
                model=model_name,
                model_type=model_type
            )

            # 标注示例文本
            result = annotator.annotate_text(sample_title, sample_abstract, "demo")

            print(f"\n📊 {model_type.upper()} 标注结果:")
            print(f"模型: {model_name}")
            print(f"实体数量: {len(result.entities)}")
            print(f"证据数量: {len(result.evidences)}")
            print(f"关系数量: {len(result.relations)}")

            print(f"\n🔍 {model_type.upper()} 识别的实体:")
            for entity in result.entities:
                print(f"  - {entity.text} ({entity.label})")

            print(f"\n🔗 {model_type.upper()} 识别的关系:")
            for relation in result.relations:
                print(f"  - {relation.subject.text} → {relation.object.text}")
                print(f"    关系类型: {relation.relation_type}")
                print(f"    证据: {relation.evidence.text[:100]}...")

        except Exception as e:
            print(f"❌ {model_type.upper()} 标注失败: {e}")


def compare_demo_results():
    """比较演示结果"""
    print("\n=== 模型结果比较 ===")

    deepseek_file = "demo_output_deepseek.json"
    qianwen_file = "demo_output_qianwen.json"

    if not (os.path.exists(deepseek_file) and os.path.exists(qianwen_file)):
        print("❌ 未找到比较所需的演示结果文件")
        print("请先运行文件演示功能并选择'两个模型都演示'")
        return

    try:
        # 读取结果
        with open(deepseek_file, 'r', encoding='utf-8') as f:
            deepseek_results = json.load(f)

        with open(qianwen_file, 'r', encoding='utf-8') as f:
            qianwen_results = json.load(f)

        print("📊 演示结果比较:")
        print(f"{'指标':<25} {'DeepSeek':<15} {'Qianwen':<15} {'差异':<10}")
        print("-" * 65)

        # 计算统计
        ds_entities = sum(len(r.get('entities', [])) for r in deepseek_results)
        ds_relations = sum(len(r.get('relations', [])) for r in deepseek_results)
        ds_articles = sum(1 for r in deepseek_results if r.get('relations', []))

        qw_entities = sum(len(r.get('entities', [])) for r in qianwen_results)
        qw_relations = sum(len(r.get('relations', [])) for r in qianwen_results)
        qw_articles = sum(1 for r in qianwen_results if r.get('relations', []))

        print(f"{'总实体数':<25} {ds_entities:<15} {qw_entities:<15} {qw_entities-ds_entities:+d}")
        print(f"{'总关系数':<25} {ds_relations:<15} {qw_relations:<15} {qw_relations-ds_relations:+d}")
        print(f"{'有关系的文章数':<25} {ds_articles:<15} {qw_articles:<15} {qw_articles-ds_articles:+d}")

        # 关系类型比较
        print(f"\n📈 关系类型分布比较:")
        relation_types = ['contributes_to', 'ameliorates', 'correlated_with', 'biomarker_for']

        for rel_type in relation_types:
            ds_count = sum(1 for r in deepseek_results
                          for rel in r.get('relations', [])
                          if rel.get('relation_type') == rel_type)
            qw_count = sum(1 for r in qianwen_results
                          for rel in r.get('relations', [])
                          if rel.get('relation_type') == rel_type)

            print(f"  {rel_type:<20}: DeepSeek {ds_count:>3}, Qianwen {qw_count:>3}")

        print(f"\n💡 结论: 可以根据实际需求和结果质量选择合适的模型")

    except Exception as e:
        print(f"❌ 比较过程中出现错误: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="医学文献标注系统演示")
    parser.add_argument("--file", action="store_true", help="演示文件标注")
    parser.add_argument("--text", action="store_true", help="演示文本标注")
    parser.add_argument("--compare", action="store_true", help="比较演示结果")

    args = parser.parse_args()

    if args.text:
        demo_with_sample_text()
    elif args.file:
        demo_annotation()
    elif args.compare:
        compare_demo_results()
    else:
        print("使用方法:")
        print("  python demo_annotation.py --file     # 演示文件标注")
        print("  python demo_annotation.py --text     # 演示文本标注")
        print("  python demo_annotation.py --compare  # 比较演示结果")
        print()
        print("Usage:")
        print("  python demo_annotation.py --file     # Demo file annotation")
        print("  python demo_annotation.py --text     # Demo text annotation")
        print("  python demo_annotation.py --compare  # Compare demo results")