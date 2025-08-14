#!/usr/bin/env python3
"""
MedLitAnno - Medical Literature Analysis and Annotation System

A comprehensive Python package for automated medical literature analysis,
annotation, and causal inference using Large Language Models (LLMs) and
Mendelian Randomization (MR).

Main Components:
- annotation: LLM-powered medical literature annotation
- mragent: Mendelian Randomization analysis agent (based on https://github.com/xuwei1997/MRAgent)
- common: Shared utilities and base classes
"""

__version__ = "1.1.0"
__author__ = "Chen Xingqiang"
__email__ = "joy66777@gmail.com"

# Import main classes for easy access
try:
    from .annotation import (
        MedicalAnnotationLLM,
        Entity,
        Evidence,
        Relation,
        AnnotationResult,
        batch_process_directory
    )
    _ANNOTATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Annotation module not available: {e}")
    _ANNOTATION_AVAILABLE = False

try:
    from .pubmed import (
        PubMedSearcher,
        PubMedArticle,
        SearchResult,
        PubMedAnnotationPipeline,
        search_and_annotate
    )
    _PUBMED_AVAILABLE = True
except ImportError as e:
    print(f"Warning: PubMed module not available: {e}")
    _PUBMED_AVAILABLE = False

try:
    from .mragent import (
        MRAgent,
        MRAgentOE
    )
    _MRAGENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: MRAgent module not available: {e}")
    _MRAGENT_AVAILABLE = False

from .common import (
    LLMClient,
    BaseAnnotator,
    BaseAgent
)

# Package metadata
__all__ = [
    # Common classes (always available)
    "LLMClient",
    "BaseAnnotator",
    "BaseAgent",

    # Package info
    "__version__",
    "__author__",
    "__email__",
]

# Add annotation classes if available
if _ANNOTATION_AVAILABLE:
    __all__.extend([
        "MedicalAnnotationLLM",
        "Entity",
        "Evidence",
        "Relation",
        "AnnotationResult",
        "batch_process_directory",
    ])

# Add PubMed classes if available
if _PUBMED_AVAILABLE:
    __all__.extend([
        "PubMedSearcher",
        "PubMedArticle",
        "SearchResult",
        "PubMedAnnotationPipeline",
        "search_and_annotate",
    ])

# Add MRAgent classes if available
if _MRAGENT_AVAILABLE:
    __all__.extend([
        "MRAgent",
        "MRAgentOE",
    ])

# Package configuration
DEFAULT_CONFIG = {
    "annotation": {
        "max_retries": 3,
        "retry_delay": 5,
        "default_model": "deepseek-chat",
        "default_model_type": "deepseek"
    },
    "pubmed": {
        "default_max_results": 50,
        "rate_limit": 1.0,
        "default_tool": "medlitanno"
    },
    "mragent": {
        "default_model": "gpt-4o",
        "default_num_articles": 100,
        "opengwas_mode": "online"
    },
    "common": {
        "log_level": "INFO",
        "cache_enabled": True
    }
}