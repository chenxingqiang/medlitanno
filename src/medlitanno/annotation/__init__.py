#!/usr/bin/env python3
"""
Medical Literature Annotation Module

This module provides LLM-powered automated annotation for medical literature,
specializing in identifying bacteria-disease relationships.
"""

from .core import (
    Entity,
    Evidence,
    Relation,
    AnnotationResult,
    MedicalAnnotationLLM,
)

from .batch_processor import (
    batch_process_directory,
    BatchProcessor,
)

from .monitor import (
    ProgressMonitor,
    BatchMonitor,
)

from .converter import (
    LabelStudioConverter,
    convert_to_label_studio,
)

from .position_matcher import (
    TextPositionMatcher,
    MatchResult,
    create_position_matcher,
)

__all__ = [
    # Core classes
    "Entity",
    "Evidence", 
    "Relation",
    "AnnotationResult",
    "MedicalAnnotationLLM",
    
    # Batch processing
    "batch_process_directory",
    "BatchProcessor",
    
    # Monitoring
    "ProgressMonitor",
    "BatchMonitor",
    
    # Conversion utilities
    "LabelStudioConverter",
    "convert_to_label_studio",
    
    # Position matching
    "TextPositionMatcher",
    "MatchResult", 
    "create_position_matcher",
] 