#!/usr/bin/env python3
"""
Unified LLM client for MedLitAnno package
"""

import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from openai import OpenAI

from .exceptions import LLMError


@dataclass
class LLMConfig:
    """Configuration for LLM client"""
    api_key: str
    model: str = "gpt-4o"
    model_type: str = "openai"
    base_url: Optional[str] = None
    max_retries: int = 3
    retry_delay: int = 5
    temperature: float = 0.1
    max_tokens: int = 2000
    top_p: float = 1.0


class LLMClient:
    """Unified LLM client supporting multiple providers"""
    
    def __init__(self, config: LLMConfig):
        """Initialize LLM client with configuration"""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize client based on model type
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the appropriate client"""
        if self.config.model_type == "openai":
            self.client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            ) if self.config.base_url else OpenAI(api_key=self.config.api_key)
            
        elif self.config.model_type == "deepseek":
            self.client = OpenAI(
                api_key=self.config.api_key,
                base_url="https://api.deepseek.com/v1"
            )
            # Set default model if not specified
            if self.config.model == "gpt-4o":
                self.config.model = "deepseek-chat"
                
        elif self.config.model_type == "deepseek-reasoner":
            self.client = OpenAI(
                api_key=self.config.api_key,
                base_url="https://api.deepseek.com/v1"
            )
            # Use reasoner model
            if self.config.model in ["gpt-4o", "deepseek-chat"]:
                self.config.model = "deepseek-reasoner"
                
        elif self.config.model_type == "qianwen":
            self.client = OpenAI(
                api_key=self.config.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
            # Set default model if not specified
            if self.config.model == "gpt-4o":
                self.config.model = "qwen-plus"
                
        else:
            raise LLMError(f"Unsupported model type: {self.config.model_type}")
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       **kwargs) -> str:
        """
        Get chat completion from LLM
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters
            
        Returns:
            str: LLM response content
        """
        # Merge config with kwargs
        params = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "top_p": kwargs.get("top_p", self.config.top_p),
        }
        
        # Adjust parameters for deepseek-reasoner
        if self.config.model_type == "deepseek-reasoner":
            params["temperature"] = kwargs.get("temperature", 0.2)
            params["max_tokens"] = kwargs.get("max_tokens", 3000)
            params["top_p"] = kwargs.get("top_p", 0.9)
        
        # Retry logic
        for attempt in range(self.config.max_retries):
            try:
                response = self.client.chat.completions.create(**params)
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                self.logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    raise LLMError(f"LLM call failed after {self.config.max_retries} attempts: {e}")
    
    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        Get embeddings for texts (if supported)
        
        Args:
            texts: List of texts to embed
            **kwargs: Additional parameters
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if self.config.model_type not in ["openai"]:
            raise LLMError(f"Embeddings not supported for model type: {self.config.model_type}")
        
        try:
            response = self.client.embeddings.create(
                model=kwargs.get("embedding_model", "text-embedding-ada-002"),
                input=texts
            )
            return [data.embedding for data in response.data]
            
        except Exception as e:
            raise LLMError(f"Embedding generation failed: {e}")
    
    def validate_connection(self) -> bool:
        """
        Validate connection to LLM service
        
        Returns:
            bool: True if connection is valid
        """
        try:
            test_messages = [
                {"role": "user", "content": "Hello"}
            ]
            response = self.chat_completion(test_messages)
            return len(response) > 0
            
        except Exception as e:
            self.logger.error(f"Connection validation failed: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model
        
        Returns:
            Dict[str, Any]: Model information
        """
        return {
            "model": self.config.model,
            "model_type": self.config.model_type,
            "base_url": self.config.base_url,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
        }
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration parameters
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Re-initialize client if model type changed
        if "model_type" in kwargs or "base_url" in kwargs:
            self._initialize_client()


class LLMManager:
    """Manager for multiple LLM clients"""
    
    def __init__(self):
        """Initialize LLM manager"""
        self.clients: Dict[str, LLMClient] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_client(self, name: str, config: LLMConfig) -> None:
        """
        Add a new LLM client
        
        Args:
            name: Client name
            config: LLM configuration
        """
        self.clients[name] = LLMClient(config)
        self.logger.info(f"Added LLM client: {name}")
    
    def get_client(self, name: str) -> LLMClient:
        """
        Get LLM client by name
        
        Args:
            name: Client name
            
        Returns:
            LLMClient: The requested client
        """
        if name not in self.clients:
            raise LLMError(f"LLM client '{name}' not found")
        return self.clients[name]
    
    def remove_client(self, name: str) -> None:
        """
        Remove LLM client
        
        Args:
            name: Client name
        """
        if name in self.clients:
            del self.clients[name]
            self.logger.info(f"Removed LLM client: {name}")
    
    def list_clients(self) -> List[str]:
        """
        List all client names
        
        Returns:
            List[str]: List of client names
        """
        return list(self.clients.keys())
    
    def validate_all_connections(self) -> Dict[str, bool]:
        """
        Validate all client connections
        
        Returns:
            Dict[str, bool]: Validation results for each client
        """
        results = {}
        for name, client in self.clients.items():
            results[name] = client.validate_connection()
        return results 