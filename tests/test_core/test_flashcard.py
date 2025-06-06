"""
Tests for the Flashcard class.

This module contains unit tests for the core Flashcard functionality
including creation, validation, and spaced repetition data.
"""

import pytest
from datetime import datetime, timedelta

from flashgenie.core.flashcard import Flashcard
from flashgenie.utils.exceptions import ValidationError


class TestFlashcard:
    """Test cases for the Flashcard class."""
    
    def test_flashcard_creation(self):
        """Test basic flashcard creation."""
        card = Flashcard("What is 2 + 2?", "4")
        
        assert card.question == "What is 2 + 2?"
        assert card.answer == "4"
        assert card.difficulty == 0.5
        assert card.ease_factor == 2.5
        assert card.review_count == 0
        assert card.correct_count == 0
        assert isinstance(card.card_id, str)
        assert isinstance(card.created_at, datetime)
    
    def test_flashcard_with_tags(self):
        """Test flashcard creation with tags."""
        card = Flashcard("Test question", "Test answer", tags=["math", "basic"])
        
        assert card.tags == ["math", "basic"]
    
    def test_empty_question_raises_error(self):
        """Test that empty question raises ValidationError."""
        with pytest.raises(ValueError, match="Question cannot be empty"):
            Flashcard("", "Answer")
    
    def test_empty_answer_raises_error(self):
        """Test that empty answer raises ValidationError."""
        with pytest.raises(ValueError, match="Answer cannot be empty"):
            Flashcard("Question", "")
    
    def test_invalid_difficulty_raises_error(self):
        """Test that invalid difficulty raises ValidationError."""
        with pytest.raises(ValueError, match="Difficulty must be between 0.0 and 1.0"):
            Flashcard("Question", "Answer", difficulty=1.5)
    
    def test_accuracy_calculation(self):
        """Test accuracy calculation."""
        card = Flashcard("Test", "Test")
        
        # No reviews yet
        assert card.accuracy == 0.0
        
        # Simulate some reviews
        card.review_count = 10
        card.correct_count = 7
        assert card.accuracy == 0.7
    
    def test_is_due_property(self):
        """Test the is_due property."""
        card = Flashcard("Test", "Test")
        
        # New card should be due
        assert card.is_due
        
        # Card scheduled for future should not be due
        card.next_review = datetime.now() + timedelta(days=1)
        assert not card.is_due
        
        # Card scheduled for past should be due
        card.next_review = datetime.now() - timedelta(days=1)
        assert card.is_due
    
    def test_mark_reviewed_correct(self):
        """Test marking a card as reviewed correctly."""
        card = Flashcard("Test", "Test")
        initial_difficulty = card.difficulty
        
        card.mark_reviewed(correct=True, quality=4)
        
        assert card.review_count == 1
        assert card.correct_count == 1
        assert card.last_reviewed is not None
        assert card.difficulty < initial_difficulty  # Should decrease
        assert card.next_review > datetime.now()
    
    def test_mark_reviewed_incorrect(self):
        """Test marking a card as reviewed incorrectly."""
        card = Flashcard("Test", "Test")
        initial_difficulty = card.difficulty
        
        card.mark_reviewed(correct=False, quality=1)
        
        assert card.review_count == 1
        assert card.correct_count == 0
        assert card.last_reviewed is not None
        assert card.difficulty > initial_difficulty  # Should increase
    
    def test_to_dict_conversion(self):
        """Test conversion to dictionary."""
        card = Flashcard("Test question", "Test answer", tags=["test"])
        card_dict = card.to_dict()
        
        assert card_dict["question"] == "Test question"
        assert card_dict["answer"] == "Test answer"
        assert card_dict["tags"] == ["test"]
        assert "card_id" in card_dict
        assert "created_at" in card_dict
    
    def test_from_dict_conversion(self):
        """Test creation from dictionary."""
        card_data = {
            "card_id": "test-id",
            "question": "Test question",
            "answer": "Test answer",
            "created_at": datetime.now().isoformat(),
            "next_review": datetime.now().isoformat(),
            "difficulty": 0.3,
            "ease_factor": 2.2,
            "review_count": 5,
            "correct_count": 4,
            "tags": ["test"],
            "metadata": {}
        }
        
        card = Flashcard.from_dict(card_data)
        
        assert card.card_id == "test-id"
        assert card.question == "Test question"
        assert card.answer == "Test answer"
        assert card.difficulty == 0.3
        assert card.ease_factor == 2.2
        assert card.review_count == 5
        assert card.correct_count == 4
        assert card.tags == ["test"]
    
    def test_string_representation(self):
        """Test string representation of flashcard."""
        card = Flashcard("Short question", "Short answer")
        
        str_repr = str(card)
        assert "Short question" in str_repr
        assert "Short answer" in str_repr
        
        repr_str = repr(card)
        assert "Flashcard" in repr_str
        assert card.card_id in repr_str
