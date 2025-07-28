#!/usr/bin/env python3
"""
Exception classes for MedLitAnno package
"""


class MedLitAnnoError(Exception):
    """Base exception for MedLitAnno package"""
    pass


class AnnotationError(MedLitAnnoError):
    """Exception raised during annotation process"""
    pass


class MRAgentError(MedLitAnnoError):
    """Exception raised in MRAgent operations"""
    pass


class LLMError(MedLitAnnoError):
    """Exception raised during LLM operations"""
    pass


class ConfigError(MedLitAnnoError):
    """Exception raised for configuration issues"""
    pass


class DataProcessingError(MedLitAnnoError):
    """Exception raised during data processing"""
    pass


class ValidationError(MedLitAnnoError):
    """Exception raised during validation"""
    pass


class NetworkError(MedLitAnnoError):
    """Exception raised for network-related issues"""
    pass


class FileError(MedLitAnnoError):
    """Exception raised for file operations"""
    pass


class APIError(MedLitAnnoError):
    """Exception raised for API-related issues"""
    pass 