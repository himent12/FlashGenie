"""
Velocity tracking utilities for the learning velocity system.

This module provides functions to track and manage learning velocity data.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from pathlib import Path

from .models import (
    VelocityDataPoint, LearningVelocityProfile, VelocityGoal, 
    VelocityBenchmark, LearningSession, LearningPhase
)
from .analyzer import VelocityAnalyzer


class VelocityTracker:
    """Tracks and manages learning velocity data."""
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the velocity tracker.
        
        Args:
            data_path: Optional path for storing velocity data
        """
        self.data_path = Path(data_path or "data/velocity")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        self.analyzer = VelocityAnalyzer()
        self.velocity_profiles: Dict[str, LearningVelocityProfile] = {}
        self.benchmarks: Dict[str, VelocityBenchmark] = {}
    
    def record_session(self, user_id: str, session: LearningSession) -> VelocityDataPoint:
        """
        Record a learning session and update velocity data.
        
        Args:
            user_id: User identifier
            session: Learning session data
            
        Returns:
            Created velocity data point
        """
        # Create velocity data point from session
        data_point = VelocityDataPoint(
            timestamp=session.end_time,
            session_id=session.session_id,
            cards_studied=session.cards_studied,
            correct_answers=session.correct_answers,
            total_answers=session.total_answers,
            session_duration=session.duration_minutes,
            difficulty_level=session.difficulty_level
        )
        
        # Get or create user profile
        if user_id not in self.velocity_profiles:
            self.velocity_profiles[user_id] = self._create_new_profile(user_id)
        
        profile = self.velocity_profiles[user_id]
        
        # Add data point to profile
        profile.velocity_history.append(data_point)
        
        # Update current metrics
        self._update_current_metrics(profile)
        
        # Update learning phase
        profile.current_phase = self.analyzer.detect_learning_phase(profile.velocity_history)
        
        # Save profile
        self._save_profile(profile)
        
        return data_point
    
    def get_velocity_profile(self, user_id: str) -> Optional[LearningVelocityProfile]:
        """
        Get velocity profile for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User's velocity profile or None if not found
        """
        if user_id in self.velocity_profiles:
            return self.velocity_profiles[user_id]
        
        # Try to load from disk
        profile = self._load_profile(user_id)
        if profile:
            self.velocity_profiles[user_id] = profile
        
        return profile
    
    def create_velocity_goal(
        self, 
        user_id: str, 
        goal_name: str, 
        metric_type: str,
        target_value: float,
        target_days: int = 30
    ) -> VelocityGoal:
        """
        Create a velocity goal for a user.
        
        Args:
            user_id: User identifier
            goal_name: Name of the goal
            metric_type: Type of metric to track
            target_value: Target value to achieve
            target_days: Days to achieve the goal
            
        Returns:
            Created velocity goal
        """
        profile = self.get_velocity_profile(user_id)
        if not profile:
            profile = self._create_new_profile(user_id)
            self.velocity_profiles[user_id] = profile
        
        # Get current value based on metric type
        current_value = self._get_current_metric_value(profile, metric_type)
        
        goal = VelocityGoal(
            goal_id=f"goal_{user_id}_{datetime.now().isoformat()}",
            name=goal_name,
            description=f"Achieve {target_value} {metric_type} within {target_days} days",
            metric_type=metric_type,
            target_value=target_value,
            current_value=current_value,
            created_at=datetime.now(),
            target_date=datetime.now() + timedelta(days=target_days)
        )
        
        goal.update_progress()
        return goal
    
    def update_goal_progress(self, user_id: str, goal: VelocityGoal) -> VelocityGoal:
        """
        Update progress for a velocity goal.
        
        Args:
            user_id: User identifier
            goal: Velocity goal to update
            
        Returns:
            Updated velocity goal
        """
        profile = self.get_velocity_profile(user_id)
        if profile:
            goal.current_value = self._get_current_metric_value(profile, goal.metric_type)
            goal.update_progress()
        
        return goal
    
    def get_velocity_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get velocity summary for a user.
        
        Args:
            user_id: User identifier
            days: Number of days to include in summary
            
        Returns:
            Dictionary with velocity summary
        """
        profile = self.get_velocity_profile(user_id)
        if not profile:
            return {"error": "No velocity data found for user"}
        
        # Filter recent data
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_data = [d for d in profile.velocity_history if d.timestamp >= cutoff_date]
        
        if not recent_data:
            return {"error": "No recent velocity data found"}
        
        # Calculate summary metrics
        total_sessions = len(recent_data)
        total_cards = sum(d.cards_studied for d in recent_data)
        total_time = sum(d.session_duration for d in recent_data)
        
        avg_velocity = profile.current_velocity
        avg_accuracy = profile.current_accuracy
        avg_efficiency = profile.current_efficiency
        
        # Analyze trends
        trends = self.analyzer.analyze_velocity_trends(recent_data, days)
        
        # Generate insights
        insights = self.analyzer.generate_velocity_insights(recent_data)
        
        return {
            "period_days": days,
            "total_sessions": total_sessions,
            "total_cards_studied": total_cards,
            "total_study_time": total_time,
            "current_metrics": {
                "velocity": avg_velocity,
                "accuracy": avg_accuracy,
                "efficiency": avg_efficiency
            },
            "learning_phase": profile.current_phase.value,
            "trends": [
                {
                    "metric": trend.metric_type.value,
                    "trend": trend.trend.value,
                    "change_percentage": trend.change_percentage,
                    "confidence": trend.confidence
                }
                for trend in trends
            ],
            "insights": [
                {
                    "type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "significance": insight.significance,
                    "actions": insight.recommended_actions
                }
                for insight in insights[:3]  # Top 3 insights
            ]
        }
    
    def compare_to_benchmark(self, user_id: str, benchmark_name: str = "general") -> Dict[str, Any]:
        """
        Compare user's velocity to benchmarks.
        
        Args:
            user_id: User identifier
            benchmark_name: Name of benchmark to compare against
            
        Returns:
            Dictionary with comparison results
        """
        profile = self.get_velocity_profile(user_id)
        if not profile:
            return {"error": "No velocity data found for user"}
        
        benchmark = self._get_benchmark(benchmark_name)
        if not benchmark:
            return {"error": f"Benchmark '{benchmark_name}' not found"}
        
        # Calculate user percentiles
        user_velocity_percentile = self._calculate_percentile(
            profile.current_velocity, 
            benchmark.velocity_percentiles
        )
        
        user_accuracy_percentile = self._calculate_percentile(
            profile.current_accuracy,
            benchmark.accuracy_percentiles
        )
        
        user_efficiency_percentile = self._calculate_percentile(
            profile.current_efficiency,
            benchmark.efficiency_percentiles
        )
        
        # Determine relative performance
        avg_percentile = (user_velocity_percentile + user_accuracy_percentile + user_efficiency_percentile) / 3
        
        if avg_percentile >= 90:
            relative_performance = "excellent"
        elif avg_percentile >= 75:
            relative_performance = "above_average"
        elif avg_percentile >= 25:
            relative_performance = "average"
        else:
            relative_performance = "below_average"
        
        return {
            "benchmark_name": benchmark_name,
            "user_percentiles": {
                "velocity": user_velocity_percentile,
                "accuracy": user_accuracy_percentile,
                "efficiency": user_efficiency_percentile
            },
            "relative_performance": relative_performance,
            "recommendations": self._generate_benchmark_recommendations(
                relative_performance, 
                user_velocity_percentile,
                user_accuracy_percentile,
                user_efficiency_percentile
            )
        }
    
    def _create_new_profile(self, user_id: str) -> LearningVelocityProfile:
        """Create a new velocity profile for a user."""
        return LearningVelocityProfile(
            user_id=user_id,
            created_at=datetime.now(),
            last_updated=datetime.now(),
            current_velocity=0.0,
            current_accuracy=0.0,
            current_efficiency=0.0
        )
    
    def _update_current_metrics(self, profile: LearningVelocityProfile) -> None:
        """Update current metrics in a velocity profile."""
        if not profile.velocity_history:
            return
        
        # Use recent data for current metrics
        recent_data = profile.velocity_history[-10:]  # Last 10 sessions
        
        if recent_data:
            # Calculate averages
            velocities = [d.cards_per_minute * 60 for d in recent_data]  # Convert to cards per hour
            accuracies = [d.accuracy_rate for d in recent_data]
            efficiencies = [d.learning_efficiency * 60 for d in recent_data]  # Convert to per hour
            
            profile.current_velocity = sum(velocities) / len(velocities)
            profile.current_accuracy = sum(accuracies) / len(accuracies)
            profile.current_efficiency = sum(efficiencies) / len(efficiencies)
            
            profile.last_updated = datetime.now()
    
    def _get_current_metric_value(self, profile: LearningVelocityProfile, metric_type: str) -> float:
        """Get current value for a specific metric type."""
        if metric_type == "velocity" or metric_type == "cards_per_hour":
            return profile.current_velocity
        elif metric_type == "accuracy":
            return profile.current_accuracy
        elif metric_type == "efficiency":
            return profile.current_efficiency
        else:
            return 0.0
    
    def _save_profile(self, profile: LearningVelocityProfile) -> None:
        """Save velocity profile to disk."""
        try:
            profile_file = self.data_path / f"profile_{profile.user_id}.json"
            
            # Convert to dictionary for JSON serialization
            profile_data = {
                "user_id": profile.user_id,
                "created_at": profile.created_at.isoformat(),
                "last_updated": profile.last_updated.isoformat(),
                "current_velocity": profile.current_velocity,
                "current_accuracy": profile.current_accuracy,
                "current_efficiency": profile.current_efficiency,
                "current_phase": profile.current_phase.value,
                "optimal_session_duration": profile.optimal_session_duration,
                "velocity_history": [
                    {
                        "timestamp": dp.timestamp.isoformat(),
                        "session_id": dp.session_id,
                        "cards_studied": dp.cards_studied,
                        "correct_answers": dp.correct_answers,
                        "total_answers": dp.total_answers,
                        "session_duration": dp.session_duration,
                        "cards_per_minute": dp.cards_per_minute,
                        "accuracy_rate": dp.accuracy_rate,
                        "learning_efficiency": dp.learning_efficiency,
                        "difficulty_level": dp.difficulty_level
                    }
                    for dp in profile.velocity_history[-100:]  # Keep last 100 sessions
                ]
            }
            
            with open(profile_file, 'w') as f:
                json.dump(profile_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving velocity profile: {e}")
    
    def _load_profile(self, user_id: str) -> Optional[LearningVelocityProfile]:
        """Load velocity profile from disk."""
        try:
            profile_file = self.data_path / f"profile_{user_id}.json"
            
            if not profile_file.exists():
                return None
            
            with open(profile_file, 'r') as f:
                profile_data = json.load(f)
            
            # Reconstruct velocity data points
            velocity_history = []
            for dp_data in profile_data.get("velocity_history", []):
                data_point = VelocityDataPoint(
                    timestamp=datetime.fromisoformat(dp_data["timestamp"]),
                    session_id=dp_data["session_id"],
                    cards_studied=dp_data["cards_studied"],
                    correct_answers=dp_data["correct_answers"],
                    total_answers=dp_data["total_answers"],
                    session_duration=dp_data["session_duration"],
                    cards_per_minute=dp_data["cards_per_minute"],
                    accuracy_rate=dp_data["accuracy_rate"],
                    learning_efficiency=dp_data["learning_efficiency"],
                    difficulty_level=dp_data["difficulty_level"]
                )
                velocity_history.append(data_point)
            
            # Reconstruct profile
            profile = LearningVelocityProfile(
                user_id=profile_data["user_id"],
                created_at=datetime.fromisoformat(profile_data["created_at"]),
                last_updated=datetime.fromisoformat(profile_data["last_updated"]),
                current_velocity=profile_data["current_velocity"],
                current_accuracy=profile_data["current_accuracy"],
                current_efficiency=profile_data["current_efficiency"],
                velocity_history=velocity_history,
                current_phase=LearningPhase(profile_data.get("current_phase", "initial")),
                optimal_session_duration=profile_data.get("optimal_session_duration", 25)
            )
            
            return profile
            
        except Exception as e:
            print(f"Error loading velocity profile: {e}")
            return None
    
    def _get_benchmark(self, benchmark_name: str) -> Optional[VelocityBenchmark]:
        """Get benchmark data."""
        if benchmark_name in self.benchmarks:
            return self.benchmarks[benchmark_name]
        
        # Create default benchmark if not found
        if benchmark_name == "general":
            benchmark = VelocityBenchmark(
                benchmark_id="general",
                name="General Learning Benchmark",
                description="General benchmark for learning velocity",
                velocity_percentiles={
                    10: 5.0, 25: 10.0, 50: 20.0, 75: 35.0, 90: 50.0
                },
                accuracy_percentiles={
                    10: 0.5, 25: 0.65, 50: 0.75, 75: 0.85, 90: 0.95
                },
                efficiency_percentiles={
                    10: 3.0, 25: 6.0, 50: 12.0, 75: 20.0, 90: 30.0
                },
                sample_size=1000,
                data_collection_period="6 months"
            )
            self.benchmarks[benchmark_name] = benchmark
            return benchmark
        
        return None
    
    def _calculate_percentile(self, value: float, percentiles: Dict[int, float]) -> int:
        """Calculate which percentile a value falls into."""
        for percentile in sorted(percentiles.keys()):
            if value <= percentiles[percentile]:
                return percentile
        return 100  # Above 90th percentile
    
    def _generate_benchmark_recommendations(
        self, 
        performance: str,
        velocity_percentile: int,
        accuracy_percentile: int,
        efficiency_percentile: int
    ) -> List[str]:
        """Generate recommendations based on benchmark comparison."""
        recommendations = []
        
        if performance == "below_average":
            recommendations.append("Focus on building consistent study habits")
            
            if velocity_percentile < 25:
                recommendations.append("Work on increasing study pace gradually")
            
            if accuracy_percentile < 25:
                recommendations.append("Prioritize accuracy over speed")
                recommendations.append("Review fundamental concepts")
        
        elif performance == "average":
            recommendations.append("You're performing at average levels")
            
            if velocity_percentile < accuracy_percentile:
                recommendations.append("Consider increasing study pace")
            else:
                recommendations.append("Focus on improving accuracy")
        
        elif performance == "above_average":
            recommendations.append("Great performance! Consider challenging yourself")
            recommendations.append("Try more difficult material")
        
        else:  # excellent
            recommendations.append("Outstanding performance!")
            recommendations.append("Consider mentoring others or exploring advanced topics")
        
        return recommendations
