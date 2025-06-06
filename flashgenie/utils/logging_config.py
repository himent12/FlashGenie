"""
Logging configuration for FlashGenie.

This module provides centralized logging configuration
and utilities for the application.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from flashgenie.config import LOGGING_CONFIG, DATA_DIR


def setup_logging(log_level: str = None, log_file: Path = None) -> logging.Logger:
    """
    Set up logging configuration for FlashGenie.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (uses config default if None)
        
    Returns:
        Configured logger instance
    """
    # Use config defaults if not provided
    if log_level is None:
        log_level = LOGGING_CONFIG["level"]
    
    if log_file is None:
        log_file = LOGGING_CONFIG["log_file"]
    
    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("flashgenie")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(LOGGING_CONFIG["format"])
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (uses 'flashgenie' if None)
        
    Returns:
        Logger instance
    """
    if name is None:
        name = "flashgenie"
    
    return logging.getLogger(name)


def log_performance(func):
    """
    Decorator to log function performance.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.3f}s")
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper


def log_method_calls(cls):
    """
    Class decorator to log all method calls.
    
    Args:
        cls: Class to decorate
        
    Returns:
        Decorated class
    """
    logger = get_logger()
    
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        
        if callable(attr) and not attr_name.startswith('_'):
            setattr(cls, attr_name, log_performance(attr))
    
    return cls


class LoggingMixin:
    """
    Mixin class to add logging capabilities to any class.
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(f"flashgenie.{self.__class__.__name__}")
    
    def log_debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def log_info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, *args, **kwargs)
    
    def log_warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def log_error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, *args, **kwargs)
    
    def log_critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)


def configure_third_party_loggers() -> None:
    """Configure logging for third-party libraries."""
    # Reduce verbosity of third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def create_session_logger(session_id: str) -> logging.Logger:
    """
    Create a logger for a specific quiz session.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Session-specific logger
    """
    logger_name = f"flashgenie.session.{session_id}"
    logger = logging.getLogger(logger_name)
    
    # Create session log file
    session_log_file = DATA_DIR / "sessions" / f"session_{session_id}.log"
    session_log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Add file handler for this session
    handler = logging.FileHandler(session_log_file)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    return logger
