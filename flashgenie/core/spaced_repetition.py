"""
Spaced repetition algorithm implementation for FlashGenie.

This module implements the SM-2 (SuperMemo 2) algorithm and related
spaced repetition functionality for optimal learning scheduling.
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from dataclasses import dataclass

from flashgenie.core.flashcard import Flashcard
from flashgenie.config import SPACED_REPETITION_CONFIG


@dataclass
class ReviewResult:
    """
    Represents the result of a flashcard review session.
    
    Attributes:
        quality: Quality of response (0-5 scale)
        response_time: Time taken to respond in seconds
        correct: Whether the answer was correct
        timestamp: When the review occurred
    """
    quality: int  # 0-5 scale (0=blackout, 5=perfect)
    response_time: float  # seconds
    correct: bool
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        if not 0 <= self.quality <= 5:
            raise ValueError("Quality must be between 0 and 5")


class SpacedRepetitionAlgorithm:
    """
    Implementation of the SM-2 spaced repetition algorithm.
    
    This algorithm optimizes the intervals between reviews based on the
    difficulty of each flashcard and the user's performance history.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the spaced repetition algorithm.
        
        Args:
            config: Configuration dictionary, uses default if None
        """
        self.config = config or SPACED_REPETITION_CONFIG.copy()
    
    def calculate_next_interval(self, flashcard: Flashcard, 
                               review_result: ReviewResult) -> int:
        """
        Calculate the next review interval using the SM-2 algorithm.
        
        Args:
            flashcard: The flashcard being reviewed
            review_result: The result of the review
            
        Returns:
            Next interval in days
        """
        quality = review_result.quality
        
        # If quality < 3, reset interval to 1 day
        if quality < 3:
            return self.config["minimum_interval"]
        
        # Calculate new ease factor
        new_ease_factor = self._calculate_ease_factor(
            flashcard.ease_factor, quality
        )
        
        # Calculate interval based on review count
        if flashcard.review_count == 0:
            interval = 1
        elif flashcard.review_count == 1:
            interval = 6
        else:
            # Get the previous interval (days since last review)
            if flashcard.last_reviewed:
                days_since_last = (datetime.now() - flashcard.last_reviewed).days
                previous_interval = max(1, days_since_last)
            else:
                previous_interval = self.config["initial_interval"]
            
            interval = int(previous_interval * new_ease_factor)
        
        # Apply constraints
        interval = max(self.config["minimum_interval"], interval)
        interval = min(self.config["maximum_interval"], interval)
        
        return interval
    
    def _calculate_ease_factor(self, current_ease_factor: float, 
                              quality: int) -> float:
        """
        Calculate the new ease factor based on response quality.
        
        Args:
            current_ease_factor: Current ease factor
            quality: Quality of response (0-5)
            
        Returns:
            New ease factor
        """
        # SM-2 formula: EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
        new_ease_factor = (
            current_ease_factor + 
            (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        )
        
        # Apply minimum constraint
        new_ease_factor = max(self.config["minimum_factor"], new_ease_factor)
        
        return new_ease_factor
    
    def update_flashcard(self, flashcard: Flashcard, 
                        review_result: ReviewResult) -> None:
        """
        Update a flashcard based on review results.
        
        Args:
            flashcard: The flashcard to update
            review_result: The result of the review
        """
        # Calculate next interval
        interval_days = self.calculate_next_interval(flashcard, review_result)
        
        # Update flashcard properties
        flashcard.last_reviewed = review_result.timestamp
        flashcard.next_review = review_result.timestamp + timedelta(days=interval_days)
        flashcard.review_count += 1
        
        if review_result.correct:
            flashcard.correct_count += 1
        
        # Update ease factor
        flashcard.ease_factor = self._calculate_ease_factor(
            flashcard.ease_factor, review_result.quality
        )
        
        # Update difficulty based on performance
        self._update_difficulty(flashcard, review_result)
    
    def _update_difficulty(self, flashcard: Flashcard, 
                          review_result: ReviewResult) -> None:
        """
        Update the difficulty rating of a flashcard.
        
        Args:
            flashcard: The flashcard to update
            review_result: The result of the review
        """
        # Adjust difficulty based on quality and response time
        quality_factor = (review_result.quality - 2.5) / 2.5  # -1 to 1
        
        # Response time factor (assuming 10 seconds is average)
        time_factor = min(1.0, review_result.response_time / 10.0)
        
        # Combine factors to adjust difficulty
        difficulty_change = -quality_factor * 0.1 + time_factor * 0.05
        
        # Update difficulty with constraints
        new_difficulty = flashcard.difficulty + difficulty_change
        flashcard.difficulty = max(0.0, min(1.0, new_difficulty))
    
    def get_review_priority(self, flashcard: Flashcard) -> float:
        """
        Calculate review priority for a flashcard.
        
        Higher priority means the card should be reviewed sooner.
        
        Args:
            flashcard: The flashcard to evaluate
            
        Returns:
            Priority score (higher = more urgent)
        """
        if not flashcard.is_due:
            return 0.0
        
        # Base priority on how overdue the card is
        days_overdue = (datetime.now() - flashcard.next_review).days
        overdue_priority = max(0, days_overdue) * 2
        
        # Add difficulty factor (harder cards get higher priority)
        difficulty_priority = flashcard.difficulty * 3
        
        # Add accuracy factor (cards with lower accuracy get higher priority)
        accuracy_priority = (1.0 - flashcard.accuracy) * 2
        
        return overdue_priority + difficulty_priority + accuracy_priority
    
    def suggest_study_session(self, flashcards: list[Flashcard], 
                             max_cards: int = 20) -> list[Flashcard]:
        """
        Suggest flashcards for a study session based on spaced repetition.
        
        Args:
            flashcards: List of available flashcards
            max_cards: Maximum number of cards to include
            
        Returns:
            List of flashcards sorted by review priority
        """
        # Filter due cards and calculate priorities
        due_cards = [card for card in flashcards if card.is_due]
        
        # Sort by priority (highest first)
        due_cards.sort(
            key=lambda card: self.get_review_priority(card),
            reverse=True
        )
        
        return due_cards[:max_cards]
    
    def get_algorithm_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the algorithm configuration.
        
        Returns:
            Dictionary with algorithm statistics
        """
        return {
            "algorithm": "SM-2",
            "config": self.config.copy(),
            "description": "SuperMemo 2 spaced repetition algorithm"
        }
