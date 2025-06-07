"""
Trend analysis utilities for the learning velocity tracking system.

This module provides functions to analyze velocity trends and patterns.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import statistics

from .models import (
    VelocityDataPoint, VelocityTrendAnalysis, VelocityTrend, VelocityMetric,
    LearningPhase
)


class VelocityTrendAnalyzer:
    """Analyzes learning velocity trends and patterns."""
    
    def __init__(self):
        """Initialize the trend analyzer."""
        self.trend_threshold = 0.1  # 10% change threshold
    
    def analyze_velocity_trends(
        self, 
        velocity_data: List[VelocityDataPoint],
        analysis_period: int = 30
    ) -> List[VelocityTrendAnalysis]:
        """
        Analyze velocity trends over a specified period.
        
        Args:
            velocity_data: Historical velocity data points
            analysis_period: Period in days to analyze
            
        Returns:
            List of trend analyses for different metrics
        """
        if len(velocity_data) < 2:
            return []
        
        # Filter data to analysis period
        cutoff_date = datetime.now() - timedelta(days=analysis_period)
        recent_data = [d for d in velocity_data if d.timestamp >= cutoff_date]
        
        if len(recent_data) < 2:
            return []
        
        trends = []
        
        # Analyze different velocity metrics
        metrics_to_analyze = [
            VelocityMetric.CARDS_PER_HOUR,
            VelocityMetric.ACCURACY_IMPROVEMENT,
            VelocityMetric.RETENTION_RATE
        ]
        
        for metric in metrics_to_analyze:
            trend_analysis = self._analyze_single_metric_trend(recent_data, metric, analysis_period)
            if trend_analysis:
                trends.append(trend_analysis)
        
        return trends
    
    def detect_learning_phase(self, velocity_data: List[VelocityDataPoint]) -> LearningPhase:
        """
        Detect the current learning phase based on velocity patterns.
        
        Args:
            velocity_data: Historical velocity data
            
        Returns:
            Current learning phase
        """
        if len(velocity_data) < 5:
            return LearningPhase.INITIAL
        
        # Analyze recent trends
        recent_data = velocity_data[-10:]  # Last 10 sessions
        
        # Calculate velocity trend
        velocities = [d.cards_per_minute * 60 for d in recent_data]  # Convert to cards per hour
        accuracies = [d.accuracy_rate for d in recent_data]
        
        velocity_trend = self._calculate_trend(velocities)
        accuracy_trend = self._calculate_trend(accuracies)
        
        # Determine phase based on trends and absolute values
        avg_velocity = statistics.mean(velocities)
        avg_accuracy = statistics.mean(accuracies)
        
        if avg_accuracy < 0.6:
            return LearningPhase.INITIAL
        elif velocity_trend > 0.1 and accuracy_trend > 0.05:
            return LearningPhase.ACCELERATION
        elif abs(velocity_trend) < 0.05 and abs(accuracy_trend) < 0.02:
            if avg_accuracy > 0.85:
                return LearningPhase.MASTERY
            else:
                return LearningPhase.PLATEAU
        elif avg_accuracy > 0.9 and velocity_trend < 0.05:
            return LearningPhase.MAINTENANCE
        else:
            return LearningPhase.ACCELERATION
    
    def analyze_velocity_patterns(self, velocity_data: List[VelocityDataPoint]) -> Dict[str, Any]:
        """
        Analyze various velocity patterns.
        
        Args:
            velocity_data: Historical velocity data
            
        Returns:
            Dictionary with pattern analysis results
        """
        if len(velocity_data) < 5:
            return {}
        
        patterns = {}
        
        # Analyze consistency patterns
        patterns["consistency"] = self._analyze_consistency_patterns(velocity_data)
        
        # Analyze time-based patterns
        patterns["time_patterns"] = self._analyze_time_based_patterns(velocity_data)
        
        # Analyze session length patterns
        patterns["session_patterns"] = self._analyze_session_length_patterns(velocity_data)
        
        # Analyze difficulty progression patterns
        patterns["difficulty_patterns"] = self._analyze_difficulty_patterns(velocity_data)
        
        return patterns
    
    def _analyze_single_metric_trend(
        self, 
        data: List[VelocityDataPoint], 
        metric: VelocityMetric,
        period: int
    ) -> Optional[VelocityTrendAnalysis]:
        """Analyze trend for a single metric."""
        if len(data) < 2:
            return None
        
        # Extract values based on metric type
        if metric == VelocityMetric.CARDS_PER_HOUR:
            values = [d.cards_per_minute * 60 for d in data]
        elif metric == VelocityMetric.ACCURACY_IMPROVEMENT:
            values = [d.accuracy_rate for d in data]
        else:
            values = [d.learning_efficiency for d in data]
        
        if not values:
            return None
        
        # Calculate trend
        trend_value = self._calculate_trend(values)
        current_value = statistics.mean(values[-3:]) if len(values) >= 3 else values[-1]
        previous_value = statistics.mean(values[:3]) if len(values) >= 6 else values[0]
        
        # Determine trend type
        if abs(trend_value) < self.trend_threshold:
            trend_type = VelocityTrend.STABLE
        elif trend_value > self.trend_threshold:
            trend_type = VelocityTrend.ACCELERATING
        else:
            trend_type = VelocityTrend.DECLINING
        
        # Calculate change percentage
        change_percentage = ((current_value - previous_value) / (previous_value + 0.001)) * 100
        
        # Calculate confidence based on data consistency
        variance = statistics.variance(values) if len(values) > 1 else 0
        confidence = max(0.1, min(0.9, 1.0 - (variance / (current_value + 0.1))))
        
        return VelocityTrendAnalysis(
            metric_type=metric,
            trend=trend_type,
            confidence=confidence,
            current_value=current_value,
            previous_value=previous_value,
            change_percentage=change_percentage,
            analysis_period=period,
            data_points=len(data),
            description=self._generate_trend_description(metric, trend_type, change_percentage)
        )
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend using simple linear regression."""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        
        # Calculate slope using least squares
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope
    
    def _generate_trend_description(
        self, 
        metric: VelocityMetric, 
        trend: VelocityTrend, 
        change_percentage: float
    ) -> str:
        """Generate a description for a trend analysis."""
        metric_name = metric.value.replace('_', ' ').title()
        
        if trend == VelocityTrend.ACCELERATING:
            return f"{metric_name} is improving by {change_percentage:.1f}%"
        elif trend == VelocityTrend.DECLINING:
            return f"{metric_name} is declining by {abs(change_percentage):.1f}%"
        elif trend == VelocityTrend.STABLE:
            return f"{metric_name} is stable with minimal change"
        else:
            return f"{metric_name} shows fluctuating patterns"
    
    def _analyze_consistency_patterns(self, velocity_data: List[VelocityDataPoint]) -> Dict[str, Any]:
        """Analyze consistency patterns in velocity data."""
        if len(velocity_data) < 5:
            return {}
        
        velocities = [d.cards_per_minute * 60 for d in velocity_data[-20:]]
        accuracies = [d.accuracy_rate for d in velocity_data[-20:]]
        
        velocity_cv = statistics.stdev(velocities) / statistics.mean(velocities) if statistics.mean(velocities) > 0 else 0
        accuracy_cv = statistics.stdev(accuracies) / statistics.mean(accuracies) if statistics.mean(accuracies) > 0 else 0
        
        return {
            "velocity_consistency": 1.0 - min(1.0, velocity_cv),
            "accuracy_consistency": 1.0 - min(1.0, accuracy_cv),
            "overall_consistency": 1.0 - min(1.0, (velocity_cv + accuracy_cv) / 2)
        }
    
    def _analyze_time_based_patterns(self, velocity_data: List[VelocityDataPoint]) -> Dict[str, Any]:
        """Analyze time-based performance patterns."""
        if len(velocity_data) < 10:
            return {}
        
        time_groups = {}
        for data_point in velocity_data:
            hour = data_point.timestamp.hour
            
            if 6 <= hour < 12:
                time_period = "morning"
            elif 12 <= hour < 18:
                time_period = "afternoon"
            elif 18 <= hour < 22:
                time_period = "evening"
            else:
                time_period = "night"
            
            if time_period not in time_groups:
                time_groups[time_period] = []
            time_groups[time_period].append(data_point)
        
        # Calculate average performance for each time period
        time_performance = {}
        for period, data_points in time_groups.items():
            if len(data_points) >= 3:
                avg_velocity = statistics.mean([d.cards_per_minute * 60 for d in data_points])
                avg_accuracy = statistics.mean([d.accuracy_rate for d in data_points])
                time_performance[period] = {
                    "velocity": avg_velocity,
                    "accuracy": avg_accuracy,
                    "sessions": len(data_points)
                }
        
        return time_performance
    
    def _analyze_session_length_patterns(self, velocity_data: List[VelocityDataPoint]) -> Dict[str, Any]:
        """Analyze session length performance patterns."""
        if len(velocity_data) < 10:
            return {}
        
        # Group sessions by duration ranges
        duration_groups = {
            "short": [d for d in velocity_data if d.session_duration <= 15],
            "medium": [d for d in velocity_data if 15 < d.session_duration <= 30],
            "long": [d for d in velocity_data if d.session_duration > 30]
        }
        
        duration_performance = {}
        for duration_type, data_points in duration_groups.items():
            if len(data_points) >= 3:
                avg_efficiency = statistics.mean([d.learning_efficiency for d in data_points])
                avg_velocity = statistics.mean([d.cards_per_minute * 60 for d in data_points])
                duration_performance[duration_type] = {
                    "efficiency": avg_efficiency,
                    "velocity": avg_velocity,
                    "sessions": len(data_points)
                }
        
        return duration_performance
    
    def _analyze_difficulty_patterns(self, velocity_data: List[VelocityDataPoint]) -> Dict[str, Any]:
        """Analyze difficulty progression patterns."""
        if len(velocity_data) < 10:
            return {}
        
        # Group by difficulty levels (if available in metadata)
        difficulty_groups = {}
        for data_point in velocity_data:
            difficulty = data_point.metadata.get("avg_difficulty", 0.5)
            
            if difficulty < 0.3:
                difficulty_level = "easy"
            elif difficulty < 0.7:
                difficulty_level = "medium"
            else:
                difficulty_level = "hard"
            
            if difficulty_level not in difficulty_groups:
                difficulty_groups[difficulty_level] = []
            difficulty_groups[difficulty_level].append(data_point)
        
        difficulty_performance = {}
        for level, data_points in difficulty_groups.items():
            if len(data_points) >= 3:
                avg_accuracy = statistics.mean([d.accuracy_rate for d in data_points])
                avg_velocity = statistics.mean([d.cards_per_minute * 60 for d in data_points])
                difficulty_performance[level] = {
                    "accuracy": avg_accuracy,
                    "velocity": avg_velocity,
                    "sessions": len(data_points)
                }
        
        return difficulty_performance
