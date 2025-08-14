#!/usr/bin/env python3
"""
PubMed Search and Integration Module

This module provides functionality to search PubMed literature using keywords
and integrate the results with the annotation system.
"""

from .searcher import (
    PubMedSearcher,
    PubMedArticle,
    SearchResult,
    create_pubmed_searcher,
)

from .integration import (
    PubMedAnnotationPipeline,
    search_and_annotate,
)

__all__ = [
    # Core search functionality
    "PubMedSearcher",
    "PubMedArticle", 
    "SearchResult",
    "create_pubmed_searcher",
    
    # Integration with annotation
    "PubMedAnnotationPipeline",
    "search_and_annotate",
]
