#!/usr/bin/env python3
"""
LLM-based Automated Annotation System for Medical Literature
自动化医学文献标注系统

This system replaces manual annotation in Label Studio with LLM-powered automation
for identifying bacteria-disease relationships in medical abstracts.
"""

import pandas as pd
import json
import os
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import requests
from openai import OpenAI


@dataclass
class Entity:
    """实体类"""
    text: str
    label: str  # 'Bacteria' or 'Disease'
    start_pos: int
    end_pos: int


@dataclass
class Evidence:
    """证据类"""
    text: str
    start_pos: int
    end_pos: int
    relation_type: str  # 'contributes_to', 'ameliorates', 'correlated_with', 'biomarker_for'


@dataclass
class Relation:
    """关系类"""
    subject: Entity  # Bacteria
    object: Entity   # Disease
    evidence: Evidence
    relation_type: str


@dataclass
class AnnotationResult:
    """标注结果"""
    pmid: str
    title: str
    abstract: str
    entities: List[Entity]
    evidences: List[Evidence]
    relations: List[Relation]


class MedicalAnnotationLLM:
    """医学文献自动标注系统"""

    def __init__(self, api_key: str, model: str = "gpt-4o", model_type: str = "openai", base_url: str = None):
        """
        初始化LLM标注系统

        Args:
            api_key: API密钥
            model: 使用的模型名称
            model_type: 模型类型 ('openai', 'deepseek', 'qianwen')
            base_url: API基础URL（可选）
        """
        self.api_key = api_key
        self.model = model
        self.model_type = model_type.lower()

        # 根据模型类型设置客户端和配置
        if self.model_type == "openai":
            self.client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
        elif self.model_type == "deepseek":
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1"
            )
            if model == "gpt-4o":  # 如果没有指定DeepSeek模型，使用默认的
                self.model = "deepseek-chat"
        elif self.model_type == "deepseek-reasoner":
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1"
            )
            # 使用推理模型，特别适合从摘要中进行复杂推理
            if model in ["gpt-4o", "deepseek-chat"]:
                self.model = "deepseek-reasoner"
        elif self.model_type == "qianwen":
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            if model == "gpt-4o":  # 如果没有指定Qianwen模型，使用默认的
                self.model = "qwen-plus"
        else:
            raise ValueError(f"不支持的模型类型: {model_type}. 支持的类型: openai, deepseek, deepseek-reasoner, qianwen")

        # 标注提示词模板 - 针对不同模型优化
        if self.model_type == "deepseek-reasoner":
            # 为推理模型优化的提示词，强调逻辑推理和深度分析
            self.annotation_prompt = """
你是一个专业的医学文献标注专家，具有强大的逻辑推理能力。请深度分析以下医学摘要，运用你的推理能力从有限的信息中推断出隐含的关系。

**分析任务：**
从医学摘要中推理并标注病原微生物与自身免疫性疾病的关系。

**推理步骤：**

**第一步：深度实体识别与推理**
1. Bacteria（病原微生物）：不仅识别明确提到的，还要推理可能相关的病原体
   - 细菌、病毒、寄生虫、真菌等
   - 注意隐含提及的病原体（如"感染"、"病原体"等）
2. Disease（自身免疫性疾病）：识别所有相关的自身免疫性疾病
   - 包括疾病的不同表现形式和阶段

**第二步：证据深度挖掘与关系推理**
基于摘要内容，深度推理病原微生物与疾病的关系类型：
- contributes_to（致病作用）：通过分子模拟、免疫激活、交叉反应等机制导致疾病
- ameliorates（保护作用）：通过免疫调节、竞争抑制等机制保护宿主
- correlated_with（流行病学关联）：统计学相关但机制不明确
- biomarker_for（诊断价值）：可用于疾病诊断、预后或分层

**第三步：逻辑关系构建**
运用医学知识和逻辑推理，将实体与证据精确关联。

**推理要点：**
- 考虑分子机制（如分子模拟、交叉反应）
- 分析免疫学过程（如Th1/Th2平衡、调节性T细胞）
- 评估时间关系（感染先于疾病发生）
- 考虑剂量效应关系

**待分析文本：**
Title: {title}
Abstract: {abstract}

{{
    "entities": [
        {{
            "text": "实体文本",
            "label": "Bacteria/Disease",
            "start_pos": 起始位置,
            "end_pos": 结束位置
        }}
    ],
    "evidences": [
        {{
            "text": "证据句子",
            "start_pos": 起始位置,
            "end_pos": 结束位置,
            "relation_type": "contributes_to/ameliorates/correlated_with/biomarker_for"
        }}
    ],
    "relations": [
        {{
            "subject_text": "病原体实体文本",
            "object_text": "疾病实体文本",
            "evidence_text": "证据句子",
            "relation_type": "关系类型"
        }}
    ]
}}

请运用你的推理能力深度分析，确保输出的JSON格式正确。如果没有找到相关实体或关系，请返回空数组。
"""
        else:
            # 为其他模型使用标准提示词
            self.annotation_prompt = """
你是一个专业的医学文献标注专家。请仔细分析以下医学摘要，按照以下三个步骤进行标注：

**第一步：实体识别**
识别文本中的两类实体：
1. Bacteria（致病菌）：包括细菌、病毒、寄生虫、真菌等病原微生物
2. Disease（自身免疫性疾病）：包括各种自身免疫性疾病

**第二步：证据识别**
找到描述病原微生物与疾病关系的完整句子，并判断关系类型：
- contributes_to（负面影响）：病原体导致、触发、加剧、促进了疾病
- ameliorates（正面影响）：病原体改善、缓解、抑制、治疗了疾病
- correlated_with（统计关联）：只描述了病原体与疾病的相关性，未明确因果关系
- biomarker_for（应用功能）：病原体可作为疾病诊断、预测或分型的生物标志物

**第三步：关系构建**
将识别的实体和证据关联起来。

**待标注文本：**
Title: {title}
Abstract: {abstract}

**输出格式（严格按照JSON格式）：**
{{
    "entities": [
        {{
            "text": "实体文本",
            "label": "Bacteria/Disease",
            "start_pos": 起始位置,
            "end_pos": 结束位置
        }}
    ],
    "evidences": [
        {{
            "text": "证据句子",
            "start_pos": 起始位置,
            "end_pos": 结束位置,
            "relation_type": "contributes_to/ameliorates/correlated_with/biomarker_for"
        }}
    ],
    "relations": [
        {{
            "subject_text": "病原体实体文本",
            "object_text": "疾病实体文本",
            "evidence_text": "证据句子",
            "relation_type": "关系类型"
        }}
    ]
}}

请确保输出的JSON格式正确，位置信息准确。如果没有找到相关实体或关系，请返回空数组。
"""

    def _call_llm(self, messages: List[Dict]) -> str:
        """
        调用LLM API

        Args:
            messages: 对话消息列表

        Returns:
            str: LLM响应内容
        """
        try:
            if self.model_type in ["openai", "deepseek", "deepseek-reasoner", "qianwen"]:
                # 为deepseek-reasoner调整参数以获得更好的推理效果
                if self.model_type == "deepseek-reasoner":
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.2,  # 稍高的温度以促进创造性推理
                        max_tokens=3000,  # 更多token以支持复杂推理
                        top_p=0.9
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.1,  # 降低随机性，提高一致性
                        max_tokens=2000
                    )
                return response.choices[0].message.content.strip()
            else:
                raise ValueError(f"不支持的模型类型: {self.model_type}")

        except Exception as e:
            raise Exception(f"LLM API调用失败: {e}")

    def annotate_text(self, title: str, abstract: str, pmid: str = "") -> AnnotationResult:
        """
        对单篇文献进行自动标注

        Args:
            title: 文章标题
            abstract: 文章摘要
            pmid: PubMed ID

        Returns:
            AnnotationResult: 标注结果
        """
        # 合并标题和摘要作为完整文本
        full_text = f"{title}\n{abstract}"

        # 构建提示词
        prompt = self.annotation_prompt.format(title=title, abstract=abstract)

        # 构建消息
        messages = [
            {"role": "system", "content": "你是一个专业的医学文献标注专家，专门识别病原微生物与自身免疫性疾病之间的关系。"},
            {"role": "user", "content": prompt}
        ]

        try:
            # 调用LLM进行标注
            llm_output = self._call_llm(messages)

            # 提取JSON部分
            json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
            if not json_match:
                print(f"Warning: No JSON found in LLM response for PMID {pmid}")
                return self._create_empty_result(pmid, title, abstract)

            try:
                annotation_data = json.loads(json_match.group())
            except json.JSONDecodeError as e:
                print(f"Warning: JSON parsing error for PMID {pmid}: {e}")
                return self._create_empty_result(pmid, title, abstract)

            # 转换为结构化数据
            return self._parse_annotation_data(annotation_data, pmid, title, abstract, full_text)

        except Exception as e:
            print(f"Error annotating PMID {pmid}: {e}")
            return self._create_empty_result(pmid, title, abstract)

    def _create_empty_result(self, pmid: str, title: str, abstract: str) -> AnnotationResult:
        """创建空的标注结果"""
        return AnnotationResult(
            pmid=pmid,
            title=title,
            abstract=abstract,
            entities=[],
            evidences=[],
            relations=[]
        )

    def _parse_annotation_data(self, data: Dict, pmid: str, title: str, abstract: str, full_text: str) -> AnnotationResult:
        """解析LLM返回的标注数据"""
        entities = []
        evidences = []
        relations = []

        # 解析实体
        for entity_data in data.get('entities', []):
            entity = Entity(
                text=entity_data['text'],
                label=entity_data['label'],
                start_pos=entity_data.get('start_pos', 0),
                end_pos=entity_data.get('end_pos', 0)
            )
            entities.append(entity)

        # 解析证据
        for evidence_data in data.get('evidences', []):
            evidence = Evidence(
                text=evidence_data['text'],
                start_pos=evidence_data.get('start_pos', 0),
                end_pos=evidence_data.get('end_pos', 0),
                relation_type=evidence_data['relation_type']
            )
            evidences.append(evidence)

        # 解析关系
        for relation_data in data.get('relations', []):
            # 查找对应的实体
            subject_entity = None
            object_entity = None
            evidence_obj = None

            for entity in entities:
                if entity.text == relation_data['subject_text'] and entity.label == 'Bacteria':
                    subject_entity = entity
                elif entity.text == relation_data['object_text'] and entity.label == 'Disease':
                    object_entity = entity

            for evidence in evidences:
                if evidence.text == relation_data['evidence_text']:
                    evidence_obj = evidence
                    break

            if subject_entity and object_entity and evidence_obj:
                relation = Relation(
                    subject=subject_entity,
                    object=object_entity,
                    evidence=evidence_obj,
                    relation_type=relation_data['relation_type']
                )
                relations.append(relation)

        return AnnotationResult(
            pmid=pmid,
            title=title,
            abstract=abstract,
            entities=entities,
            evidences=evidences,
            relations=relations
        )

    def annotate_excel_file(self, excel_path: str, output_path: str = None) -> List[AnnotationResult]:
        """
        对Excel文件中的所有文献进行批量标注

        Args:
            excel_path: Excel文件路径
            output_path: 输出文件路径（可选）

        Returns:
            List[AnnotationResult]: 所有文献的标注结果
        """
        # 读取Excel文件
        df = pd.read_excel(excel_path)
        results = []

        print(f"Processing {len(df)} articles from {excel_path} using {self.model_type.upper()} {self.model}")

        for idx, row in df.iterrows():
            pmid = str(row.get('pmid', ''))
            title = str(row.get('title', ''))
            abstract = str(row.get('abstract', ''))

            print(f"Processing {idx+1}/{len(df)}: PMID {pmid}")

            # 进行标注
            result = self.annotate_text(title, abstract, pmid)
            results.append(result)

        # 保存结果
        if output_path:
            self.save_results(results, output_path)

        return results

    def save_results(self, results: List[AnnotationResult], output_path: str):
        """保存标注结果到JSON文件"""
        output_data = []

        for result in results:
            result_dict = {
                'pmid': result.pmid,
                'title': result.title,
                'abstract': result.abstract,
                'model_info': {
                    'model_type': self.model_type,
                    'model_name': self.model
                },
                'entities': [
                    {
                        'text': entity.text,
                        'label': entity.label,
                        'start_pos': entity.start_pos,
                        'end_pos': entity.end_pos
                    }
                    for entity in result.entities
                ],
                'evidences': [
                    {
                        'text': evidence.text,
                        'start_pos': evidence.start_pos,
                        'end_pos': evidence.end_pos,
                        'relation_type': evidence.relation_type
                    }
                    for evidence in result.evidences
                ],
                'relations': [
                    {
                        'subject_text': relation.subject.text,
                        'subject_label': relation.subject.label,
                        'object_text': relation.object.text,
                        'object_label': relation.object.label,
                        'evidence_text': relation.evidence.text,
                        'relation_type': relation.relation_type
                    }
                    for relation in result.relations
                ]
            }
            output_data.append(result_dict)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"Results saved to {output_path}")

    def generate_statistics(self, results: List[AnnotationResult]) -> Dict:
        """生成标注统计信息"""
        stats = {
            'model_info': {
                'model_type': self.model_type,
                'model_name': self.model
            },
            'total_articles': len(results),
            'articles_with_entities': 0,
            'articles_with_relations': 0,
            'total_bacteria': 0,
            'total_diseases': 0,
            'total_relations': 0,
            'relation_types': {
                'contributes_to': 0,
                'ameliorates': 0,
                'correlated_with': 0,
                'biomarker_for': 0
            }
        }

        for result in results:
            if result.entities:
                stats['articles_with_entities'] += 1
            if result.relations:
                stats['articles_with_relations'] += 1

            for entity in result.entities:
                if entity.label == 'Bacteria':
                    stats['total_bacteria'] += 1
                elif entity.label == 'Disease':
                    stats['total_diseases'] += 1

            stats['total_relations'] += len(result.relations)

            for relation in result.relations:
                if relation.relation_type in stats['relation_types']:
                    stats['relation_types'][relation.relation_type] += 1

        return stats


def batch_process_directory(data_dir: str, output_dir: str = None, api_key: str = None, model: str = "deepseek-chat", model_type: str = "deepseek"):
    """
    批量处理目录中的所有Excel文件

    Args:
        data_dir: 数据目录路径
        output_dir: 输出目录路径 (已弃用，现在保存在各自目录的annotation子目录下)
        api_key: API密钥
        model: 模型名称
        model_type: 模型类型
    """
    if api_key is None:
        raise ValueError("API key is required")

    # 初始化标注器
    annotator = MedicalAnnotationLLM(api_key=api_key, model=model, model_type=model_type)

    # 遍历所有Excel文件
    excel_files = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.xlsx'):
                excel_files.append(os.path.join(root, file))

    print(f"📊 发现 {len(excel_files)} 个Excel文件待处理")
    print(f"Found {len(excel_files)} Excel files to process")
    print()

    for file_path in excel_files:
        try:
            print(f"=== Processing {file_path} ===")

            # 创建对应的annotation目录
            # 例如: datatrain/bacteria-ids-4937/A/Achalasia.xlsx
            # 变成: datatrain/bacteria-ids-4937/A/annotation/
            dir_path = os.path.dirname(file_path)
            annotation_dir = os.path.join(dir_path, "annotation")
            os.makedirs(annotation_dir, exist_ok=True)

            # 生成输出文件名
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = os.path.join(annotation_dir, f"{base_name}_annotated_{model_type}.json")
            stats_file = os.path.join(annotation_dir, f"{base_name}_stats_{model_type}.json")

            # 检查是否已经处理过
            if os.path.exists(output_file):
                print(f"⏭️  文件已处理，跳过: {output_file}")
                continue

            # 处理文件
            results = annotator.annotate_excel_file(file_path)

            if results:
                # 保存结果
                annotator.save_results(results, output_file)

                # 生成统计信息
                stats = annotator.generate_statistics(results)
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)

                print(f"Results saved to {output_file}")
                print(f"Statistics: {stats}")
                print()
            else:
                print(f"⚠️  处理失败: {file_path}")
                print()

        except Exception as e:
            print(f"❌ 处理文件出错 {file_path}: {e}")
            print()
            continue

    print("🎉 批量处理完成!")
    print("Batch processing completed!")


if __name__ == "__main__":
    # 示例用法
    DEEPSEEK_API_KEY = "sk-d02fca54e07f4bdfb1778aeb62ae7671"
    QIANWEN_API_KEY = "sk-296434b603504719b9f5aca8286f5166"

    DATA_DIR = "datatrain"
    OUTPUT_DIR = "annotated_results"

    # 使用DeepSeek批量处理
    print("=== 使用 DeepSeek 模型 ===")
    batch_process_directory(DATA_DIR, api_key=DEEPSEEK_API_KEY, model="deepseek-chat", model_type="deepseek")

    # 使用Qianwen批量处理
    print("\n=== 使用 Qianwen 模型 ===")
    batch_process_directory(DATA_DIR, api_key=QIANWEN_API_KEY, model="qwen-plus", model_type="qianwen")