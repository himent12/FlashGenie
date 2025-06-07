"""
Recommendation generation utilities for the contextual learning system.

This module provides functions to generate contextual recommendations.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from ..content_system.deck import Deck
from .models import (
    StudyContext, ContextualRecommendation, EnergyLevel, AttentionLevel, 
    StudyEnvironment, StudyMode
)


class RecommendationGenerator:
    """Generates contextual recommendations for study optimization."""
    
    def __init__(self):
        """Initialize the recommendation generator."""
        pass
    
    def generate_recommendations(self, context: StudyContext, deck: Deck) -> List[ContextualRecommendation]:
        """
        Generate contextual recommendations for study optimization.
        
        Args:
            context: Study context
            deck: Deck to study
            
        Returns:
            List of contextual recommendations
        """
        recommendations = []
        
        # Energy-based recommendations
        energy_recs = self._generate_energy_recommendations(context)
        recommendations.extend(energy_recs)
        
        # Environment-based recommendations
        env_recs = self._generate_environment_recommendations(context)
        recommendations.extend(env_recs)
        
        # Time-based recommendations
        time_recs = self._generate_time_recommendations(context)
        recommendations.extend(time_recs)
        
        # Content-based recommendations
        content_recs = self._generate_content_recommendations(context, deck)
        recommendations.extend(content_recs)
        
        # Attention-based recommendations
        attention_recs = self._generate_attention_recommendations(context)
        recommendations.extend(attention_recs)
        
        # Stress-based recommendations
        stress_recs = self._generate_stress_recommendations(context)
        recommendations.extend(stress_recs)
        
        # Sort by confidence and expected benefit
        recommendations.sort(key=lambda r: r.confidence * self._benefit_score(r.expected_benefit), reverse=True)
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def _generate_energy_recommendations(self, context: StudyContext) -> List[ContextualRecommendation]:
        """Generate energy-based recommendations."""
        recommendations = []
        
        if context.energy_level == EnergyLevel.VERY_LOW:
            rec = ContextualRecommendation(
                recommendation_type="energy",
                title="Consider Taking a Break",
                description="Your energy level is very low. Consider resting before studying.",
                confidence=0.9,
                suggested_actions=[
                    "Take a 10-15 minute break",
                    "Do some light physical activity",
                    "Have a healthy snack",
                    "Consider postponing intensive study"
                ],
                expected_benefit="Improved focus and retention",
                effort_required="low"
            )
            recommendations.append(rec)
            
        elif context.energy_level == EnergyLevel.LOW:
            rec = ContextualRecommendation(
                recommendation_type="energy",
                title="Light Study Session Recommended",
                description="Your energy is low. Focus on review and easy material.",
                confidence=0.8,
                suggested_actions=[
                    "Review familiar material",
                    "Avoid learning new concepts",
                    "Take frequent short breaks",
                    "Keep session under 30 minutes"
                ],
                expected_benefit="Maintained learning without fatigue",
                effort_required="low"
            )
            recommendations.append(rec)
        
        elif context.energy_level == EnergyLevel.VERY_HIGH:
            rec = ContextualRecommendation(
                recommendation_type="energy",
                title="Tackle Challenging Material",
                description="Your high energy level is perfect for learning difficult concepts.",
                confidence=0.8,
                suggested_actions=[
                    "Focus on new or difficult material",
                    "Extend study session if time allows",
                    "Practice complex problem-solving",
                    "Take on challenging topics"
                ],
                expected_benefit="Accelerated learning progress",
                effort_required="medium"
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_environment_recommendations(self, context: StudyContext) -> List[ContextualRecommendation]:
        """Generate environment-based recommendations."""
        recommendations = []
        
        if context.environment == StudyEnvironment.NOISY:
            rec = ContextualRecommendation(
                recommendation_type="environment",
                title="Optimize Study Environment",
                description="Noisy environment may impact learning effectiveness.",
                confidence=0.8,
                suggested_actions=[
                    "Use noise-canceling headphones",
                    "Find a quieter location",
                    "Focus on review rather than new learning",
                    "Take shorter, more frequent breaks"
                ],
                expected_benefit="Improved concentration and retention",
                effort_required="medium"
            )
            recommendations.append(rec)
        
        elif context.environment == StudyEnvironment.DISTRACTED:
            rec = ContextualRecommendation(
                recommendation_type="environment",
                title="Minimize Distractions",
                description="Current environment has many distractions.",
                confidence=0.9,
                suggested_actions=[
                    "Turn off notifications",
                    "Clear workspace of distractions",
                    "Use website blockers",
                    "Inform others you're studying"
                ],
                expected_benefit="Significantly improved focus",
                effort_required="low"
            )
            recommendations.append(rec)
        
        elif context.environment == StudyEnvironment.MOBILE:
            rec = ContextualRecommendation(
                recommendation_type="environment",
                title="Adapt for Mobile Study",
                description="Mobile environment requires different study strategies.",
                confidence=0.7,
                suggested_actions=[
                    "Use shorter study sessions",
                    "Focus on review and flashcards",
                    "Avoid complex new material",
                    "Be prepared for interruptions"
                ],
                expected_benefit="Effective learning despite mobility",
                effort_required="low"
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_time_recommendations(self, context: StudyContext) -> List[ContextualRecommendation]:
        """Generate time-based recommendations."""
        recommendations = []
        
        if context.time_available < 15:
            rec = ContextualRecommendation(
                recommendation_type="time",
                title="Quick Review Session",
                description="Limited time available - focus on quick review.",
                confidence=0.8,
                suggested_actions=[
                    "Review 5-10 flashcards",
                    "Quick scan of difficult concepts",
                    "Use spaced repetition",
                    "Focus on due cards only"
                ],
                expected_benefit="Maintained knowledge retention",
                effort_required="low"
            )
            recommendations.append(rec)
        
        elif context.time_available > 60:
            rec = ContextualRecommendation(
                recommendation_type="time",
                title="Extended Study Session",
                description="You have plenty of time for comprehensive study.",
                confidence=0.7,
                suggested_actions=[
                    "Plan multiple study phases",
                    "Include breaks every 25-30 minutes",
                    "Mix review and new learning",
                    "End with consolidation practice"
                ],
                expected_benefit="Comprehensive learning progress",
                effort_required="medium"
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_content_recommendations(self, context: StudyContext, deck: Deck) -> List[ContextualRecommendation]:
        """Generate content-based recommendations."""
        recommendations = []
        
        # Check deck status
        due_count = sum(1 for card in deck.flashcards if card.is_due)
        total_count = len(deck.flashcards)
        due_ratio = due_count / total_count if total_count > 0 else 0
        
        if due_ratio > 0.5:
            rec = ContextualRecommendation(
                recommendation_type="content",
                title="Focus on Due Cards",
                description=f"You have {due_count} cards due for review.",
                confidence=0.9,
                suggested_actions=[
                    "Prioritize due cards",
                    "Use spaced repetition",
                    "Review before learning new material",
                    "Consider shorter sessions to avoid overload"
                ],
                expected_benefit="Maintained retention and progress",
                effort_required="medium"
            )
            recommendations.append(rec)
        
        # Check for difficult cards
        difficult_cards = [card for card in deck.flashcards if card.difficulty > 0.7]
        if len(difficult_cards) > 5 and context.energy_level in [EnergyLevel.HIGH, EnergyLevel.VERY_HIGH]:
            rec = ContextualRecommendation(
                recommendation_type="content",
                title="Tackle Difficult Cards",
                description="Good time to work on challenging material.",
                confidence=0.7,
                suggested_actions=[
                    "Focus on difficult cards",
                    "Break down complex concepts",
                    "Use active recall techniques",
                    "Take notes for difficult topics"
                ],
                expected_benefit="Progress on challenging material",
                effort_required="high"
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_attention_recommendations(self, context: StudyContext) -> List[ContextualRecommendation]:
        """Generate attention-based recommendations."""
        recommendations = []
        
        if context.attention_level == AttentionLevel.POOR:
            rec = ContextualRecommendation(
                recommendation_type="attention",
                title="Improve Focus Before Studying",
                description="Poor attention may significantly impact learning.",
                confidence=0.9,
                suggested_actions=[
                    "Do a 5-minute meditation",
                    "Take deep breaths",
                    "Clear your mind of distractions",
                    "Consider postponing if very unfocused"
                ],
                expected_benefit="Significantly improved learning effectiveness",
                effort_required="low"
            )
            recommendations.append(rec)
        
        elif context.attention_level == AttentionLevel.EXCELLENT:
            rec = ContextualRecommendation(
                recommendation_type="attention",
                title="Maximize Learning Opportunity",
                description="Excellent attention - perfect for intensive learning.",
                confidence=0.8,
                suggested_actions=[
                    "Focus on complex new material",
                    "Extend study session",
                    "Practice active recall",
                    "Work on challenging concepts"
                ],
                expected_benefit="Maximum learning progress",
                effort_required="medium"
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_stress_recommendations(self, context: StudyContext) -> List[ContextualRecommendation]:
        """Generate stress-based recommendations."""
        recommendations = []
        
        if context.stress_level >= 4:
            rec = ContextualRecommendation(
                recommendation_type="stress",
                title="Manage Stress Before Studying",
                description="High stress levels can impair learning and memory.",
                confidence=0.9,
                suggested_actions=[
                    "Take 5-10 minutes to relax",
                    "Practice deep breathing",
                    "Do light physical activity",
                    "Focus on easier, familiar material"
                ],
                expected_benefit="Reduced stress and improved learning",
                effort_required="low"
            )
            recommendations.append(rec)
        
        elif context.stress_level <= 2:
            rec = ContextualRecommendation(
                recommendation_type="stress",
                title="Optimal Stress Level",
                description="Low stress creates ideal learning conditions.",
                confidence=0.7,
                suggested_actions=[
                    "Maintain current relaxed state",
                    "Take advantage of calm mindset",
                    "Focus on challenging material",
                    "Extend session if energy allows"
                ],
                expected_benefit="Enhanced learning in relaxed state",
                effort_required="low"
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _benefit_score(self, benefit_description: str) -> float:
        """Calculate a numeric score for expected benefit."""
        benefit_keywords = {
            "significantly": 1.0,
            "improved": 0.8,
            "enhanced": 0.8,
            "maximum": 1.0,
            "accelerated": 0.9,
            "comprehensive": 0.7,
            "maintained": 0.5,
            "effective": 0.6
        }
        
        score = 0.5  # Base score
        benefit_lower = benefit_description.lower()
        
        for keyword, value in benefit_keywords.items():
            if keyword in benefit_lower:
                score = max(score, value)
        
        return score
    
    def generate_session_tips(self, context: StudyContext) -> List[str]:
        """
        Generate quick tips for the current session.
        
        Args:
            context: Study context
            
        Returns:
            List of quick tips
        """
        tips = []
        
        # Energy-based tips
        if context.energy_level == EnergyLevel.LOW:
            tips.append("💡 Start with easier cards to build momentum")
        elif context.energy_level == EnergyLevel.VERY_HIGH:
            tips.append("🚀 Perfect time for learning new concepts!")
        
        # Attention-based tips
        if context.attention_level == AttentionLevel.POOR:
            tips.append("🧘 Take a moment to center yourself before starting")
        elif context.attention_level == AttentionLevel.EXCELLENT:
            tips.append("🎯 Your focus is sharp - tackle challenging material")
        
        # Environment-based tips
        if context.environment == StudyEnvironment.NOISY:
            tips.append("🎧 Consider using headphones to block distractions")
        elif context.environment == StudyEnvironment.FOCUSED:
            tips.append("✨ Great environment for deep learning")
        
        # Time-based tips
        if context.time_available < 20:
            tips.append("⏰ Quick session - focus on review and due cards")
        elif context.time_available > 45:
            tips.append("📚 Plenty of time - plan breaks every 25-30 minutes")
        
        return tips[:5]  # Return top 5 tips
