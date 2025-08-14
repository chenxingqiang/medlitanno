#!/usr/bin/env python3
"""
PubMed Search and Annotation Demo

This script demonstrates how to search PubMed for medical literature
and automatically annotate the results using LLM.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from medlitanno.pubmed import PubMedSearcher, PubMedAnnotationPipeline, search_and_annotate
from medlitanno.annotation import MedicalAnnotationLLM
from medlitanno.common import get_env_var


def demo_basic_search():
    """Demo: Basic PubMed search without annotation"""
    print("🔍 Demo 1: Basic PubMed Search")
    print("=" * 50)
    
    try:
        # Create searcher
        searcher = PubMedSearcher()
        
        # Search for articles
        query = "Helicobacter pylori rheumatoid arthritis"
        print(f"Searching: '{query}'")
        
        result = searcher.search(query, max_results=10)
        
        print(f"\n📊 Search Results:")
        print(f"  • Query: {result.query}")
        print(f"  • Articles found: {len(result.articles)}")
        print(f"  • Search duration: {result.search_duration:.2f}s")
        
        # Show first few articles
        print(f"\n📑 Sample Articles:")
        for i, article in enumerate(result.articles[:3], 1):
            print(f"\n  {i}. PMID: {article.pmid}")
            print(f"     Title: {article.title[:100]}...")
            print(f"     Journal: {article.journal}")
            print(f"     Authors: {', '.join(article.authors[:3])}{'...' if len(article.authors) > 3 else ''}")
            print(f"     Abstract: {article.abstract[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic search failed: {e}")
        return False


def demo_specialized_search():
    """Demo: Specialized search methods"""
    print("\n🎯 Demo 2: Specialized Search Methods")
    print("=" * 50)
    
    try:
        searcher = PubMedSearcher()
        
        # Disease-bacteria search
        print("🦠 Searching for disease-bacteria relationships...")
        result = searcher.search_by_disease_bacteria(
            disease="rheumatoid arthritis",
            bacteria="Helicobacter pylori",
            max_results=5
        )
        print(f"Found {len(result.articles)} articles on H. pylori and RA")
        
        # Recent articles search
        print("\n📅 Searching for recent articles (last 30 days)...")
        result = searcher.search_recent(
            query="autoimmune disease bacteria",
            days=30,
            max_results=5
        )
        print(f"Found {len(result.articles)} recent articles")
        
        # Keyword search
        print("\n🔤 Searching by multiple keywords...")
        result = searcher.search_by_keywords(
            keywords=["molecular mimicry", "autoimmune", "bacteria"],
            max_results=5,
            operator="AND"
        )
        print(f"Found {len(result.articles)} articles with all keywords")
        
        return True
        
    except Exception as e:
        print(f"❌ Specialized search failed: {e}")
        return False


def demo_search_and_annotation():
    """Demo: Complete search and annotation pipeline"""
    print("\n🤖 Demo 3: Search and Automatic Annotation")
    print("=" * 50)
    
    try:
        # Check for API key
        try:
            api_key = get_env_var("DEEPSEEK_API_KEY")
            print("✅ API key found")
        except:
            print("❌ No API key found. Skipping annotation demo.")
            print("Set DEEPSEEK_API_KEY environment variable to run this demo.")
            return False
        
        # Run search and annotation
        query = "Helicobacter pylori autoimmune disease"
        print(f"🔍 Searching and annotating: '{query}'")
        
        search_result, annotation_results = search_and_annotate(
            query=query,
            max_results=5,  # Small number for demo
            model="deepseek-chat",
            model_type="deepseek",
            output_dir="demo_pubmed_results"
        )
        
        print(f"\n📊 Combined Results:")
        print(f"  • Articles retrieved: {len(search_result.articles)}")
        print(f"  • Articles annotated: {len(annotation_results)}")
        
        # Analyze annotation results
        articles_with_entities = sum(1 for r in annotation_results if r.entities)
        articles_with_relations = sum(1 for r in annotation_results if r.relations)
        total_entities = sum(len(r.entities) for r in annotation_results)
        total_relations = sum(len(r.relations) for r in annotation_results)
        
        print(f"  • Articles with entities: {articles_with_entities}")
        print(f"  • Articles with relations: {articles_with_relations}")
        print(f"  • Total entities found: {total_entities}")
        print(f"  • Total relations found: {total_relations}")
        
        # Show sample annotations
        print(f"\n🏷️  Sample Annotations:")
        for i, result in enumerate(annotation_results[:2], 1):
            if result.entities or result.relations:
                print(f"\n  Article {i} (PMID: {result.pmid}):")
                print(f"    Title: {result.title[:80]}...")
                
                if result.entities:
                    print(f"    Entities ({len(result.entities)}):")
                    for entity in result.entities[:3]:
                        pos_info = f" [{entity.start_pos}-{entity.end_pos}]" if entity.has_position() else ""
                        print(f"      • {entity.text} ({entity.label}){pos_info}")
                
                if result.relations:
                    print(f"    Relations ({len(result.relations)}):")
                    for relation in result.relations[:2]:
                        print(f"      • {relation.subject.text} --[{relation.relation_type}]--> {relation.object.text}")
        
        print(f"\n💾 Results saved to: demo_pubmed_results/")
        return True
        
    except Exception as e:
        print(f"❌ Search and annotation failed: {e}")
        return False


def demo_pipeline_usage():
    """Demo: Using the annotation pipeline directly"""
    print("\n🔧 Demo 4: Using PubMed Annotation Pipeline")
    print("=" * 50)
    
    try:
        # Check for API key
        try:
            api_key = get_env_var("DEEPSEEK_API_KEY")
        except:
            print("❌ No API key found. Skipping pipeline demo.")
            return False
        
        # Create components
        searcher = PubMedSearcher()
        annotator = MedicalAnnotationLLM(
            api_key=api_key,
            model="deepseek-chat",
            model_type="deepseek"
        )
        
        # Create pipeline
        pipeline = PubMedAnnotationPipeline(
            pubmed_searcher=searcher,
            annotator=annotator,
            output_dir="demo_pipeline_results"
        )
        
        # Run pipeline
        query = "molecular mimicry bacteria autoimmune"
        print(f"🔄 Running pipeline for: '{query}'")
        
        search_result, annotation_results = pipeline.search_and_annotate(
            query=query,
            max_results=3,
            save_intermediate=True
        )
        
        # Save combined results
        saved_files = pipeline.save_combined_results(
            search_result, 
            annotation_results,
            "demo_pipeline"
        )
        
        print(f"\n📁 Files saved:")
        for file_type, file_path in saved_files.items():
            print(f"  • {file_type}: {file_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline demo failed: {e}")
        return False


def main():
    """Run all demos"""
    print("🧬 PubMed Search and Annotation Demo")
    print("=" * 70)
    
    # Check requirements
    print("🔧 Checking requirements...")
    
    # Check PubMed email
    try:
        email = get_env_var("PUBMED_EMAIL")
        print(f"✅ PubMed email configured: {email}")
    except:
        print("❌ PUBMED_EMAIL environment variable not set")
        print("Please set your email address for PubMed API access")
        return
    
    # Run demos
    demos = [
        ("Basic Search", demo_basic_search),
        ("Specialized Search", demo_specialized_search), 
        ("Search and Annotation", demo_search_and_annotation),
        ("Pipeline Usage", demo_pipeline_usage)
    ]
    
    results = []
    for name, demo_func in demos:
        try:
            success = demo_func()
            results.append((name, success))
        except KeyboardInterrupt:
            print(f"\n⚠️  Demo '{name}' interrupted by user")
            results.append((name, False))
            break
        except Exception as e:
            print(f"\n❌ Demo '{name}' failed with unexpected error: {e}")
            results.append((name, False))
    
    # Summary
    print(f"\n" + "=" * 70)
    print("📋 Demo Summary:")
    
    for name, success in results:
        status = "✅ Passed" if success else "❌ Failed"
        print(f"  • {name}: {status}")
    
    successful = sum(1 for _, success in results if success)
    print(f"\n🎯 Overall: {successful}/{len(results)} demos successful")
    
    if successful > 0:
        print("\n🎉 PubMed search and annotation system is working!")
        print("\nNext steps:")
        print("  • Try: medlitanno search 'your query here' --max-results 20")
        print("  • Check the demo_*_results/ directories for output files")
        print("  • Customize search parameters for your research needs")


if __name__ == "__main__":
    main()
