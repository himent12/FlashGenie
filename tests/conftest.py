"""
Pytest configuration and fixtures for FlashGenie tests.

This module provides common test fixtures and configuration
for the FlashGenie test suite.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_flashcard():
    """Create a sample flashcard for testing."""
    return Flashcard(
        question="What is the capital of France?",
        answer="Paris",
        tags=["geography", "europe"]
    )


@pytest.fixture
def sample_flashcards():
    """Create a list of sample flashcards for testing."""
    return [
        Flashcard("What is 2 + 2?", "4", tags=["math"]),
        Flashcard("What is the capital of Spain?", "Madrid", tags=["geography"]),
        Flashcard("Who wrote Romeo and Juliet?", "William Shakespeare", tags=["literature"]),
    ]


@pytest.fixture
def sample_deck(sample_flashcards):
    """Create a sample deck for testing."""
    return Deck(
        name="Test Deck",
        description="A deck for testing",
        flashcards=sample_flashcards,
        tags=["test"]
    )


@pytest.fixture
def csv_content():
    """Sample CSV content for import testing."""
    return """question,answer
What is the capital of France?,Paris
What is 2 + 2?,4
Who wrote Hamlet?,William Shakespeare"""


@pytest.fixture
def txt_content():
    """Sample TXT content for import testing."""
    return """Q: What is the capital of Italy?
A: Rome

Q: What is 3 + 3?
A: 6

Q: Who painted the Mona Lisa?
A: Leonardo da Vinci"""


@pytest.fixture
def csv_file(temp_dir, csv_content):
    """Create a temporary CSV file for testing."""
    csv_file = temp_dir / "test.csv"
    csv_file.write_text(csv_content)
    return csv_file


@pytest.fixture
def txt_file(temp_dir, txt_content):
    """Create a temporary TXT file for testing."""
    txt_file = temp_dir / "test.txt"
    txt_file.write_text(txt_content)
    return txt_file
