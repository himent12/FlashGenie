"""
Data models for content recommendation system.

This module contains all the data classes and enums used by the content recommendation engine.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from ..content_system.flashcard import Flashcard


class SuggestionType(Enum):
    """Types of content suggestions."""
    NEW_CARD = "new_card"  # Suggest new flashcard content
    RELATED_TOPIC = "related_topic"  # Suggest related topics to study
    PREREQUISITE = "prerequisite"  # Suggest prerequisite knowledge
    ADVANCED = "advanced"  # Suggest advanced topics
    REVIEW = "review"  # Suggest cards for review
    WEAK_AREA = "weak_area"  # Suggest focus on weak areas


class ContentSource(Enum):
    """Sources for content suggestions."""
    PATTERN_ANALYSIS = "pattern_analysis"  # Based on existing content patterns
    KNOWLEDGE_GRAPH = "knowledge_graph"  # Based on knowledge relationships
    DIFFICULTY_PROGRESSION = "difficulty_progression"  # Based on difficulty gaps
    USER_PERFORMANCE = "user_performance"  # Based on performance analysis
    EXTERNAL_RESOURCES = "external_resources"  # From external knowledge bases


@dataclass
class CardSuggestion:
    """A suggestion for a new flashcard."""
    suggested_question: str
    suggested_answer: str
    confidence_score: float  # 0.0 to 1.0
    reasoning: str
    suggested_tags: Set[str]
    estimated_difficulty: float
    source: ContentSource
    related_cards: List[str] = field(default_factory=list)  # Related card IDs
    
    def generate_card(self) -> Flashcard:
        """Generate a flashcard from this suggestion."""
        return Flashcard(
            question=self.suggested_question,
            answer=self.suggested_answer,
            tags=self.suggested_tags,
            difficulty=self.estimated_difficulty
        )


@dataclass
class TopicSuggestion:
    """A suggestion for a topic to study."""
    topic_name: str
    description: str
    confidence_score: float
    reasoning: str
    suggested_tags: Set[str]
    estimated_card_count: int
    priority_score: float  # Higher = more important
    source: ContentSource


@dataclass
class ContentGap:
    """An identified gap in content coverage."""
    gap_type: str  # "missing_basics", "difficulty_jump", "isolated_topic"
    description: str
    severity: float  # 0.0 to 1.0
    affected_tags: Set[str]
    suggested_actions: List[str]
    related_cards: List[str] = field(default_factory=list)


@dataclass
class LearningGoals:
    """User's learning goals and preferences."""
    target_topics: Set[str] = field(default_factory=set)
    difficulty_preference: float = 0.5  # 0.0 = easy, 1.0 = hard
    learning_pace: str = "moderate"  # slow, moderate, fast
    focus_areas: Set[str] = field(default_factory=set)
    avoid_topics: Set[str] = field(default_factory=set)
    time_constraints: Optional[int] = None  # minutes per day


@dataclass
class ContentAnalysis:
    """Analysis results for deck content."""
    total_cards: int
    topics: Set[str]
    difficulty_distribution: Dict[str, float]
    tag_frequency: Dict[str, int]
    content_patterns: Dict[str, Any]
    mastery_levels: Dict[str, float]
    
    
@dataclass
class StudyPhase:
    """A phase in the recommended study sequence."""
    phase: str
    description: str
    topics: List[str]
    estimated_duration: int  # days
    focus: str
    priority: int = 1  # 1 = highest priority
    prerequisites: List[str] = field(default_factory=list)
    
    
@dataclass
class RecommendationContext:
    """Context for generating recommendations."""
    user_goals: Optional[LearningGoals] = None
    focus_areas: Optional[Set[str]] = None
    time_available: Optional[int] = None  # minutes
    difficulty_preference: float = 0.5
    learning_style: str = "balanced"  # visual, auditory, kinesthetic, balanced
