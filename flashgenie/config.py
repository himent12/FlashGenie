"""
Configuration settings for FlashGenie application.

This module contains all configuration constants and settings used throughout
the application, including file paths, algorithm parameters, and UI settings.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Application settings
APP_NAME = "FlashGenie"
APP_VERSION = "1.8.3"

# File paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DECKS_DIR = DATA_DIR / "decks"
SESSIONS_DIR = DATA_DIR / "sessions"
EXPORTS_DIR = DATA_DIR / "exports"
IMPORTS_DIR = DATA_DIR / "imports"

# Ensure data directories exist
try:
    for directory in [DATA_DIR, DECKS_DIR, SESSIONS_DIR, EXPORTS_DIR, IMPORTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
except PermissionError:
    # Fallback to user directory if we can't create in project directory
    import tempfile
    DATA_DIR = Path(tempfile.gettempdir()) / "flashgenie"
    DECKS_DIR = DATA_DIR / "decks"
    SESSIONS_DIR = DATA_DIR / "sessions"
    EXPORTS_DIR = DATA_DIR / "exports"
    IMPORTS_DIR = DATA_DIR / "imports"

    for directory in [DATA_DIR, DECKS_DIR, SESSIONS_DIR, EXPORTS_DIR, IMPORTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

# Spaced repetition algorithm settings
SPACED_REPETITION_CONFIG: Dict[str, Any] = {
    "initial_interval": 1,  # days
    "easy_factor": 2.5,
    "minimum_factor": 1.3,
    "factor_change": 0.1,
    "minimum_interval": 1,  # days
    "maximum_interval": 365,  # days
}

# Quiz settings
QUIZ_CONFIG: Dict[str, Any] = {
    "max_questions_per_session": 50,
    "show_progress": True,
    "case_sensitive": False,
    "allow_partial_answers": True,
}

# File format settings
SUPPORTED_IMPORT_FORMATS = [".csv", ".txt"]
SUPPORTED_EXPORT_FORMATS = [".csv", ".json"]

# CSV import settings
CSV_CONFIG: Dict[str, Any] = {
    "default_delimiter": ",",
    "default_encoding": "utf-8",
    "question_column": "question",
    "answer_column": "answer",
}

# TXT import settings
TXT_CONFIG: Dict[str, Any] = {
    "question_prefix": "Q:",
    "answer_prefix": "A:",
    "default_encoding": "utf-8",
}

# Terminal UI settings
TERMINAL_CONFIG: Dict[str, Any] = {
    "use_colors": True,
    "clear_screen": True,
    "show_statistics": True,
}

# Logging settings
LOGGING_CONFIG: Dict[str, Any] = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": DATA_DIR / "flashgenie.log",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
}

# Performance settings
PERFORMANCE_CONFIG: Dict[str, Any] = {
    "enable_monitoring": True,
    "cache_size": 1000,
    "memory_threshold_mb": 500,
    "execution_time_threshold": 1.0,
    "auto_optimize_memory": True,
    "lazy_loading": True,
    "batch_size": 100,
}

# Security settings
SECURITY_CONFIG: Dict[str, Any] = {
    "enable_input_validation": True,
    "max_file_size_mb": 100,
    "allowed_file_extensions": [".csv", ".txt", ".json"],
    "enable_plugin_sandboxing": True,
    "max_plugin_memory_mb": 50,
    "plugin_timeout_seconds": 30,
}

# Plugin system settings
PLUGIN_CONFIG: Dict[str, Any] = {
    "plugin_dir": DATA_DIR / "plugins",
    "marketplace_url": "https://plugins.flashgenie.com",
    "auto_update_plugins": False,
    "enable_hot_reload": True,
    "max_concurrent_plugins": 10,
}
