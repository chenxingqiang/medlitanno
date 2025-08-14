#!/usr/bin/env python3
"""
Utility functions for MedLitAnno package
"""

import os
import json
import time
import logging
import functools
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from .exceptions import ConfigError, FileError


def timer(func):
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f'{func.__name__} cost time: {elapsed_time:.3f} s')
        return result
    return wrapper


def setup_logging(level: str = "INFO", 
                 log_file: Optional[str] = None,
                 format_string: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        level: Logging level
        log_file: Optional log file path
        format_string: Optional custom format string
        
    Returns:
        logging.Logger: Configured logger
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(),
            *([] if log_file is None else [logging.FileHandler(log_file)])
        ]
    )
    
    return logging.getLogger("medlitanno")


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        raise ConfigError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in configuration file: {e}")


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to JSON file
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
    """
    try:
        # Create directory if it doesn't exist
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise ConfigError(f"Failed to save configuration: {e}")


def save_results(results: List[Any], 
                output_path: str,
                format: str = "json") -> None:
    """
    Save results to file
    
    Args:
        results: Results to save
        output_path: Output file path
        format: Output format ('json', 'csv', 'xlsx')
    """
    try:
        # Create directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
                
        elif format.lower() == "csv":
            import pandas as pd
            if isinstance(results, list) and len(results) > 0:
                if isinstance(results[0], dict):
                    df = pd.DataFrame(results)
                    df.to_csv(output_path, index=False, encoding='utf-8')
                else:
                    raise FileError("CSV format requires list of dictionaries")
            else:
                # Create empty CSV
                pd.DataFrame().to_csv(output_path, index=False)
                
        elif format.lower() == "xlsx":
            import pandas as pd
            if isinstance(results, list) and len(results) > 0:
                if isinstance(results[0], dict):
                    df = pd.DataFrame(results)
                    df.to_excel(output_path, index=False)
                else:
                    raise FileError("Excel format requires list of dictionaries")
            else:
                # Create empty Excel file
                pd.DataFrame().to_excel(output_path, index=False)
        else:
            raise FileError(f"Unsupported format: {format}")
            
    except Exception as e:
        raise FileError(f"Failed to save results: {e}")


def load_results(file_path: str) -> List[Any]:
    """
    Load results from file
    
    Args:
        file_path: Path to results file
        
    Returns:
        List[Any]: Loaded results
    """
    try:
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == ".json":
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        elif file_ext == ".csv":
            import pandas as pd
            df = pd.read_csv(file_path)
            return df.to_dict('records')
            
        elif file_ext in [".xlsx", ".xls"]:
            import pandas as pd
            df = pd.read_excel(file_path)
            return df.to_dict('records')
            
        else:
            raise FileError(f"Unsupported file format: {file_ext}")
            
    except Exception as e:
        raise FileError(f"Failed to load results: {e}")


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if necessary
    
    Args:
        path: Directory path
        
    Returns:
        Path: Path object
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_timestamp() -> str:
    """
    Get current timestamp string
    
    Returns:
        str: Timestamp string
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def validate_api_key(api_key: Optional[str], service: str) -> str:
    """
    Validate and return API key
    
    Args:
        api_key: API key to validate
        service: Service name for error messages
        
    Returns:
        str: Valid API key
    """
    if not api_key:
        raise ConfigError(f"API key for {service} is required")
    
    if not isinstance(api_key, str) or len(api_key.strip()) == 0:
        raise ConfigError(f"Invalid API key for {service}")
    
    return api_key.strip()


def get_env_var(var_name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get environment variable with optional default
    
    Args:
        var_name: Environment variable name
        default: Default value if not found
        required: Whether the variable is required (raises error if not found)
        
    Returns:
        Optional[str]: Environment variable value or default
        
    Raises:
        ValueError: If required=True and variable is not found
    """
    value = os.getenv(var_name, default)
    
    if required and value is None:
        raise ValueError(f"Required environment variable '{var_name}' is not set")
    
    return value


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries recursively
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (overwrites dict1)
        
    Returns:
        Dict[str, Any]: Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    import re
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    return sanitized


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List[List[Any]]: List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f}{size_names[i]}"


def progress_bar(current: int, total: int, width: int = 50) -> str:
    """
    Generate a text progress bar
    
    Args:
        current: Current progress
        total: Total items
        width: Width of progress bar
        
    Returns:
        str: Progress bar string
    """
    if total == 0:
        return "[" + "=" * width + "] 100%"
    
    progress = current / total
    filled_width = int(width * progress)
    bar = "=" * filled_width + "-" * (width - filled_width)
    percentage = int(progress * 100)
    
    return f"[{bar}] {percentage}% ({current}/{total})" 