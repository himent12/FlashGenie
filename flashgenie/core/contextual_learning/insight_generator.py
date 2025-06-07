"""
Insight generation utilities for the contextual learning system.

This module provides functions to generate contextual insights and recommendations.
"""

from typing import Dict, List, Any
import statistics
from ..content_system.deck import Deck
from .models import ContextualInsight


class InsightGenerator:
    """Generates contextual insights and recommendations."""
    
    def __init__(self):
        """Initialize the insight generator."""
        pass
    
    def generate_performance_insights(self, performance_history: List[Dict[str, Any]]) -> List[ContextualInsight]:
        """
        Generate performance optimization insights.
        
        Args:
            performance_history: Historical performance data
            
        Returns:
            List of performance insights
        """
        insights = []
        
        if len(performance_history) < 5:
            return insights
        
        # Analyze overall performance trends
        recent_sessions = performance_history[-10:]  # Last 10 sessions
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
        
        # Analyze consistency
        accuracy_variance = statistics.variance([s.get("accuracy", 0) for s in recent_sessions])
        if accuracy_variance > 0.05:  # High variance
            insight = ContextualInsight(
                insight_type="consistency",
                title="Inconsistent Performance",
                description="Performance varies significantly between sessions",
                evidence=[f"Accuracy variance: {accuracy_variance:.3f}"],
                confidence=0.7,
                recommended_changes=[
                    "Standardize study environment",
                    "Maintain consistent energy levels",
                    "Use regular study schedule"
                ],
                potential_improvement=0.1
            )
            insights.append(insight)
        
        return insights
    
    def generate_time_insights(self, performance_history: List[Dict[str, Any]]) -> List[ContextualInsight]:
        """
        Generate time management insights.
        
        Args:
            performance_history: Historical performance data
            
        Returns:
            List of time-related insights
        """
        insights = []
        
        # Analyze time of day performance
        time_performance = {}
        for session in performance_history:
            time_of_day = session.get("time_of_day", "unknown")
            accuracy = session.get("accuracy", 0)
            
            if time_of_day not in time_performance:
                time_performance[time_of_day] = []
            time_performance[time_of_day].append(accuracy)
        
        # Find best and worst times
        avg_performance = {}
        for time_of_day, accuracies in time_performance.items():
            if len(accuracies) >= 3:
                avg_performance[time_of_day] = statistics.mean(accuracies)
        
        if len(avg_performance) >= 2:
            best_time = max(avg_performance, key=avg_performance.get)
            worst_time = min(avg_performance, key=avg_performance.get)
            
            if avg_performance[best_time] - avg_performance[worst_time] > 0.15:
                insight = ContextualInsight(
                    insight_type="timing",
                    title="Optimal Study Time Identified",
                    description=f"Performance is significantly better during {best_time}",
                    evidence=[
                        f"{best_time}: {avg_performance[best_time]:.1%} accuracy",
                        f"{worst_time}: {avg_performance[worst_time]:.1%} accuracy"
                    ],
                    confidence=0.8,
                    recommended_changes=[
                        f"Schedule important study sessions during {best_time}",
                        f"Use {worst_time} for light review only"
                    ],
                    potential_improvement=avg_performance[best_time] - avg_performance[worst_time]
                )
                insights.append(insight)
        
        # Analyze session duration
        durations = [s.get("duration", 30) for s in performance_history]
        accuracies = [s.get("accuracy", 0) for s in performance_history]
        
        if len(durations) >= 10:
            # Find correlation between duration and performance
            short_sessions = [(d, a) for d, a in zip(durations, accuracies) if d <= 30]
            long_sessions = [(d, a) for d, a in zip(durations, accuracies) if d > 45]
            
            if len(short_sessions) >= 3 and len(long_sessions) >= 3:
                short_avg = statistics.mean([a for _, a in short_sessions])
                long_avg = statistics.mean([a for _, a in long_sessions])
                
                if abs(short_avg - long_avg) > 0.1:
                    better_type = "shorter" if short_avg > long_avg else "longer"
                    insight = ContextualInsight(
                        insight_type="duration",
                        title=f"Optimal Session Length: {better_type.title()}",
                        description=f"Performance is better with {better_type} study sessions",
                        evidence=[
                            f"Short sessions (≤30 min): {short_avg:.1%} accuracy",
                            f"Long sessions (>45 min): {long_avg:.1%} accuracy"
                        ],
                        confidence=0.7,
                        recommended_changes=[
                            f"Prefer {better_type} study sessions",
                            "Adjust session planning accordingly"
                        ],
                        potential_improvement=abs(short_avg - long_avg)
                    )
                    insights.append(insight)
        
        return insights
    
    def generate_environment_insights(self, performance_history: List[Dict[str, Any]]) -> List[ContextualInsight]:
        """
        Generate environment optimization insights.
        
        Args:
            performance_history: Historical performance data
            
        Returns:
            List of environment-related insights
        """
        insights = []
        
        # Analyze environment performance
        env_performance = {}
        for session in performance_history:
            environment = session.get("environment", "unknown")
            accuracy = session.get("accuracy", 0)
            satisfaction = session.get("satisfaction", 3)
            
            if environment not in env_performance:
                env_performance[environment] = {"accuracies": [], "satisfactions": []}
            env_performance[environment]["accuracies"].append(accuracy)
            env_performance[environment]["satisfactions"].append(satisfaction)
        
        # Find optimal environment
        env_scores = {}
        for env, data in env_performance.items():
            if len(data["accuracies"]) >= 3:
                avg_accuracy = statistics.mean(data["accuracies"])
                avg_satisfaction = statistics.mean(data["satisfactions"])
                env_scores[env] = (avg_accuracy + avg_satisfaction / 5) / 2  # Combined score
        
        if len(env_scores) >= 2:
            best_env = max(env_scores, key=env_scores.get)
            worst_env = min(env_scores, key=env_scores.get)
            
            if env_scores[best_env] - env_scores[worst_env] > 0.1:
                insight = ContextualInsight(
                    insight_type="environment",
                    title="Optimal Study Environment Identified",
                    description=f"Performance is significantly better in {best_env} environment",
                    evidence=[
                        f"{best_env}: {env_scores[best_env]:.1%} combined score",
                        f"{worst_env}: {env_scores[worst_env]:.1%} combined score"
                    ],
                    confidence=0.8,
                    recommended_changes=[
                        f"Prioritize studying in {best_env} environment",
                        f"Avoid or minimize {worst_env} environment"
                    ],
                    potential_improvement=env_scores[best_env] - env_scores[worst_env]
                )
                insights.append(insight)
        
        return insights
    
    def generate_content_insights(self, deck: Deck, performance_history: List[Dict[str, Any]]) -> List[ContextualInsight]:
        """
        Generate content adaptation insights.
        
        Args:
            deck: The deck being studied
            performance_history: Historical performance data
            
        Returns:
            List of content-related insights
        """
        insights = []
        
        # Analyze difficulty preferences
        difficulty_performance = {}
        for session in performance_history:
            avg_difficulty = session.get("avg_difficulty", 0.5)
            accuracy = session.get("accuracy", 0)
            engagement = session.get("engagement", 3)
            
            # Group by difficulty ranges
            if avg_difficulty < 0.3:
                difficulty_range = "easy"
            elif avg_difficulty < 0.7:
                difficulty_range = "medium"
            else:
                difficulty_range = "hard"
            
            if difficulty_range not in difficulty_performance:
                difficulty_performance[difficulty_range] = {"accuracies": [], "engagements": []}
            difficulty_performance[difficulty_range]["accuracies"].append(accuracy)
            difficulty_performance[difficulty_range]["engagements"].append(engagement)
        
        # Find optimal difficulty
        for difficulty, data in difficulty_performance.items():
            if len(data["accuracies"]) >= 3:
                avg_accuracy = statistics.mean(data["accuracies"])
                avg_engagement = statistics.mean(data["engagements"])
                
                if avg_accuracy > 0.85 and avg_engagement > 4.0:
                    insight = ContextualInsight(
                        insight_type="content",
                        title=f"Optimal Difficulty: {difficulty.title()}",
                        description=f"High performance and engagement with {difficulty} content",
                        evidence=[
                            f"{difficulty} content: {avg_accuracy:.1%} accuracy",
                            f"Engagement rating: {avg_engagement:.1f}/5"
                        ],
                        confidence=0.7,
                        recommended_changes=[
                            f"Focus on {difficulty} difficulty content",
                            "Adjust content selection accordingly"
                        ],
                        potential_improvement=0.1
                    )
                    insights.append(insight)
        
        # Analyze deck-specific patterns
        if deck.size > 10:
            due_ratio = deck.due_count / deck.size
            if due_ratio > 0.8:
                insight = ContextualInsight(
                    insight_type="content",
                    title="High Review Load",
                    description="Most cards in this deck are due for review",
                    evidence=[f"{deck.due_count}/{deck.size} cards due ({due_ratio:.1%})"],
                    confidence=0.9,
                    recommended_changes=[
                        "Focus on review sessions",
                        "Consider breaking into smaller study chunks",
                        "Prioritize most difficult cards"
                    ],
                    potential_improvement=0.05
                )
                insights.append(insight)
        
        return insights
    
    def generate_all_insights(
        self, 
        deck: Deck, 
        performance_history: List[Dict[str, Any]]
    ) -> List[ContextualInsight]:
        """
        Generate all types of contextual insights.
        
        Args:
            deck: The deck being studied
            performance_history: Historical performance data
            
        Returns:
            List of all contextual insights
        """
        all_insights = []
        
        # Generate different types of insights
        all_insights.extend(self.generate_performance_insights(performance_history))
        all_insights.extend(self.generate_time_insights(performance_history))
        all_insights.extend(self.generate_environment_insights(performance_history))
        all_insights.extend(self.generate_content_insights(deck, performance_history))
        
        # Sort by potential improvement and confidence
        all_insights.sort(
            key=lambda i: i.potential_improvement * i.confidence, 
            reverse=True
        )
        
        return all_insights
