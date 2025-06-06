"""
FlashGenie - A powerful and beginner-friendly flashcard app with spaced repetition.

This package provides tools for creating, managing, and studying flashcards
using scientifically-backed spaced repetition algorithms.
"""

__version__ = "0.1.0"
__author__ = "FlashGenie Team"
__email__ = "huckflower@gmail.com"

from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck
from flashgenie.core.quiz_engine import QuizEngine

__all__ = ["Flashcard", "Deck", "QuizEngine"]
