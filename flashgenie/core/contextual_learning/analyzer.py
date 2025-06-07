"""
Context analysis utilities for the contextual learning system.

This module provides functions to analyze study context and patterns.
Refactored for better maintainability and smaller file size.
"""

from typing import Dict, List, Optional, Any
import statistics
import logging

from ..content_system.deck import Deck
from .models import (
    StudyContext, PerformancePattern, ContextualInsight
)
from .context_scorer import ContextScorer
from .pattern_analyzer import PatternAnalyzer
from .insight_generator import InsightGenerator


class ContextAnalyzer:
    """Analyzes study context and identifies patterns."""
    
    def __init__(self):
        """Initialize the context analyzer."""
        self.performance_history: List[Dict[str, Any]] = []
        self.context_patterns: List[PerformancePattern] = []
        
        # Initialize component analyzers
        self.context_scorer = ContextScorer()
        self.pattern_analyzer = PatternAnalyzer()
        self.insight_generator = InsightGenerator()
        
        self.logger = logging.getLogger(__name__)
    
    def analyze_current_context(self, context: StudyContext) -> Dict[str, Any]:
        """
        Analyze the current study context.
        
        Args:
            context: Current study context
            
        Returns:
            Dictionary with context analysis results
        """
        try:
            analysis = {
                "context_score": self.context_scorer.calculate_context_score(context),
                "optimal_duration": self.context_scorer.estimate_optimal_duration(context),
                "recommended_difficulty": self.context_scorer.recommend_difficulty(context),
                "attention_prediction": self.context_scorer.predict_attention_span(context),
                "energy_assessment": self.context_scorer.assess_energy_impact(context),
                "environment_factors": self.context_scorer.analyze_environment(context)
            }
            
            self.logger.debug(f"Context analysis completed with score: {analysis['context_score']:.2f}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing context: {e}")
            return self._get_default_analysis()
    
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
        try:
            self.performance_history = performance_history
            
            if len(performance_history) < 3:
                self.logger.warning("Insufficient data for pattern analysis")
                return []
            
            # Use pattern analyzer to identify all patterns
            patterns = self.pattern_analyzer.identify_all_patterns(performance_history)
            
            self.context_patterns = patterns
            self.logger.info(f"Identified {len(patterns)} performance patterns")
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error identifying patterns: {e}")
            return []
    
    def generate_contextual_insights(self, deck: Deck) -> List[ContextualInsight]:
        """
        Generate insights based on contextual analysis.
        
        Args:
            deck: The deck being studied
            
        Returns:
            List of contextual insights
        """
        try:
            if len(self.performance_history) < 3:
                self.logger.warning("Insufficient data for insight generation")
                return []
            
            # Use insight generator to create all insights
            insights = self.insight_generator.generate_all_insights(deck, self.performance_history)
            
            self.logger.info(f"Generated {len(insights)} contextual insights")
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {e}")
            return []
    
    def predict_session_outcome(self, context: StudyContext, deck: Deck) -> Dict[str, Any]:
        """
        Predict the outcome of a study session based on context.
        
        Args:
            context: Study context
            deck: Deck to be studied
            
        Returns:
            Dictionary with outcome predictions
        """
        try:
            # Find similar historical contexts
            similar_contexts = self.context_scorer.find_similar_contexts(
                context, self.performance_history
            )
            
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
            
            # Generate recommendations
            recommendations = self.context_scorer.generate_context_recommendations(
                context, similar_contexts
            )
            
            prediction = {
                "predicted_accuracy": statistics.mean(accuracies),
                "predicted_completion_rate": statistics.mean(completion_rates),
                "predicted_satisfaction": statistics.mean(satisfactions),
                "confidence": min(len(similar_contexts) / 10, 1.0),
                "recommendations": recommendations,
                "similar_sessions_count": len(similar_contexts)
            }
            
            self.logger.debug(f"Session outcome predicted with {prediction['confidence']:.2f} confidence")
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting session outcome: {e}")
            return self._get_default_prediction()
    
    def update_performance_history(self, session_data: Dict[str, Any]) -> None:
        """
        Update performance history with new session data.
        
        Args:
            session_data: Data from completed study session
        """
        try:
            # Validate session data
            required_fields = ["accuracy", "duration", "timestamp"]
            if not all(field in session_data for field in required_fields):
                self.logger.warning("Session data missing required fields")
                return
            
            self.performance_history.append(session_data)
            
            # Keep only recent history to manage memory
            max_history_size = 1000
            if len(self.performance_history) > max_history_size:
                self.performance_history = self.performance_history[-max_history_size:]
            
            self.logger.debug("Performance history updated")
            
        except Exception as e:
            self.logger.error(f"Error updating performance history: {e}")
    
    def get_context_summary(self, context: StudyContext) -> Dict[str, Any]:
        """
        Get a summary of context analysis.
        
        Args:
            context: Study context
            
        Returns:
            Dictionary with context summary
        """
        try:
            analysis = self.analyze_current_context(context)
            
            summary = {
                "overall_score": analysis["context_score"],
                "readiness_level": self._categorize_readiness(analysis["context_score"]),
                "key_recommendations": self._extract_key_recommendations(analysis),
                "optimal_session_length": analysis["optimal_duration"],
                "attention_span": analysis["attention_prediction"]["predicted_span"],
                "energy_impact": analysis["energy_assessment"]["impact"]
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating context summary: {e}")
            return {"error": "Unable to generate context summary"}
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Get default analysis when errors occur."""
        return {
            "context_score": 0.5,
            "optimal_duration": 30,
            "recommended_difficulty": 0.5,
            "attention_prediction": {"predicted_span": 25, "recommended_breaks": 1, "break_duration": 5},
            "energy_assessment": {"impact": "neutral", "recommendations": [], "optimal_activities": []},
            "environment_factors": {"suitability": "fair", "recommended_activities": [], "adjustments": []}
        }
    
    def _get_default_prediction(self) -> Dict[str, Any]:
        """Get default prediction when errors occur."""
        return {
            "predicted_accuracy": 0.75,
            "predicted_completion_rate": 0.8,
            "predicted_satisfaction": 3.5,
            "confidence": 0.3,
            "recommendations": ["Unable to generate specific recommendations"],
            "similar_sessions_count": 0
        }
    
    def _categorize_readiness(self, score: float) -> str:
        """Categorize readiness level based on context score."""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    def _extract_key_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract key recommendations from analysis."""
        recommendations = []
        
        # Energy recommendations
        energy_recs = analysis.get("energy_assessment", {}).get("recommendations", [])
        if energy_recs:
            recommendations.extend(energy_recs[:2])  # Top 2
        
        # Environment recommendations
        env_adjustments = analysis.get("environment_factors", {}).get("adjustments", [])
        if env_adjustments:
            recommendations.extend(env_adjustments[:2])  # Top 2
        
        # Attention recommendations
        attention_info = analysis.get("attention_prediction", {})
        if attention_info.get("predicted_span", 25) < 20:
            recommendations.append("Take frequent breaks due to limited attention span")
        
        return recommendations[:5]  # Limit to top 5 recommendations
