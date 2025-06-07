"""
Context scoring utilities for the contextual learning system.

This module provides functions to score and evaluate study contexts.
"""

from typing import Dict, Any, List
import statistics
from .models import (
    StudyContext, EnergyLevel, AttentionLevel, StudyEnvironment
)


class ContextScorer:
    """Scores and evaluates study contexts."""
    
    def __init__(self):
        """Initialize the context scorer."""
        pass
    
    def calculate_context_score(self, context: StudyContext) -> float:
        """
        Calculate an overall context quality score.
        
        Args:
            context: Study context to score
            
        Returns:
            Context quality score (0.0 to 1.0)
        """
        score = 0.0
        
        # Energy level contribution (30%)
        energy_score = context.energy_level.value / 5.0
        score += energy_score * 0.3
        
        # Attention level contribution (25%)
        attention_score = context.attention_level.value / 4.0
        score += attention_score * 0.25
        
        # Environment contribution (20%)
        env_scores = {
            StudyEnvironment.QUIET: 1.0,
            StudyEnvironment.FOCUSED: 0.9,
            StudyEnvironment.NOISY: 0.6,
            StudyEnvironment.MOBILE: 0.5,
            StudyEnvironment.DISTRACTED: 0.3
        }
        score += env_scores.get(context.environment, 0.5) * 0.2
        
        # Stress level contribution (15%) - inverse relationship
        stress_score = (6 - context.stress_level) / 5.0
        score += stress_score * 0.15
        
        # Time availability contribution (10%)
        time_score = min(context.time_available / 60, 1.0)  # Normalize to 60 minutes
        score += time_score * 0.1
        
        return min(score, 1.0)
    
    def estimate_optimal_duration(self, context: StudyContext) -> int:
        """
        Estimate optimal study duration based on context.
        
        Args:
            context: Study context
            
        Returns:
            Optimal duration in minutes
        """
        base_duration = context.time_available
        
        # Adjust based on energy level
        energy_multipliers = {
            EnergyLevel.VERY_LOW: 0.5,
            EnergyLevel.LOW: 0.7,
            EnergyLevel.MEDIUM: 1.0,
            EnergyLevel.HIGH: 1.2,
            EnergyLevel.VERY_HIGH: 1.3
        }
        
        duration = base_duration * energy_multipliers.get(context.energy_level, 1.0)
        
        # Adjust based on attention level
        attention_multipliers = {
            AttentionLevel.POOR: 0.6,
            AttentionLevel.FAIR: 0.8,
            AttentionLevel.GOOD: 1.0,
            AttentionLevel.EXCELLENT: 1.1
        }
        
        duration *= attention_multipliers.get(context.attention_level, 1.0)
        
        # Adjust based on environment
        env_multipliers = {
            StudyEnvironment.QUIET: 1.0,
            StudyEnvironment.FOCUSED: 1.1,
            StudyEnvironment.NOISY: 0.8,
            StudyEnvironment.MOBILE: 0.7,
            StudyEnvironment.DISTRACTED: 0.6
        }
        
        duration *= env_multipliers.get(context.environment, 1.0)
        
        # Cap the duration
        return min(int(duration), context.time_available)
    
    def recommend_difficulty(self, context: StudyContext) -> float:
        """
        Recommend difficulty level based on context.
        
        Args:
            context: Study context
            
        Returns:
            Recommended difficulty level (0.0 to 1.0)
        """
        base_difficulty = context.preferred_difficulty
        
        # Adjust based on energy level
        if context.energy_level in [EnergyLevel.VERY_LOW, EnergyLevel.LOW]:
            base_difficulty *= 0.8  # Easier content when tired
        elif context.energy_level in [EnergyLevel.HIGH, EnergyLevel.VERY_HIGH]:
            base_difficulty *= 1.2  # Harder content when energetic
        
        # Adjust based on attention level
        if context.attention_level == AttentionLevel.POOR:
            base_difficulty *= 0.7
        elif context.attention_level == AttentionLevel.EXCELLENT:
            base_difficulty *= 1.1
        
        # Adjust based on stress level
        if context.stress_level >= 4:
            base_difficulty *= 0.8  # Easier when stressed
        
        return max(0.1, min(1.0, base_difficulty))
    
    def predict_attention_span(self, context: StudyContext) -> Dict[str, Any]:
        """
        Predict attention span based on context.
        
        Args:
            context: Study context
            
        Returns:
            Dictionary with attention span predictions
        """
        base_span = 25  # minutes (Pomodoro technique)
        
        # Adjust based on energy and attention
        energy_factor = context.energy_level.value / 3.0
        attention_factor = context.attention_level.value / 2.0
        
        predicted_span = base_span * energy_factor * attention_factor
        
        # Adjust based on environment
        if context.environment in [StudyEnvironment.NOISY, StudyEnvironment.DISTRACTED]:
            predicted_span *= 0.7
        elif context.environment == StudyEnvironment.FOCUSED:
            predicted_span *= 1.2
        
        return {
            "predicted_span": int(predicted_span),
            "recommended_breaks": max(1, context.time_available // int(predicted_span)),
            "break_duration": 5 if predicted_span < 30 else 10
        }
    
    def assess_energy_impact(self, context: StudyContext) -> Dict[str, Any]:
        """
        Assess the impact of energy level on study session.
        
        Args:
            context: Study context
            
        Returns:
            Dictionary with energy impact assessment
        """
        energy_level = context.energy_level
        
        assessments = {
            EnergyLevel.VERY_LOW: {
                "impact": "high_negative",
                "recommendations": ["Take a break", "Do light review only", "Consider postponing"],
                "optimal_activities": ["review", "easy_practice"]
            },
            EnergyLevel.LOW: {
                "impact": "moderate_negative",
                "recommendations": ["Focus on review", "Avoid new material", "Take frequent breaks"],
                "optimal_activities": ["review", "light_practice"]
            },
            EnergyLevel.MEDIUM: {
                "impact": "neutral",
                "recommendations": ["Balanced study session", "Mix of review and learning"],
                "optimal_activities": ["review", "learning", "practice"]
            },
            EnergyLevel.HIGH: {
                "impact": "positive",
                "recommendations": ["Tackle challenging material", "Learn new concepts"],
                "optimal_activities": ["learning", "challenging_practice", "problem_solving"]
            },
            EnergyLevel.VERY_HIGH: {
                "impact": "high_positive",
                "recommendations": ["Intensive learning session", "Tackle difficult concepts"],
                "optimal_activities": ["intensive_learning", "difficult_practice", "creative_work"]
            }
        }
        
        return assessments.get(energy_level, assessments[EnergyLevel.MEDIUM])
    
    def analyze_environment(self, context: StudyContext) -> Dict[str, Any]:
        """
        Analyze environmental factors.
        
        Args:
            context: Study context
            
        Returns:
            Dictionary with environment analysis
        """
        environment = context.environment
        
        analysis = {
            StudyEnvironment.QUIET: {
                "suitability": "excellent",
                "recommended_activities": ["deep_learning", "complex_practice", "memorization"],
                "adjustments": []
            },
            StudyEnvironment.FOCUSED: {
                "suitability": "excellent",
                "recommended_activities": ["intensive_study", "problem_solving", "analysis"],
                "adjustments": ["maintain_focus_techniques"]
            },
            StudyEnvironment.NOISY: {
                "suitability": "poor",
                "recommended_activities": ["review", "simple_practice"],
                "adjustments": ["use_headphones", "find_quieter_location", "shorter_sessions"]
            },
            StudyEnvironment.MOBILE: {
                "suitability": "fair",
                "recommended_activities": ["review", "quick_practice", "flashcard_drill"],
                "adjustments": ["shorter_sessions", "simpler_content", "frequent_breaks"]
            },
            StudyEnvironment.DISTRACTED: {
                "suitability": "poor",
                "recommended_activities": ["light_review", "easy_practice"],
                "adjustments": ["eliminate_distractions", "postpone_session", "meditation"]
            }
        }
        
        return analysis.get(environment, analysis[StudyEnvironment.QUIET])
    
    def find_similar_contexts(
        self, 
        context: StudyContext, 
        performance_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find historically similar contexts.
        
        Args:
            context: Current study context
            performance_history: Historical performance data
            
        Returns:
            List of similar historical contexts
        """
        similar_contexts = []
        
        for session in performance_history:
            similarity_score = 0.0
            
            # Time of day similarity
            if session.get("time_of_day") == context.time_of_day:
                similarity_score += 0.2
            
            # Energy level similarity
            energy_diff = abs(session.get("energy_level", 3) - context.energy_level.value)
            similarity_score += (1 - energy_diff / 4) * 0.3
            
            # Environment similarity
            if session.get("environment") == context.environment.value:
                similarity_score += 0.3
            
            # Attention level similarity
            attention_diff = abs(session.get("attention_level", 3) - context.attention_level.value)
            similarity_score += (1 - attention_diff / 3) * 0.2
            
            if similarity_score > 0.6:  # Threshold for similarity
                similar_contexts.append(session)
        
        return similar_contexts
    
    def generate_context_recommendations(
        self, 
        context: StudyContext, 
        similar_contexts: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate recommendations based on similar contexts.
        
        Args:
            context: Current study context
            similar_contexts: List of similar historical contexts
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if not similar_contexts:
            return ["No similar historical contexts found"]
        
        # Analyze what worked well in similar contexts
        successful_sessions = [s for s in similar_contexts if s.get("accuracy", 0) > 0.8]
        
        if successful_sessions:
            avg_duration = statistics.mean([s.get("duration", 30) for s in successful_sessions])
            recommendations.append(f"Aim for {int(avg_duration)} minute sessions based on past success")
            
            common_activities = {}
            for session in successful_sessions:
                activities = session.get("activities", [])
                for activity in activities:
                    common_activities[activity] = common_activities.get(activity, 0) + 1
            
            if common_activities:
                best_activity = max(common_activities, key=common_activities.get)
                recommendations.append(f"Focus on {best_activity} - it worked well in similar contexts")
        
        return recommendations
