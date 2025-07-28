#!/usr/bin/env python3
"""
Mendelian Randomization Agent Module

This module provides LLM-powered automated agents for causal knowledge discovery
in disease research via Mendelian Randomization (MR).
"""

try:
    from .core import MRAgent as _MRAgent, MRAgentOE as _MRAgentOE
except ImportError as e:
    raise ImportError(f"Failed to import MRAgent components: {e}. Make sure all dependencies are installed.")

from ..common import BaseAgent


class MRAgent(_MRAgent, BaseAgent):
    """
    Enhanced MRAgent with unified base class
    
    Inherits from both the original MRAgent and BaseAgent for consistency
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize MRAgent with enhanced features"""
        # Initialize the original MRAgent
        _MRAgent.__init__(self, *args, **kwargs)
        
        # Don't call BaseAgent.__init__ as it conflicts with MRAgent's initialization
        # Instead, just setup logging
        import logging
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_info(self) -> dict:
        """Get agent information"""
        return {
            "agent_type": "MRAgent",
            "mode": self.mode,
            "outcome": self.outcome,
            "exposure": self.exposure,
            "model": self.LLM_model,
            "model_type": getattr(self, 'model_type', 'openai'),
            "bidirectional": self.bidirectional,
            "synonyms": self.synonyms
        }


class MRAgentOE(_MRAgentOE, BaseAgent):
    """
    Enhanced MRAgentOE with unified base class
    
    Inherits from both the original MRAgentOE and BaseAgent for consistency
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize MRAgentOE with enhanced features"""
        # Initialize the original MRAgentOE
        _MRAgentOE.__init__(self, *args, **kwargs)
        
        # Don't call BaseAgent.__init__ as it conflicts with MRAgentOE's initialization
        # Instead, just setup logging
        import logging
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_info(self) -> dict:
        """Get agent information"""
        return {
            "agent_type": "MRAgentOE",
            "mode": self.mode,
            "outcome": self.outcome,
            "exposure": self.exposure,
            "model": self.LLM_model,
            "model_type": getattr(self, 'model_type', 'openai'),
            "bidirectional": self.bidirectional,
            "synonyms": self.synonyms
        }


# Convenience functions
def create_mr_agent(outcome: str, **kwargs) -> MRAgent:
    """
    Create MRAgent for Knowledge Discovery mode
    
    Args:
        outcome: Disease outcome to analyze
        **kwargs: Additional parameters
        
    Returns:
        MRAgent: Configured MRAgent instance
    """
    return MRAgent(outcome=outcome, **kwargs)


def create_mr_agent_oe(exposure: str, outcome: str, **kwargs) -> MRAgentOE:
    """
    Create MRAgentOE for Causal Validation mode
    
    Args:
        exposure: Exposure variable
        outcome: Outcome variable
        **kwargs: Additional parameters
        
    Returns:
        MRAgentOE: Configured MRAgentOE instance
    """
    return MRAgentOE(exposure=exposure, outcome=outcome, **kwargs)


__all__ = [
    "MRAgent",
    "MRAgentOE",
    "create_mr_agent",
    "create_mr_agent_oe",
] 