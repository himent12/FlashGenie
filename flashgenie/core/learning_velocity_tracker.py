"""
Learning Velocity Tracker for FlashGenie.

This module provides the main LearningVelocityTracker class that serves as the
public interface for learning velocity tracking functionality.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .learning_velocity.models import (
    LearningSession, VelocityGoal, LearningVelocityProfile
)
from .learning_velocity.tracker import VelocityTracker
from .learning_velocity.analyzer import VelocityAnalyzer
from flashgenie.utils.exceptions import FlashGenieError


class LearningVelocityTracker:
    """
    Main interface for learning velocity tracking functionality.
    
    This class provides a simplified interface to the learning velocity
    system while maintaining backward compatibility.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the learning velocity tracker.
        
        Args:
            data_path: Optional path for storing velocity data
        """
        self.tracker = VelocityTracker(data_path)
        self.analyzer = VelocityAnalyzer()
        self.current_session: Optional[Dict[str, Any]] = None
    
    def start_session(self, user_id: str, deck_id: str = "", study_mode: str = "review") -> str:
        """
        Start a new learning session.
        
        Args:
            user_id: User identifier
            deck_id: Deck being studied
            study_mode: Type of study session
            
        Returns:
            Session ID
        """
        session_id = f"session_{user_id}_{datetime.now().isoformat()}"
        
        self.current_session = {
            "session_id": session_id,
            "user_id": user_id,
            "deck_id": deck_id,
            "study_mode": study_mode,
            "start_time": datetime.now(),
            "cards_studied": 0,
            "correct_answers": 0,
            "total_answers": 0,
            "difficulty_levels": []
        }
        
        return session_id
    
    def record_card_interaction(
        self, 
        session_id: str, 
        correct: bool, 
        difficulty: float = 0.5
    ) -> None:
        """
        Record a card interaction during a session.
        
        Args:
            session_id: Session identifier
            correct: Whether the answer was correct
            difficulty: Difficulty level of the card
        """
        if not self.current_session or self.current_session["session_id"] != session_id:
            raise FlashGenieError(f"No active session found: {session_id}")
        
        self.current_session["cards_studied"] += 1
        self.current_session["total_answers"] += 1
        
        if correct:
            self.current_session["correct_answers"] += 1
        
        self.current_session["difficulty_levels"].append(difficulty)
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End a learning session and record velocity data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session summary
        """
        if not self.current_session or self.current_session["session_id"] != session_id:
            raise FlashGenieError(f"No active session found: {session_id}")
        
        session_data = self.current_session
        end_time = datetime.now()
        
        # Calculate average difficulty
        avg_difficulty = 0.5
        if session_data["difficulty_levels"]:
            avg_difficulty = sum(session_data["difficulty_levels"]) / len(session_data["difficulty_levels"])
        
        # Create learning session object
        learning_session = LearningSession(
            session_id=session_data["session_id"],
            start_time=session_data["start_time"],
            end_time=end_time,
            cards_studied=session_data["cards_studied"],
            correct_answers=session_data["correct_answers"],
            total_answers=session_data["total_answers"],
            deck_id=session_data["deck_id"],
            study_mode=session_data["study_mode"],
            difficulty_level=avg_difficulty
        )
        
        # Record session with tracker
        velocity_data = self.tracker.record_session(session_data["user_id"], learning_session)
        
        # Clear current session
        self.current_session = None
        
        # Return session summary
        return {
            "session_id": session_id,
            "duration_minutes": learning_session.duration_minutes,
            "cards_studied": learning_session.cards_studied,
            "accuracy_rate": learning_session.accuracy_rate,
            "cards_per_minute": learning_session.cards_per_minute,
            "velocity_data_recorded": True
        }
    
    def get_velocity_metrics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get velocity metrics for a user.
        
        Args:
            user_id: User identifier
            days: Number of days to include in metrics
            
        Returns:
            Dictionary with velocity metrics
        """
        try:
            return self.tracker.get_velocity_summary(user_id, days)
        except Exception as e:
            raise FlashGenieError(f"Failed to get velocity metrics: {e}")
    
    def analyze_learning_trends(self, user_id: str, period_days: int = 30) -> List[Dict[str, Any]]:
        """
        Analyze learning trends for a user.
        
        Args:
            user_id: User identifier
            period_days: Period in days to analyze
            
        Returns:
            List of trend analyses
        """
        profile = self.tracker.get_velocity_profile(user_id)
        if not profile:
            return []
        
        try:
            # Filter data to analysis period
            cutoff_date = datetime.now() - timedelta(days=period_days)
            recent_data = [d for d in profile.velocity_history if d.timestamp >= cutoff_date]
            
            trends = self.analyzer.analyze_velocity_trends(recent_data, period_days)
            
            return [
                {
                    "metric": trend.metric_type.value,
                    "trend": trend.trend.value,
                    "current_value": trend.current_value,
                    "previous_value": trend.previous_value,
                    "change_percentage": trend.change_percentage,
                    "confidence": trend.confidence,
                    "description": trend.description,
                    "data_points": trend.data_points
                }
                for trend in trends
            ]
        except Exception as e:
            raise FlashGenieError(f"Failed to analyze learning trends: {e}")
    
    def predict_performance(self, user_id: str, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Predict future learning performance.
        
        Args:
            user_id: User identifier
            days_ahead: Days to predict ahead
            
        Returns:
            Dictionary with performance predictions
        """
        profile = self.tracker.get_velocity_profile(user_id)
        if not profile:
            return {"error": "No velocity data found for user"}
        
        try:
            prediction = self.analyzer.predict_future_velocity(profile.velocity_history, days_ahead)
            
            return {
                "prediction_horizon": prediction.prediction_horizon,
                "confidence_level": prediction.confidence_level,
                "predicted_velocity": prediction.predicted_velocity,
                "predicted_accuracy": prediction.predicted_accuracy,
                "predicted_efficiency": prediction.predicted_efficiency,
                "trend_factor": prediction.trend_factor
            }
        except Exception as e:
            raise FlashGenieError(f"Failed to predict performance: {e}")
    
    def create_velocity_goal(
        self, 
        user_id: str, 
        goal_name: str, 
        target_metric: str,
        target_value: float,
        target_days: int = 30
    ) -> Dict[str, Any]:
        """
        Create a velocity improvement goal.
        
        Args:
            user_id: User identifier
            goal_name: Name of the goal
            target_metric: Metric to improve (velocity, accuracy, efficiency)
            target_value: Target value to achieve
            target_days: Days to achieve the goal
            
        Returns:
            Dictionary with goal information
        """
        try:
            goal = self.tracker.create_velocity_goal(
                user_id, goal_name, target_metric, target_value, target_days
            )
            
            return {
                "goal_id": goal.goal_id,
                "name": goal.name,
                "description": goal.description,
                "metric_type": goal.metric_type,
                "target_value": goal.target_value,
                "current_value": goal.current_value,
                "progress_percentage": goal.progress_percentage,
                "target_date": goal.target_date.isoformat(),
                "is_achieved": goal.is_achieved
            }
        except Exception as e:
            raise FlashGenieError(f"Failed to create velocity goal: {e}")
    
    def get_learning_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get learning insights based on velocity analysis.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of learning insights
        """
        profile = self.tracker.get_velocity_profile(user_id)
        if not profile:
            return []
        
        try:
            insights = self.analyzer.generate_velocity_insights(profile.velocity_history)
            
            return [
                {
                    "type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "significance": insight.significance,
                    "confidence": insight.confidence,
                    "actionable": insight.actionable,
                    "recommended_actions": insight.recommended_actions,
                    "potential_improvement": insight.potential_improvement,
                    "implementation_effort": insight.implementation_effort
                }
                for insight in insights
            ]
        except Exception as e:
            raise FlashGenieError(f"Failed to get learning insights: {e}")
    
    def compare_to_benchmarks(self, user_id: str, benchmark: str = "general") -> Dict[str, Any]:
        """
        Compare user's performance to benchmarks.
        
        Args:
            user_id: User identifier
            benchmark: Benchmark to compare against
            
        Returns:
            Dictionary with benchmark comparison
        """
        try:
            return self.tracker.compare_to_benchmark(user_id, benchmark)
        except Exception as e:
            raise FlashGenieError(f"Failed to compare to benchmarks: {e}")
    
    def get_velocity_alerts(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get velocity alerts for significant changes.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of velocity alerts
        """
        profile = self.tracker.get_velocity_profile(user_id)
        if not profile:
            return []
        
        try:
            alerts = self.analyzer.detect_velocity_alerts(profile.velocity_history)
            
            return [
                {
                    "alert_id": alert.alert_id,
                    "timestamp": alert.timestamp.isoformat(),
                    "alert_type": alert.alert_type,
                    "metric_affected": alert.metric_affected.value,
                    "severity": alert.severity,
                    "description": alert.description,
                    "current_value": alert.current_value,
                    "previous_value": alert.previous_value,
                    "acknowledged": alert.acknowledged
                }
                for alert in alerts
            ]
        except Exception as e:
            raise FlashGenieError(f"Failed to get velocity alerts: {e}")
    
    def get_optimal_study_schedule(self, user_id: str) -> Dict[str, Any]:
        """
        Get optimal study schedule recommendations.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with schedule recommendations
        """
        profile = self.tracker.get_velocity_profile(user_id)
        if not profile:
            return {"error": "No velocity data found for user"}
        
        # Analyze time patterns from velocity data
        time_performance = {}
        for data_point in profile.velocity_history[-50:]:  # Last 50 sessions
            hour = data_point.timestamp.hour
            
            if 6 <= hour < 12:
                time_period = "morning"
            elif 12 <= hour < 18:
                time_period = "afternoon"
            elif 18 <= hour < 22:
                time_period = "evening"
            else:
                time_period = "night"
            
            if time_period not in time_performance:
                time_performance[time_period] = []
            time_performance[time_period].append(data_point.learning_efficiency)
        
        # Find optimal times
        optimal_times = []
        for period, efficiencies in time_performance.items():
            if len(efficiencies) >= 3:
                avg_efficiency = sum(efficiencies) / len(efficiencies)
                optimal_times.append({
                    "time_period": period,
                    "average_efficiency": avg_efficiency,
                    "session_count": len(efficiencies)
                })
        
        # Sort by efficiency
        optimal_times.sort(key=lambda x: x["average_efficiency"], reverse=True)
        
        return {
            "optimal_session_duration": profile.optimal_session_duration,
            "optimal_difficulty_range": profile.optimal_difficulty_range,
            "best_times": optimal_times[:3],  # Top 3 time periods
            "recommendations": [
                f"Schedule important sessions during {optimal_times[0]['time_period']}" if optimal_times else "Collect more data to determine optimal times",
                f"Aim for {profile.optimal_session_duration}-minute sessions",
                f"Target difficulty range: {profile.optimal_difficulty_range[0]:.1f}-{profile.optimal_difficulty_range[1]:.1f}"
            ]
        }
    
    def export_velocity_data(self, user_id: str, format_type: str = "json") -> Dict[str, Any]:
        """
        Export velocity data for a user.
        
        Args:
            user_id: User identifier
            format_type: Export format (json, csv)
            
        Returns:
            Dictionary with export data or file path
        """
        profile = self.tracker.get_velocity_profile(user_id)
        if not profile:
            return {"error": "No velocity data found for user"}
        
        if format_type == "json":
            return {
                "user_id": profile.user_id,
                "created_at": profile.created_at.isoformat(),
                "last_updated": profile.last_updated.isoformat(),
                "current_metrics": {
                    "velocity": profile.current_velocity,
                    "accuracy": profile.current_accuracy,
                    "efficiency": profile.current_efficiency
                },
                "learning_phase": profile.current_phase.value,
                "session_count": len(profile.velocity_history),
                "velocity_history": [
                    {
                        "timestamp": dp.timestamp.isoformat(),
                        "cards_studied": dp.cards_studied,
                        "accuracy_rate": dp.accuracy_rate,
                        "cards_per_minute": dp.cards_per_minute,
                        "learning_efficiency": dp.learning_efficiency,
                        "session_duration": dp.session_duration
                    }
                    for dp in profile.velocity_history
                ]
            }
        else:
            return {"error": f"Export format '{format_type}' not supported"}
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with user statistics
        """
        profile = self.tracker.get_velocity_profile(user_id)
        if not profile:
            return {"error": "No velocity data found for user"}
        
        # Calculate comprehensive statistics
        total_sessions = len(profile.velocity_history)
        total_cards = sum(dp.cards_studied for dp in profile.velocity_history)
        total_time = sum(dp.session_duration for dp in profile.velocity_history)
        
        # Recent performance (last 30 days)
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_sessions = [dp for dp in profile.velocity_history if dp.timestamp >= recent_cutoff]
        
        return {
            "user_id": user_id,
            "profile_age_days": (datetime.now() - profile.created_at).days,
            "total_statistics": {
                "total_sessions": total_sessions,
                "total_cards_studied": total_cards,
                "total_study_time_minutes": total_time,
                "average_session_length": total_time / total_sessions if total_sessions > 0 else 0
            },
            "current_metrics": {
                "velocity_cards_per_hour": profile.current_velocity,
                "accuracy_rate": profile.current_accuracy,
                "learning_efficiency": profile.current_efficiency,
                "learning_phase": profile.current_phase.value
            },
            "recent_performance": {
                "sessions_last_30_days": len(recent_sessions),
                "cards_last_30_days": sum(dp.cards_studied for dp in recent_sessions),
                "avg_accuracy_last_30_days": sum(dp.accuracy_rate for dp in recent_sessions) / len(recent_sessions) if recent_sessions else 0
            },
            "optimization_data": {
                "optimal_session_duration": profile.optimal_session_duration,
                "optimal_difficulty_range": profile.optimal_difficulty_range,
                "peak_performance_times": profile.peak_performance_times
            }
        }
