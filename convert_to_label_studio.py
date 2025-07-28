#!/usr/bin/env python3
"""
将LLM标注结果转换为Label Studio格式
Convert LLM annotation results to Label Studio format
"""

import json
import os
from typing import Dict, List, Any
from pathlib import Path


def convert_to_label_studio_format(annotation_file: str, output_file: str = None) -> List[Dict]:
    """
    将自动标注结果转换为Label Studio格式
    
    Args:
        annotation_file: 标注结果JSON文件路径
        output_file: 输出文件路径（可选）
        
    Returns:
        List[Dict]: Label Studio格式的数据
    """
    
    # 读取标注结果
    with open(annotation_file, 'r', encoding='utf-8') as f:
        annotations = json.load(f)
    
    label_studio_data = []
    
    for idx, annotation in enumerate(annotations):
        pmid = annotation['pmid']
        title = annotation['title']
        abstract = annotation['abstract']
        
        # 合并标题和摘要
        full_text = f"{title}\n\n{abstract}"
        
        # 构建Label Studio任务数据
        task_data = {
            "id": idx,
            "data": {
                "text": full_text,
                "pmid": pmid,
                "title": title,
                "abstract": abstract
            },
            "annotations": []
        }
        
        # 如果有标注结果，添加到annotations中
        if annotation['entities'] or annotation['relations']:
            annotation_result = {
                "id": idx,
                "created_username": "llm_annotator",
                "created_ago": "0 minutes",
                "task": idx,
                "result": []
            }
            
            # 转换实体标注
            for entity in annotation['entities']:
                entity_annotation = {
                    "value": {
                        "start": entity['start_pos'],
                        "end": entity['end_pos'],
                        "text": entity['text'],
                        "labels": [entity['label']]
                    },
                    "id": f"entity_{len(annotation_result['result'])}",
                    "from_name": "label",
                    "to_name": "text",
                    "type": "labels"
                }
                annotation_result['result'].append(entity_annotation)
            
            # 转换证据标注
            for evidence in annotation['evidences']:
                evidence_annotation = {
                    "value": {
                        "start": evidence['start_pos'],
                        "end": evidence['end_pos'],
                        "text": evidence['text'],
                        "labels": ["Evidence"]
                    },
                    "id": f"evidence_{len(annotation_result['result'])}",
                    "from_name": "evidence_label",
                    "to_name": "text",
                    "type": "labels"
                }
                annotation_result['result'].append(evidence_annotation)
            
            # 转换关系标注
            for relation in annotation['relations']:
                relation_annotation = {
                    "value": {
                        "labels": [relation['relation_type']]
                    },
                    "id": f"relation_{len(annotation_result['result'])}",
                    "from_name": "relation",
                    "to_name": "text",
                    "type": "relation",
                    "meta": {
                        "subject": relation['subject_text'],
                        "object": relation['object_text'],
                        "evidence": relation['evidence_text']
                    }
                }
                annotation_result['result'].append(relation_annotation)
            
            task_data['annotations'].append(annotation_result)
        
        label_studio_data.append(task_data)
    
    # 保存结果
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(label_studio_data, f, ensure_ascii=False, indent=2)
        print(f"Label Studio格式数据已保存到: {output_file}")
    
    return label_studio_data


def create_label_studio_config() -> Dict[str, Any]:
    """
    创建Label Studio配置文件
    
    Returns:
        Dict: Label Studio配置
    """
    config = {
        "type": "View",
        "children": [
            {
                "type": "Header",
                "value": "Medical Literature Annotation"
            },
            {
                "type": "Text",
                "name": "text",
                "value": "$text"
            },
            {
                "type": "Labels",
                "name": "label",
                "toName": "text",
                "choice": "multiple",
                "children": [
                    {
                        "value": "Bacteria",
                        "background": "#3498db",
                        "hotkey": "b"
                    },
                    {
                        "value": "Disease",
                        "background": "#e74c3c",
                        "hotkey": "d"
                    }
                ]
            },
            {
                "type": "Labels",
                "name": "evidence_label",
                "toName": "text",
                "choice": "multiple",
                "children": [
                    {
                        "value": "Evidence",
                        "background": "#f1c40f",
                        "hotkey": "e"
                    }
                ]
            },
            {
                "type": "Relations",
                "name": "relation",
                "toName": "text",
                "choice": "multiple",
                "children": [
                    {
                        "value": "contributes_to",
                        "background": "#ff6b6b"
                    },
                    {
                        "value": "ameliorates",
                        "background": "#4ecdc4"
                    },
                    {
                        "value": "correlated_with",
                        "background": "#45b7d1"
                    },
                    {
                        "value": "biomarker_for",
                        "background": "#96ceb4"
                    }
                ]
            }
        ]
    }
    
    return config


def batch_convert_to_label_studio(input_dir: str, output_dir: str):
    """
    批量转换标注结果为Label Studio格式
    
    Args:
        input_dir: 输入目录（包含标注结果JSON文件）
        output_dir: 输出目录
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建Label Studio配置文件
    config = create_label_studio_config()
    config_file = os.path.join(output_dir, "label_studio_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"Label Studio配置文件已保存到: {config_file}")
    
    # 转换所有标注文件
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('_annotated.json'):
                input_file = os.path.join(root, file)
                
                # 构建输出路径
                relative_path = os.path.relpath(input_file, input_dir)
                output_file = os.path.join(output_dir, relative_path.replace('_annotated.json', '_label_studio.json'))
                
                # 创建输出子目录
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                print(f"转换: {input_file} -> {output_file}")
                
                try:
                    convert_to_label_studio_format(input_file, output_file)
                except Exception as e:
                    print(f"转换失败 {input_file}: {e}")


def generate_annotation_summary(annotation_dir: str, output_file: str = "annotation_summary.json"):
    """
    生成标注结果汇总报告
    
    Args:
        annotation_dir: 标注结果目录
        output_file: 输出文件名
    """
    
    summary = {
        "total_files": 0,
        "total_articles": 0,
        "total_entities": 0,
        "total_relations": 0,
        "entity_distribution": {"Bacteria": 0, "Disease": 0},
        "relation_distribution": {
            "contributes_to": 0,
            "ameliorates": 0,
            "correlated_with": 0,
            "biomarker_for": 0
        },
        "files_with_annotations": 0,
        "coverage_rate": 0.0
    }
    
    for root, dirs, files in os.walk(annotation_dir):
        for file in files:
            if file.endswith('_annotated.json'):
                summary["total_files"] += 1
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        annotations = json.load(f)
                    
                    summary["total_articles"] += len(annotations)
                    
                    file_has_annotations = False
                    for annotation in annotations:
                        entities = annotation.get('entities', [])
                        relations = annotation.get('relations', [])
                        
                        if entities or relations:
                            file_has_annotations = True
                        
                        summary["total_entities"] += len(entities)
                        summary["total_relations"] += len(relations)
                        
                        for entity in entities:
                            label = entity.get('label', 'Unknown')
                            if label in summary["entity_distribution"]:
                                summary["entity_distribution"][label] += 1
                        
                        for relation in relations:
                            rel_type = relation.get('relation_type', 'Unknown')
                            if rel_type in summary["relation_distribution"]:
                                summary["relation_distribution"][rel_type] += 1
                    
                    if file_has_annotations:
                        summary["files_with_annotations"] += 1
                
                except Exception as e:
                    print(f"处理文件时出错 {file_path}: {e}")
    
    # 计算覆盖率
    if summary["total_files"] > 0:
        summary["coverage_rate"] = summary["files_with_annotations"] / summary["total_files"]
    
    # 保存汇总报告
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 标注汇总报告:")
    print(f"总文件数: {summary['total_files']}")
    print(f"总文章数: {summary['total_articles']}")
    print(f"总实体数: {summary['total_entities']}")
    print(f"总关系数: {summary['total_relations']}")
    print(f"有标注的文件数: {summary['files_with_annotations']}")
    print(f"标注覆盖率: {summary['coverage_rate']:.2%}")
    print(f"实体分布: {summary['entity_distribution']}")
    print(f"关系分布: {summary['relation_distribution']}")
    print(f"汇总报告已保存到: {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="转换标注结果为Label Studio格式")
    parser.add_argument("--input", "-i", required=True, help="输入目录（包含标注结果）")
    parser.add_argument("--output", "-o", required=True, help="输出目录")
    parser.add_argument("--summary", "-s", action="store_true", help="生成汇总报告")
    
    args = parser.parse_args()
    
    if args.summary:
        generate_annotation_summary(args.input)
    
    batch_convert_to_label_studio(args.input, args.output)
    print("转换完成!") 