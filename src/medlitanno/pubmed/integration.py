#!/usr/bin/env python3
"""
PubMed Search and Annotation Integration

This module provides functionality to search PubMed and automatically annotate
the retrieved articles using the LLM annotation system.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from .searcher import PubMedSearcher, SearchResult, PubMedArticle
from ..annotation import MedicalAnnotationLLM, AnnotationResult
from ..common.utils import ensure_directory, get_timestamp, save_results
from ..common.exceptions import MedLitAnnoError

logger = logging.getLogger(__name__)


class PubMedAnnotationPipeline:
    """Pipeline for searching PubMed and annotating results"""
    
    def __init__(self,
                 pubmed_searcher: PubMedSearcher,
                 annotator: MedicalAnnotationLLM,
                 output_dir: str = "pubmed_results"):
        """
        Initialize the pipeline
        
        Args:
            pubmed_searcher: Configured PubMed searcher
            annotator: Configured medical annotation LLM
            output_dir: Directory to save results
        """
        self.pubmed_searcher = pubmed_searcher
        self.annotator = annotator
        self.output_dir = output_dir
        ensure_directory(output_dir)
        
        logger.info(f"PubMed annotation pipeline initialized (output: {output_dir})")
    
    def search_and_annotate(self,
                           query: str,
                           max_results: int = 50,
                           save_intermediate: bool = True) -> Tuple[SearchResult, List[AnnotationResult]]:
        """
        Search PubMed and annotate all retrieved articles
        
        Args:
            query: Search query
            max_results: Maximum articles to retrieve and annotate
            save_intermediate: Whether to save intermediate results
            
        Returns:
            Tuple of (SearchResult, List[AnnotationResult])
        """
        logger.info(f"Starting search and annotation pipeline for: '{query}'")
        
        # Step 1: Search PubMed
        logger.info("Step 1: Searching PubMed...")
        search_result = self.pubmed_searcher.search(query, max_results=max_results)
        
        if not search_result.articles:
            logger.warning("No articles found for the query")
            return search_result, []
        
        logger.info(f"Found {len(search_result.articles)} articles")
        
        # Save search results if requested
        if save_intermediate:
            search_file = os.path.join(
                self.output_dir, 
                f"search_results_{get_timestamp()}.xlsx"
            )
            search_result.save_to_excel(search_file)
        
        # Step 2: Annotate articles
        logger.info("Step 2: Annotating articles...")
        annotation_results = []
        
        for i, article in enumerate(search_result.articles, 1):
            logger.info(f"Annotating article {i}/{len(search_result.articles)}: PMID {article.pmid}")
            
            try:
                # Annotate the article
                result = self.annotator.annotate_text(
                    title=article.title,
                    abstract=article.abstract,
                    pmid=article.pmid
                )
                annotation_results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to annotate article PMID {article.pmid}: {e}")
                # Create empty result for failed annotation
                empty_result = self.annotator._create_empty_result(
                    article.pmid, article.title, article.abstract
                )
                annotation_results.append(empty_result)
        
        logger.info(f"Annotation completed: {len(annotation_results)} articles processed")
        
        return search_result, annotation_results
    
    def save_combined_results(self,
                             search_result: SearchResult,
                             annotation_results: List[AnnotationResult],
                             output_prefix: str = None) -> Dict[str, str]:
        """
        Save combined search and annotation results
        
        Args:
            search_result: PubMed search results
            annotation_results: Annotation results
            output_prefix: Prefix for output files
            
        Returns:
            Dictionary of saved file paths
        """
        if not output_prefix:
            output_prefix = f"pubmed_annotated_{get_timestamp()}"
        
        saved_files = {}
        
        # Save annotation results as JSON
        annotation_file = os.path.join(self.output_dir, f"{output_prefix}_annotations.json")
        self.annotator.save_results(annotation_results, annotation_file)
        saved_files['annotations'] = annotation_file
        
        # Save search results as Excel
        search_file = os.path.join(self.output_dir, f"{output_prefix}_search.xlsx")
        search_result.save_to_excel(search_file)
        saved_files['search'] = search_file
        
        # Save combined summary
        summary_file = os.path.join(self.output_dir, f"{output_prefix}_summary.json")
        summary = self._create_summary(search_result, annotation_results)
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        saved_files['summary'] = summary_file
        
        # Save annotation statistics
        stats_file = os.path.join(self.output_dir, f"{output_prefix}_statistics.json")
        stats = self.annotator.generate_statistics(annotation_results)
        stats['search_info'] = {
            'query': search_result.query,
            'total_articles': len(search_result.articles),
            'search_time': search_result.search_time,
            'search_duration': search_result.search_duration
        }
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        saved_files['statistics'] = stats_file
        
        logger.info(f"Combined results saved: {len(saved_files)} files")
        return saved_files
    
    def _create_summary(self,
                       search_result: SearchResult,
                       annotation_results: List[AnnotationResult]) -> Dict:
        """Create a summary of search and annotation results"""
        # Count annotations
        articles_with_entities = sum(1 for r in annotation_results if r.entities)
        articles_with_relations = sum(1 for r in annotation_results if r.relations)
        total_entities = sum(len(r.entities) for r in annotation_results)
        total_relations = sum(len(r.relations) for r in annotation_results)
        
        # Count by type
        bacteria_count = sum(
            sum(1 for e in r.entities if e.label == 'Bacteria')
            for r in annotation_results
        )
        disease_count = sum(
            sum(1 for e in r.entities if e.label == 'Disease')
            for r in annotation_results
        )
        
        # Relation type counts
        relation_types = {}
        for result in annotation_results:
            for relation in result.relations:
                rel_type = relation.relation_type
                relation_types[rel_type] = relation_types.get(rel_type, 0) + 1
        
        return {
            'search_summary': {
                'query': search_result.query,
                'articles_found': len(search_result.articles),
                'search_time': search_result.search_time,
                'search_duration_seconds': search_result.search_duration
            },
            'annotation_summary': {
                'total_articles': len(annotation_results),
                'articles_with_entities': articles_with_entities,
                'articles_with_relations': articles_with_relations,
                'total_entities': total_entities,
                'total_bacteria': bacteria_count,
                'total_diseases': disease_count,
                'total_relations': total_relations,
                'relation_types': relation_types,
                'annotation_success_rate': {
                    'entities': articles_with_entities / len(annotation_results) if annotation_results else 0,
                    'relations': articles_with_relations / len(annotation_results) if annotation_results else 0
                }
            },
            'top_articles': [
                {
                    'pmid': result.pmid,
                    'title': result.title[:100] + '...' if len(result.title) > 100 else result.title,
                    'entities_count': len(result.entities),
                    'relations_count': len(result.relations)
                }
                for result in sorted(
                    annotation_results, 
                    key=lambda x: len(x.relations) + len(x.entities), 
                    reverse=True
                )[:10]
            ]
        }
    
    def batch_search_and_annotate(self,
                                 queries: List[str],
                                 max_results_per_query: int = 20) -> Dict[str, Tuple[SearchResult, List[AnnotationResult]]]:
        """
        Perform multiple searches and annotations
        
        Args:
            queries: List of search queries
            max_results_per_query: Maximum results per query
            
        Returns:
            Dictionary mapping queries to their results
        """
        logger.info(f"Starting batch processing for {len(queries)} queries")
        
        results = {}
        
        for i, query in enumerate(queries, 1):
            logger.info(f"Processing query {i}/{len(queries)}: '{query}'")
            
            try:
                search_result, annotation_results = self.search_and_annotate(
                    query, 
                    max_results=max_results_per_query,
                    save_intermediate=False
                )
                
                results[query] = (search_result, annotation_results)
                
                # Save individual results
                query_safe = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                self.save_combined_results(
                    search_result, 
                    annotation_results,
                    f"batch_{i}_{query_safe}"
                )
                
            except Exception as e:
                logger.error(f"Failed to process query '{query}': {e}")
                results[query] = (None, [])
        
        logger.info(f"Batch processing completed: {len(results)} queries processed")
        return results


def search_and_annotate(query: str,
                       max_results: int = 50,
                       pubmed_tool: str = None,
                       pubmed_email: str = None,
                       api_key: str = None,
                       model: str = "deepseek-chat",
                       model_type: str = "deepseek",
                       output_dir: str = "pubmed_results") -> Tuple[SearchResult, List[AnnotationResult]]:
    """
    Convenience function to search PubMed and annotate results
    
    Args:
        query: Search query
        max_results: Maximum articles to retrieve and annotate
        pubmed_tool: PubMed tool name
        pubmed_email: PubMed email
        api_key: LLM API key
        model: LLM model name
        model_type: LLM model type
        output_dir: Output directory
        
    Returns:
        Tuple of (SearchResult, List[AnnotationResult])
    """
    from .searcher import create_pubmed_searcher
    from ..common.utils import get_env_var
    
    # Create PubMed searcher
    searcher = create_pubmed_searcher(tool=pubmed_tool, email=pubmed_email)
    
    # Create annotator
    if not api_key:
        api_key = get_env_var("DEEPSEEK_API_KEY")
    
    annotator = MedicalAnnotationLLM(
        api_key=api_key,
        model=model,
        model_type=model_type
    )
    
    # Create pipeline
    pipeline = PubMedAnnotationPipeline(searcher, annotator, output_dir)
    
    # Execute search and annotation
    search_result, annotation_results = pipeline.search_and_annotate(
        query, max_results=max_results
    )
    
    # Save results
    pipeline.save_combined_results(search_result, annotation_results)
    
    return search_result, annotation_results
