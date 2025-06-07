"""
Velocity analysis utilities for the learning velocity tracking system.

This module provides functions to analyze learning velocity and identify patterns.
Refactored for better maintainability and smaller file size.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import statistics
import logging

from .models import (
    VelocityDataPoint, VelocityTrendAnalysis, VelocityTrend, VelocityMetric,
    LearningPhase, VelocityPrediction, VelocityInsight, VelocityAlert
)
from .trend_analyzer import VelocityTrendAnalyzer
from .velocity_insight_generator import VelocityInsightGenerator
from .alert_detector import VelocityAlertDetector


class VelocityAnalyzer:
    """Analyzes learning velocity data and identifies patterns."""
    
    def __init__(self):
        """Initialize the velocity analyzer."""
        self.trend_analyzer = VelocityTrendAnalyzer()
        self.insight_generator = VelocityInsightGenerator()
        self.alert_detector = VelocityAlertDetector()
        
        self.logger = logging.getLogger(__name__)
    
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
        try:
            trends = self.trend_analyzer.analyze_velocity_trends(velocity_data, analysis_period)
            self.logger.debug(f"Analyzed {len(trends)} velocity trends")
            return trends
        except Exception as e:
            self.logger.error(f"Error analyzing velocity trends: {e}")
            return []
    
    def detect_learning_phase(self, velocity_data: List[VelocityDataPoint]) -> LearningPhase:
        """
        Detect the current learning phase based on velocity patterns.
        
        Args:
            velocity_data: Historical velocity data
            
        Returns:
            Current learning phase
        """
        try:
            phase = self.trend_analyzer.detect_learning_phase(velocity_data)
            self.logger.debug(f"Detected learning phase: {phase.value}")
            return phase
        except Exception as e:
            self.logger.error(f"Error detecting learning phase: {e}")
            return LearningPhase.INITIAL
    
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
        try:
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
            velocity_trend = self.trend_analyzer._calculate_trend(velocities)
            accuracy_trend = self.trend_analyzer._calculate_trend(accuracies)
            efficiency_trend = self.trend_analyzer._calculate_trend(efficiencies)
            
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
            
            prediction = VelocityPrediction(
                prediction_id=f"pred_{datetime.now().isoformat()}",
                created_at=datetime.now(),
                prediction_horizon=prediction_horizon,
                confidence_level=confidence,
                predicted_velocity=predicted_velocity,
                predicted_accuracy=predicted_accuracy,
                predicted_efficiency=predicted_efficiency,
                trend_factor=velocity_trend
            )
            
            self.logger.debug(f"Generated velocity prediction with {confidence:.2f} confidence")
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting future velocity: {e}")
            return self._get_default_prediction(prediction_horizon)
    
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
        try:
            insights = self.insight_generator.generate_velocity_insights(velocity_data)
            self.logger.info(f"Generated {len(insights)} velocity insights")
            return insights
        except Exception as e:
            self.logger.error(f"Error generating velocity insights: {e}")
            return []
    
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
        try:
            alerts = self.alert_detector.detect_velocity_alerts(velocity_data)
            self.logger.info(f"Detected {len(alerts)} velocity alerts")
            return alerts
        except Exception as e:
            self.logger.error(f"Error detecting velocity alerts: {e}")
            return []
    
    def analyze_velocity_patterns(self, velocity_data: List[VelocityDataPoint]) -> Dict[str, Any]:
        """
        Analyze various velocity patterns.
        
        Args:
            velocity_data: Historical velocity data
            
        Returns:
            Dictionary with pattern analysis results
        """
        try:
            patterns = self.trend_analyzer.analyze_velocity_patterns(velocity_data)
            self.logger.debug(f"Analyzed velocity patterns: {list(patterns.keys())}")
            return patterns
        except Exception as e:
            self.logger.error(f"Error analyzing velocity patterns: {e}")
            return {}
    
    def get_velocity_summary(self, velocity_data: List[VelocityDataPoint]) -> Dict[str, Any]:
        """
        Get a comprehensive summary of velocity analysis.
        
        Args:
            velocity_data: Historical velocity data
            
        Returns:
            Dictionary with velocity summary
        """
        try:
            if not velocity_data:
                return {"error": "No velocity data available"}
            
            # Basic statistics
            recent_data = velocity_data[-10:] if len(velocity_data) >= 10 else velocity_data
            
            avg_velocity = statistics.mean([d.cards_per_minute * 60 for d in recent_data])
            avg_accuracy = statistics.mean([d.accuracy_rate for d in recent_data])
            avg_efficiency = statistics.mean([d.learning_efficiency for d in recent_data])
            
            # Trends
            trends = self.analyze_velocity_trends(velocity_data, analysis_period=14)
            
            # Learning phase
            current_phase = self.detect_learning_phase(velocity_data)
            
            # Alerts
            alerts = self.detect_velocity_alerts(velocity_data)
            high_priority_alerts = [a for a in alerts if a.severity in ["high", "medium"]]
            
            # Insights
            insights = self.generate_velocity_insights(velocity_data)
            top_insights = sorted(insights, key=lambda i: i.potential_improvement, reverse=True)[:3]
            
            summary = {
                "current_metrics": {
                    "velocity": avg_velocity,
                    "accuracy": avg_accuracy,
                    "efficiency": avg_efficiency
                },
                "learning_phase": current_phase.value,
                "trend_count": len(trends),
                "alert_count": len(high_priority_alerts),
                "insight_count": len(top_insights),
                "top_insights": [
                    {
                        "title": insight.title,
                        "description": insight.description,
                        "potential_improvement": insight.potential_improvement
                    }
                    for insight in top_insights
                ],
                "recent_alerts": [
                    {
                        "type": alert.alert_type,
                        "severity": alert.severity,
                        "description": alert.description
                    }
                    for alert in high_priority_alerts[:3]
                ]
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating velocity summary: {e}")
            return {"error": "Unable to generate velocity summary"}
    
    def _get_default_prediction(self, prediction_horizon: int) -> VelocityPrediction:
        """Get default prediction when errors occur."""
        return VelocityPrediction(
            prediction_id=f"pred_default_{datetime.now().isoformat()}",
            created_at=datetime.now(),
            prediction_horizon=prediction_horizon,
            confidence_level=0.1,
            predicted_velocity=0.0,
            predicted_accuracy=0.0,
            predicted_efficiency=0.0
        )
    
    def update_analysis_settings(self, settings: Dict[str, Any]) -> None:
        """
        Update analysis settings.
        
        Args:
            settings: Dictionary with new settings
        """
        try:
            if "trend_threshold" in settings:
                self.trend_analyzer.trend_threshold = settings["trend_threshold"]
            
            if "alert_thresholds" in settings:
                self.alert_detector.alert_thresholds.update(settings["alert_thresholds"])
            
            self.logger.info("Updated velocity analysis settings")
            
        except Exception as e:
            self.logger.error(f"Error updating analysis settings: {e}")
    
    def export_analysis_data(self, velocity_data: List[VelocityDataPoint]) -> Dict[str, Any]:
        """
        Export comprehensive analysis data.
        
        Args:
            velocity_data: Historical velocity data
            
        Returns:
            Dictionary with all analysis data
        """
        try:
            return {
                "trends": [trend.__dict__ for trend in self.analyze_velocity_trends(velocity_data)],
                "insights": [insight.__dict__ for insight in self.generate_velocity_insights(velocity_data)],
                "alerts": [alert.__dict__ for alert in self.detect_velocity_alerts(velocity_data)],
                "patterns": self.analyze_velocity_patterns(velocity_data),
                "learning_phase": self.detect_learning_phase(velocity_data).value,
                "prediction": self.predict_future_velocity(velocity_data).__dict__,
                "summary": self.get_velocity_summary(velocity_data)
            }
        except Exception as e:
            self.logger.error(f"Error exporting analysis data: {e}")
            return {"error": "Unable to export analysis data"}
