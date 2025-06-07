"""
Learning Velocity Tracker for FlashGenie v1.5

This module implements advanced analytics that track learning velocity, predict mastery
timelines, and identify optimal learning paths for individual users.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import math
import statistics
from pathlib import Path

from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck


class LearningPhase(Enum):
    """Different phases of learning progression."""
    INITIAL = "initial"  # First exposure to material
    ACQUISITION = "acquisition"  # Active learning phase
    CONSOLIDATION = "consolidation"  # Strengthening knowledge
    MASTERY = "mastery"  # Deep understanding achieved
    MAINTENANCE = "maintenance"  # Maintaining learned knowledge


class VelocityTrend(Enum):
    """Trends in learning velocity."""
    ACCELERATING = "accelerating"
    STEADY = "steady"
    DECELERATING = "decelerating"
    PLATEAUED = "plateaued"
    DECLINING = "declining"


@dataclass
class LearningMetrics:
    """Core learning metrics for velocity calculation."""
    cards_learned: int = 0
    cards_mastered: int = 0
    total_reviews: int = 0
    study_time_minutes: int = 0
    accuracy_rate: float = 0.0
    retention_rate: float = 0.0
    difficulty_progression: float = 0.0
    consistency_score: float = 0.0


@dataclass
class VelocitySnapshot:
    """Snapshot of learning velocity at a specific time."""
    timestamp: datetime
    cards_per_day: float
    mastery_per_day: float
    accuracy_trend: float
    difficulty_trend: float
    study_efficiency: float  # cards learned per minute
    retention_strength: float
    phase: LearningPhase


@dataclass
class MasteryPrediction:
    """Prediction of when mastery will be achieved."""
    estimated_days_to_mastery: int
    confidence_interval: Tuple[int, int]  # (min_days, max_days)
    confidence_score: float  # 0.0 to 1.0
    recommended_daily_time: int  # minutes
    bottleneck_cards: List[Flashcard]
    acceleration_opportunities: List[str]
    risk_factors: List[str]


@dataclass
class LearningPath:
    """Optimal learning path recommendation."""
    path_id: str
    description: str
    estimated_duration: int  # days
    daily_commitment: int  # minutes
    milestones: List[Dict[str, Any]]
    difficulty_progression: List[float]
    success_probability: float


class LearningVelocityTracker:
    """
    Advanced analytics system for tracking learning velocity and predicting outcomes.
    
    This tracker analyzes learning patterns to:
    - Calculate current learning velocity
    - Predict mastery timelines
    - Identify optimal learning paths
    - Detect learning plateaus and bottlenecks
    - Recommend acceleration strategies
    """
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = Path(data_path or "data/velocity_tracking")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Load historical data
        self.velocity_history = self._load_velocity_history()
        self.learning_curves = self._load_learning_curves()
        self.mastery_models = self._load_mastery_models()
    
    def calculate_current_velocity(self, deck: Deck, days_back: int = 30) -> VelocitySnapshot:
        """
        Calculate current learning velocity based on recent performance.
        
        Args:
            deck: The deck to analyze
            days_back: Number of days to look back for calculation
            
        Returns:
            Current velocity snapshot
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Gather recent performance data
        recent_cards = [
            card for card in deck.flashcards
            if card.last_reviewed and card.last_reviewed >= cutoff_date
        ]
        
        if not recent_cards:
            return self._create_empty_velocity_snapshot()
        
        # Calculate velocity metrics
        cards_per_day = len(recent_cards) / days_back
        mastery_per_day = len([c for c in recent_cards if self._is_mastered(c)]) / days_back
        
        # Calculate trends
        accuracy_trend = self._calculate_accuracy_trend(recent_cards)
        difficulty_trend = self._calculate_difficulty_trend(recent_cards)
        
        # Calculate efficiency
        total_study_time = sum(
            len(card.response_times) * statistics.mean(card.response_times) / 60
            for card in recent_cards if card.response_times
        )
        study_efficiency = len(recent_cards) / max(total_study_time, 1)
        
        # Calculate retention strength
        retention_strength = self._calculate_retention_strength(recent_cards)
        
        # Determine learning phase
        phase = self._determine_learning_phase(deck, recent_cards)
        
        return VelocitySnapshot(
            timestamp=datetime.now(),
            cards_per_day=cards_per_day,
            mastery_per_day=mastery_per_day,
            accuracy_trend=accuracy_trend,
            difficulty_trend=difficulty_trend,
            study_efficiency=study_efficiency,
            retention_strength=retention_strength,
            phase=phase
        )
    
    def predict_mastery_timeline(
        self, 
        deck: Deck, 
        target_mastery_rate: float = 0.9
    ) -> MasteryPrediction:
        """
        Predict when the user will achieve mastery of the deck.
        
        Args:
            deck: The deck to analyze
            target_mastery_rate: Target mastery percentage (0.0 to 1.0)
            
        Returns:
            Mastery prediction with timeline and recommendations
        """
        current_velocity = self.calculate_current_velocity(deck)
        
        # Calculate current mastery state
        total_cards = len(deck.flashcards)
        mastered_cards = len([c for c in deck.flashcards if self._is_mastered(c)])
        current_mastery_rate = mastered_cards / total_cards if total_cards > 0 else 0
        
        # Cards still needed for mastery
        target_mastered = int(total_cards * target_mastery_rate)
        cards_to_master = max(0, target_mastered - mastered_cards)
        
        # Predict timeline based on current velocity
        if current_velocity.mastery_per_day > 0:
            base_estimate = int(cards_to_master / current_velocity.mastery_per_day)
        else:
            # Fallback calculation based on overall progress
            base_estimate = self._estimate_from_historical_patterns(deck, cards_to_master)
        
        # Apply confidence intervals and adjustments
        confidence_score = self._calculate_prediction_confidence(deck, current_velocity)
        
        # Adjust for learning curve effects
        adjusted_estimate = self._adjust_for_learning_curve(
            base_estimate, current_velocity, cards_to_master
        )
        
        # Calculate confidence interval
        uncertainty = max(5, int(adjusted_estimate * (1 - confidence_score)))
        min_days = max(1, adjusted_estimate - uncertainty)
        max_days = adjusted_estimate + uncertainty
        
        # Identify bottlenecks and opportunities
        bottleneck_cards = self._identify_bottleneck_cards(deck)
        acceleration_opportunities = self._identify_acceleration_opportunities(
            deck, current_velocity
        )
        risk_factors = self._identify_risk_factors(deck, current_velocity)
        
        # Calculate recommended daily time
        recommended_daily_time = self._calculate_recommended_daily_time(
            cards_to_master, adjusted_estimate, current_velocity
        )
        
        return MasteryPrediction(
            estimated_days_to_mastery=adjusted_estimate,
            confidence_interval=(min_days, max_days),
            confidence_score=confidence_score,
            recommended_daily_time=recommended_daily_time,
            bottleneck_cards=bottleneck_cards,
            acceleration_opportunities=acceleration_opportunities,
            risk_factors=risk_factors
        )
    
    def analyze_learning_trends(self, deck: Deck, days_back: int = 90) -> Dict[str, Any]:
        """
        Analyze learning trends over time.
        
        Args:
            deck: The deck to analyze
            days_back: Number of days to analyze
            
        Returns:
            Comprehensive trend analysis
        """
        # Get velocity snapshots over time
        snapshots = self._get_historical_snapshots(deck, days_back)
        
        if len(snapshots) < 2:
            return self._create_empty_trend_analysis()
        
        # Analyze velocity trends
        velocity_trend = self._analyze_velocity_trend(snapshots)
        accuracy_trend = self._analyze_accuracy_trend(snapshots)
        efficiency_trend = self._analyze_efficiency_trend(snapshots)
        
        # Identify patterns
        learning_patterns = self._identify_learning_patterns(snapshots)
        
        # Calculate overall progress
        progress_metrics = self._calculate_progress_metrics(deck, snapshots)
        
        # Generate insights and recommendations
        insights = self._generate_learning_insights(
            snapshots, velocity_trend, accuracy_trend, efficiency_trend
        )
        
        return {
            'velocity_trend': velocity_trend,
            'accuracy_trend': accuracy_trend,
            'efficiency_trend': efficiency_trend,
            'learning_patterns': learning_patterns,
            'progress_metrics': progress_metrics,
            'insights': insights,
            'snapshots': snapshots[-10:]  # Last 10 snapshots for visualization
        }
    
    def recommend_learning_paths(
        self, 
        deck: Deck, 
        available_time_per_day: int,
        target_completion_days: Optional[int] = None
    ) -> List[LearningPath]:
        """
        Recommend optimal learning paths based on constraints and goals.
        
        Args:
            deck: The deck to learn
            available_time_per_day: Available study time in minutes
            target_completion_days: Optional target completion timeline
            
        Returns:
            List of recommended learning paths
        """
        current_velocity = self.calculate_current_velocity(deck)
        mastery_prediction = self.predict_mastery_timeline(deck)
        
        paths = []
        
        # Conservative path (high success probability)
        conservative_path = self._create_conservative_path(
            deck, available_time_per_day, mastery_prediction
        )
        paths.append(conservative_path)
        
        # Balanced path (moderate intensity)
        balanced_path = self._create_balanced_path(
            deck, available_time_per_day, mastery_prediction
        )
        paths.append(balanced_path)
        
        # Aggressive path (fast completion)
        if available_time_per_day >= 30:
            aggressive_path = self._create_aggressive_path(
                deck, available_time_per_day, mastery_prediction
            )
            paths.append(aggressive_path)
        
        # Custom path for specific timeline
        if target_completion_days:
            custom_path = self._create_custom_timeline_path(
                deck, available_time_per_day, target_completion_days, mastery_prediction
            )
            if custom_path:
                paths.append(custom_path)
        
        # Sort by success probability
        paths.sort(key=lambda p: p.success_probability, reverse=True)
        
        return paths
    
    def track_velocity_change(self, deck: Deck) -> None:
        """Record current velocity for historical tracking."""
        velocity = self.calculate_current_velocity(deck)
        
        # Add to history
        deck_id = deck.name  # Use deck name as ID
        if deck_id not in self.velocity_history:
            self.velocity_history[deck_id] = []
        
        self.velocity_history[deck_id].append({
            'timestamp': velocity.timestamp.isoformat(),
            'cards_per_day': velocity.cards_per_day,
            'mastery_per_day': velocity.mastery_per_day,
            'accuracy_trend': velocity.accuracy_trend,
            'difficulty_trend': velocity.difficulty_trend,
            'study_efficiency': velocity.study_efficiency,
            'retention_strength': velocity.retention_strength,
            'phase': velocity.phase.value
        })
        
        # Keep only last 100 entries per deck
        self.velocity_history[deck_id] = self.velocity_history[deck_id][-100:]
        
        # Save to disk
        self._save_velocity_history()
    
    def _is_mastered(self, card: Flashcard, threshold: float = 0.9) -> bool:
        """Check if a card is considered mastered."""
        if card.review_count < 3:
            return False
        
        accuracy = card.calculate_accuracy()
        return accuracy >= threshold and card.difficulty < 0.4
    
    def _calculate_accuracy_trend(self, cards: List[Flashcard]) -> float:
        """Calculate the trend in accuracy over time."""
        if not cards:
            return 0.0
        
        # Sort by last reviewed date
        sorted_cards = sorted(
            [c for c in cards if c.last_reviewed],
            key=lambda c: c.last_reviewed
        )
        
        if len(sorted_cards) < 2:
            return 0.0
        
        # Calculate accuracy for first and second half
        mid_point = len(sorted_cards) // 2
        first_half_accuracy = statistics.mean(
            c.calculate_accuracy() for c in sorted_cards[:mid_point]
        )
        second_half_accuracy = statistics.mean(
            c.calculate_accuracy() for c in sorted_cards[mid_point:]
        )
        
        return second_half_accuracy - first_half_accuracy
    
    def _calculate_difficulty_trend(self, cards: List[Flashcard]) -> float:
        """Calculate the trend in difficulty progression."""
        if not cards:
            return 0.0
        
        # Look at difficulty changes over time
        difficulty_changes = []
        for card in cards:
            if len(card.difficulty_history) >= 2:
                recent_change = card.difficulty_history[-1] - card.difficulty_history[-2]
                difficulty_changes.append(recent_change)
        
        if not difficulty_changes:
            return 0.0
        
        return statistics.mean(difficulty_changes)
    
    def _calculate_retention_strength(self, cards: List[Flashcard]) -> float:
        """Calculate overall retention strength."""
        if not cards:
            return 0.0
        
        retention_scores = []
        for card in cards:
            if card.review_count > 0:
                # Simple retention score based on accuracy and review frequency
                accuracy = card.calculate_accuracy()
                review_consistency = min(1.0, card.review_count / 10.0)
                retention_scores.append(accuracy * review_consistency)
        
        return statistics.mean(retention_scores) if retention_scores else 0.0
    
    def _determine_learning_phase(self, deck: Deck, recent_cards: List[Flashcard]) -> LearningPhase:
        """Determine the current learning phase."""
        total_cards = len(deck.flashcards)
        reviewed_cards = len([c for c in deck.flashcards if c.review_count > 0])
        mastered_cards = len([c for c in deck.flashcards if self._is_mastered(c)])
        
        reviewed_ratio = reviewed_cards / total_cards if total_cards > 0 else 0
        mastery_ratio = mastered_cards / total_cards if total_cards > 0 else 0
        
        if reviewed_ratio < 0.2:
            return LearningPhase.INITIAL
        elif mastery_ratio < 0.3:
            return LearningPhase.ACQUISITION
        elif mastery_ratio < 0.7:
            return LearningPhase.CONSOLIDATION
        elif mastery_ratio < 0.9:
            return LearningPhase.MASTERY
        else:
            return LearningPhase.MAINTENANCE
    
    def _create_empty_velocity_snapshot(self) -> VelocitySnapshot:
        """Create an empty velocity snapshot for new decks."""
        return VelocitySnapshot(
            timestamp=datetime.now(),
            cards_per_day=0.0,
            mastery_per_day=0.0,
            accuracy_trend=0.0,
            difficulty_trend=0.0,
            study_efficiency=0.0,
            retention_strength=0.0,
            phase=LearningPhase.INITIAL
        )
    
    def _load_velocity_history(self) -> Dict[str, List[Dict]]:
        """Load velocity history from storage."""
        history_file = self.data_path / "velocity_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_velocity_history(self) -> None:
        """Save velocity history to storage."""
        history_file = self.data_path / "velocity_history.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(self.velocity_history, f, indent=2)
        except Exception:
            pass
    
    def _load_learning_curves(self) -> Dict[str, Any]:
        """Load learning curve models."""
        return {}  # Placeholder for learning curve models
    
    def _load_mastery_models(self) -> Dict[str, Any]:
        """Load mastery prediction models."""
        return {}  # Placeholder for mastery models
    
    # Additional helper methods would be implemented here...
    def _estimate_from_historical_patterns(self, deck: Deck, cards_to_master: int) -> int:
        """Estimate timeline from historical patterns."""
        # Fallback estimation - can be enhanced with ML models
        return max(30, cards_to_master * 2)  # Conservative estimate
    
    def _calculate_prediction_confidence(self, deck: Deck, velocity: VelocitySnapshot) -> float:
        """Calculate confidence in the prediction."""
        # Base confidence on data quality and consistency
        base_confidence = 0.7
        
        # Adjust based on data availability
        if len(deck.flashcards) < 10:
            base_confidence -= 0.2
        
        if velocity.cards_per_day < 1:
            base_confidence -= 0.1
        
        return max(0.1, min(1.0, base_confidence))
    
    def _adjust_for_learning_curve(self, estimate: int, velocity: VelocitySnapshot, cards_remaining: int) -> int:
        """Adjust estimate based on learning curve effects."""
        # Simple adjustment - can be enhanced with more sophisticated models
        if velocity.phase == LearningPhase.INITIAL:
            return int(estimate * 1.2)  # Learning takes longer initially
        elif velocity.phase == LearningPhase.MASTERY:
            return int(estimate * 0.9)  # Faster progress near mastery
        return estimate
    
    def _identify_bottleneck_cards(self, deck: Deck) -> List[Flashcard]:
        """Identify cards that are bottlenecks to progress."""
        bottlenecks = []
        for card in deck.flashcards:
            if (card.review_count > 5 and 
                card.calculate_accuracy() < 0.6 and 
                card.difficulty > 0.7):
                bottlenecks.append(card)
        
        return sorted(bottlenecks, key=lambda c: c.calculate_accuracy())[:5]
    
    def _identify_acceleration_opportunities(self, deck: Deck, velocity: VelocitySnapshot) -> List[str]:
        """Identify opportunities to accelerate learning."""
        opportunities = []
        
        if velocity.study_efficiency < 1.0:
            opportunities.append("Increase study session frequency")
        
        if velocity.accuracy_trend < 0:
            opportunities.append("Focus on review of struggling cards")
        
        if velocity.retention_strength < 0.7:
            opportunities.append("Implement more frequent review cycles")
        
        return opportunities
    
    def _identify_risk_factors(self, deck: Deck, velocity: VelocitySnapshot) -> List[str]:
        """Identify factors that might slow progress."""
        risks = []
        
        if velocity.cards_per_day < 2:
            risks.append("Low study frequency may slow progress")
        
        if velocity.accuracy_trend < -0.1:
            risks.append("Declining accuracy trend detected")
        
        return risks
    
    def _calculate_recommended_daily_time(self, cards_to_master: int, days: int, velocity: VelocitySnapshot) -> int:
        """Calculate recommended daily study time."""
        if velocity.study_efficiency > 0:
            cards_per_day_needed = cards_to_master / max(days, 1)
            minutes_needed = cards_per_day_needed / velocity.study_efficiency
            return max(15, min(120, int(minutes_needed)))
        return 30  # Default recommendation
    
    # Placeholder methods for learning path creation
    def _create_conservative_path(self, deck: Deck, daily_time: int, prediction: MasteryPrediction) -> LearningPath:
        """Create a conservative learning path."""
        return LearningPath(
            path_id="conservative",
            description="Steady, sustainable progress with high success probability",
            estimated_duration=prediction.estimated_days_to_mastery + 14,
            daily_commitment=min(daily_time, 30),
            milestones=[],
            difficulty_progression=[0.3, 0.5, 0.7],
            success_probability=0.9
        )
    
    def _create_balanced_path(self, deck: Deck, daily_time: int, prediction: MasteryPrediction) -> LearningPath:
        """Create a balanced learning path."""
        return LearningPath(
            path_id="balanced",
            description="Balanced approach with moderate intensity",
            estimated_duration=prediction.estimated_days_to_mastery,
            daily_commitment=min(daily_time, 45),
            milestones=[],
            difficulty_progression=[0.4, 0.6, 0.8],
            success_probability=0.75
        )
    
    def _create_aggressive_path(self, deck: Deck, daily_time: int, prediction: MasteryPrediction) -> LearningPath:
        """Create an aggressive learning path."""
        return LearningPath(
            path_id="aggressive",
            description="Intensive study for rapid completion",
            estimated_duration=max(14, prediction.estimated_days_to_mastery - 7),
            daily_commitment=min(daily_time, 60),
            milestones=[],
            difficulty_progression=[0.5, 0.7, 0.9],
            success_probability=0.6
        )
    
    def _create_custom_timeline_path(self, deck: Deck, daily_time: int, target_days: int, prediction: MasteryPrediction) -> Optional[LearningPath]:
        """Create a path for a specific timeline."""
        if target_days < prediction.estimated_days_to_mastery // 2:
            return None  # Unrealistic timeline
        
        return LearningPath(
            path_id="custom",
            description=f"Custom path to complete in {target_days} days",
            estimated_duration=target_days,
            daily_commitment=daily_time,
            milestones=[],
            difficulty_progression=[0.4, 0.6, 0.8],
            success_probability=0.7
        )
    
    # Additional placeholder methods for trend analysis
    def _get_historical_snapshots(self, deck: Deck, days_back: int) -> List[VelocitySnapshot]:
        """Get historical velocity snapshots."""
        return []  # Placeholder
    
    def _create_empty_trend_analysis(self) -> Dict[str, Any]:
        """Create empty trend analysis for new decks."""
        return {
            'velocity_trend': VelocityTrend.STEADY,
            'accuracy_trend': 0.0,
            'efficiency_trend': 0.0,
            'learning_patterns': [],
            'progress_metrics': {},
            'insights': [],
            'snapshots': []
        }
    
    def _analyze_velocity_trend(self, snapshots: List[VelocitySnapshot]) -> VelocityTrend:
        """Analyze velocity trend from snapshots."""
        return VelocityTrend.STEADY  # Placeholder
    
    def _analyze_accuracy_trend(self, snapshots: List[VelocitySnapshot]) -> float:
        """Analyze accuracy trend."""
        return 0.0  # Placeholder
    
    def _analyze_efficiency_trend(self, snapshots: List[VelocitySnapshot]) -> float:
        """Analyze efficiency trend."""
        return 0.0  # Placeholder
    
    def _identify_learning_patterns(self, snapshots: List[VelocitySnapshot]) -> List[str]:
        """Identify learning patterns."""
        return []  # Placeholder
    
    def _calculate_progress_metrics(self, deck: Deck, snapshots: List[VelocitySnapshot]) -> Dict[str, Any]:
        """Calculate progress metrics."""
        return {}  # Placeholder
    
    def _generate_learning_insights(self, snapshots, velocity_trend, accuracy_trend, efficiency_trend) -> List[str]:
        """Generate learning insights."""
        return []  # Placeholder
