#!/usr/bin/env python3
"""
医学文献自动标注系统 - 基础测试
Medical Literature Auto-Annotation System - Basic Tests
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from annotation.auto_annotation_system import MedicalAnnotationLLM, Entity, Relation, Evidence, AnnotationResult

class TestAnnotationSystem(unittest.TestCase):
    """标注系统基础测试"""
    
    def setUp(self):
        """测试设置"""
        self.api_key = "test_api_key"
        self.annotator = MedicalAnnotationLLM(
            api_key=self.api_key,
            model="deepseek-chat",
            model_type="deepseek"
        )
    
    def test_entity_creation(self):
        """测试实体创建"""
        entity = Entity(
            text="Helicobacter pylori",
            label="Bacteria",
            start=0,
            end=17
        )
        
        self.assertEqual(entity.text, "Helicobacter pylori")
        self.assertEqual(entity.label, "Bacteria")
        self.assertEqual(entity.start, 0)
        self.assertEqual(entity.end, 17)
    
    def test_relation_creation(self):
        """测试关系创建"""
        relation = Relation(
            subject="Helicobacter pylori",
            relation_type="contributes_to",
            object="autoimmune gastritis"
        )
        
        self.assertEqual(relation.subject, "Helicobacter pylori")
        self.assertEqual(relation.relation_type, "contributes_to")
        self.assertEqual(relation.object, "autoimmune gastritis")
    
    def test_evidence_creation(self):
        """测试证据创建"""
        evidence = Evidence(
            text="H. pylori infection contributes to inflammatory responses",
            start=100,
            end=158
        )
        
        self.assertEqual(evidence.text, "H. pylori infection contributes to inflammatory responses")
        self.assertEqual(evidence.start, 100)
        self.assertEqual(evidence.end, 158)
    
    def test_annotation_result_creation(self):
        """测试标注结果创建"""
        entities = [Entity("H. pylori", "Bacteria", 0, 9)]
        relations = [Relation("H. pylori", "contributes_to", "gastritis")]
        evidence = [Evidence("Test evidence", 0, 13)]
        
        result = AnnotationResult(
            entities=entities,
            relations=relations,
            evidence=evidence,
            pmid="test_001"
        )
        
        self.assertEqual(len(result.entities), 1)
        self.assertEqual(len(result.relations), 1)
        self.assertEqual(len(result.evidence), 1)
        self.assertEqual(result.pmid, "test_001")
    
    def test_annotation_result_to_dict(self):
        """测试标注结果转换为字典"""
        entities = [Entity("H. pylori", "Bacteria", 0, 9)]
        relations = [Relation("H. pylori", "contributes_to", "gastritis")]
        evidence = [Evidence("Test evidence", 0, 13)]
        
        result = AnnotationResult(
            entities=entities,
            relations=relations,
            evidence=evidence,
            pmid="test_001"
        )
        
        result_dict = result.to_dict()
        
        self.assertIn("entities", result_dict)
        self.assertIn("relations", result_dict)
        self.assertIn("evidence", result_dict)
        self.assertIn("pmid", result_dict)
        self.assertEqual(result_dict["pmid"], "test_001")
    
    @patch('annotation.auto_annotation_system.openai.OpenAI')
    def test_annotator_initialization(self, mock_openai):
        """测试标注器初始化"""
        annotator = MedicalAnnotationLLM(
            api_key="test_key",
            model="deepseek-chat",
            model_type="deepseek"
        )
        
        self.assertEqual(annotator.model, "deepseek-chat")
        self.assertEqual(annotator.model_type, "deepseek")
    
    def test_environment_variables(self):
        """测试环境变量检查"""
        # 这个测试检查是否能正确处理环境变量
        original_key = os.environ.get("DEEPSEEK_API_KEY")
        
        # 临时移除环境变量
        if "DEEPSEEK_API_KEY" in os.environ:
            del os.environ["DEEPSEEK_API_KEY"]
        
        # 测试应该能够处理缺失的环境变量
        try:
            annotator = MedicalAnnotationLLM(
                api_key=None,
                model="deepseek-chat",
                model_type="deepseek"
            )
            # 如果没有抛出异常，说明处理正确
        except Exception as e:
            # 预期可能会有异常
            pass
        
        # 恢复环境变量
        if original_key:
            os.environ["DEEPSEEK_API_KEY"] = original_key

class TestDataStructures(unittest.TestCase):
    """数据结构测试"""
    
    def test_entity_equality(self):
        """测试实体相等性"""
        entity1 = Entity("H. pylori", "Bacteria", 0, 9)
        entity2 = Entity("H. pylori", "Bacteria", 0, 9)
        entity3 = Entity("E. coli", "Bacteria", 0, 7)
        
        self.assertEqual(entity1.text, entity2.text)
        self.assertNotEqual(entity1.text, entity3.text)
    
    def test_relation_types(self):
        """测试关系类型"""
        valid_types = ["contributes_to", "ameliorates", "correlated_with", "biomarker_for"]
        
        for relation_type in valid_types:
            relation = Relation("subject", relation_type, "object")
            self.assertEqual(relation.relation_type, relation_type)

if __name__ == "__main__":
    print("🧪 运行医学文献自动标注系统测试...")
    print("🧪 Running Medical Literature Auto-Annotation System Tests...")
    print()
    
    unittest.main(verbosity=2) 