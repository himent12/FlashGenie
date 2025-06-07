"""
Context analysis utilities for the contextual learning system.

This module provides functions to analyze study context and patterns.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import statistics

from ..content_system.deck import Deck
from .models import (
    StudyContext, PerformancePattern, ContextualInsight, 
    EnergyLevel, AttentionLevel, StudyEnvironment
)


class ContextAnalyzer:
    """Analyzes study context and identifies patterns."""
    
    def __init__(self):
        """Initialize the context analyzer."""
        self.performance_history: List[Dict[str, Any]] = []
        self.context_patterns: List[PerformancePattern] = []
    
    def analyze_current_context(self, context: StudyContext) -> Dict[str, Any]:
        """
        Analyze the current study context.
        
        Args:
            context: Current study context
            
        Returns:
            Dictionary with context analysis results
        """
        analysis = {
            "context_score": self._calculate_context_score(context),
            "optimal_duration": self._estimate_optimal_duration(context),
            "recommended_difficulty": self._recommend_difficulty(context),
            "attention_prediction": self._predict_attention_span(context),
            "energy_assessment": self._assess_energy_impact(context),
            "environment_factors": self._analyze_environment(context)
        }
        
        return analysis
    
    def identify_performance_patterns(
        self, 
        performance_history: List[Dict[str, Any]]
    ) -> List[PerformancePattern]:
        """
        Identify patterns in performance based on context.
        
        Args:
            performance_history: Historical performance data
            
        Returns:
            List of identified performance patterns
        """
        self.performance_history = performance_history
        patterns = []
        
        # Analyze time-based patterns
        time_patterns = self._analyze_time_patterns()
        patterns.extend(time_patterns)
        
        # Analyze energy-based patterns
        energy_patterns = self._analyze_energy_patterns()
        patterns.extend(energy_patterns)
        
        # Analyze environment-based patterns
        environment_patterns = self._analyze_environment_patterns()
        patterns.extend(environment_patterns)
        
        # Analyze difficulty preference patterns
        difficulty_patterns = self._analyze_difficulty_patterns()
        patterns.extend(difficulty_patterns)
        
        self.context_patterns = patterns
        return patterns
    
    def generate_contextual_insights(self, deck: Deck) -> List[ContextualInsight]:
        """
        Generate insights based on contextual analysis.
        
        Args:
            deck: The deck being studied
            
        Returns:
            List of contextual insights
        """
        insights = []
        
        # Performance optimization insights
        perf_insights = self._generate_performance_insights()
        insights.extend(perf_insights)
        
        # Time management insights
        time_insights = self._generate_time_insights()
        insights.extend(time_insights)
        
        # Environment optimization insights
        env_insights = self._generate_environment_insights()
        insights.extend(env_insights)
        
        # Content adaptation insights
        content_insights = self._generate_content_insights(deck)
        insights.extend(content_insights)
        
        return insights
    
    def predict_session_outcome(self, context: StudyContext, deck: Deck) -> Dict[str, Any]:
        """
        Predict the outcome of a study session based on context.
        
        Args:
            context: Study context
            deck: Deck to be studied
            
        Returns:
            Dictionary with outcome predictions
        """
        # Find similar historical contexts
        similar_contexts = self._find_similar_contexts(context)
        
        if not similar_contexts:
            # Use default predictions
            return {
                "predicted_accuracy": 0.75,
                "predicted_completion_rate": 0.8,
                "predicted_satisfaction": 3.5,
                "confidence": 0.3,
                "recommendations": ["No historical data available for this context"]
            }
        
        # Calculate predictions based on similar contexts
        accuracies = [ctx.get("accuracy", 0.75) for ctx in similar_contexts]
        completion_rates = [ctx.get("completion_rate", 0.8) for ctx in similar_contexts]
        satisfactions = [ctx.get("satisfaction", 3.5) for ctx in similar_contexts]
        
        return {
            "predicted_accuracy": statistics.mean(accuracies),
            "predicted_completion_rate": statistics.mean(completion_rates),
            "predicted_satisfaction": statistics.mean(satisfactions),
            "confidence": min(len(similar_contexts) / 10, 1.0),
            "recommendations": self._generate_context_recommendations(context, similar_contexts)
        }
    
    def _calculate_context_score(self, context: StudyContext) -> float:
        """Calculate an overall context quality score."""
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
    
    def _estimate_optimal_duration(self, context: StudyContext) -> int:
        """Estimate optimal study duration based on context."""
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
    
    def _recommend_difficulty(self, context: StudyContext) -> float:
        """Recommend difficulty level based on context."""
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
    
    def _predict_attention_span(self, context: StudyContext) -> Dict[str, Any]:
        """Predict attention span based on context."""
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
    
    def _assess_energy_impact(self, context: StudyContext) -> Dict[str, Any]:
        """Assess the impact of energy level on study session."""
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
    
    def _analyze_environment(self, context: StudyContext) -> Dict[str, Any]:
        """Analyze environmental factors."""
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
    
    def _analyze_time_patterns(self) -> List[PerformancePattern]:
        """Analyze time-based performance patterns."""
        patterns = []
        
        # Group by time of day
        time_groups = {}
        for session in self.performance_history:
            time_of_day = session.get("time_of_day", "unknown")
            if time_of_day not in time_groups:
                time_groups[time_of_day] = []
            time_groups[time_of_day].append(session)
        
        # Analyze each time group
        for time_of_day, sessions in time_groups.items():
            if len(sessions) >= 3:  # Need minimum data
                avg_accuracy = statistics.mean([s.get("accuracy", 0) for s in sessions])
                avg_completion = statistics.mean([s.get("completion_rate", 0) for s in sessions])
                
                if avg_accuracy > 0.8:  # High performance pattern
                    pattern = PerformancePattern(
                        pattern_id=f"time_{time_of_day}",
                        name=f"High Performance - {time_of_day.title()}",
                        description=f"Consistently high performance during {time_of_day}",
                        context_factors={"time_of_day": time_of_day},
                        performance_metrics={"accuracy": avg_accuracy, "completion_rate": avg_completion},
                        occurrence_count=len(sessions),
                        confidence_level=min(len(sessions) / 10, 1.0)
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _analyze_energy_patterns(self) -> List[PerformancePattern]:
        """Analyze energy-based performance patterns."""
        patterns = []
        
        # Group by energy level
        energy_groups = {}
        for session in self.performance_history:
            energy = session.get("energy_level", 3)
            if energy not in energy_groups:
                energy_groups[energy] = []
            energy_groups[energy].append(session)
        
        # Find optimal energy levels
        for energy_level, sessions in energy_groups.items():
            if len(sessions) >= 3:
                avg_accuracy = statistics.mean([s.get("accuracy", 0) for s in sessions])
                
                if avg_accuracy > 0.85:
                    pattern = PerformancePattern(
                        pattern_id=f"energy_{energy_level}",
                        name=f"Optimal Energy Level {energy_level}",
                        description=f"High performance at energy level {energy_level}",
                        context_factors={"energy_level": energy_level},
                        performance_metrics={"accuracy": avg_accuracy},
                        occurrence_count=len(sessions),
                        confidence_level=min(len(sessions) / 10, 1.0)
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _analyze_environment_patterns(self) -> List[PerformancePattern]:
        """Analyze environment-based performance patterns."""
        patterns = []
        
        # Group by environment
        env_groups = {}
        for session in self.performance_history:
            environment = session.get("environment", "unknown")
            if environment not in env_groups:
                env_groups[environment] = []
            env_groups[environment].append(session)
        
        # Find optimal environments
        for environment, sessions in env_groups.items():
            if len(sessions) >= 3:
                avg_accuracy = statistics.mean([s.get("accuracy", 0) for s in sessions])
                avg_satisfaction = statistics.mean([s.get("satisfaction", 3) for s in sessions])
                
                if avg_accuracy > 0.8 and avg_satisfaction > 3.5:
                    pattern = PerformancePattern(
                        pattern_id=f"env_{environment}",
                        name=f"Optimal Environment - {environment.title()}",
                        description=f"High performance in {environment} environment",
                        context_factors={"environment": environment},
                        performance_metrics={"accuracy": avg_accuracy, "satisfaction": avg_satisfaction},
                        occurrence_count=len(sessions),
                        confidence_level=min(len(sessions) / 10, 1.0)
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _analyze_difficulty_patterns(self) -> List[PerformancePattern]:
        """Analyze difficulty preference patterns."""
        patterns = []
        
        # Group by difficulty ranges
        difficulty_ranges = [(0.0, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 1.0)]
        
        for min_diff, max_diff in difficulty_ranges:
            relevant_sessions = [
                s for s in self.performance_history
                if min_diff <= s.get("avg_difficulty", 0.5) < max_diff
            ]
            
            if len(relevant_sessions) >= 3:
                avg_accuracy = statistics.mean([s.get("accuracy", 0) for s in relevant_sessions])
                avg_engagement = statistics.mean([s.get("engagement", 3) for s in relevant_sessions])
                
                if avg_accuracy > 0.8 and avg_engagement > 3.5:
                    pattern = PerformancePattern(
                        pattern_id=f"difficulty_{min_diff}_{max_diff}",
                        name=f"Optimal Difficulty Range {min_diff}-{max_diff}",
                        description=f"High performance with difficulty {min_diff}-{max_diff}",
                        context_factors={"difficulty_range": (min_diff, max_diff)},
                        performance_metrics={"accuracy": avg_accuracy, "engagement": avg_engagement},
                        occurrence_count=len(relevant_sessions),
                        confidence_level=min(len(relevant_sessions) / 10, 1.0)
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _find_similar_contexts(self, context: StudyContext) -> List[Dict[str, Any]]:
        """Find historically similar contexts."""
        similar_contexts = []
        
        for session in self.performance_history:
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
    
    def _generate_context_recommendations(
        self, 
        context: StudyContext, 
        similar_contexts: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on similar contexts."""
        recommendations = []
        
        if not similar_contexts:
            return ["No similar historical contexts found"]
        
        # Analyze what worked well in similar contexts
        successful_sessions = [s for s in similar_contexts if s.get("accuracy", 0) > 0.8]
        
        if successful_sessions:
            # Find common factors in successful sessions
            common_durations = [s.get("duration", 30) for s in successful_sessions]
            avg_duration = statistics.mean(common_durations)
            
            recommendations.append(f"Aim for {int(avg_duration)} minute sessions based on past success")
            
            # Check for common difficulty preferences
            common_difficulties = [s.get("avg_difficulty", 0.5) for s in successful_sessions]
            avg_difficulty = statistics.mean(common_difficulties)
            
            recommendations.append(f"Target difficulty around {avg_difficulty:.1f} for optimal performance")
        
        return recommendations
    
    def _generate_performance_insights(self) -> List[ContextualInsight]:
        """Generate performance optimization insights."""
        insights = []
        
        if len(self.performance_history) < 5:
            return insights
        
        # Analyze overall performance trends
        recent_sessions = self.performance_history[-10:]  # Last 10 sessions
        recent_accuracy = statistics.mean([s.get("accuracy", 0) for s in recent_sessions])
        
        if recent_accuracy < 0.7:
            insight = ContextualInsight(
                insight_type="performance",
                title="Performance Below Target",
                description=f"Recent accuracy ({recent_accuracy:.1%}) is below optimal levels",
                evidence=[f"Last 10 sessions averaged {recent_accuracy:.1%} accuracy"],
                confidence=0.8,
                recommended_changes=[
                    "Review study context factors",
                    "Consider adjusting difficulty level",
                    "Evaluate energy and attention patterns"
                ],
                potential_improvement=0.15
            )
            insights.append(insight)
        
        return insights
    
    def _generate_time_insights(self) -> List[ContextualInsight]:
        """Generate time management insights."""
        insights = []
        
        # Analyze session duration patterns
        if self.performance_history:
            durations = [s.get("duration", 30) for s in self.performance_history]
            completion_rates = [s.get("completion_rate", 1.0) for s in self.performance_history]
            
            # Find correlation between duration and completion
            if len(durations) >= 5:
                avg_duration = statistics.mean(durations)
                avg_completion = statistics.mean(completion_rates)
                
                if avg_completion < 0.8:
                    insight = ContextualInsight(
                        insight_type="time_management",
                        title="Session Completion Issues",
                        description=f"Average completion rate ({avg_completion:.1%}) suggests sessions may be too long",
                        evidence=[f"Average session: {avg_duration:.0f} minutes with {avg_completion:.1%} completion"],
                        confidence=0.7,
                        recommended_changes=[
                            "Reduce session duration",
                            "Add more breaks",
                            "Split complex topics into smaller chunks"
                        ],
                        potential_improvement=0.2
                    )
                    insights.append(insight)
        
        return insights
    
    def _generate_environment_insights(self) -> List[ContextualInsight]:
        """Generate environment optimization insights."""
        insights = []
        
        # Analyze environment impact
        env_performance = {}
        for session in self.performance_history:
            env = session.get("environment", "unknown")
            if env not in env_performance:
                env_performance[env] = []
            env_performance[env].append(session.get("accuracy", 0))
        
        # Find best and worst environments
        if len(env_performance) > 1:
            env_averages = {env: statistics.mean(accs) for env, accs in env_performance.items() if len(accs) >= 3}
            
            if env_averages:
                best_env = max(env_averages, key=env_averages.get)
                worst_env = min(env_averages, key=env_averages.get)
                
                if env_averages[best_env] - env_averages[worst_env] > 0.15:
                    insight = ContextualInsight(
                        insight_type="environment",
                        title="Environment Impact Detected",
                        description=f"Performance varies significantly by environment",
                        evidence=[
                            f"Best: {best_env} ({env_averages[best_env]:.1%})",
                            f"Worst: {worst_env} ({env_averages[worst_env]:.1%})"
                        ],
                        confidence=0.8,
                        recommended_changes=[
                            f"Prefer {best_env} environment when possible",
                            f"Avoid or modify {worst_env} environment",
                            "Consider environmental factors in planning"
                        ],
                        potential_improvement=env_averages[best_env] - env_averages[worst_env]
                    )
                    insights.append(insight)
        
        return insights
    
    def _generate_content_insights(self, deck: Deck) -> List[ContextualInsight]:
        """Generate content adaptation insights."""
        insights = []
        
        # Analyze difficulty distribution vs performance
        if self.performance_history:
            difficulty_performance = {}
            for session in self.performance_history:
                difficulty = session.get("avg_difficulty", 0.5)
                accuracy = session.get("accuracy", 0)
                
                # Group by difficulty ranges
                diff_range = int(difficulty * 10) / 10  # Round to nearest 0.1
                if diff_range not in difficulty_performance:
                    difficulty_performance[diff_range] = []
                difficulty_performance[diff_range].append(accuracy)
            
            # Find optimal difficulty range
            if len(difficulty_performance) > 1:
                range_averages = {
                    diff: statistics.mean(accs) 
                    for diff, accs in difficulty_performance.items() 
                    if len(accs) >= 2
                }
                
                if range_averages:
                    optimal_difficulty = max(range_averages, key=range_averages.get)
                    
                    insight = ContextualInsight(
                        insight_type="content",
                        title="Optimal Difficulty Range Identified",
                        description=f"Best performance at difficulty level {optimal_difficulty}",
                        evidence=[f"Difficulty {optimal_difficulty}: {range_averages[optimal_difficulty]:.1%} accuracy"],
                        confidence=0.7,
                        recommended_changes=[
                            f"Focus on cards with difficulty around {optimal_difficulty}",
                            "Gradually increase difficulty as mastery improves",
                            "Review cards outside optimal range more frequently"
                        ],
                        potential_improvement=0.1
                    )
                    insights.append(insight)
        
        return insights
