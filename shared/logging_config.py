"""
shared/logging_config.py - Centralized logging configuration for both services
"""

import os
import logging
from logging.handlers import RotatingFileHandler
import sys

def configure_logging(name, log_dir="logs"):
    """Configure logging for application components
    
    Args:
        name: The logger name (typically the module name)
        log_dir: Directory to store log files
        
    Returns:
        A configured logger instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Get logger
    logger = logging.getLogger(name)
    
    # Set base level
    level = logging.INFO
    if os.getenv("DEBUG", "").lower() in ("true", "1", "yes"):
        level = logging.DEBUG
    logger.setLevel(level)
    
    # File handler with rotation (keep logs manageable)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, f"{name}.log"),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # Add handlers if not already added
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger