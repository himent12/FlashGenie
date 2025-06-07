"""
Flashcard data model for FlashGenie.

This module defines the core Flashcard class that represents individual
flashcards with their content, metadata, and spaced repetition data.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import uuid


@dataclass
class Flashcard:
    """
    Represents a single flashcard with question, answer, and spaced repetition data.
    
    Attributes:
        question: The question or prompt text
        answer: The correct answer text
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
    answer: str
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
