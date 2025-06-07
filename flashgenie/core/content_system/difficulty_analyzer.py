"""
Smart difficulty analysis for FlashGenie.

This module provides intelligent difficulty adjustment based on user performance,
response times, and learning patterns to optimize the spaced repetition experience.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics
from enum import Enum

from .flashcard import Flashcard


class ConfidenceLevel(Enum):
    """User confidence levels for self-assessment."""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


@dataclass
class PerformanceMetrics:
    """Metrics for analyzing card performance."""
    average_response_time: float
    accuracy_rate: float
    consistency_score: float  # How consistent the performance is
    recent_trend: float  # Positive = improving, negative = declining
    confidence_trend: float  # User's confidence over time


class DifficultyAnalyzer:
    """
    Analyzes flashcard performance and suggests difficulty adjustments.
    
    Uses multiple factors to determine optimal difficulty:
    - Response time patterns
    - Accuracy trends
    - User confidence ratings
    - Learning velocity
    - Consistency metrics
    """
    
    def __init__(self):
        """Initialize the difficulty analyzer with default thresholds."""
        # Response time thresholds (in seconds)
        self.fast_response_threshold = 3.0
        self.slow_response_threshold = 10.0
        
        # Accuracy thresholds
        self.high_accuracy_threshold = 0.85
        self.low_accuracy_threshold = 0.60
        
        # Minimum reviews needed for reliable analysis
        self.min_reviews_for_analysis = 3
        
        # Difficulty adjustment factors
        self.max_difficulty_change = 0.2  # Maximum change per adjustment
        self.confidence_weight = 0.3
        self.response_time_weight = 0.4
        self.accuracy_weight = 0.3
    
    def analyze_card_performance(self, flashcard: Flashcard, 
                                recent_sessions: List[Dict[str, Any]] = None) -> PerformanceMetrics:
        """
        Analyze the performance metrics for a flashcard.
        
        Args:
            flashcard: The flashcard to analyze
            recent_sessions: Recent quiz session data for this card
            
        Returns:
            Performance metrics for the card
        """
        if flashcard.review_count < self.min_reviews_for_analysis:
            # Not enough data for reliable analysis
            return PerformanceMetrics(
                average_response_time=5.0,  # Default
                accuracy_rate=flashcard.accuracy,
                consistency_score=0.5,  # Neutral
                recent_trend=0.0,  # No trend
                confidence_trend=0.0
            )
        
        # Calculate metrics from flashcard data
        accuracy_rate = flashcard.accuracy
        
        # Estimate response time trend (would be enhanced with session data)
        avg_response_time = self._estimate_response_time(flashcard)
        
        # Calculate consistency (how stable the performance is)
        consistency_score = self._calculate_consistency(flashcard, recent_sessions)
        
        # Calculate recent performance trend
        recent_trend = self._calculate_trend(flashcard, recent_sessions)
        
        # Confidence trend (placeholder - would use actual confidence ratings)
        confidence_trend = self._estimate_confidence_trend(flashcard)
        
        return PerformanceMetrics(
            average_response_time=avg_response_time,
            accuracy_rate=accuracy_rate,
            consistency_score=consistency_score,
            recent_trend=recent_trend,
            confidence_trend=confidence_trend
        )
    
    def suggest_difficulty_adjustment(self, flashcard: Flashcard, 
                                    performance: PerformanceMetrics,
                                    user_confidence: Optional[ConfidenceLevel] = None) -> float:
        """
        Suggest a new difficulty level based on performance analysis.
        
        Args:
            flashcard: The flashcard to adjust
            performance: Performance metrics
            user_confidence: Optional user confidence rating
            
        Returns:
            Suggested new difficulty level (0.0 to 1.0)
        """
        current_difficulty = flashcard.difficulty
        
        # Calculate adjustment factors
        accuracy_factor = self._calculate_accuracy_factor(performance.accuracy_rate)
        response_time_factor = self._calculate_response_time_factor(performance.average_response_time)
        consistency_factor = self._calculate_consistency_factor(performance.consistency_score)
        trend_factor = self._calculate_trend_factor(performance.recent_trend)
        
        # User confidence factor
        confidence_factor = 0.0
        if user_confidence:
            confidence_factor = self._calculate_confidence_factor(user_confidence)
        
        # Weighted combination of factors
        total_adjustment = (
            accuracy_factor * self.accuracy_weight +
            response_time_factor * self.response_time_weight +
            confidence_factor * self.confidence_weight +
            trend_factor * 0.1 +  # Small weight for trend
            consistency_factor * 0.1  # Small weight for consistency
        )
        
        # Apply adjustment with limits
        new_difficulty = current_difficulty + total_adjustment
        new_difficulty = max(0.0, min(1.0, new_difficulty))
        
        # Limit the change per adjustment
        max_change = self.max_difficulty_change
        if abs(new_difficulty - current_difficulty) > max_change:
            if new_difficulty > current_difficulty:
                new_difficulty = current_difficulty + max_change
            else:
                new_difficulty = current_difficulty - max_change
        
        return new_difficulty
    
    def _estimate_response_time(self, flashcard: Flashcard) -> float:
        """Estimate average response time based on difficulty and performance."""
        # This is a simplified estimation - would be enhanced with actual timing data
        base_time = 5.0  # Base response time in seconds
        difficulty_multiplier = 1.0 + (flashcard.difficulty * 2.0)
        accuracy_multiplier = 2.0 - flashcard.accuracy  # Lower accuracy = longer time
        
        return base_time * difficulty_multiplier * accuracy_multiplier
    
    def _calculate_consistency(self, flashcard: Flashcard, 
                             recent_sessions: List[Dict[str, Any]] = None) -> float:
        """Calculate performance consistency score."""
        if not recent_sessions or len(recent_sessions) < 3:
            # Use accuracy as a proxy for consistency
            return min(flashcard.accuracy * 1.2, 1.0)
        
        # Calculate variance in recent performance
        recent_accuracies = [session.get('correct', False) for session in recent_sessions[-10:]]
        if len(recent_accuracies) < 2:
            return 0.5
        
        # Higher consistency = lower variance
        variance = statistics.variance([1.0 if acc else 0.0 for acc in recent_accuracies])
        consistency = max(0.0, 1.0 - variance)
        
        return consistency
    
    def _calculate_trend(self, flashcard: Flashcard, 
                        recent_sessions: List[Dict[str, Any]] = None) -> float:
        """Calculate recent performance trend."""
        if not recent_sessions or len(recent_sessions) < 5:
            return 0.0  # No trend data
        
        # Compare recent performance to earlier performance
        recent_performance = recent_sessions[-5:]
        earlier_performance = recent_sessions[-10:-5] if len(recent_sessions) >= 10 else []
        
        if not earlier_performance:
            return 0.0
        
        recent_accuracy = sum(1 for session in recent_performance if session.get('correct', False)) / len(recent_performance)
        earlier_accuracy = sum(1 for session in earlier_performance if session.get('correct', False)) / len(earlier_performance)
        
        # Return trend (-1 to 1)
        return recent_accuracy - earlier_accuracy
    
    def _estimate_confidence_trend(self, flashcard: Flashcard) -> float:
        """Estimate confidence trend based on performance."""
        # Simplified estimation - would use actual confidence ratings
        if flashcard.accuracy > 0.8 and flashcard.review_count > 5:
            return 0.2  # Likely increasing confidence
        elif flashcard.accuracy < 0.5:
            return -0.2  # Likely decreasing confidence
        return 0.0
    
    def _calculate_accuracy_factor(self, accuracy: float) -> float:
        """Calculate difficulty adjustment based on accuracy."""
        if accuracy > self.high_accuracy_threshold:
            # High accuracy - increase difficulty
            return (accuracy - self.high_accuracy_threshold) * 0.5
        elif accuracy < self.low_accuracy_threshold:
            # Low accuracy - decrease difficulty
            return (accuracy - self.low_accuracy_threshold) * 0.5
        else:
            # Moderate accuracy - small adjustment
            return (accuracy - 0.75) * 0.1
    
    def _calculate_response_time_factor(self, response_time: float) -> float:
        """Calculate difficulty adjustment based on response time."""
        if response_time < self.fast_response_threshold:
            # Fast response - increase difficulty
            return 0.1
        elif response_time > self.slow_response_threshold:
            # Slow response - decrease difficulty
            return -0.1
        else:
            # Normal response time - no adjustment
            return 0.0
    
    def _calculate_consistency_factor(self, consistency: float) -> float:
        """Calculate adjustment based on performance consistency."""
        if consistency > 0.8:
            # Very consistent - can handle slight increase
            return 0.05
        elif consistency < 0.4:
            # Inconsistent - decrease difficulty
            return -0.05
        return 0.0
    
    def _calculate_trend_factor(self, trend: float) -> float:
        """Calculate adjustment based on performance trend."""
        # Positive trend = improving, negative = declining
        return trend * 0.1
    
    def _calculate_confidence_factor(self, confidence: ConfidenceLevel) -> float:
        """Calculate adjustment based on user confidence."""
        confidence_map = {
            ConfidenceLevel.VERY_LOW: -0.15,
            ConfidenceLevel.LOW: -0.05,
            ConfidenceLevel.MEDIUM: 0.0,
            ConfidenceLevel.HIGH: 0.05,
            ConfidenceLevel.VERY_HIGH: 0.15
        }
        return confidence_map.get(confidence, 0.0)
    
    def get_difficulty_explanation(self, old_difficulty: float, 
                                 new_difficulty: float,
                                 performance: PerformanceMetrics) -> str:
        """
        Generate a human-readable explanation for difficulty adjustment.
        
        Args:
            old_difficulty: Previous difficulty level
            new_difficulty: New difficulty level
            performance: Performance metrics used for adjustment
            
        Returns:
            Explanation string
        """
        change = new_difficulty - old_difficulty
        
        if abs(change) < 0.01:
            return "Difficulty maintained - performance is stable"
        
        direction = "increased" if change > 0 else "decreased"
        magnitude = "slightly" if abs(change) < 0.1 else "moderately" if abs(change) < 0.2 else "significantly"
        
        reasons = []
        
        if performance.accuracy_rate > 0.85:
            reasons.append("high accuracy")
        elif performance.accuracy_rate < 0.6:
            reasons.append("low accuracy")
        
        if performance.average_response_time < 3.0:
            reasons.append("fast response times")
        elif performance.average_response_time > 10.0:
            reasons.append("slow response times")
        
        if performance.recent_trend > 0.1:
            reasons.append("improving performance")
        elif performance.recent_trend < -0.1:
            reasons.append("declining performance")
        
        reason_text = ", ".join(reasons) if reasons else "overall performance patterns"
        
        return f"Difficulty {direction} {magnitude} based on {reason_text}"
    
    def should_adjust_difficulty(self, flashcard: Flashcard, 
                               performance: PerformanceMetrics) -> bool:
        """
        Determine if difficulty should be adjusted based on performance.
        
        Args:
            flashcard: The flashcard to evaluate
            performance: Performance metrics
            
        Returns:
            True if difficulty should be adjusted
        """
        # Don't adjust if not enough reviews
        if flashcard.review_count < self.min_reviews_for_analysis:
            return False
        
        # Adjust if accuracy is very high or very low
        if (performance.accuracy_rate > self.high_accuracy_threshold or 
            performance.accuracy_rate < self.low_accuracy_threshold):
            return True
        
        # Adjust if there's a strong trend
        if abs(performance.recent_trend) > 0.2:
            return True
        
        # Adjust if response time is consistently very fast or slow
        if (performance.average_response_time < self.fast_response_threshold or 
            performance.average_response_time > self.slow_response_threshold):
            return True
        
        return False
