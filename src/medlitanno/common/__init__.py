#!/usr/bin/env python3
"""
Common utilities and base classes for MedLitAnno package
"""

from .base import (
    BaseAnnotator,
    BaseAgent,
    BaseProcessor,
    ProcessingResult,
)

from .llm_client import (
    LLMClient,
    LLMConfig,
)

from .utils import (
    timer,
    setup_logging,
    load_config,
    save_results,
    ensure_directory,
    get_env_var,
    validate_api_key,
)

from .exceptions import (
    MedLitAnnoError,
    AnnotationError,
    MRAgentError,
    LLMError,
    ConfigError,
)

__all__ = [
    # Base classes
    "BaseAnnotator",
    "BaseAgent",
    "BaseProcessor",
    "ProcessingResult",
    
    # LLM client
    "LLMClient", 
    "LLMConfig",
    
    # Utilities
    "timer",
    "setup_logging",
    "load_config",
    "save_results",
    "ensure_directory",
    "get_env_var",
    "validate_api_key",
    
    # Exceptions
    "MedLitAnnoError",
    "AnnotationError", 
    "MRAgentError",
    "LLMError",
    "ConfigError",
] 