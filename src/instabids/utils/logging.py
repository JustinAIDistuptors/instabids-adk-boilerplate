"""
Logging utilities for InstaBids.
"""
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import get_settings

# Configure default logging format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_LEVEL = logging.INFO

def setup_logger(
    name: str,
    log_level: int = None,
    log_format: str = DEFAULT_FORMAT,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Sets up a logger with the specified configuration.
    
    Args:
        name: The name of the logger
        log_level: The logging level (default: INFO)
        log_format: The logging format
        log_file: Optional path to a log file
        
    Returns:
        Configured logger instance
    """
    # Use default if log_level not specified
    if log_level is None:
        settings = get_settings()
        env = settings.environment
        # Use DEBUG level in development, INFO in other environments
        log_level = logging.DEBUG if env == "development" else DEFAULT_LOG_LEVEL
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logs_directory() -> Path:
    """
    Get the logs directory path, creating it if it doesn't exist.
    
    Returns:
        Path to the logs directory
    """
    # Use project root / logs
    logs_dir = Path(__file__).parent.parent.parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True, parents=True)
    return logs_dir

def get_default_logger() -> logging.Logger:
    """
    Get the default application logger.
    
    Returns:
        Default logger configured for the application
    """
    settings = get_settings()
    app_name = settings.app_name.lower()
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = get_logs_directory() / f"{app_name}_{timestamp}.log"
    
    return setup_logger(
        name=app_name,
        log_file=str(log_file)
    )

def get_agent_logger(agent_name: str) -> logging.Logger:
    """
    Get a logger specifically for an agent.
    
    Args:
        agent_name: The name of the agent
        
    Returns:
        Logger configured for the agent
    """
    settings = get_settings()
    app_name = settings.app_name.lower()
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = get_logs_directory() / f"{app_name}_{agent_name.lower()}_{timestamp}.log"
    
    return setup_logger(
        name=f"{app_name}.agents.{agent_name.lower()}",
        log_file=str(log_file)
    )