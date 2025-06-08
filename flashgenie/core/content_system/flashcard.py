"""
Flashcard data model for FlashGenie.

This module defines the core Flashcard class that represents individual
flashcards with their content, metadata, and spaced repetition data.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
import uuid
import re


@dataclass
class Flashcard:
    """
    Represents a single flashcard with question, answer(s), and spaced repetition data.

    Attributes:
        question: The question or prompt text
        answer: The primary correct answer text (for backward compatibility)
        valid_answers: List of all valid answers (including the primary answer)
        card_id: Unique identifier for the card
        created_at: When the card was created
        last_reviewed: When the card was last reviewed
        next_review: When the card should be reviewed next
        difficulty: Current difficulty level (0.0 to 1.0)
        ease_factor: Spaced repetition ease factor
        review_count: Number of times the card has been reviewed
        correct_count: Number of correct answers
        tags: Optional tags for categorization
        metadata: Additional metadata dictionary
    """
    
    question: str
    answer: str  # Primary answer for backward compatibility
    card_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    last_reviewed: Optional[datetime] = None
    next_review: datetime = field(default_factory=lambda: datetime.now())
    difficulty: float = 0.5  # 0.0 = easy, 1.0 = hard
    ease_factor: float = 2.5  # SM-2 algorithm ease factor
    review_count: int = 0
    correct_count: int = 0
    tags: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Multiple valid answers support
    valid_answers: List[str] = field(default_factory=list)

    # Enhanced difficulty tracking
    response_times: List[float] = field(default_factory=list)
    confidence_ratings: List[int] = field(default_factory=list)  # 1-5 scale
    difficulty_history: List[float] = field(default_factory=list)
    last_difficulty_update: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate flashcard data after initialization."""
        if not self.question.strip():
            raise ValueError("Question cannot be empty")
        if not self.answer.strip():
            raise ValueError("Answer cannot be empty")
        if not 0.0 <= self.difficulty <= 1.0:
            raise ValueError("Difficulty must be between 0.0 and 1.0")
        if self.ease_factor < 1.3:
            self.ease_factor = 1.3  # Minimum ease factor

        # Initialize valid_answers if empty (for backward compatibility)
        if not self.valid_answers:
            self.valid_answers = [self.answer]
        elif self.answer not in self.valid_answers:
            # Ensure primary answer is always in valid_answers
            self.valid_answers.insert(0, self.answer)
    
    @property
    def accuracy(self) -> float:
        """Calculate the accuracy rate for this card."""
        if self.review_count == 0:
            return 0.0
        return self.correct_count / self.review_count
    
    @property
    def is_due(self) -> bool:
        """Check if the card is due for review."""
        return datetime.now() >= self.next_review
    
    def mark_reviewed(self, correct: bool, quality: int = 3,
                     response_time: float = 0.0, confidence: Optional[int] = None) -> None:
        """
        Mark the card as reviewed and update spaced repetition data.

        Args:
            correct: Whether the answer was correct
            quality: Quality of response (0-5, SM-2 algorithm)
            response_time: Time taken to respond in seconds
            confidence: User confidence rating (1-5 scale)
        """
        self.last_reviewed = datetime.now()
        self.review_count += 1

        if correct:
            self.correct_count += 1

        # Store response time and confidence for analysis
        if response_time > 0:
            self.response_times.append(response_time)
            # Keep only last 20 response times to manage memory
            if len(self.response_times) > 20:
                self.response_times = self.response_times[-20:]

        if confidence is not None:
            self.confidence_ratings.append(confidence)
            # Keep only last 20 confidence ratings
            if len(self.confidence_ratings) > 20:
                self.confidence_ratings = self.confidence_ratings[-20:]

        # Store current difficulty in history before potential update
        self.difficulty_history.append(self.difficulty)
        if len(self.difficulty_history) > 10:
            self.difficulty_history = self.difficulty_history[-10:]

        # Basic difficulty adjustment (will be enhanced by DifficultyAnalyzer)
        if correct:
            self.difficulty = max(0.0, self.difficulty - 0.05)
        else:
            self.difficulty = min(1.0, self.difficulty + 0.1)

        # Implement SM-2 algorithm for next review calculation
        # For now, use simple interval based on difficulty
        if correct:
            interval_days = max(1, int(self.ease_factor * (1 - self.difficulty)))
        else:
            interval_days = 1  # Review again tomorrow if incorrect

        self.next_review = datetime.now() + timedelta(days=interval_days)

    def add_valid_answer(self, answer: str) -> None:
        """
        Add a new valid answer to this flashcard.

        Args:
            answer: The new valid answer to add
        """
        answer = answer.strip()
        if answer and answer not in self.valid_answers:
            self.valid_answers.append(answer)

    def remove_valid_answer(self, answer: str) -> bool:
        """
        Remove a valid answer from this flashcard.

        Args:
            answer: The answer to remove

        Returns:
            True if the answer was removed, False if it wasn't found
        """
        if answer in self.valid_answers:
            # Don't allow removing the primary answer if it's the only one
            if len(self.valid_answers) == 1 and answer == self.answer:
                return False

            self.valid_answers.remove(answer)

            # If we removed the primary answer, make the first valid answer the new primary
            if answer == self.answer and self.valid_answers:
                self.answer = self.valid_answers[0]

            return True
        return False

    def set_valid_answers(self, answers: List[str]) -> None:
        """
        Set all valid answers for this flashcard.

        Args:
            answers: List of valid answers
        """
        # Filter out empty answers and remove duplicates while preserving order
        valid_answers = []
        seen = set()
        for answer in answers:
            answer = answer.strip()
            if answer and answer not in seen:
                valid_answers.append(answer)
                seen.add(answer)

        if not valid_answers:
            raise ValueError("At least one valid answer is required")

        self.valid_answers = valid_answers
        # Set the first answer as the primary answer
        self.answer = valid_answers[0]

    def is_answer_correct(self, user_answer: str, case_sensitive: bool = False) -> bool:
        """
        Check if a user's answer matches any of the valid answers.

        Args:
            user_answer: The user's answer to check
            case_sensitive: Whether to perform case-sensitive matching

        Returns:
            True if the answer matches any valid answer, False otherwise
        """
        user_answer = user_answer.strip()

        for valid_answer in self.valid_answers:
            if case_sensitive:
                if user_answer == valid_answer:
                    return True
            else:
                if user_answer.lower() == valid_answer.lower():
                    return True

        return False

    def get_matching_answer(self, user_answer: str, case_sensitive: bool = False) -> Optional[str]:
        """
        Get the valid answer that matches the user's input.

        Args:
            user_answer: The user's answer to check
            case_sensitive: Whether to perform case-sensitive matching

        Returns:
            The matching valid answer, or None if no match found
        """
        user_answer = user_answer.strip()

        for valid_answer in self.valid_answers:
            if case_sensitive:
                if user_answer == valid_answer:
                    return valid_answer
            else:
                if user_answer.lower() == valid_answer.lower():
                    return valid_answer

        return None

    def update_difficulty(self, new_difficulty: float, reason: str = "") -> None:
        """
        Update the card's difficulty level with tracking.

        Args:
            new_difficulty: New difficulty level (0.0 to 1.0)
            reason: Optional reason for the change
        """
        if not 0.0 <= new_difficulty <= 1.0:
            raise ValueError("Difficulty must be between 0.0 and 1.0")

        # Store old difficulty in history
        self.difficulty_history.append(self.difficulty)
        if len(self.difficulty_history) > 10:
            self.difficulty_history = self.difficulty_history[-10:]

        # Update difficulty
        self.difficulty = new_difficulty
        self.last_difficulty_update = datetime.now()

        # Store reason in metadata
        if reason:
            if 'difficulty_updates' not in self.metadata:
                self.metadata['difficulty_updates'] = []
            self.metadata['difficulty_updates'].append({
                'timestamp': datetime.now().isoformat(),
                'old_difficulty': self.difficulty_history[-1] if self.difficulty_history else 0.5,
                'new_difficulty': new_difficulty,
                'reason': reason
            })

    @property
    def average_response_time(self) -> float:
        """Get average response time for this card."""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)

    @property
    def average_confidence(self) -> float:
        """Get average confidence rating for this card."""
        if not self.confidence_ratings:
            return 0.0
        return sum(self.confidence_ratings) / len(self.confidence_ratings)

    @property
    def difficulty_trend(self) -> float:
        """Calculate difficulty trend (positive = getting harder, negative = getting easier)."""
        if len(self.difficulty_history) < 2:
            return 0.0

        # Compare recent difficulty to earlier difficulty
        recent = self.difficulty_history[-3:] if len(self.difficulty_history) >= 3 else self.difficulty_history[-1:]
        earlier = self.difficulty_history[:-3] if len(self.difficulty_history) >= 6 else self.difficulty_history[:-1]

        if not earlier:
            return 0.0

        recent_avg = sum(recent) / len(recent)
        earlier_avg = sum(earlier) / len(earlier)

        return recent_avg - earlier_avg

    def to_dict(self) -> Dict[str, Any]:
        """Convert flashcard to dictionary for serialization."""
        return {
            "card_id": self.card_id,
            "question": self.question,
            "answer": self.answer,
            "valid_answers": self.valid_answers,
            "created_at": self.created_at.isoformat(),
            "last_reviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "next_review": self.next_review.isoformat(),
            "difficulty": self.difficulty,
            "ease_factor": self.ease_factor,
            "review_count": self.review_count,
            "correct_count": self.correct_count,
            "tags": self.tags,
            "metadata": self.metadata,
            "response_times": self.response_times,
            "confidence_ratings": self.confidence_ratings,
            "difficulty_history": self.difficulty_history,
            "last_difficulty_update": self.last_difficulty_update.isoformat() if self.last_difficulty_update else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Flashcard":
        """Create flashcard from dictionary."""
        # Parse datetime fields
        created_at = datetime.fromisoformat(data["created_at"])
        last_reviewed = None
        if data.get("last_reviewed"):
            last_reviewed = datetime.fromisoformat(data["last_reviewed"])
        next_review = datetime.fromisoformat(data["next_review"])

        last_difficulty_update = None
        if data.get("last_difficulty_update"):
            last_difficulty_update = datetime.fromisoformat(data["last_difficulty_update"])

        card = cls(
            card_id=data["card_id"],
            question=data["question"],
            answer=data["answer"],
            created_at=created_at,
            last_reviewed=last_reviewed,
            next_review=next_review,
            difficulty=data.get("difficulty", 0.5),
            ease_factor=data.get("ease_factor", 2.5),
            review_count=data.get("review_count", 0),
            correct_count=data.get("correct_count", 0),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )

        # Set enhanced difficulty tracking fields
        card.response_times = data.get("response_times", [])
        card.confidence_ratings = data.get("confidence_ratings", [])
        card.difficulty_history = data.get("difficulty_history", [])
        card.last_difficulty_update = last_difficulty_update

        # Set valid answers (with backward compatibility)
        card.valid_answers = data.get("valid_answers", [data["answer"]])

        return card
    
    def __str__(self) -> str:
        """String representation of the flashcard."""
        return f"Flashcard(Q: {self.question[:50]}..., A: {self.answer[:50]}...)"
    
    def __repr__(self) -> str:
        """Detailed string representation of the flashcard."""
        return (f"Flashcard(id={self.card_id}, question='{self.question}', "
                f"answer='{self.answer}', difficulty={self.difficulty:.2f})")

    def calculate_accuracy(self) -> float:
        """
        Calculate the accuracy rate for this flashcard.

        Returns:
            Accuracy rate as a float between 0.0 and 1.0
        """
        if self.review_count == 0:
            return 0.0
        return self.correct_count / self.review_count

    def is_due_for_review(self) -> bool:
        """
        Check if this flashcard is due for review.

        Returns:
            True if the card is due for review, False otherwise
        """
        if self.next_review is None:
            return True  # New cards are always due
        return datetime.now() >= self.next_review
