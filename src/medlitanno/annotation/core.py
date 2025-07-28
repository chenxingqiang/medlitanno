#!/usr/bin/env python3
"""
Core annotation classes for medical literature
"""

import pandas as pd
import json
import os
import re
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

from ..common import BaseAnnotator, timer
from ..common.exceptions import AnnotationError, LLMError


@dataclass
class Entity:
    """Medical entity (Bacteria or Disease)"""
    text: str
    label: str  # 'Bacteria' or 'Disease'
    start_pos: int
    end_pos: int
    
    def __str__(self) -> str:
        return f"{self.text} ({self.label})"


@dataclass
class Evidence:
    """Evidence supporting a relation"""
    text: str
    start_pos: int
    end_pos: int
    relation_type: str  # 'contributes_to', 'ameliorates', 'correlated_with', 'biomarker_for'
    
    def __str__(self) -> str:
        return f"{self.text[:50]}... ({self.relation_type})"


@dataclass
class Relation:
    """Relation between entities"""
    subject: Entity  # Bacteria
    object: Entity   # Disease
    evidence: Evidence
    relation_type: str
    
    def __str__(self) -> str:
        return f"{self.subject.text} --{self.relation_type}--> {self.object.text}"


@dataclass
class AnnotationResult:
    """Complete annotation result for a document"""
    pmid: str
    title: str
    abstract: str
    entities: List[Entity]
    evidences: List[Evidence]
    relations: List[Relation]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format"""
        return {
            "pmid": self.pmid,
            "title": self.title,
            "abstract": self.abstract,
            "entities": [
                {
                    "text": entity.text,
                    "label": entity.label,
                    "start_pos": entity.start_pos,
                    "end_pos": entity.end_pos
                }
                for entity in self.entities
            ],
            "evidences": [
                {
                    "text": evidence.text,
                    "start_pos": evidence.start_pos,
                    "end_pos": evidence.end_pos,
                    "relation_type": evidence.relation_type
                }
                for evidence in self.evidences
            ],
            "relations": [
                {
                    "subject_text": relation.subject.text,
                    "subject_label": relation.subject.label,
                    "object_text": relation.object.text,
                    "object_label": relation.object.label,
                    "evidence_text": relation.evidence.text,
                    "relation_type": relation.relation_type
                }
                for relation in self.relations
            ]
        }
    
    def get_statistics(self) -> Dict:
        """Get annotation statistics"""
        bacteria_count = sum(1 for e in self.entities if e.label == 'Bacteria')
        disease_count = sum(1 for e in self.entities if e.label == 'Disease')
        
        relation_counts = {}
        for relation in self.relations:
            rel_type = relation.relation_type
            relation_counts[rel_type] = relation_counts.get(rel_type, 0) + 1
        
        return {
            "total_entities": len(self.entities),
            "bacteria_entities": bacteria_count,
            "disease_entities": disease_count,
            "total_relations": len(self.relations),
            "total_evidences": len(self.evidences),
            "relation_types": relation_counts
        }


class MedicalAnnotationLLM(BaseAnnotator):
    """LLM-powered medical literature annotation system"""

    def __init__(self, 
                 api_key: str,
                 model: str = "deepseek-chat",
                 model_type: str = "deepseek",
                 base_url: Optional[str] = None,
                 max_retries: int = 3,
                 retry_delay: int = 5,
                 **kwargs):
        """
        Initialize medical annotation LLM
        
        Args:
            api_key: API key for LLM service
            model: Model name to use
            model_type: Type of model service
            base_url: Base URL for API (optional)
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
            **kwargs: Additional configuration
        """
        super().__init__(
            api_key=api_key,
            model=model,
            model_type=model_type,
            base_url=base_url,
            max_retries=max_retries,
            retry_delay=retry_delay,
            **kwargs
        )
        
        # Initialize annotation prompts
        self._setup_prompts()
    
    def _setup_prompts(self) -> None:
        """Setup annotation prompts based on model type"""
        if self.model_type == "deepseek-reasoner":
            # Enhanced prompt for reasoning model
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

请运用你的推理能力深度分析，确保输出的JSON格式正确。如果没有找到相关实体或关系，请返回空数组。

输出格式：
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
"""
        else:
            # Standard prompt for other models
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
    
    def annotate_text(self, 
                     title: str, 
                     abstract: str, 
                     pmid: str = "",
                     max_retries: Optional[int] = None,
                     retry_delay: Optional[int] = None) -> AnnotationResult:
        """
        Annotate a single text
        
        Args:
            title: Article title
            abstract: Article abstract
            pmid: PubMed ID
            max_retries: Maximum retries (override default)
            retry_delay: Retry delay (override default)
            
        Returns:
            AnnotationResult: Annotation result
        """
        # Use instance defaults if not provided
        max_retries = max_retries or self.max_retries
        retry_delay = retry_delay or self.retry_delay
        
        # Combine title and abstract
        full_text = f"{title}\n{abstract}"
        
        # Build prompt
        prompt = self.annotation_prompt.format(title=title, abstract=abstract)
        
        # Build messages
        messages = [
            {"role": "system", "content": "你是一个专业的医学文献标注专家，专门识别病原微生物与自身免疫性疾病之间的关系。"},
            {"role": "user", "content": prompt}
        ]
        
        # Retry logic
        for attempt in range(max_retries):
            try:
                # Call LLM
                llm_output = self.llm_client.chat_completion(messages)
                
                # Extract JSON
                json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
                if not json_match:
                    self.logger.warning(f"No JSON found in LLM response for PMID {pmid}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return self._create_empty_result(pmid, title, abstract)
                
                try:
                    annotation_data = json.loads(json_match.group())
                except json.JSONDecodeError as e:
                    self.logger.warning(f"JSON parsing error for PMID {pmid}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return self._create_empty_result(pmid, title, abstract)
                
                # Parse annotation data
                return self._parse_annotation_data(annotation_data, pmid, title, abstract, full_text)
                
            except Exception as e:
                self.logger.warning(f"Annotation attempt {attempt + 1} failed for PMID {pmid}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"All annotation attempts failed for PMID {pmid}: {e}")
                    return self._create_empty_result(pmid, title, abstract)
        
        return self._create_empty_result(pmid, title, abstract)
    
    def batch_process(self, inputs: List[Tuple[str, str, str]], **kwargs) -> List[AnnotationResult]:
        """
        Process multiple texts in batch
        
        Args:
            inputs: List of (title, abstract, pmid) tuples
            **kwargs: Additional parameters
            
        Returns:
            List[AnnotationResult]: List of annotation results
        """
        results = []
        
        self.logger.info(f"Processing {len(inputs)} articles using {self.model_type.upper()} {self.model}")
        
        for idx, (title, abstract, pmid) in enumerate(inputs):
            self.logger.info(f"Processing {idx+1}/{len(inputs)}: PMID {pmid}")
            
            result = self.annotate_text(title, abstract, pmid)
            results.append(result)
        
        return results
    
    def annotate_excel_file(self, 
                           excel_path: str, 
                           output_path: Optional[str] = None) -> List[AnnotationResult]:
        """
        Annotate all articles in an Excel file
        
        Args:
            excel_path: Path to Excel file
            output_path: Optional output path
            
        Returns:
            List[AnnotationResult]: Annotation results
        """
        try:
            # Read Excel file
            df = pd.read_excel(excel_path)
            
            # Prepare inputs
            inputs = []
            for _, row in df.iterrows():
                pmid = str(row.get('pmid', ''))
                title = str(row.get('title', ''))
                abstract = str(row.get('abstract', ''))
                inputs.append((title, abstract, pmid))
            
            # Process batch
            results = self.batch_process(inputs)
            
            # Save results if output path provided
            if output_path:
                self.save_results(results, output_path)
            
            return results
            
        except Exception as e:
            raise AnnotationError(f"Failed to process Excel file {excel_path}: {e}")
    
    def _create_empty_result(self, pmid: str, title: str, abstract: str) -> AnnotationResult:
        """Create empty annotation result"""
        return AnnotationResult(
            pmid=pmid,
            title=title,
            abstract=abstract,
            entities=[],
            evidences=[],
            relations=[]
        )
    
    def _parse_annotation_data(self, 
                              data: Dict, 
                              pmid: str, 
                              title: str, 
                              abstract: str, 
                              full_text: str) -> AnnotationResult:
        """Parse LLM annotation data into structured format"""
        entities = []
        evidences = []
        relations = []
        
        # Parse entities
        for entity_data in data.get('entities', []):
            entity = Entity(
                text=entity_data['text'],
                label=entity_data['label'],
                start_pos=entity_data.get('start_pos', 0),
                end_pos=entity_data.get('end_pos', 0)
            )
            entities.append(entity)
        
        # Parse evidences
        for evidence_data in data.get('evidences', []):
            evidence = Evidence(
                text=evidence_data['text'],
                start_pos=evidence_data.get('start_pos', 0),
                end_pos=evidence_data.get('end_pos', 0),
                relation_type=evidence_data['relation_type']
            )
            evidences.append(evidence)
        
        # Parse relations
        for relation_data in data.get('relations', []):
            # Find corresponding entities
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
    
    def save_results(self, results: List[AnnotationResult], output_path: str) -> None:
        """Save annotation results to JSON file"""
        output_data = []
        
        for result in results:
            result_dict = result.to_dict()
            result_dict['model_info'] = {
                'model_type': self.model_type,
                'model_name': self.model
            }
            output_data.append(result_dict)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Results saved to {output_path}")
    
    def generate_statistics(self, results: List[AnnotationResult]) -> Dict:
        """Generate annotation statistics"""
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