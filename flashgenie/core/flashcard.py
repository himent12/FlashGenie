"""
Flashcard data model for FlashGenie.

This module defines the core Flashcard class that represents individual
flashcards with their content, metadata, and spaced repetition data.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
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
    
    def mark_reviewed(self, correct: bool, quality: int = 3) -> None:
        """
        Mark the card as reviewed and update spaced repetition data.
        
        Args:
            correct: Whether the answer was correct
            quality: Quality of response (0-5, SM-2 algorithm)
        """
        self.last_reviewed = datetime.now()
        self.review_count += 1
        
        if correct:
            self.correct_count += 1
        
        # Update difficulty based on performance
        if correct:
            self.difficulty = max(0.0, self.difficulty - 0.1)
        else:
            self.difficulty = min(1.0, self.difficulty + 0.2)
        
        # TODO: Implement full SM-2 algorithm for next_review calculation
        # For now, use simple interval based on difficulty
        if correct:
            interval_days = max(1, int(self.ease_factor * (1 - self.difficulty)))
        else:
            interval_days = 1  # Review again tomorrow if incorrect
        
        self.next_review = datetime.now() + timedelta(days=interval_days)
    
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
        
        return cls(
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
    
    def __str__(self) -> str:
        """String representation of the flashcard."""
        return f"Flashcard(Q: {self.question[:50]}..., A: {self.answer[:50]}...)"
    
    def __repr__(self) -> str:
        """Detailed string representation of the flashcard."""
        return (f"Flashcard(id={self.card_id}, question='{self.question}', "
                f"answer='{self.answer}', difficulty={self.difficulty:.2f})")
