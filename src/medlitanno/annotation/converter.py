#!/usr/bin/env python3
"""
Format conversion utilities for medical literature annotation
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

from .core import AnnotationResult


class LabelStudioConverter:
    """Convert annotation results to Label Studio format"""
    
    def __init__(self):
        """Initialize converter"""
        pass
    
    def convert_annotation_result(self, result: AnnotationResult, task_id: int = 0) -> Dict[str, Any]:
        """
        Convert single annotation result to Label Studio format
        
        Args:
            result: Annotation result
            task_id: Task ID for Label Studio
            
        Returns:
            Dict[str, Any]: Label Studio format data
        """
        # Combine title and abstract
        full_text = f"{result.title}\n\n{result.abstract}"
        
        # Build Label Studio task
        task_data = {
            "id": task_id,
            "data": {
                "text": full_text,
                "pmid": result.pmid,
                "title": result.title,
                "abstract": result.abstract
            },
            "annotations": []
        }
        
        # Add annotations if they exist
        if result.entities or result.relations:
            annotation_result = {
                "id": task_id,
                "created_username": "llm_annotator",
                "created_ago": "0 minutes",
                "task": task_id,
                "result": []
            }
            
            # Convert entities
            for i, entity in enumerate(result.entities):
                entity_annotation = {
                    "value": {
                        "start": entity.start_pos,
                        "end": entity.end_pos,
                        "text": entity.text,
                        "labels": [entity.label]
                    },
                    "id": f"entity_{i}",
                    "from_name": "label",
                    "to_name": "text",
                    "type": "labels"
                }
                annotation_result['result'].append(entity_annotation)
            
            # Convert evidences
            for i, evidence in enumerate(result.evidences):
                evidence_annotation = {
                    "value": {
                        "start": evidence.start_pos,
                        "end": evidence.end_pos,
                        "text": evidence.text,
                        "labels": ["Evidence"]
                    },
                    "id": f"evidence_{i}",
                    "from_name": "evidence_label",
                    "to_name": "text",
                    "type": "labels"
                }
                annotation_result['result'].append(evidence_annotation)
            
            # Convert relations
            for i, relation in enumerate(result.relations):
                relation_annotation = {
                    "value": {
                        "labels": [relation.relation_type]
                    },
                    "id": f"relation_{i}",
                    "from_name": "relation",
                    "to_name": "text",
                    "type": "relation",
                    "meta": {
                        "subject": relation.subject.text,
                        "object": relation.object.text,
                        "evidence": relation.evidence.text
                    }
                }
                annotation_result['result'].append(relation_annotation)
            
            task_data['annotations'].append(annotation_result)
        
        return task_data
    
    def convert_results_list(self, results: List[AnnotationResult]) -> List[Dict[str, Any]]:
        """
        Convert list of annotation results to Label Studio format
        
        Args:
            results: List of annotation results
            
        Returns:
            List[Dict[str, Any]]: Label Studio format data
        """
        label_studio_data = []
        
        for i, result in enumerate(results):
            task_data = self.convert_annotation_result(result, task_id=i)
            label_studio_data.append(task_data)
        
        return label_studio_data
    
    def create_label_config(self) -> Dict[str, Any]:
        """
        Create Label Studio configuration
        
        Returns:
            Dict[str, Any]: Label Studio configuration
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
    
    def save_label_studio_data(self, 
                              results: List[AnnotationResult], 
                              output_file: str,
                              include_config: bool = True) -> None:
        """
        Save annotation results as Label Studio format
        
        Args:
            results: List of annotation results
            output_file: Output file path
            include_config: Whether to include Label Studio config
        """
        # Convert to Label Studio format
        label_studio_data = self.convert_results_list(results)
        
        # Create output directory
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(label_studio_data, f, ensure_ascii=False, indent=2)
        
        # Save config if requested
        if include_config:
            config_file = output_path.with_name(f"{output_path.stem}_config.json")
            config = self.create_label_config()
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"Label Studio config saved to: {config_file}")
        
        print(f"Label Studio data saved to: {output_file}")


class CSVConverter:
    """Convert annotation results to CSV format"""
    
    def __init__(self):
        """Initialize converter"""
        pass
    
    def convert_to_csv(self, results: List[AnnotationResult], output_file: str) -> None:
        """
        Convert annotation results to CSV format
        
        Args:
            results: List of annotation results
            output_file: Output CSV file path
        """
        import pandas as pd
        
        # Flatten results into rows
        rows = []
        
        for result in results:
            base_row = {
                'pmid': result.pmid,
                'title': result.title,
                'abstract': result.abstract,
                'total_entities': len(result.entities),
                'total_relations': len(result.relations),
                'total_evidences': len(result.evidences)
            }
            
            # Add entity information
            bacteria_entities = [e.text for e in result.entities if e.label == 'Bacteria']
            disease_entities = [e.text for e in result.entities if e.label == 'Disease']
            
            base_row['bacteria_entities'] = '; '.join(bacteria_entities)
            base_row['disease_entities'] = '; '.join(disease_entities)
            
            # Add relation information
            relation_types = [r.relation_type for r in result.relations]
            relation_pairs = [f"{r.subject.text} -> {r.object.text}" for r in result.relations]
            
            base_row['relation_types'] = '; '.join(relation_types)
            base_row['relation_pairs'] = '; '.join(relation_pairs)
            
            rows.append(base_row)
        
        # Create DataFrame and save
        df = pd.DataFrame(rows)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"CSV data saved to: {output_file}")


class SummaryGenerator:
    """Generate summary reports from annotation results"""
    
    def __init__(self):
        """Initialize summary generator"""
        pass
    
    def generate_summary(self, results: List[AnnotationResult]) -> Dict[str, Any]:
        """
        Generate comprehensive summary
        
        Args:
            results: List of annotation results
            
        Returns:
            Dict[str, Any]: Summary statistics
        """
        total_articles = len(results)
        articles_with_entities = sum(1 for r in results if r.entities)
        articles_with_relations = sum(1 for r in results if r.relations)
        
        total_entities = sum(len(r.entities) for r in results)
        total_bacteria = sum(len([e for e in r.entities if e.label == 'Bacteria']) for r in results)
        total_diseases = sum(len([e for e in r.entities if e.label == 'Disease']) for r in results)
        
        total_relations = sum(len(r.relations) for r in results)
        relation_types = {}
        
        for result in results:
            for relation in result.relations:
                rel_type = relation.relation_type
                relation_types[rel_type] = relation_types.get(rel_type, 0) + 1
        
        return {
            'total_articles': total_articles,
            'articles_with_entities': articles_with_entities,
            'articles_with_relations': articles_with_relations,
            'entity_coverage': (articles_with_entities / total_articles * 100) if total_articles > 0 else 0,
            'relation_coverage': (articles_with_relations / total_articles * 100) if total_articles > 0 else 0,
            'total_entities': total_entities,
            'total_bacteria': total_bacteria,
            'total_diseases': total_diseases,
            'total_relations': total_relations,
            'relation_types': relation_types,
            'avg_entities_per_article': total_entities / total_articles if total_articles > 0 else 0,
            'avg_relations_per_article': total_relations / total_articles if total_articles > 0 else 0
        }
    
    def save_summary_report(self, results: List[AnnotationResult], output_file: str) -> None:
        """
        Save summary report
        
        Args:
            results: List of annotation results
            output_file: Output file path
        """
        summary = self.generate_summary(results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"Summary report saved to: {output_file}")


# Convenience functions
def convert_to_label_studio(results: List[AnnotationResult], 
                           output_file: str,
                           include_config: bool = True) -> None:
    """
    Convert annotation results to Label Studio format (convenience function)
    
    Args:
        results: List of annotation results
        output_file: Output file path
        include_config: Whether to include Label Studio config
    """
    converter = LabelStudioConverter()
    converter.save_label_studio_data(results, output_file, include_config)


def convert_to_csv(results: List[AnnotationResult], output_file: str) -> None:
    """
    Convert annotation results to CSV format (convenience function)
    
    Args:
        results: List of annotation results
        output_file: Output CSV file path
    """
    converter = CSVConverter()
    converter.convert_to_csv(results, output_file)


def generate_summary_report(results: List[AnnotationResult], output_file: str) -> None:
    """
    Generate summary report (convenience function)
    
    Args:
        results: List of annotation results
        output_file: Output file path
    """
    generator = SummaryGenerator()
    generator.save_summary_report(results, output_file) 