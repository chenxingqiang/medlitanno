#!/usr/bin/env python3
"""
Test script for the new position matching system
"""

import os
import sys
import json
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from medlitanno.annotation import MedicalAnnotationLLM, TextPositionMatcher
from medlitanno.common import get_env_var


def test_position_matching():
    """Test the position matching functionality"""
    
    print("🧪 Testing Position Matching System")
    print("=" * 50)
    
    # Sample medical text
    title = "Helicobacter pylori infection and rheumatoid arthritis"
    abstract = """
    Background: Helicobacter pylori is a gram-negative bacterium that colonizes the human stomach. 
    Recent studies suggest that H. pylori infection may contribute to the development of rheumatoid arthritis 
    through molecular mimicry mechanisms. This study investigates the relationship between H. pylori infection 
    and autoimmune diseases.
    
    Methods: We analyzed serum samples from 200 patients with rheumatoid arthritis and 150 healthy controls.
    
    Results: H. pylori seropositivity was significantly higher in rheumatoid arthritis patients (75%) 
    compared to controls (45%, p<0.001). The bacteria appears to trigger autoimmune responses that 
    contribute to joint inflammation in susceptible individuals.
    
    Conclusions: Our findings suggest that Helicobacter pylori infection contributes to rheumatoid arthritis 
    pathogenesis through cross-reactive immune responses.
    """
    
    full_text = f"{title}\n{abstract}"
    
    # Test position matcher directly
    print("\n1. Testing Position Matcher Directly")
    print("-" * 30)
    
    matcher = TextPositionMatcher(min_confidence=0.7)
    
    # Test entity matching
    test_entities = [
        "Helicobacter pylori",
        "H. pylori",
        "rheumatoid arthritis",
        "gram-negative bacterium"
    ]
    
    print("Testing entity position matching:")
    for entity_text in test_entities:
        result = matcher.find_text_position(entity_text, full_text)
        if result:
            print(f"  ✅ '{entity_text}' -> pos: {result.start_pos}-{result.end_pos}, "
                  f"confidence: {result.confidence:.2f}")
            print(f"     Matched: '{result.matched_text}'")
        else:
            print(f"  ❌ '{entity_text}' -> No match found")
    
    # Test evidence matching
    test_evidences = [
        "H. pylori infection may contribute to the development of rheumatoid arthritis",
        "The bacteria appears to trigger autoimmune responses",
        "Helicobacter pylori infection contributes to rheumatoid arthritis pathogenesis"
    ]
    
    print("\nTesting evidence position matching:")
    for evidence_text in test_evidences:
        result = matcher.find_text_position(evidence_text, full_text)
        if result:
            print(f"  ✅ '{evidence_text[:50]}...' -> pos: {result.start_pos}-{result.end_pos}, "
                  f"confidence: {result.confidence:.2f}")
        else:
            print(f"  ❌ '{evidence_text[:50]}...' -> No match found")
    
    # Test with mock LLM output (simulating what LLM would return without positions)
    print("\n2. Testing Full Annotation System")
    print("-" * 30)
    
    # Mock annotation data without positions
    mock_annotation_data = {
        "entities": [
            {"text": "Helicobacter pylori", "label": "Bacteria"},
            {"text": "H. pylori", "label": "Bacteria"},
            {"text": "rheumatoid arthritis", "label": "Disease"}
        ],
        "evidences": [
            {
                "text": "H. pylori infection may contribute to the development of rheumatoid arthritis through molecular mimicry mechanisms",
                "relation_type": "contributes_to"
            },
            {
                "text": "The bacteria appears to trigger autoimmune responses that contribute to joint inflammation",
                "relation_type": "contributes_to"
            }
        ],
        "relations": [
            {
                "subject_text": "Helicobacter pylori",
                "object_text": "rheumatoid arthritis",
                "evidence_text": "H. pylori infection may contribute to the development of rheumatoid arthritis through molecular mimicry mechanisms",
                "relation_type": "contributes_to"
            }
        ]
    }
    
    # Get API key for testing (optional - we'll just test the parsing logic)
    try:
        api_key = get_env_var("DEEPSEEK_API_KEY")
    except Exception:
        api_key = None
    
    if api_key:
        print("API key found - testing with real LLM")
        
        # Initialize annotation system
        annotator = MedicalAnnotationLLM(
            api_key=api_key,
            model="deepseek-chat",
            model_type="deepseek"
        )
        
        # Test annotation
        try:
            result = annotator.annotate_text(title, abstract, "test_pmid")
            
            print(f"\nAnnotation Results:")
            print(f"  Entities found: {len(result.entities)}")
            print(f"  Evidences found: {len(result.evidences)}")
            print(f"  Relations found: {len(result.relations)}")
            
            # Show position matching results
            entities_with_pos = [e for e in result.entities if e.has_position()]
            evidences_with_pos = [e for e in result.evidences if e.has_position()]
            
            print(f"\nPosition Matching Results:")
            print(f"  Entities with positions: {len(entities_with_pos)}/{len(result.entities)}")
            print(f"  Evidences with positions: {len(evidences_with_pos)}/{len(result.evidences)}")
            
            if entities_with_pos:
                avg_entity_conf = sum(e.confidence for e in entities_with_pos) / len(entities_with_pos)
                print(f"  Average entity confidence: {avg_entity_conf:.2f}")
            
            if evidences_with_pos:
                avg_evidence_conf = sum(e.confidence for e in evidences_with_pos) / len(evidences_with_pos)
                print(f"  Average evidence confidence: {avg_evidence_conf:.2f}")
            
            # Show detailed results
            print(f"\nDetailed Entity Results:")
            for entity in result.entities:
                pos_info = f"pos: {entity.start_pos}-{entity.end_pos}" if entity.has_position() else "no position"
                conf_info = f"conf: {entity.confidence:.2f}" if entity.has_position() else ""
                print(f"  - {entity.text} ({entity.label}) [{pos_info}] {conf_info}")
            
        except Exception as e:
            print(f"❌ LLM annotation failed: {e}")
    else:
        print("No API key found - testing parsing logic only")
        
        # Test parsing logic without LLM call
        annotator = MedicalAnnotationLLM(
            api_key="dummy_key",
            model="deepseek-chat",
            model_type="deepseek"
        )
        
        # Test the parsing method directly
        result = annotator._parse_annotation_data(
            mock_annotation_data, 
            "test_pmid", 
            title, 
            abstract, 
            full_text
        )
        
        print(f"\nParsing Results (Mock Data):")
        print(f"  Entities: {len(result.entities)}")
        print(f"  Evidences: {len(result.evidences)}")
        print(f"  Relations: {len(result.relations)}")
        
        # Show position matching results
        entities_with_pos = [e for e in result.entities if e.has_position()]
        evidences_with_pos = [e for e in result.evidences if e.has_position()]
        
        print(f"\nPosition Matching Results:")
        print(f"  Entities with positions: {len(entities_with_pos)}/{len(result.entities)}")
        print(f"  Evidences with positions: {len(evidences_with_pos)}/{len(result.evidences)}")
        
        print(f"\nDetailed Results:")
        for entity in result.entities:
            if entity.has_position():
                print(f"  ✅ Entity '{entity.text}' -> {entity.start_pos}-{entity.end_pos} (conf: {entity.confidence:.2f})")
                print(f"     Matched: '{entity.matched_text}'")
            else:
                print(f"  ❌ Entity '{entity.text}' -> No position found")
        
        for evidence in result.evidences:
            if evidence.has_position():
                print(f"  ✅ Evidence '{evidence.text[:50]}...' -> {evidence.start_pos}-{evidence.end_pos} (conf: {evidence.confidence:.2f})")
            else:
                print(f"  ❌ Evidence '{evidence.text[:50]}...' -> No position found")
    
    print("\n" + "=" * 50)
    print("✅ Position matching test completed!")


def test_edge_cases():
    """Test edge cases for position matching"""
    
    print("\n🔍 Testing Edge Cases")
    print("=" * 50)
    
    matcher = TextPositionMatcher(min_confidence=0.6)
    
    # Test cases
    test_cases = [
        {
            "name": "Exact match",
            "text": "Helicobacter pylori",
            "full_text": "Studies on Helicobacter pylori infection show interesting results.",
            "expected": True
        },
        {
            "name": "Case insensitive",
            "text": "helicobacter pylori",
            "full_text": "Studies on Helicobacter pylori infection show interesting results.",
            "expected": True
        },
        {
            "name": "With extra spaces",
            "text": "Helicobacter  pylori",
            "full_text": "Studies on Helicobacter pylori infection show interesting results.",
            "expected": True
        },
        {
            "name": "Partial match",
            "text": "Helicobacter pylori causes gastritis",
            "full_text": "Studies show that Helicobacter pylori can cause gastritis in patients.",
            "expected": True
        },
        {
            "name": "No match",
            "text": "Escherichia coli",
            "full_text": "Studies on Helicobacter pylori infection show interesting results.",
            "expected": False
        },
        {
            "name": "Fuzzy match",
            "text": "H. pylory infection",
            "full_text": "Studies on H. pylori infection show interesting results.",
            "expected": True
        }
    ]
    
    for case in test_cases:
        print(f"\nTesting: {case['name']}")
        result = matcher.find_text_position(case['text'], case['full_text'])
        
        if result and case['expected']:
            print(f"  ✅ Found match: pos {result.start_pos}-{result.end_pos}, confidence: {result.confidence:.2f}")
            print(f"     Matched text: '{result.matched_text}'")
        elif not result and not case['expected']:
            print(f"  ✅ Correctly found no match")
        elif result and not case['expected']:
            print(f"  ⚠️  Unexpected match found: '{result.matched_text}' (confidence: {result.confidence:.2f})")
        else:
            print(f"  ❌ Expected match but none found")


if __name__ == "__main__":
    test_position_matching()
    test_edge_cases()
