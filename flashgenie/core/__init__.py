"""
Core business logic for FlashGenie.

This package contains the fundamental data models and algorithms that power
the flashcard application, including flashcard management, spaced repetition,
and quiz functionality.
"""

from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck
from flashgenie.core.spaced_repetition import SpacedRepetitionAlgorithm
from flashgenie.core.quiz_engine import QuizEngine, QuizSession
from flashgenie.core.performance_tracker import PerformanceTracker

__all__ = [
    "Flashcard",
    "Deck", 
    "SpacedRepetitionAlgorithm",
    "QuizEngine",
    "QuizSession",
    "PerformanceTracker"
]
