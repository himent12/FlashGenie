"""
FlashGenie v1.0 - Intelligent Flashcard Application

An advanced flashcard application with adaptive spaced repetition algorithms,
smart difficulty adjustment, and intelligent tagging for optimized learning.

Features:
- Smart difficulty auto-adjustment based on performance
- Hierarchical tagging with auto-categorization
- Smart collections for dynamic card grouping
- Enhanced spaced repetition with confidence tracking
- Comprehensive analytics and progress tracking
"""

__version__ = "1.0.0"
__author__ = "FlashGenie Team"
__email__ = "huckflower@gmail.com"

# Core imports for easy access
from flashgenie.core.content_system.flashcard import Flashcard
from flashgenie.core.content_system.deck import Deck
from flashgenie.core.study_system.quiz_engine import QuizEngine
from flashgenie.core.content_system.difficulty_analyzer import DifficultyAnalyzer
from flashgenie.core.content_system.tag_manager import TagManager
from flashgenie.core.content_system.smart_collections import SmartCollectionManager
# from flashgenie.data.storage import DataStorage  # Temporarily disabled due to import issues

__all__ = [
    "Flashcard",
    "Deck",
    "QuizEngine",
    "DifficultyAnalyzer",
    "TagManager",
    "SmartCollectionManager",
    # "DataStorage",  # Temporarily disabled
]
