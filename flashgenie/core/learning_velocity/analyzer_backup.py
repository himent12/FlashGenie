"""
Velocity analysis utilities for the learning velocity tracking system.

This module provides functions to analyze learning velocity and identify patterns.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import statistics
import math

from .models import (
    VelocityDataPoint, VelocityTrendAnalysis, VelocityTrend, VelocityMetric,
    LearningPhase, VelocityPrediction, VelocityInsight, VelocityAlert
)


class VelocityAnalyzer:
    """Analyzes learning velocity data and identifies patterns."""
    
    def __init__(self):
        """Initialize the velocity analyzer."""
        self.trend_threshold = 0.1  # 10% change threshold
        self.alert_thresholds = {
            "velocity_decline": -0.2,  # 20% decline
            "velocity_improvement": 0.3,  # 30% improvement
            "accuracy_decline": -0.15,  # 15% decline
            "plateau_duration": 7  # days
        }
    
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
    
    def predict_future_velocity(
        self, 
        velocity_data: List[VelocityDataPoint],
        prediction_horizon: int = 7
    ) -> VelocityPrediction:
        """
        Predict future learning velocity.
        
        Args:
            velocity_data: Historical velocity data
            prediction_horizon: Days to predict ahead
            
        Returns:
            Velocity prediction
        """
        if len(velocity_data) < 5:
            # Insufficient data for prediction
            return VelocityPrediction(
                prediction_id=f"pred_{datetime.now().isoformat()}",
                created_at=datetime.now(),
                prediction_horizon=prediction_horizon,
                confidence_level=0.1,
                predicted_velocity=0.0,
                predicted_accuracy=0.0,
                predicted_efficiency=0.0
            )
        
        # Use recent data for prediction
        recent_data = velocity_data[-20:]  # Last 20 sessions
        
        # Extract metrics
        velocities = [d.cards_per_minute * 60 for d in recent_data]
        accuracies = [d.accuracy_rate for d in recent_data]
        efficiencies = [d.learning_efficiency * 60 for d in recent_data]
        
        # Simple trend-based prediction
        velocity_trend = self._calculate_trend(velocities)
        accuracy_trend = self._calculate_trend(accuracies)
        efficiency_trend = self._calculate_trend(efficiencies)
        
        # Current averages
        current_velocity = statistics.mean(velocities[-5:])  # Last 5 sessions
        current_accuracy = statistics.mean(accuracies[-5:])
        current_efficiency = statistics.mean(efficiencies[-5:])
        
        # Predict future values
        predicted_velocity = current_velocity + (velocity_trend * prediction_horizon)
        predicted_accuracy = min(1.0, max(0.0, current_accuracy + (accuracy_trend * prediction_horizon)))
        predicted_efficiency = current_efficiency + (efficiency_trend * prediction_horizon)
        
        # Calculate confidence based on data consistency
        velocity_variance = statistics.variance(velocities) if len(velocities) > 1 else 0
        confidence = max(0.1, min(0.9, 1.0 - (velocity_variance / (current_velocity + 0.1))))
        
        return VelocityPrediction(
            prediction_id=f"pred_{datetime.now().isoformat()}",
            created_at=datetime.now(),
            prediction_horizon=prediction_horizon,
            confidence_level=confidence,
            predicted_velocity=predicted_velocity,
            predicted_accuracy=predicted_accuracy,
            predicted_efficiency=predicted_efficiency,
            trend_factor=velocity_trend
        )
    
    def generate_velocity_insights(
        self, 
        velocity_data: List[VelocityDataPoint]
    ) -> List[VelocityInsight]:
        """
        Generate insights from velocity analysis.
        
        Args:
            velocity_data: Historical velocity data
            
        Returns:
            List of velocity insights
        """
        insights = []
        
        if len(velocity_data) < 5:
            return insights
        
        # Performance consistency insight
        consistency_insight = self._analyze_performance_consistency(velocity_data)
        if consistency_insight:
            insights.append(consistency_insight)
        
        # Optimal session length insight
        session_insight = self._analyze_optimal_session_length(velocity_data)
        if session_insight:
            insights.append(session_insight)
        
        # Time-of-day performance insight
        time_insight = self._analyze_time_patterns(velocity_data)
        if time_insight:
            insights.append(time_insight)
        
        # Difficulty progression insight
        difficulty_insight = self._analyze_difficulty_progression(velocity_data)
        if difficulty_insight:
            insights.append(difficulty_insight)
        
        return insights
    
    def detect_velocity_alerts(
        self, 
        velocity_data: List[VelocityDataPoint]
    ) -> List[VelocityAlert]:
        """
        Detect alerts based on velocity changes.
        
        Args:
            velocity_data: Historical velocity data
            
        Returns:
            List of velocity alerts
        """
        alerts = []
        
        if len(velocity_data) < 10:
            return alerts
        
        # Compare recent performance to baseline
        recent_data = velocity_data[-5:]  # Last 5 sessions
        baseline_data = velocity_data[-15:-5]  # Previous 10 sessions
        
        recent_velocity = statistics.mean([d.cards_per_minute * 60 for d in recent_data])
        baseline_velocity = statistics.mean([d.cards_per_minute * 60 for d in baseline_data])
        
        recent_accuracy = statistics.mean([d.accuracy_rate for d in recent_data])
        baseline_accuracy = statistics.mean([d.accuracy_rate for d in baseline_data])
        
        # Check for significant changes
        velocity_change = (recent_velocity - baseline_velocity) / (baseline_velocity + 0.1)
        accuracy_change = (recent_accuracy - baseline_accuracy) / (baseline_accuracy + 0.1)
        
        # Velocity decline alert
        if velocity_change < self.alert_thresholds["velocity_decline"]:
            alert = VelocityAlert(
                alert_id=f"alert_velocity_decline_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                alert_type="decline",
                metric_affected=VelocityMetric.CARDS_PER_HOUR,
                severity="medium" if velocity_change > -0.3 else "high",
                description=f"Learning velocity has declined by {abs(velocity_change):.1%}",
                current_value=recent_velocity,
                previous_value=baseline_velocity,
                threshold_crossed=self.alert_thresholds["velocity_decline"]
            )
            alerts.append(alert)
        
        # Velocity improvement alert
        elif velocity_change > self.alert_thresholds["velocity_improvement"]:
            alert = VelocityAlert(
                alert_id=f"alert_velocity_improvement_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                alert_type="improvement",
                metric_affected=VelocityMetric.CARDS_PER_HOUR,
                severity="low",
                description=f"Learning velocity has improved by {velocity_change:.1%}",
                current_value=recent_velocity,
                previous_value=baseline_velocity,
                threshold_crossed=self.alert_thresholds["velocity_improvement"]
            )
            alerts.append(alert)
        
        # Accuracy decline alert
        if accuracy_change < self.alert_thresholds["accuracy_decline"]:
            alert = VelocityAlert(
                alert_id=f"alert_accuracy_decline_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                alert_type="decline",
                metric_affected=VelocityMetric.ACCURACY_IMPROVEMENT,
                severity="medium" if accuracy_change > -0.25 else "high",
                description=f"Accuracy has declined by {abs(accuracy_change):.1%}",
                current_value=recent_accuracy,
                previous_value=baseline_accuracy,
                threshold_crossed=self.alert_thresholds["accuracy_decline"]
            )
            alerts.append(alert)
        
        return alerts
    
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
    
    def _analyze_performance_consistency(
        self, 
        velocity_data: List[VelocityDataPoint]
    ) -> Optional[VelocityInsight]:
        """Analyze performance consistency."""
        if len(velocity_data) < 10:
            return None
        
        # Calculate coefficient of variation for velocity
        velocities = [d.cards_per_minute * 60 for d in velocity_data[-20:]]
        
        if not velocities or statistics.mean(velocities) == 0:
            return None
        
        cv = statistics.stdev(velocities) / statistics.mean(velocities)
        
        if cv > 0.3:  # High variability
            return VelocityInsight(
                insight_id=f"consistency_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                insight_type="consistency",
                title="Inconsistent Performance Detected",
                description=f"Your learning velocity varies significantly (CV: {cv:.2f})",
                significance="medium",
                confidence=0.8,
                recommended_actions=[
                    "Establish a consistent study routine",
                    "Monitor factors affecting performance",
                    "Consider shorter, more frequent sessions"
                ],
                potential_improvement=0.2
            )
        
        return None
    
    def _analyze_optimal_session_length(
        self, 
        velocity_data: List[VelocityDataPoint]
    ) -> Optional[VelocityInsight]:
        """Analyze optimal session length."""
        if len(velocity_data) < 15:
            return None
        
        # Group sessions by duration ranges
        short_sessions = [d for d in velocity_data if d.session_duration <= 15]
        medium_sessions = [d for d in velocity_data if 15 < d.session_duration <= 30]
        long_sessions = [d for d in velocity_data if d.session_duration > 30]
        
        # Calculate average efficiency for each group
        groups = [
            ("short", short_sessions),
            ("medium", medium_sessions),
            ("long", long_sessions)
        ]
        
        group_efficiencies = {}
        for name, sessions in groups:
            if len(sessions) >= 3:
                avg_efficiency = statistics.mean([s.learning_efficiency for s in sessions])
                group_efficiencies[name] = avg_efficiency
        
        if len(group_efficiencies) < 2:
            return None
        
        # Find optimal duration
        best_group = max(group_efficiencies, key=group_efficiencies.get)
        
        duration_recommendations = {
            "short": "Consider shorter sessions (10-15 minutes) for optimal efficiency",
            "medium": "Medium sessions (15-30 minutes) work best for you",
            "long": "Longer sessions (30+ minutes) maximize your learning efficiency"
        }
        
        return VelocityInsight(
            insight_id=f"session_length_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            insight_type="optimization",
            title="Optimal Session Length Identified",
            description=duration_recommendations[best_group],
            significance="medium",
            confidence=0.7,
            recommended_actions=[
                f"Plan sessions in the {best_group} duration range",
                "Monitor efficiency across different session lengths",
                "Adjust based on energy levels and content difficulty"
            ],
            potential_improvement=0.15
        )
    
    def _analyze_time_patterns(
        self, 
        velocity_data: List[VelocityDataPoint]
    ) -> Optional[VelocityInsight]:
        """Analyze time-of-day performance patterns."""
        if len(velocity_data) < 20:
            return None
        
        # Group by time of day (simplified)
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
            time_groups[time_period].append(data_point.learning_efficiency)
        
        # Find best time period
        time_averages = {}
        for period, efficiencies in time_groups.items():
            if len(efficiencies) >= 3:
                time_averages[period] = statistics.mean(efficiencies)
        
        if len(time_averages) < 2:
            return None
        
        best_time = max(time_averages, key=time_averages.get)
        worst_time = min(time_averages, key=time_averages.get)
        
        improvement_potential = time_averages[best_time] - time_averages[worst_time]
        
        if improvement_potential > 0.1:  # Significant difference
            return VelocityInsight(
                insight_id=f"time_pattern_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                insight_type="timing",
                title="Optimal Study Time Identified",
                description=f"You perform best during {best_time} sessions",
                significance="medium",
                confidence=0.7,
                evidence=[f"{best_time.title()}: {time_averages[best_time]:.2f} efficiency"],
                recommended_actions=[
                    f"Schedule important study sessions during {best_time}",
                    f"Use {worst_time} for lighter review activities",
                    "Track energy levels at different times"
                ],
                potential_improvement=improvement_potential
            )
        
        return None
    
    def _analyze_difficulty_progression(
        self, 
        velocity_data: List[VelocityDataPoint]
    ) -> Optional[VelocityInsight]:
        """Analyze difficulty progression patterns."""
        if len(velocity_data) < 15:
            return None
        
        # Group by difficulty levels
        easy_sessions = [d for d in velocity_data if d.difficulty_level <= 0.4]
        medium_sessions = [d for d in velocity_data if 0.4 < d.difficulty_level <= 0.7]
        hard_sessions = [d for d in velocity_data if d.difficulty_level > 0.7]
        
        # Calculate accuracy for each difficulty level
        difficulty_performance = {}
        
        for name, sessions in [("easy", easy_sessions), ("medium", medium_sessions), ("hard", hard_sessions)]:
            if len(sessions) >= 3:
                avg_accuracy = statistics.mean([s.accuracy_rate for s in sessions])
                difficulty_performance[name] = avg_accuracy
        
        if len(difficulty_performance) < 2:
            return None
        
        # Check if user is ready for harder content
        if "medium" in difficulty_performance and difficulty_performance["medium"] > 0.85:
            if "hard" not in difficulty_performance or len(hard_sessions) < 3:
                return VelocityInsight(
                    insight_id=f"difficulty_progression_{datetime.now().isoformat()}",
                    timestamp=datetime.now(),
                    insight_type="progression",
                    title="Ready for More Challenging Content",
                    description="High accuracy on medium difficulty suggests readiness for harder material",
                    significance="medium",
                    confidence=0.8,
                    evidence=[f"Medium difficulty accuracy: {difficulty_performance['medium']:.1%}"],
                    recommended_actions=[
                        "Gradually introduce harder content",
                        "Mix difficulty levels in study sessions",
                        "Monitor accuracy as difficulty increases"
                    ],
                    potential_improvement=0.2
                )
        
        return None
