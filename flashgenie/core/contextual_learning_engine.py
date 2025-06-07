"""
Contextual Learning Engine for FlashGenie.

This module provides the main ContextualLearningEngine class that serves as the
public interface for contextual learning functionality.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .content_system.deck import Deck
from .contextual_learning.models import (
    StudyContext, StudyPlan, ContextualRecommendation, ContextualInsight,
    EnergyLevel, AttentionLevel, StudyEnvironment, StudyMode
)
from .contextual_learning.analyzer import ContextAnalyzer
from .contextual_learning.planner import StudyPlanner
from flashgenie.utils.exceptions import FlashGenieError


class ContextualLearningEngine:
    """
    Main interface for contextual learning functionality.
    
    This class provides a simplified interface to the contextual learning
    system while maintaining backward compatibility.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the contextual learning engine.
        
        Args:
            data_path: Optional path for storing learning data
        """
        self.analyzer = ContextAnalyzer()
        self.planner = StudyPlanner()
        self.performance_history: List[Dict[str, Any]] = []
        self.current_context: Optional[StudyContext] = None
        self.current_plan: Optional[StudyPlan] = None
    
    def create_study_context(
        self,
        time_available: int,
        energy_level: int = 3,
        attention_level: int = 3,
        environment: str = "quiet",
        **kwargs
    ) -> StudyContext:
        """
        Create a study context for the current session.
        
        Args:
            time_available: Available study time in minutes
            energy_level: Energy level (1-5 scale)
            attention_level: Attention level (1-4 scale)
            environment: Study environment type
            **kwargs: Additional context parameters
            
        Returns:
            Study context object
        """
        try:
            # Convert numeric values to enums
            energy_enum = EnergyLevel(energy_level)
            attention_enum = AttentionLevel(attention_level)
            environment_enum = StudyEnvironment(environment)
            
            context = StudyContext(
                time_available=time_available,
                energy_level=energy_enum,
                attention_level=attention_enum,
                environment=environment_enum,
                time_of_day=kwargs.get("time_of_day", self._get_current_time_of_day()),
                stress_level=kwargs.get("stress_level", 3),
                device_type=kwargs.get("device_type", "desktop"),
                study_mode=StudyMode(kwargs.get("study_mode", "review")),
                target_accuracy=kwargs.get("target_accuracy", 0.8),
                preferred_difficulty=kwargs.get("preferred_difficulty", 0.5),
                focus_areas=set(kwargs.get("focus_areas", []))
            )
            
            self.current_context = context
            return context
            
        except ValueError as e:
            raise FlashGenieError(f"Invalid context parameters: {e}")
    
    def analyze_context(self, context: StudyContext) -> Dict[str, Any]:
        """
        Analyze the study context and provide insights.
        
        Args:
            context: Study context to analyze
            
        Returns:
            Dictionary with context analysis results
        """
        try:
            return self.analyzer.analyze_current_context(context)
        except Exception as e:
            raise FlashGenieError(f"Context analysis failed: {e}")
    
    def create_adaptive_plan(self, deck: Deck, context: StudyContext) -> StudyPlan:
        """
        Create an adaptive study plan based on context.
        
        Args:
            deck: The deck to study
            context: Current study context
            
        Returns:
            Adaptive study plan
        """
        try:
            plan = self.planner.create_study_plan(deck, context)
            self.current_plan = plan
            return plan
        except Exception as e:
            raise FlashGenieError(f"Failed to create study plan: {e}")
    
    def get_contextual_recommendations(
        self, 
        context: StudyContext, 
        deck: Deck
    ) -> List[ContextualRecommendation]:
        """
        Get contextual recommendations for study optimization.
        
        Args:
            context: Study context
            deck: Deck to study
            
        Returns:
            List of contextual recommendations
        """
        try:
            return self.planner.generate_recommendations(context, deck)
        except Exception as e:
            raise FlashGenieError(f"Failed to generate recommendations: {e}")
    
    def adapt_plan_realtime(self, performance_data: Dict[str, Any]) -> Optional[StudyPlan]:
        """
        Adapt the current study plan based on real-time performance.
        
        Args:
            performance_data: Real-time performance metrics
            
        Returns:
            Adapted study plan or None if no current plan
        """
        if not self.current_plan:
            return None
        
        try:
            adapted_plan = self.planner.adapt_plan_realtime(self.current_plan, performance_data)
            self.current_plan = adapted_plan
            return adapted_plan
        except Exception as e:
            raise FlashGenieError(f"Failed to adapt plan: {e}")
    
    def record_session_performance(self, session_data: Dict[str, Any]) -> None:
        """
        Record performance data from a completed study session.
        
        Args:
            session_data: Session performance data
        """
        # Add timestamp if not present
        if "timestamp" not in session_data:
            session_data["timestamp"] = datetime.now().isoformat()
        
        # Add context information if available
        if self.current_context:
            session_data.update({
                "energy_level": self.current_context.energy_level.value,
                "attention_level": self.current_context.attention_level.value,
                "environment": self.current_context.environment.value,
                "time_of_day": self.current_context.time_of_day,
                "stress_level": self.current_context.stress_level
            })
        
        self.performance_history.append(session_data)
    
    def analyze_learning_patterns(self) -> List[Dict[str, Any]]:
        """
        Analyze learning patterns from historical data.
        
        Returns:
            List of identified learning patterns
        """
        try:
            patterns = self.analyzer.identify_performance_patterns(self.performance_history)
            
            # Convert to dictionaries for easier consumption
            return [
                {
                    "pattern_id": pattern.pattern_id,
                    "name": pattern.name,
                    "description": pattern.description,
                    "context_factors": pattern.context_factors,
                    "performance_metrics": pattern.performance_metrics,
                    "confidence": pattern.confidence_level,
                    "occurrence_count": pattern.occurrence_count
                }
                for pattern in patterns
            ]
        except Exception as e:
            raise FlashGenieError(f"Failed to analyze learning patterns: {e}")
    
    def generate_insights(self, deck: Deck) -> List[Dict[str, Any]]:
        """
        Generate contextual insights for learning optimization.
        
        Args:
            deck: The deck being studied
            
        Returns:
            List of contextual insights
        """
        try:
            insights = self.analyzer.generate_contextual_insights(deck)
            
            # Convert to dictionaries
            return [
                {
                    "type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "evidence": insight.evidence,
                    "confidence": insight.confidence,
                    "actionable": insight.actionable,
                    "recommended_changes": insight.recommended_changes,
                    "potential_improvement": insight.potential_improvement,
                    "implementation_difficulty": insight.implementation_difficulty
                }
                for insight in insights
            ]
        except Exception as e:
            raise FlashGenieError(f"Failed to generate insights: {e}")
    
    def predict_session_outcome(self, context: StudyContext, deck: Deck) -> Dict[str, Any]:
        """
        Predict the outcome of a study session.
        
        Args:
            context: Study context
            deck: Deck to be studied
            
        Returns:
            Dictionary with outcome predictions
        """
        try:
            return self.analyzer.predict_session_outcome(context, deck)
        except Exception as e:
            raise FlashGenieError(f"Failed to predict session outcome: {e}")
    
    def get_optimal_study_times(self) -> List[Dict[str, Any]]:
        """
        Get optimal study times based on historical performance.
        
        Returns:
            List of optimal study time recommendations
        """
        if not self.performance_history:
            return []
        
        # Group performance by time of day
        time_performance = {}
        for session in self.performance_history:
            time_of_day = session.get("time_of_day", "unknown")
            accuracy = session.get("accuracy", 0)
            
            if time_of_day not in time_performance:
                time_performance[time_of_day] = []
            time_performance[time_of_day].append(accuracy)
        
        # Calculate averages and recommendations
        recommendations = []
        for time_of_day, accuracies in time_performance.items():
            if len(accuracies) >= 3:  # Need sufficient data
                avg_accuracy = sum(accuracies) / len(accuracies)
                
                recommendations.append({
                    "time_of_day": time_of_day,
                    "average_accuracy": avg_accuracy,
                    "session_count": len(accuracies),
                    "recommendation": "optimal" if avg_accuracy > 0.8 else "good" if avg_accuracy > 0.7 else "fair"
                })
        
        # Sort by performance
        recommendations.sort(key=lambda x: x["average_accuracy"], reverse=True)
        return recommendations
    
    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current context and recommendations.
        
        Returns:
            Dictionary with context summary
        """
        if not self.current_context:
            return {"error": "No current context available"}
        
        context = self.current_context
        
        # Analyze current context
        analysis = self.analyzer.analyze_current_context(context)
        
        return {
            "context": {
                "time_available": context.time_available,
                "energy_level": context.energy_level.name.lower(),
                "attention_level": context.attention_level.name.lower(),
                "environment": context.environment.value,
                "time_of_day": context.time_of_day,
                "stress_level": context.stress_level
            },
            "analysis": {
                "context_score": analysis.get("context_score", 0),
                "optimal_duration": analysis.get("optimal_duration", context.time_available),
                "recommended_difficulty": analysis.get("recommended_difficulty", 0.5),
                "attention_prediction": analysis.get("attention_prediction", {})
            },
            "current_plan": {
                "plan_id": self.current_plan.plan_id if self.current_plan else None,
                "total_duration": self.current_plan.total_duration if self.current_plan else 0,
                "phase_count": len(self.current_plan.session_phases) if self.current_plan else 0,
                "predicted_accuracy": self.current_plan.predicted_accuracy if self.current_plan else 0
            } if self.current_plan else None
        }
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """
        Get performance statistics from historical data.
        
        Returns:
            Dictionary with performance statistics
        """
        if not self.performance_history:
            return {"total_sessions": 0}
        
        # Calculate basic statistics
        total_sessions = len(self.performance_history)
        accuracies = [s.get("accuracy", 0) for s in self.performance_history]
        completion_rates = [s.get("completion_rate", 0) for s in self.performance_history]
        satisfactions = [s.get("satisfaction", 0) for s in self.performance_history if s.get("satisfaction")]
        
        stats = {
            "total_sessions": total_sessions,
            "average_accuracy": sum(accuracies) / len(accuracies) if accuracies else 0,
            "average_completion_rate": sum(completion_rates) / len(completion_rates) if completion_rates else 0,
            "average_satisfaction": sum(satisfactions) / len(satisfactions) if satisfactions else 0
        }
        
        # Recent performance (last 10 sessions)
        recent_sessions = self.performance_history[-10:]
        recent_accuracies = [s.get("accuracy", 0) for s in recent_sessions]
        
        stats["recent_performance"] = {
            "session_count": len(recent_sessions),
            "average_accuracy": sum(recent_accuracies) / len(recent_accuracies) if recent_accuracies else 0,
            "trend": self._calculate_trend(recent_accuracies)
        }
        
        return stats
    
    def _get_current_time_of_day(self) -> str:
        """Get the current time of day category."""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from a list of values."""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        diff = second_avg - first_avg
        
        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "declining"
        else:
            return "stable"
