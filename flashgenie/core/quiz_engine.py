"""
Quiz engine for FlashGenie.

This module manages quiz sessions, tracks progress, and coordinates
between the spaced repetition algorithm and user interface.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck
from flashgenie.core.spaced_repetition import SpacedRepetitionAlgorithm, ReviewResult
from flashgenie.config import QUIZ_CONFIG


class QuizMode(Enum):
    """Quiz mode enumeration."""
    SPACED_REPETITION = "spaced_repetition"
    RANDOM = "random"
    SEQUENTIAL = "sequential"
    DIFFICULT_FIRST = "difficult_first"


@dataclass
class QuizQuestion:
    """
    Represents a question in a quiz session.
    
    Attributes:
        flashcard: The flashcard being quizzed
        question_number: Position in the quiz sequence
        start_time: When the question was presented
        end_time: When the question was answered
        user_answer: The user's response
        correct: Whether the answer was correct
        quality: Quality rating (0-5)
    """
    flashcard: Flashcard
    question_number: int
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    user_answer: str = ""
    correct: Optional[bool] = None
    quality: Optional[int] = None
    
    @property
    def response_time(self) -> float:
        """Get response time in seconds."""
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()


@dataclass
class QuizSession:
    """
    Represents a complete quiz session with statistics and results.
    
    Attributes:
        session_id: Unique identifier for the session
        deck: The deck being studied
        mode: Quiz mode used
        questions: List of quiz questions
        start_time: When the session started
        end_time: When the session ended
        max_questions: Maximum questions in the session
        completed: Whether the session is completed
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    deck: Optional[Deck] = None
    mode: QuizMode = QuizMode.SPACED_REPETITION
    questions: List[QuizQuestion] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    max_questions: int = 20
    completed: bool = False
    
    @property
    def total_questions(self) -> int:
        """Get total number of questions in the session."""
        return len(self.questions)
    
    @property
    def correct_answers(self) -> int:
        """Get number of correct answers."""
        return sum(1 for q in self.questions if q.correct)
    
    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage."""
        if not self.questions:
            return 0.0
        return (self.correct_answers / len(self.questions)) * 100
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time in seconds."""
        if not self.questions:
            return 0.0
        
        total_time = sum(q.response_time for q in self.questions if q.end_time)
        answered_questions = sum(1 for q in self.questions if q.end_time)
        
        return total_time / answered_questions if answered_questions > 0 else 0.0
    
    @property
    def session_duration(self) -> timedelta:
        """Get total session duration."""
        end = self.end_time or datetime.now()
        return end - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "deck_id": self.deck.deck_id if self.deck else None,
            "deck_name": self.deck.name if self.deck else None,
            "mode": self.mode.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "max_questions": self.max_questions,
            "completed": self.completed,
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "accuracy": self.accuracy,
            "average_response_time": self.average_response_time,
            "session_duration": str(self.session_duration),
            "questions": [
                {
                    "card_id": q.flashcard.card_id,
                    "question": q.flashcard.question,
                    "correct_answer": q.flashcard.answer,
                    "user_answer": q.user_answer,
                    "correct": q.correct,
                    "quality": q.quality,
                    "response_time": q.response_time,
                }
                for q in self.questions
            ]
        }


class QuizEngine:
    """
    Main quiz engine that manages quiz sessions and coordinates learning.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the quiz engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or QUIZ_CONFIG.copy()
        self.sr_algorithm = SpacedRepetitionAlgorithm()
        self.current_session: Optional[QuizSession] = None
        self.answer_checker: Optional[Callable[[str, str], bool]] = None
    
    def start_session(self, deck: Deck, mode: QuizMode = QuizMode.SPACED_REPETITION,
                     max_questions: int = None) -> QuizSession:
        """
        Start a new quiz session.
        
        Args:
            deck: The deck to study
            mode: Quiz mode to use
            max_questions: Maximum questions (uses config default if None)
            
        Returns:
            New quiz session
        """
        if max_questions is None:
            max_questions = self.config["max_questions_per_session"]
        
        self.current_session = QuizSession(
            deck=deck,
            mode=mode,
            max_questions=max_questions
        )
        
        return self.current_session
    
    def get_next_question(self) -> Optional[QuizQuestion]:
        """
        Get the next question for the current session.
        
        Returns:
            Next quiz question or None if session is complete
        """
        if not self.current_session or self.current_session.completed:
            return None
        
        if len(self.current_session.questions) >= self.current_session.max_questions:
            self.end_session()
            return None
        
        # Select flashcard based on quiz mode
        flashcard = self._select_next_flashcard()
        if not flashcard:
            self.end_session()
            return None
        
        question = QuizQuestion(
            flashcard=flashcard,
            question_number=len(self.current_session.questions) + 1
        )
        
        self.current_session.questions.append(question)
        return question
    
    def _select_next_flashcard(self) -> Optional[Flashcard]:
        """Select the next flashcard based on the current quiz mode."""
        if not self.current_session or not self.current_session.deck:
            return None
        
        deck = self.current_session.deck
        mode = self.current_session.mode
        
        # Get cards not yet asked in this session
        asked_card_ids = {q.flashcard.card_id for q in self.current_session.questions}
        available_cards = [
            card for card in deck.flashcards 
            if card.card_id not in asked_card_ids
        ]
        
        if not available_cards:
            return None
        
        if mode == QuizMode.SPACED_REPETITION:
            # Use spaced repetition algorithm
            suggested_cards = self.sr_algorithm.suggest_study_session(
                available_cards, max_cards=1
            )
            return suggested_cards[0] if suggested_cards else available_cards[0]
        
        elif mode == QuizMode.DIFFICULT_FIRST:
            # Sort by difficulty (hardest first)
            available_cards.sort(key=lambda c: c.difficulty, reverse=True)
            return available_cards[0]
        
        elif mode == QuizMode.RANDOM:
            # Random selection
            import random
            return random.choice(available_cards)
        
        else:  # SEQUENTIAL
            # Sequential order
            return available_cards[0]
    
    def submit_answer(self, question: QuizQuestion, user_answer: str,
                     quality: int = None) -> bool:
        """
        Submit an answer for a quiz question.
        
        Args:
            question: The quiz question being answered
            user_answer: The user's answer
            quality: Optional quality rating (0-5)
            
        Returns:
            Whether the answer was correct
        """
        question.end_time = datetime.now()
        question.user_answer = user_answer.strip()
        
        # Check if answer is correct
        correct = self._check_answer(
            question.flashcard.answer, 
            question.user_answer
        )
        question.correct = correct
        
        # Determine quality if not provided
        if quality is None:
            quality = self._calculate_quality(question)
        question.quality = quality
        
        # Update flashcard using spaced repetition
        review_result = ReviewResult(
            quality=quality,
            response_time=question.response_time,
            correct=correct,
            timestamp=question.end_time
        )
        
        self.sr_algorithm.update_flashcard(question.flashcard, review_result)
        
        return correct
    
    def _check_answer(self, correct_answer: str, user_answer: str) -> bool:
        """
        Check if the user's answer is correct.
        
        Args:
            correct_answer: The correct answer
            user_answer: The user's answer
            
        Returns:
            Whether the answer is correct
        """
        if self.answer_checker:
            return self.answer_checker(correct_answer, user_answer)
        
        # Default checking logic
        correct = correct_answer.strip()
        user = user_answer.strip()
        
        if not self.config.get("case_sensitive", False):
            correct = correct.lower()
            user = user.lower()
        
        # Exact match
        if correct == user:
            return True
        
        # Partial match if enabled
        if self.config.get("allow_partial_answers", True):
            # Check if user answer is contained in correct answer or vice versa
            return user in correct or correct in user
        
        return False
    
    def _calculate_quality(self, question: QuizQuestion) -> int:
        """
        Calculate quality rating based on correctness and response time.
        
        Args:
            question: The quiz question
            
        Returns:
            Quality rating (0-5)
        """
        if not question.correct:
            return 0  # Incorrect answer
        
        # Base quality for correct answer
        quality = 3
        
        # Adjust based on response time (assuming 5 seconds is ideal)
        response_time = question.response_time
        if response_time <= 3:
            quality = 5  # Very fast
        elif response_time <= 5:
            quality = 4  # Fast
        elif response_time <= 10:
            quality = 3  # Normal
        else:
            quality = 2  # Slow but correct
        
        return quality
    
    def end_session(self) -> Optional[QuizSession]:
        """
        End the current quiz session.
        
        Returns:
            The completed session
        """
        if self.current_session:
            self.current_session.end_time = datetime.now()
            self.current_session.completed = True
            
            # Save deck with updated flashcard data
            if self.current_session.deck:
                self.current_session.deck.save()
        
        completed_session = self.current_session
        self.current_session = None
        return completed_session
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get statistics for the current session.
        
        Returns:
            Dictionary with session statistics
        """
        if not self.current_session:
            return {}
        
        return {
            "questions_answered": len(self.current_session.questions),
            "correct_answers": self.current_session.correct_answers,
            "accuracy": self.current_session.accuracy,
            "average_response_time": self.current_session.average_response_time,
            "session_duration": str(self.current_session.session_duration),
            "remaining_questions": max(0, 
                self.current_session.max_questions - len(self.current_session.questions)
            )
        }
    
    def set_answer_checker(self, checker: Callable[[str, str], bool]) -> None:
        """
        Set a custom answer checking function.
        
        Args:
            checker: Function that takes (correct_answer, user_answer) and returns bool
        """
        self.answer_checker = checker
