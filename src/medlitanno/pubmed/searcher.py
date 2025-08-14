#!/usr/bin/env python3
"""
PubMed Searcher - Interface to PubMed API using PyMed
"""

import os
import time
import logging
from typing import List, Dict, Optional, Iterator, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import pandas as pd

try:
    from pymed import PubMed
    PYMED_AVAILABLE = True
except ImportError:
    PYMED_AVAILABLE = False
    PubMed = None

from ..common.exceptions import MedLitAnnoError, NetworkError, ConfigError
from ..common.utils import get_env_var, ensure_directory, get_timestamp

logger = logging.getLogger(__name__)


@dataclass
class PubMedArticle:
    """Represents a PubMed article"""
    pmid: str
    title: str
    abstract: str
    authors: List[str]
    journal: str
    publication_date: str
    doi: str
    keywords: List[str]
    mesh_terms: List[str]
    url: str
    
    def __post_init__(self):
        """Ensure all fields are strings or lists"""
        # Handle None values
        self.pmid = str(self.pmid) if self.pmid else ""
        self.title = str(self.title) if self.title else ""
        self.abstract = str(self.abstract) if self.abstract else ""
        self.journal = str(self.journal) if self.journal else ""
        self.publication_date = str(self.publication_date) if self.publication_date else ""
        self.doi = str(self.doi) if self.doi else ""
        self.url = str(self.url) if self.url else ""
        
        # Ensure lists
        self.authors = self.authors if isinstance(self.authors, list) else []
        self.keywords = self.keywords if isinstance(self.keywords, list) else []
        self.mesh_terms = self.mesh_terms if isinstance(self.mesh_terms, list) else []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def get_full_text(self) -> str:
        """Get combined title and abstract"""
        return f"{self.title}\n{self.abstract}"


@dataclass 
class SearchResult:
    """Represents search results from PubMed"""
    query: str
    articles: List[PubMedArticle]
    total_found: int
    search_time: str
    search_duration: float
    
    def __len__(self) -> int:
        return len(self.articles)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert articles to pandas DataFrame"""
        if not self.articles:
            return pd.DataFrame()
        
        data = []
        for article in self.articles:
            row = article.to_dict()
            # Convert lists to strings for DataFrame
            row['authors'] = '; '.join(article.authors)
            row['keywords'] = '; '.join(article.keywords) 
            row['mesh_terms'] = '; '.join(article.mesh_terms)
            data.append(row)
        
        return pd.DataFrame(data)
    
    def save_to_excel(self, output_path: str) -> None:
        """Save results to Excel file"""
        df = self.to_dataframe()
        ensure_directory(os.path.dirname(output_path))
        df.to_excel(output_path, index=False)
        logger.info(f"Search results saved to {output_path}")


class PubMedSearcher:
    """PubMed literature searcher using PyMed"""
    
    def __init__(self, 
                 tool: str = "medlitanno",
                 email: str = None,
                 rate_limit: float = 1.0):
        """
        Initialize PubMed searcher
        
        Args:
            tool: Tool name for PubMed API identification
            email: Email address (required by PubMed)
            rate_limit: Minimum seconds between requests
        """
        if not PYMED_AVAILABLE:
            raise ConfigError(
                "PyMed library is not installed. Install it with: pip install pymed"
            )
        
        # Get configuration from environment if not provided
        if not email:
            email = get_env_var("PUBMED_EMAIL", required=True)
        if not tool:
            tool = get_env_var("PUBMED_TOOL", default="medlitanno")
        
        self.tool = tool
        self.email = email
        self.rate_limit = rate_limit
        self.last_request_time = 0
        
        # Initialize PubMed API
        try:
            self.pubmed = PubMed(tool=tool, email=email)
            logger.info(f"PubMed searcher initialized with tool='{tool}', email='{email}'")
        except Exception as e:
            raise ConfigError(f"Failed to initialize PubMed API: {e}")
    
    def _rate_limit_delay(self) -> None:
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _parse_article(self, article) -> Optional[PubMedArticle]:
        """Parse PyMed article object to our PubMedArticle format"""
        try:
            # Extract basic information
            pmid = getattr(article, 'pubmed_id', '')
            title = getattr(article, 'title', '')
            abstract = getattr(article, 'abstract', '')
            
            # Extract authors
            authors = []
            if hasattr(article, 'authors') and article.authors:
                for author in article.authors:
                    if hasattr(author, 'lastname') and hasattr(author, 'firstname'):
                        name = f"{author.firstname} {author.lastname}".strip()
                        if name:
                            authors.append(name)
            
            # Extract journal information
            journal = getattr(article, 'journal', '')
            
            # Extract publication date
            pub_date = ""
            if hasattr(article, 'publication_date') and article.publication_date:
                pub_date = str(article.publication_date)
            
            # Extract DOI
            doi = getattr(article, 'doi', '')
            
            # Extract keywords
            keywords = []
            if hasattr(article, 'keywords') and article.keywords:
                keywords = [str(kw) for kw in article.keywords if kw]
            
            # Extract MeSH terms
            mesh_terms = []
            if hasattr(article, 'mesh') and article.mesh:
                for mesh in article.mesh:
                    if hasattr(mesh, 'term'):
                        mesh_terms.append(str(mesh.term))
            
            # Generate URL
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
            
            return PubMedArticle(
                pmid=pmid,
                title=title,
                abstract=abstract,
                authors=authors,
                journal=journal,
                publication_date=pub_date,
                doi=doi,
                keywords=keywords,
                mesh_terms=mesh_terms,
                url=url
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse article: {e}")
            return None
    
    def search(self, 
               query: str,
               max_results: int = 100,
               sort: str = "relevance") -> SearchResult:
        """
        Search PubMed for articles matching the query
        
        Args:
            query: Search query using PubMed syntax
            max_results: Maximum number of results to retrieve
            sort: Sort order ('relevance', 'pub_date', 'author', 'journal')
            
        Returns:
            SearchResult containing matched articles
        """
        logger.info(f"Searching PubMed: '{query}' (max_results={max_results})")
        
        start_time = time.time()
        search_timestamp = get_timestamp()
        
        try:
            # Apply rate limiting
            self._rate_limit_delay()
            
            # Perform search
            results = self.pubmed.query(query, max_results=max_results)
            
            # Parse results
            articles = []
            total_processed = 0
            
            for article in results:
                total_processed += 1
                parsed_article = self._parse_article(article)
                if parsed_article:
                    articles.append(parsed_article)
                
                # Apply rate limiting for each article processing
                if total_processed % 10 == 0:  # Every 10 articles
                    self._rate_limit_delay()
            
            duration = time.time() - start_time
            
            logger.info(f"Search completed: {len(articles)} articles retrieved in {duration:.2f}s")
            
            return SearchResult(
                query=query,
                articles=articles,
                total_found=len(articles),  # PyMed doesn't provide total count
                search_time=search_timestamp,
                search_duration=duration
            )
            
        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            raise NetworkError(f"PubMed search failed: {e}")
    
    def search_by_keywords(self,
                          keywords: List[str],
                          max_results: int = 100,
                          operator: str = "AND") -> SearchResult:
        """
        Search by multiple keywords
        
        Args:
            keywords: List of keywords to search for
            max_results: Maximum results to retrieve
            operator: Boolean operator ('AND', 'OR')
            
        Returns:
            SearchResult containing matched articles
        """
        if not keywords:
            raise ValueError("At least one keyword must be provided")
        
        # Build query
        query = f" {operator} ".join(f'"{keyword}"' for keyword in keywords)
        
        return self.search(query, max_results=max_results)
    
    def search_recent(self,
                     query: str,
                     days: int = 30,
                     max_results: int = 100) -> SearchResult:
        """
        Search for recent articles (within specified days)
        
        Args:
            query: Search query
            days: Number of days back to search
            max_results: Maximum results to retrieve
            
        Returns:
            SearchResult containing matched articles
        """
        # Add date filter to query
        date_query = f'({query}) AND ("last {days} days"[PDat])'
        
        return self.search(date_query, max_results=max_results)
    
    def search_by_disease_bacteria(self,
                                  disease: str,
                                  bacteria: str = None,
                                  max_results: int = 100) -> SearchResult:
        """
        Search for articles about disease-bacteria relationships
        
        Args:
            disease: Disease name
            bacteria: Bacteria name (optional)
            max_results: Maximum results to retrieve
            
        Returns:
            SearchResult containing matched articles
        """
        if bacteria:
            query = f'("{disease}") AND ("{bacteria}") AND (bacteria OR infection OR microbiome)'
        else:
            query = f'("{disease}") AND (bacteria OR infection OR microbiome OR pathogen)'
        
        return self.search(query, max_results=max_results)


def create_pubmed_searcher(tool: str = None, email: str = None) -> PubMedSearcher:
    """
    Create a configured PubMed searcher
    
    Args:
        tool: Tool name (defaults to environment variable)
        email: Email address (defaults to environment variable)
        
    Returns:
        Configured PubMedSearcher instance
    """
    return PubMedSearcher(tool=tool, email=email)
