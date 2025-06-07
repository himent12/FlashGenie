"""
Data models for learning velocity tracking system.

This module contains all the data classes and enums used by the learning velocity tracker.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class VelocityTrend(Enum):
    """Trends in learning velocity."""
    ACCELERATING = "accelerating"
    STABLE = "stable"
    DECLINING = "declining"
    FLUCTUATING = "fluctuating"


class LearningPhase(Enum):
    """Phases of learning progression."""
    INITIAL = "initial"
    ACCELERATION = "acceleration"
    PLATEAU = "plateau"
    MASTERY = "mastery"
    MAINTENANCE = "maintenance"


class VelocityMetric(Enum):
    """Types of velocity metrics."""
    CARDS_PER_HOUR = "cards_per_hour"
    ACCURACY_IMPROVEMENT = "accuracy_improvement"
    RETENTION_RATE = "retention_rate"
    DIFFICULTY_PROGRESSION = "difficulty_progression"
    CONCEPT_MASTERY = "concept_mastery"


@dataclass
class VelocityDataPoint:
    """A single data point for velocity tracking."""
    timestamp: datetime
    session_id: str
    
    # Performance metrics
    cards_studied: int
    correct_answers: int
    total_answers: int
    session_duration: int  # minutes
    
    # Velocity calculations
    cards_per_minute: float = 0.0
    accuracy_rate: float = 0.0
    learning_efficiency: float = 0.0
    
    # Context information
    difficulty_level: float = 0.5
    energy_level: int = 3
    focus_score: float = 0.5
    
    def __post_init__(self):
        """Calculate derived metrics."""
        if self.session_duration > 0:
            self.cards_per_minute = self.cards_studied / self.session_duration
        
        if self.total_answers > 0:
            self.accuracy_rate = self.correct_answers / self.total_answers
        
        # Learning efficiency combines speed and accuracy
        self.learning_efficiency = self.cards_per_minute * self.accuracy_rate


@dataclass
class VelocityTrendAnalysis:
    """Analysis of velocity trends over time."""
    metric_type: VelocityMetric
    trend: VelocityTrend
    confidence: float
    
    # Trend data
    current_value: float
    previous_value: float
    change_percentage: float
    
    # Time analysis
    analysis_period: int  # days
    data_points: int
    
    # Predictions
    predicted_next_value: float = 0.0
    prediction_confidence: float = 0.0
    
    # Insights
    description: str = ""
    recommendations: List[str] = field(default_factory=list)


@dataclass
class LearningVelocityProfile:
    """Complete learning velocity profile for a user."""
    user_id: str
    created_at: datetime
    last_updated: datetime
    
    # Current metrics
    current_velocity: float  # cards per hour
    current_accuracy: float
    current_efficiency: float
    
    # Historical data
    velocity_history: List[VelocityDataPoint] = field(default_factory=list)
    trend_analyses: List[VelocityTrendAnalysis] = field(default_factory=list)
    
    # Learning phases
    current_phase: LearningPhase = LearningPhase.INITIAL
    phase_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Optimization insights
    optimal_session_duration: int = 25  # minutes
    optimal_difficulty_range: tuple = (0.4, 0.7)
    peak_performance_times: List[str] = field(default_factory=list)
    
    # Goals and targets
    velocity_target: float = 0.0
    accuracy_target: float = 0.8
    efficiency_target: float = 0.0


@dataclass
class VelocityGoal:
    """A learning velocity goal."""
    goal_id: str
    name: str
    description: str
    
    # Goal parameters
    metric_type: VelocityMetric
    target_value: float
    current_value: float
    
    # Timeline
    created_at: datetime
    target_date: datetime
    
    # Progress tracking
    progress_percentage: float = 0.0
    is_achieved: bool = False
    achieved_at: Optional[datetime] = None
    
    # Milestones
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    
    def update_progress(self):
        """Update progress towards the goal."""
        if self.target_value > 0:
            self.progress_percentage = min(100.0, (self.current_value / self.target_value) * 100)
            self.is_achieved = self.progress_percentage >= 100.0
            
            if self.is_achieved and not self.achieved_at:
                self.achieved_at = datetime.now()


@dataclass
class VelocityPrediction:
    """Prediction of future learning velocity."""
    prediction_id: str
    created_at: datetime
    
    # Prediction parameters
    prediction_horizon: int  # days
    confidence_level: float
    
    # Predicted values
    predicted_velocity: float
    predicted_accuracy: float
    predicted_efficiency: float
    
    # Prediction factors
    trend_factor: float = 0.0
    seasonality_factor: float = 0.0
    external_factors: Dict[str, float] = field(default_factory=dict)
    
    # Validation
    actual_values: Optional[Dict[str, float]] = None
    prediction_error: Optional[float] = None


@dataclass
class VelocityOptimization:
    """Optimization recommendations for learning velocity."""
    optimization_id: str
    created_at: datetime
    
    # Current state
    current_metrics: Dict[str, float]
    bottlenecks: List[str]
    
    # Recommendations
    recommended_changes: List[Dict[str, Any]]
    expected_improvements: Dict[str, float]
    
    # Implementation
    priority_level: str = "medium"  # low, medium, high
    effort_required: str = "medium"  # low, medium, high
    estimated_impact: float = 0.0
    
    # Tracking
    implemented: bool = False
    implementation_date: Optional[datetime] = None
    actual_impact: Optional[float] = None


@dataclass
class VelocityBenchmark:
    """Benchmark data for velocity comparison."""
    benchmark_id: str
    name: str
    description: str
    
    # Benchmark values
    velocity_percentiles: Dict[int, float]  # percentile -> value
    accuracy_percentiles: Dict[int, float]
    efficiency_percentiles: Dict[int, float]
    
    # Context
    sample_size: int
    data_collection_period: str
    user_demographics: Dict[str, Any] = field(default_factory=dict)
    
    # Comparison
    user_percentile: Optional[int] = None
    relative_performance: str = ""  # below_average, average, above_average, excellent


@dataclass
class VelocityAlert:
    """Alert for significant velocity changes."""
    alert_id: str
    timestamp: datetime
    alert_type: str  # improvement, decline, plateau, anomaly
    
    # Alert details
    metric_affected: VelocityMetric
    severity: str  # low, medium, high
    description: str
    
    # Data
    current_value: float
    previous_value: float
    threshold_crossed: float
    
    # Response
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    action_taken: str = ""


@dataclass
class LearningSession:
    """Data for a single learning session."""
    session_id: str
    start_time: datetime
    end_time: datetime
    
    # Session metrics
    cards_studied: int
    correct_answers: int
    total_answers: int
    
    # Performance calculations
    duration_minutes: int = 0
    accuracy_rate: float = 0.0
    cards_per_minute: float = 0.0
    
    # Context
    deck_id: str = ""
    study_mode: str = "review"
    difficulty_level: float = 0.5
    
    def __post_init__(self):
        """Calculate session metrics."""
        self.duration_minutes = int((self.end_time - self.start_time).total_seconds() / 60)
        
        if self.total_answers > 0:
            self.accuracy_rate = self.correct_answers / self.total_answers
        
        if self.duration_minutes > 0:
            self.cards_per_minute = self.cards_studied / self.duration_minutes


@dataclass
class VelocityInsight:
    """An insight derived from velocity analysis."""
    insight_id: str
    timestamp: datetime
    insight_type: str
    
    # Insight content
    title: str
    description: str
    significance: str  # low, medium, high
    
    # Supporting data
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    # Actionability
    actionable: bool = True
    recommended_actions: List[str] = field(default_factory=list)
    
    # Impact assessment
    potential_improvement: float = 0.0
    implementation_effort: str = "medium"
