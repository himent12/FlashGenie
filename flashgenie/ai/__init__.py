"""
AI-Powered Features for FlashGenie v1.8.5 Phase 3.

This module provides AI-powered content generation, smart suggestions,
and intelligent analysis for enhanced learning experiences.
"""

from .content_generator import (
    AIContentGenerator,
    ContentType,
    DifficultyLevel,
    GeneratedContent
)

__version__ = "1.8.5"

__all__ = [
    "AIContentGenerator",
    "ContentType", 
    "DifficultyLevel",
    "GeneratedContent"
]
