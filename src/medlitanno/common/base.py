#!/usr/bin/env python3
"""
Base classes for MedLitAnno package
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path

from .exceptions import MedLitAnnoError, AnnotationError, MRAgentError
from .llm_client import LLMClient, LLMConfig


class BaseAnnotator(ABC):
    """Base class for all annotation systems"""
    
    def __init__(self, 
                 api_key: str,
                 model: str = "gpt-4o",
                 model_type: str = "openai",
                 base_url: Optional[str] = None,
                 max_retries: int = 3,
                 retry_delay: int = 5,
                 **kwargs):
        """
        Initialize base annotator
        
        Args:
            api_key: API key for LLM service
            model: Model name to use
            model_type: Type of model service
            base_url: Base URL for API (optional)
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
            **kwargs: Additional configuration
        """
        self.api_key = api_key
        self.model = model
        self.model_type = model_type
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Initialize LLM client
        self.llm_config = LLMConfig(
            api_key=api_key,
            model=model,
            model_type=model_type,
            base_url=base_url,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        self.llm_client = LLMClient(self.llm_config)
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def annotate_text(self, text: str, **kwargs) -> Any:
        """Annotate a single text"""
        pass
    
    @abstractmethod
    def batch_process(self, inputs: List[Any], **kwargs) -> List[Any]:
        """Process multiple inputs in batch"""
        pass
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data"""
        return True
    
    def save_results(self, results: List[Any], output_path: str) -> None:
        """Save results to file"""
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)


class BaseAgent(ABC):
    """Base class for all analysis agents"""
    
    def __init__(self,
                 ai_key: Optional[str] = None,
                 llm_model: str = "gpt-4o",
                 model_type: str = "openai",
                 base_url: Optional[str] = None,
                 **kwargs):
        """
        Initialize base agent
        
        Args:
            ai_key: API key for LLM service
            llm_model: LLM model name
            model_type: Type of model service
            base_url: Base URL for API
            **kwargs: Additional configuration
        """
        self.ai_key = ai_key or os.getenv("OPENAI_API_KEY")
        self.llm_model = llm_model
        self.model_type = model_type
        self.base_url = base_url
        
        # Initialize LLM client if API key is provided
        if self.ai_key:
            self.llm_config = LLMConfig(
                api_key=self.ai_key,
                model=llm_model,
                model_type=model_type,
                base_url=base_url
            )
            self.llm_client = LLMClient(self.llm_config)
        else:
            self.llm_client = None
            
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize paths
        self.define_path()
    
    @abstractmethod
    def define_path(self) -> None:
        """Define working paths"""
        pass
    
    @abstractmethod
    def run(self, **kwargs) -> Any:
        """Run the agent"""
        pass
    
    def setup_output_directory(self, base_path: str) -> Path:
        """Setup output directory"""
        output_path = Path(base_path)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    
    def call_llm(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call LLM with messages"""
        if not self.llm_client:
            raise MRAgentError("LLM client not initialized. Please provide API key.")
        
        return self.llm_client.chat_completion(messages, **kwargs)


@dataclass
class ProcessingResult:
    """Base result class for processing operations"""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[Exception] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": str(self.error) if self.error else None
        }


class BaseProcessor(ABC):
    """Base class for data processors"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize processor with config"""
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def process(self, input_data: Any) -> ProcessingResult:
        """Process input data"""
        pass
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        return True
    
    def setup(self) -> None:
        """Setup processor"""
        if not self.validate_config():
            raise MedLitAnnoError("Invalid configuration")
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        pass
    
    def __enter__(self):
        """Context manager entry"""
        self.setup()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
        return False 