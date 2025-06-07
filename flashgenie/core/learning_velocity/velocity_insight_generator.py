"""
Velocity insight generation utilities for the learning velocity tracking system.

This module provides functions to generate velocity insights and recommendations.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import statistics

from .models import VelocityDataPoint, VelocityInsight


class VelocityInsightGenerator:
    """Generates velocity insights and recommendations."""
    
    def __init__(self):
        """Initialize the insight generator."""
        pass
    
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
        
        # Learning efficiency insight
        efficiency_insight = self._analyze_learning_efficiency(velocity_data)
        if efficiency_insight:
            insights.append(efficiency_insight)
        
        # Break pattern insight
        break_insight = self._analyze_break_patterns(velocity_data)
        if break_insight:
            insights.append(break_insight)
        
        return insights
    
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
        elif cv < 0.15:  # Very consistent
            return VelocityInsight(
                insight_id=f"consistency_good_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                insight_type="consistency",
                title="Excellent Performance Consistency",
                description=f"Your learning velocity is very consistent (CV: {cv:.2f})",
                significance="low",
                confidence=0.9,
                recommended_actions=[
                    "Maintain your current study routine",
                    "Consider gradually increasing difficulty"
                ],
                potential_improvement=0.05
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
        worst_group = min(group_efficiencies, key=group_efficiencies.get)
        
        # Only generate insight if there's a significant difference
        if group_efficiencies[best_group] - group_efficiencies[worst_group] < 0.1:
            return None
        
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
        
        # Group by time of day
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
                combined_score = (avg_velocity / 60) * avg_accuracy  # Normalize and combine
                time_performance[period] = combined_score
        
        if len(time_performance) < 2:
            return None
        
        # Find best and worst times
        best_time = max(time_performance, key=time_performance.get)
        worst_time = min(time_performance, key=time_performance.get)
        
        # Only generate insight if there's a significant difference
        if time_performance[best_time] - time_performance[worst_time] < 0.2:
            return None
        
        return VelocityInsight(
            insight_id=f"time_pattern_{datetime.now().isoformat()}",
            timestamp=datetime.now(),
            insight_type="timing",
            title=f"Peak Performance Time: {best_time.title()}",
            description=f"You perform significantly better during {best_time} sessions",
            significance="high",
            confidence=0.8,
            recommended_actions=[
                f"Schedule important study sessions during {best_time}",
                f"Use {worst_time} for light review or easier content",
                "Track energy levels throughout the day"
            ],
            potential_improvement=0.25
        )
    
    def _analyze_difficulty_progression(
        self, 
        velocity_data: List[VelocityDataPoint]
    ) -> Optional[VelocityInsight]:
        """Analyze difficulty progression patterns."""
        if len(velocity_data) < 15:
            return None
        
        # Analyze progression over time
        recent_data = velocity_data[-10:]
        older_data = velocity_data[-20:-10] if len(velocity_data) >= 20 else velocity_data[:-10]
        
        if not older_data:
            return None
        
        # Calculate average difficulty and accuracy for each period
        recent_difficulty = statistics.mean([d.metadata.get("avg_difficulty", 0.5) for d in recent_data])
        older_difficulty = statistics.mean([d.metadata.get("avg_difficulty", 0.5) for d in older_data])
        
        recent_accuracy = statistics.mean([d.accuracy_rate for d in recent_data])
        older_accuracy = statistics.mean([d.accuracy_rate for d in older_data])
        
        difficulty_increase = recent_difficulty - older_difficulty
        accuracy_change = recent_accuracy - older_accuracy
        
        # Generate insights based on progression patterns
        if difficulty_increase > 0.1 and accuracy_change > -0.05:
            return VelocityInsight(
                insight_id=f"difficulty_progression_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                insight_type="progression",
                title="Successful Difficulty Progression",
                description="You're successfully handling increased difficulty while maintaining accuracy",
                significance="high",
                confidence=0.8,
                recommended_actions=[
                    "Continue gradual difficulty increases",
                    "Monitor accuracy to ensure sustainable progression",
                    "Celebrate your learning progress"
                ],
                potential_improvement=0.1
            )
        elif difficulty_increase < -0.1:
            return VelocityInsight(
                insight_id=f"difficulty_regression_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                insight_type="regression",
                title="Difficulty Level Decreased",
                description="Recent sessions have been easier than previous ones",
                significance="medium",
                confidence=0.7,
                recommended_actions=[
                    "Consider gradually increasing difficulty",
                    "Review mastered concepts to maintain retention",
                    "Challenge yourself with harder content"
                ],
                potential_improvement=0.15
            )
        
        return None
    
    def _analyze_learning_efficiency(
        self, 
        velocity_data: List[VelocityDataPoint]
    ) -> Optional[VelocityInsight]:
        """Analyze learning efficiency trends."""
        if len(velocity_data) < 10:
            return None
        
        recent_efficiency = statistics.mean([d.learning_efficiency for d in velocity_data[-5:]])
        overall_efficiency = statistics.mean([d.learning_efficiency for d in velocity_data])
        
        efficiency_change = (recent_efficiency - overall_efficiency) / overall_efficiency
        
        if efficiency_change > 0.2:  # 20% improvement
            return VelocityInsight(
                insight_id=f"efficiency_improvement_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                insight_type="improvement",
                title="Learning Efficiency Improving",
                description=f"Your learning efficiency has improved by {efficiency_change:.1%}",
                significance="high",
                confidence=0.8,
                recommended_actions=[
                    "Maintain current study strategies",
                    "Document what's working well",
                    "Consider sharing techniques with others"
                ],
                potential_improvement=0.1
            )
        elif efficiency_change < -0.2:  # 20% decline
            return VelocityInsight(
                insight_id=f"efficiency_decline_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                insight_type="decline",
                title="Learning Efficiency Declining",
                description=f"Your learning efficiency has declined by {abs(efficiency_change):.1%}",
                significance="high",
                confidence=0.8,
                recommended_actions=[
                    "Review recent changes in study habits",
                    "Consider taking a break to recharge",
                    "Evaluate study environment and methods"
                ],
                potential_improvement=0.2
            )
        
        return None
    
    def _analyze_break_patterns(
        self, 
        velocity_data: List[VelocityDataPoint]
    ) -> Optional[VelocityInsight]:
        """Analyze break frequency and effectiveness."""
        if len(velocity_data) < 15:
            return None
        
        # Analyze sessions with and without breaks
        sessions_with_breaks = [d for d in velocity_data if d.metadata.get("break_count", 0) > 0]
        sessions_without_breaks = [d for d in velocity_data if d.metadata.get("break_count", 0) == 0]
        
        if len(sessions_with_breaks) < 3 or len(sessions_without_breaks) < 3:
            return None
        
        # Compare efficiency
        efficiency_with_breaks = statistics.mean([d.learning_efficiency for d in sessions_with_breaks])
        efficiency_without_breaks = statistics.mean([d.learning_efficiency for d in sessions_without_breaks])
        
        efficiency_difference = efficiency_with_breaks - efficiency_without_breaks
        
        if efficiency_difference > 0.1:  # Breaks help significantly
            return VelocityInsight(
                insight_id=f"break_benefit_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                insight_type="optimization",
                title="Breaks Improve Learning Efficiency",
                description=f"Sessions with breaks are {efficiency_difference:.1%} more efficient",
                significance="medium",
                confidence=0.7,
                recommended_actions=[
                    "Take regular breaks during study sessions",
                    "Use techniques like Pomodoro (25 min work, 5 min break)",
                    "Monitor break timing and duration"
                ],
                potential_improvement=0.15
            )
        elif efficiency_difference < -0.1:  # Breaks seem to hurt
            return VelocityInsight(
                insight_id=f"break_hindrance_{datetime.now().isoformat()}",
                timestamp=datetime.now(),
                insight_type="optimization",
                title="Fewer Breaks May Improve Focus",
                description=f"Continuous sessions are {abs(efficiency_difference):.1%} more efficient for you",
                significance="medium",
                confidence=0.7,
                recommended_actions=[
                    "Try longer focused sessions without breaks",
                    "Ensure you're well-rested before studying",
                    "Monitor fatigue levels during extended sessions"
                ],
                potential_improvement=0.1
            )
        
        return None
