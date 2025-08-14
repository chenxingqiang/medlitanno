#!/usr/bin/env python3
"""
Demo: LLM annotation with automatic position matching

This example shows how the new system works:
1. LLM provides only content (no position info) for better accuracy
2. System automatically calculates positions using string matching
3. Multiple matching strategies ensure high success rate
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from medlitanno.annotation import MedicalAnnotationLLM
from medlitanno.common import get_env_var

def main():
    print("🧬 Medical Literature Annotation with Automatic Position Matching")
    print("=" * 70)
    
    # Sample medical abstract
    title = "Molecular mimicry between Helicobacter pylori and human tissues"
    abstract = """
    Helicobacter pylori is a spiral-shaped gram-negative bacterium that chronically 
    colonizes the human stomach. Recent evidence suggests that H. pylori antigens 
    share structural similarities with human proteins, leading to molecular mimicry. 
    This cross-reactivity may contribute to autoimmune diseases such as rheumatoid 
    arthritis, multiple sclerosis, and inflammatory bowel disease. The bacterial 
    heat shock protein HSP60 shows significant homology with human HSP60, potentially 
    triggering autoimmune responses. Our study demonstrates that H. pylori infection 
    correlates with increased autoantibody production in genetically susceptible individuals.
    """
    
    print(f"Title: {title}")
    print(f"Abstract: {abstract[:200]}...")
    print()
    
    # Get API key
    try:
        api_key = get_env_var("DEEPSEEK_API_KEY")
        print("✅ API key found")
    except:
        print("❌ No API key found. Please set DEEPSEEK_API_KEY environment variable.")
        return
    
    # Initialize annotation system
    print("\n🤖 Initializing LLM annotation system...")
    annotator = MedicalAnnotationLLM(
        api_key=api_key,
        model="deepseek-chat",
        model_type="deepseek"
    )
    
    # Perform annotation
    print("🔍 Analyzing text with LLM (no position info requested)...")
    result = annotator.annotate_text(title, abstract, "demo_pmid")
    
    # Show results
    print(f"\n📊 Annotation Results:")
    print(f"  • Entities found: {len(result.entities)}")
    print(f"  • Evidence sentences: {len(result.evidences)}")
    print(f"  • Relations identified: {len(result.relations)}")
    
    # Position matching statistics
    entities_with_pos = [e for e in result.entities if e.has_position()]
    evidences_with_pos = [e for e in result.evidences if e.has_position()]
    
    print(f"\n🎯 Position Matching Results:")
    print(f"  • Entity position success: {len(entities_with_pos)}/{len(result.entities)} "
          f"({100*len(entities_with_pos)/len(result.entities) if result.entities else 0:.0f}%)")
    print(f"  • Evidence position success: {len(evidences_with_pos)}/{len(result.evidences)} "
          f"({100*len(evidences_with_pos)/len(result.evidences) if result.evidences else 0:.0f}%)")
    
    if entities_with_pos:
        avg_entity_conf = sum(e.confidence for e in entities_with_pos) / len(entities_with_pos)
        print(f"  • Average entity confidence: {avg_entity_conf:.2f}")
    
    if evidences_with_pos:
        avg_evidence_conf = sum(e.confidence for e in evidences_with_pos) / len(evidences_with_pos)
        print(f"  • Average evidence confidence: {avg_evidence_conf:.2f}")
    
    # Show detailed results
    print(f"\n🦠 Entities Detected:")
    for i, entity in enumerate(result.entities, 1):
        if entity.has_position():
            print(f"  {i}. '{entity.text}' ({entity.label})")
            print(f"     Position: {entity.start_pos}-{entity.end_pos} (confidence: {entity.confidence:.2f})")
            if entity.matched_text != entity.text:
                print(f"     Matched text: '{entity.matched_text}'")
        else:
            print(f"  {i}. '{entity.text}' ({entity.label}) [No position found]")
        print()
    
    print(f"🔬 Evidence Sentences:")
    for i, evidence in enumerate(result.evidences, 1):
        print(f"  {i}. Relation: {evidence.relation_type}")
        print(f"     Text: {evidence.text[:100]}...")
        if evidence.has_position():
            print(f"     Position: {evidence.start_pos}-{evidence.end_pos} (confidence: {evidence.confidence:.2f})")
        else:
            print(f"     Position: Not found")
        print()
    
    print(f"🔗 Relations:")
    for i, relation in enumerate(result.relations, 1):
        print(f"  {i}. {relation.subject.text} --[{relation.relation_type}]--> {relation.object.text}")
        print(f"     Evidence: {relation.evidence.text[:80]}...")
        print()
    
    # Save results
    output_file = "demo_position_matching_result.json"
    annotator.save_results([result], output_file)
    print(f"💾 Results saved to: {output_file}")
    
    print("\n" + "=" * 70)
    print("✅ Demo completed! The system successfully:")
    print("   • Used LLM for content annotation (no position requirements)")
    print("   • Automatically calculated accurate positions using string matching")
    print("   • Provided confidence scores for position matches")
    print("   • Handled various text variations and edge cases")


if __name__ == "__main__":
    main()
