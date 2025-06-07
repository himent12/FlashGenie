"""
Alert detection utilities for the learning velocity tracking system.

This module provides functions to detect velocity alerts and anomalies.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import statistics

from .models import VelocityDataPoint, VelocityAlert, VelocityMetric


class VelocityAlertDetector:
    """Detects velocity alerts and anomalies."""
    
    def __init__(self):
        """Initialize the alert detector."""
        self.alert_thresholds = {
            "velocity_decline": -0.2,  # 20% decline
            "velocity_improvement": 0.3,  # 30% improvement
            "accuracy_decline": -0.15,  # 15% decline
            "accuracy_improvement": 0.2,  # 20% improvement
            "efficiency_decline": -0.25,  # 25% decline
            "plateau_duration": 7,  # days
            "consistency_threshold": 0.4,  # CV threshold for inconsistency
            "session_gap": 3  # days without sessions
        }
    
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
        
        # Performance change alerts
        alerts.extend(self._detect_performance_change_alerts(velocity_data))
        
        # Consistency alerts
        alerts.extend(self._detect_consistency_alerts(velocity_data))
        
        # Plateau alerts
        alerts.extend(self._detect_plateau_alerts(velocity_data))
        
        # Session gap alerts
        alerts.extend(self._detect_session_gap_alerts(velocity_data))
        
        # Anomaly alerts
        alerts.extend(self._detect_anomaly_alerts(velocity_data))
        
        return alerts
    
    def _detect_performance_change_alerts(
        self, 
        velocity_data: List[VelocityDataPoint]
    ) -> List[VelocityAlert]:
        """Detect performance change alerts."""
        alerts = []
        
        # Compare recent performance to baseline
        recent_data = velocity_data[-5:]  # Last 5 sessions
        baseline_data = velocity_data[-15:-5]  # Previous 10 sessions
        
        if len(baseline_data) < 5:
            return alerts
        
        recent_velocity = statistics.mean([d.cards_per_minute * 60 for d in recent_data])
        baseline_velocity = statistics.mean([d.cards_per_minute * 60 for d in baseline_data])
        
        recent_accuracy = statistics.mean([d.accuracy_rate for d in recent_data])
        baseline_accuracy = statistics.mean([d.accuracy_rate for d in baseline_data])
        
        recent_efficiency = statistics.mean([d.learning_efficiency for d in recent_data])
        baseline_efficiency = statistics.mean([d.learning_efficiency for d in baseline_data])
        
        # Check for significant changes
        velocity_change = (recent_velocity - baseline_velocity) / (baseline_velocity + 0.1)
        accuracy_change = (recent_accuracy - baseline_accuracy) / (baseline_accuracy + 0.1)
        efficiency_change = (recent_efficiency - baseline_efficiency) / (baseline_efficiency + 0.1)
        
        # Velocity alerts
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
                threshold_crossed=self.alert_thresholds["velocity_decline"],
                recommended_actions=[
                    "Review recent study conditions",
                    "Consider taking a break to recharge",
                    "Evaluate study environment and methods"
                ]
            )
            alerts.append(alert)
        
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
                threshold_crossed=self.alert_thresholds["velocity_improvement"],
                recommended_actions=[
                    "Maintain current study strategies",
                    "Document what's working well",
                    "Consider gradually increasing difficulty"
                ]
            )
            alerts.append(alert)
        
        # Accuracy alerts
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
                threshold_crossed=self.alert_thresholds["accuracy_decline"],
                recommended_actions=[
                    "Review difficult concepts",
                    "Reduce study pace temporarily",
                    "Focus on understanding over speed"
                ]
            )
            alerts.append(alert)
        
        elif accuracy_change > self.alert_thresholds["accuracy_improvement"]:
            alert = VelocityAlert(
                alert_id=f"alert_accuracy_improvement_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                alert_type="improvement",
                metric_affected=VelocityMetric.ACCURACY_IMPROVEMENT,
                severity="low",
                description=f"Accuracy has improved by {accuracy_change:.1%}",
                current_value=recent_accuracy,
                previous_value=baseline_accuracy,
                threshold_crossed=self.alert_thresholds["accuracy_improvement"],
                recommended_actions=[
                    "Continue current learning approach",
                    "Consider increasing difficulty level",
                    "Celebrate your progress"
                ]
            )
            alerts.append(alert)
        
        # Efficiency alerts
        if efficiency_change < self.alert_thresholds["efficiency_decline"]:
            alert = VelocityAlert(
                alert_id=f"alert_efficiency_decline_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                alert_type="decline",
                metric_affected=VelocityMetric.LEARNING_EFFICIENCY,
                severity="medium",
                description=f"Learning efficiency has declined by {abs(efficiency_change):.1%}",
                current_value=recent_efficiency,
                previous_value=baseline_efficiency,
                threshold_crossed=self.alert_thresholds["efficiency_decline"],
                recommended_actions=[
                    "Evaluate study methods and environment",
                    "Consider changing study schedule",
                    "Take breaks to avoid burnout"
                ]
            )
            alerts.append(alert)
        
        return alerts
    
    def _detect_consistency_alerts(
        self, 
        velocity_data: List[VelocityDataPoint]
    ) -> List[VelocityAlert]:
        """Detect consistency-related alerts."""
        alerts = []
        
        if len(velocity_data) < 15:
            return alerts
        
        # Calculate coefficient of variation for recent sessions
        recent_velocities = [d.cards_per_minute * 60 for d in velocity_data[-15:]]
        recent_accuracies = [d.accuracy_rate for d in velocity_data[-15:]]
        
        if statistics.mean(recent_velocities) > 0:
            velocity_cv = statistics.stdev(recent_velocities) / statistics.mean(recent_velocities)
        else:
            velocity_cv = 0
        
        if statistics.mean(recent_accuracies) > 0:
            accuracy_cv = statistics.stdev(recent_accuracies) / statistics.mean(recent_accuracies)
        else:
            accuracy_cv = 0
        
        # High inconsistency alert
        if velocity_cv > self.alert_thresholds["consistency_threshold"]:
            alert = VelocityAlert(
                alert_id=f"alert_inconsistency_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                alert_type="inconsistency",
                metric_affected=VelocityMetric.CARDS_PER_HOUR,
                severity="medium",
                description=f"High performance variability detected (CV: {velocity_cv:.2f})",
                current_value=velocity_cv,
                previous_value=None,
                threshold_crossed=self.alert_thresholds["consistency_threshold"],
                recommended_actions=[
                    "Establish a consistent study routine",
                    "Monitor factors affecting performance",
                    "Consider standardizing study environment"
                ]
            )
            alerts.append(alert)
        
        return alerts
    
    def _detect_plateau_alerts(
        self, 
        velocity_data: List[VelocityDataPoint]
    ) -> List[VelocityAlert]:
        """Detect learning plateau alerts."""
        alerts = []
        
        if len(velocity_data) < 20:
            return alerts
        
        # Check for extended periods without improvement
        recent_data = velocity_data[-14:]  # Last 2 weeks
        
        velocities = [d.cards_per_minute * 60 for d in recent_data]
        accuracies = [d.accuracy_rate for d in recent_data]
        
        # Calculate trend (slope)
        from .trend_analyzer import VelocityTrendAnalyzer
        trend_analyzer = VelocityTrendAnalyzer()
        
        velocity_trend = trend_analyzer._calculate_trend(velocities)
        accuracy_trend = trend_analyzer._calculate_trend(accuracies)
        
        # Plateau detected if both trends are near zero
        if abs(velocity_trend) < 0.02 and abs(accuracy_trend) < 0.01:
            alert = VelocityAlert(
                alert_id=f"alert_plateau_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                alert_type="plateau",
                metric_affected=VelocityMetric.CARDS_PER_HOUR,
                severity="low",
                description="Learning plateau detected - minimal progress in recent sessions",
                current_value=statistics.mean(velocities[-5:]),
                previous_value=statistics.mean(velocities[:5]),
                threshold_crossed=0.02,
                recommended_actions=[
                    "Try new study techniques or methods",
                    "Increase difficulty or introduce new topics",
                    "Take a short break to refresh motivation",
                    "Vary study environment or schedule"
                ]
            )
            alerts.append(alert)
        
        return alerts
    
    def _detect_session_gap_alerts(
        self, 
        velocity_data: List[VelocityDataPoint]
    ) -> List[VelocityAlert]:
        """Detect alerts for gaps in study sessions."""
        alerts = []
        
        if len(velocity_data) < 2:
            return alerts
        
        # Check time since last session
        last_session = velocity_data[-1].timestamp
        time_since_last = datetime.now() - last_session
        
        if time_since_last.days >= self.alert_thresholds["session_gap"]:
            alert = VelocityAlert(
                alert_id=f"alert_session_gap_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                alert_type="gap",
                metric_affected=VelocityMetric.CARDS_PER_HOUR,
                severity="medium" if time_since_last.days < 7 else "high",
                description=f"No study sessions for {time_since_last.days} days",
                current_value=time_since_last.days,
                previous_value=0,
                threshold_crossed=self.alert_thresholds["session_gap"],
                recommended_actions=[
                    "Resume regular study schedule",
                    "Start with a light review session",
                    "Set reminders for future sessions"
                ]
            )
            alerts.append(alert)
        
        return alerts
    
    def _detect_anomaly_alerts(
        self, 
        velocity_data: List[VelocityDataPoint]
    ) -> List[VelocityAlert]:
        """Detect anomalous performance patterns."""
        alerts = []
        
        if len(velocity_data) < 10:
            return alerts
        
        # Detect sudden drops in performance
        recent_sessions = velocity_data[-3:]
        baseline_sessions = velocity_data[-10:-3]
        
        recent_avg = statistics.mean([d.accuracy_rate for d in recent_sessions])
        baseline_avg = statistics.mean([d.accuracy_rate for d in baseline_sessions])
        
        # Sudden drop alert
        if recent_avg < baseline_avg * 0.7:  # 30% drop
            alert = VelocityAlert(
                alert_id=f"alert_sudden_drop_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                alert_type="anomaly",
                metric_affected=VelocityMetric.ACCURACY_IMPROVEMENT,
                severity="high",
                description=f"Sudden performance drop detected ({recent_avg:.1%} vs {baseline_avg:.1%})",
                current_value=recent_avg,
                previous_value=baseline_avg,
                threshold_crossed=0.7,
                recommended_actions=[
                    "Check for external factors affecting performance",
                    "Consider taking a break if feeling overwhelmed",
                    "Review recent study material for difficulty spikes"
                ]
            )
            alerts.append(alert)
        
        return alerts
