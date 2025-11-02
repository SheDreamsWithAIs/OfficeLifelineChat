"""
Logging configuration for agent debugging and tracing.

Provides structured logging with console output for debugging agent behavior,
tool calls, and structured responses.
"""

import logging
import sys
from typing import Any, Optional


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging configuration with console handler.
    
    Args:
        level: Logging level (default: INFO)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("officelifeline")
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '[%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(f"officelifeline.{name}")
    if not logger.handlers:
        # Ensure parent logger is set up
        setup_logging()
    return logger


def log_dict_keys(logger: logging.Logger, data: dict, prefix: str = ""):
    """
    Log dictionary keys for debugging.
    
    Args:
        logger: Logger instance
        data: Dictionary to inspect
        prefix: Optional prefix for log message
    """
    keys = list(data.keys())
    msg = f"{prefix}Result keys={keys}" if prefix else f"Result keys={keys}"
    logger.info(msg)


def log_truncated(logger: logging.Logger, data: Any, prefix: str = "", max_chars: int = 200):
    """
    Log truncated string data.
    
    Args:
        logger: Logger instance
        data: Data to log (will be converted to string)
        prefix: Optional prefix for log message
        max_chars: Maximum characters to show
    """
    text = str(data)
    if len(text) > max_chars:
        truncated = text[:max_chars] + "..."
        length_info = f" (length={len(text)} chars)"
    else:
        truncated = text
        length_info = ""
    
    msg = f"{prefix}{truncated}{length_info}" if prefix else f"{truncated}{length_info}"
    logger.info(msg)

