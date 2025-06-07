"""
Data models for contextual learning system.

This module contains all the data classes and enums used by the contextual learning engine.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum


class StudyEnvironment(Enum):
    """Types of study environments."""
    QUIET = "quiet"
    NOISY = "noisy"
    MOBILE = "mobile"
    FOCUSED = "focused"
    DISTRACTED = "distracted"


class EnergyLevel(Enum):
    """Energy levels for study sessions."""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


class AttentionLevel(Enum):
    """Attention levels during study."""
    POOR = 1
    FAIR = 2
    GOOD = 3
    EXCELLENT = 4


class StudyMode(Enum):
    """Different study modes."""
    REVIEW = "review"
    LEARNING = "learning"
    PRACTICE = "practice"
    TESTING = "testing"
    EXPLORATION = "exploration"


@dataclass
class StudyContext:
    """Context information for a study session."""
    # Time context
    time_available: int  # minutes
    time_of_day: str = "morning"  # morning, afternoon, evening, night
    
    # Personal context
    energy_level: EnergyLevel = EnergyLevel.MEDIUM
    attention_level: AttentionLevel = AttentionLevel.GOOD
    stress_level: int = 3  # 1-5 scale
    
    # Environmental context
    environment: StudyEnvironment = StudyEnvironment.QUIET
    device_type: str = "desktop"  # desktop, tablet, mobile
    
    # Learning context
    study_mode: StudyMode = StudyMode.REVIEW
    previous_session_performance: Optional[float] = None
    days_since_last_study: int = 0
    
    # Goals and preferences
    target_accuracy: float = 0.8
    preferred_difficulty: float = 0.5
    focus_areas: Set[str] = field(default_factory=set)


@dataclass
class StudyPlan:
    """A personalized study plan."""
    plan_id: str
    created_at: datetime
    context: StudyContext
    
    # Plan structure
    total_duration: int  # minutes
    session_phases: List['StudyPhase'] = field(default_factory=list)
    
    # Content selection
    recommended_cards: List[str] = field(default_factory=list)  # Card IDs
    focus_topics: List[str] = field(default_factory=list)
    difficulty_range: tuple = (0.3, 0.7)
    
    # Adaptive features
    break_intervals: List[int] = field(default_factory=list)  # minutes
    difficulty_progression: List[float] = field(default_factory=list)
    
    # Predictions
    estimated_completion: int = 0  # minutes
    predicted_accuracy: float = 0.0
    confidence_score: float = 0.0


@dataclass
class StudyPhase:
    """A phase within a study session."""
    phase_name: str
    duration: int  # minutes
    description: str
    
    # Phase configuration
    card_count: int = 0
    difficulty_target: float = 0.5
    focus_areas: Set[str] = field(default_factory=set)
    
    # Phase type
    phase_type: str = "review"  # review, learning, practice, break
    
    # Adaptive parameters
    success_threshold: float = 0.8
    adjustment_factor: float = 0.1


@dataclass
class ContextualRecommendation:
    """A contextual recommendation for study optimization."""
    recommendation_type: str
    title: str
    description: str
    confidence: float
    
    # Implementation details
    suggested_actions: List[str] = field(default_factory=list)
    expected_benefit: str = ""
    effort_required: str = "low"  # low, medium, high
    
    # Context relevance
    relevant_contexts: List[str] = field(default_factory=list)
    effectiveness_score: float = 0.0


@dataclass
class AdaptationRule:
    """A rule for adapting study sessions based on context."""
    rule_id: str
    name: str
    description: str
    
    # Conditions
    context_conditions: Dict[str, Any] = field(default_factory=dict)
    performance_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Actions
    adaptations: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    priority: int = 1
    active: bool = True
    success_rate: float = 0.0


@dataclass
class PerformancePattern:
    """A pattern in user performance based on context."""
    pattern_id: str
    name: str
    description: str
    
    # Pattern characteristics
    context_factors: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Statistical data
    occurrence_count: int = 0
    confidence_level: float = 0.0
    last_observed: Optional[datetime] = None
    
    # Predictive value
    predictive_accuracy: float = 0.0
    recommended_actions: List[str] = field(default_factory=list)


@dataclass
class ContextualInsight:
    """An insight derived from contextual analysis."""
    insight_type: str
    title: str
    description: str
    
    # Supporting data
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    # Actionability
    actionable: bool = True
    recommended_changes: List[str] = field(default_factory=list)
    
    # Impact assessment
    potential_improvement: float = 0.0
    implementation_difficulty: str = "medium"


@dataclass
class SessionAdaptation:
    """Real-time adaptation during a study session."""
    adaptation_id: str
    timestamp: datetime
    trigger: str
    
    # Adaptation details
    original_plan: Dict[str, Any]
    adapted_plan: Dict[str, Any]
    adaptation_reason: str
    
    # Effectiveness
    expected_improvement: float = 0.0
    actual_improvement: Optional[float] = None
    user_satisfaction: Optional[int] = None  # 1-5 scale
