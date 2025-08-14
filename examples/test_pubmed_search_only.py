#!/usr/bin/env python3
"""
Test PubMed search functionality only (without annotation)
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from medlitanno.pubmed import PubMedSearcher


def test_pubmed_search():
    """Test basic PubMed search functionality"""
    print("🔍 Testing PubMed Search Functionality")
    print("=" * 50)
    
    try:
        # Create searcher
        searcher = PubMedSearcher()
        
        # Test 1: Basic search
        print("Test 1: Basic search")
        query = "Helicobacter pylori molecular mimicry"
        result = searcher.search(query, max_results=5)
        
        print(f"✅ Search successful:")
        print(f"  • Query: {result.query}")
        print(f"  • Articles found: {len(result.articles)}")
        print(f"  • Search duration: {result.search_duration:.2f}s")
        
        # Show article details
        if result.articles:
            article = result.articles[0]
            print(f"\n📄 First Article:")
            print(f"  • PMID: {article.pmid}")
            print(f"  • Title: {article.title[:100]}...")
            print(f"  • Journal: {article.journal}")
            print(f"  • Authors: {len(article.authors)} authors")
            print(f"  • Abstract length: {len(article.abstract)} chars")
            print(f"  • Keywords: {len(article.keywords)} keywords")
            print(f"  • MeSH terms: {len(article.mesh_terms)} terms")
            print(f"  • URL: {article.url}")
        
        # Test 2: Save to Excel
        print(f"\nTest 2: Save to Excel")
        output_file = "test_pubmed_results.xlsx"
        result.save_to_excel(output_file)
        print(f"✅ Results saved to: {output_file}")
        
        # Test 3: Disease-bacteria search
        print(f"\nTest 3: Disease-bacteria search")
        result2 = searcher.search_by_disease_bacteria(
            disease="rheumatoid arthritis",
            bacteria="Helicobacter pylori",
            max_results=3
        )
        print(f"✅ Disease-bacteria search successful: {len(result2.articles)} articles")
        
        # Test 4: Keyword search
        print(f"\nTest 4: Multiple keywords search")
        result3 = searcher.search_by_keywords(
            keywords=["autoimmune", "bacteria", "infection"],
            max_results=3,
            operator="AND"
        )
        print(f"✅ Keyword search successful: {len(result3.articles)} articles")
        
        print(f"\n🎉 All PubMed search tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pubmed_search()
    sys.exit(0 if success else 1)
