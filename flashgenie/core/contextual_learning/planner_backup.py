"""
Study planning utilities for the contextual learning system.

This module provides functions to create adaptive study plans based on context.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

from ..content_system.deck import Deck
from .models import (
    StudyContext, StudyPlan, StudyPhase, ContextualRecommendation,
    EnergyLevel, AttentionLevel, StudyEnvironment, StudyMode
)


class StudyPlanner:
    """Creates adaptive study plans based on context."""
    
    def __init__(self):
        """Initialize the study planner."""
        self.adaptation_rules = self._load_default_adaptation_rules()
    
    def create_study_plan(self, deck: Deck, context: StudyContext) -> StudyPlan:
        """
        Create an adaptive study plan based on context.
        
        Args:
            deck: The deck to study
            context: Current study context
            
        Returns:
            Personalized study plan
        """
        plan_id = str(uuid.uuid4())
        
        # Calculate optimal session structure
        session_phases = self._plan_session_phases(deck, context)
        
        # Select appropriate cards
        recommended_cards = self._select_cards(deck, context)
        
        # Determine focus topics
        focus_topics = self._determine_focus_topics(deck, context)
        
        # Calculate break intervals
        break_intervals = self._calculate_break_intervals(context)
        
        # Create difficulty progression
        difficulty_progression = self._create_difficulty_progression(context, len(session_phases))
        
        # Estimate completion time and accuracy
        estimated_completion = sum(phase.duration for phase in session_phases)
        predicted_accuracy = self._predict_session_accuracy(context, deck)
        
        plan = StudyPlan(
            plan_id=plan_id,
            created_at=datetime.now(),
            context=context,
            total_duration=estimated_completion,
            session_phases=session_phases,
            recommended_cards=recommended_cards,
            focus_topics=focus_topics,
            difficulty_range=self._calculate_difficulty_range(context),
            break_intervals=break_intervals,
            difficulty_progression=difficulty_progression,
            estimated_completion=estimated_completion,
            predicted_accuracy=predicted_accuracy,
            confidence_score=self._calculate_plan_confidence(context)
        )
        
        return plan
    
    def adapt_plan_realtime(
        self, 
        current_plan: StudyPlan, 
        performance_data: Dict[str, Any]
    ) -> StudyPlan:
        """
        Adapt a study plan in real-time based on performance.
        
        Args:
            current_plan: Current study plan
            performance_data: Real-time performance data
            
        Returns:
            Adapted study plan
        """
        # Analyze current performance
        current_accuracy = performance_data.get("accuracy", 0.75)
        current_speed = performance_data.get("speed", 1.0)
        current_engagement = performance_data.get("engagement", 3)
        
        # Create adapted plan
        adapted_plan = StudyPlan(
            plan_id=current_plan.plan_id + "_adapted",
            created_at=datetime.now(),
            context=current_plan.context,
            total_duration=current_plan.total_duration,
            session_phases=current_plan.session_phases.copy(),
            recommended_cards=current_plan.recommended_cards.copy(),
            focus_topics=current_plan.focus_topics.copy(),
            difficulty_range=current_plan.difficulty_range,
            break_intervals=current_plan.break_intervals.copy(),
            difficulty_progression=current_plan.difficulty_progression.copy(),
            estimated_completion=current_plan.estimated_completion,
            predicted_accuracy=current_plan.predicted_accuracy,
            confidence_score=current_plan.confidence_score
        )
        
        # Apply adaptations based on performance
        if current_accuracy < 0.6:
            # Performance is low - make content easier
            adapted_plan = self._adapt_for_low_performance(adapted_plan)
        elif current_accuracy > 0.9:
            # Performance is high - increase challenge
            adapted_plan = self._adapt_for_high_performance(adapted_plan)
        
        if current_engagement < 2:
            # Low engagement - add variety
            adapted_plan = self._adapt_for_low_engagement(adapted_plan)
        
        return adapted_plan
    
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
        
        return recommendations
    
    def _plan_session_phases(self, deck: Deck, context: StudyContext) -> List[StudyPhase]:
        """Plan the phases of a study session."""
        phases = []
        total_time = context.time_available
        
        # Determine phase structure based on context
        if context.energy_level in [EnergyLevel.VERY_LOW, EnergyLevel.LOW]:
            # Low energy - simple structure
            phases = [
                StudyPhase(
                    phase_name="Light Review",
                    duration=min(total_time, 20),
                    description="Review familiar cards at comfortable pace",
                    phase_type="review",
                    difficulty_target=0.3
                )
            ]
        elif context.energy_level == EnergyLevel.MEDIUM:
            # Medium energy - balanced structure
            review_time = int(total_time * 0.4)
            practice_time = total_time - review_time
            
            phases = [
                StudyPhase(
                    phase_name="Warm-up Review",
                    duration=review_time,
                    description="Review previous material",
                    phase_type="review",
                    difficulty_target=0.4
                ),
                StudyPhase(
                    phase_name="Active Practice",
                    duration=practice_time,
                    description="Practice and learn new material",
                    phase_type="practice",
                    difficulty_target=0.6
                )
            ]
        else:
            # High energy - intensive structure
            warmup_time = int(total_time * 0.2)
            learning_time = int(total_time * 0.5)
            practice_time = total_time - warmup_time - learning_time
            
            phases = [
                StudyPhase(
                    phase_name="Quick Warmup",
                    duration=warmup_time,
                    description="Quick review to get started",
                    phase_type="review",
                    difficulty_target=0.3
                ),
                StudyPhase(
                    phase_name="Intensive Learning",
                    duration=learning_time,
                    description="Learn challenging new material",
                    phase_type="learning",
                    difficulty_target=0.7
                ),
                StudyPhase(
                    phase_name="Consolidation Practice",
                    duration=practice_time,
                    description="Practice and reinforce learning",
                    phase_type="practice",
                    difficulty_target=0.5
                )
            ]
        
        # Adjust phases based on environment
        if context.environment in [StudyEnvironment.NOISY, StudyEnvironment.DISTRACTED]:
            # Shorten phases and reduce difficulty
            for phase in phases:
                phase.duration = min(phase.duration, 15)
                phase.difficulty_target *= 0.8
        
        return phases
    
    def _select_cards(self, deck: Deck, context: StudyContext) -> List[str]:
        """Select appropriate cards based on context."""
        recommended_difficulty = self._calculate_recommended_difficulty(context)
        
        # Filter cards by difficulty range
        difficulty_tolerance = 0.2
        suitable_cards = [
            card.id for card in deck.flashcards
            if abs(card.difficulty - recommended_difficulty) <= difficulty_tolerance
        ]
        
        # If focus areas specified, prioritize those
        if context.focus_areas:
            focus_cards = [
                card.id for card in deck.flashcards
                if any(tag in context.focus_areas for tag in card.tags)
            ]
            # Combine with suitable cards
            suitable_cards = list(set(suitable_cards) & set(focus_cards))
        
        # Limit number of cards based on time available
        max_cards = context.time_available // 2  # Rough estimate: 2 minutes per card
        
        return suitable_cards[:max_cards]
    
    def _determine_focus_topics(self, deck: Deck, context: StudyContext) -> List[str]:
        """Determine focus topics based on context."""
        if context.focus_areas:
            return list(context.focus_areas)
        
        # Auto-determine based on deck analysis
        all_tags = set()
        for card in deck.flashcards:
            all_tags.update(card.tags)
        
        # For now, return all tags (could be more sophisticated)
        return list(all_tags)[:5]  # Limit to top 5
    
    def _calculate_break_intervals(self, context: StudyContext) -> List[int]:
        """Calculate when to take breaks."""
        total_time = context.time_available
        
        # Base break interval on attention span
        if context.attention_level == AttentionLevel.POOR:
            break_interval = 15
        elif context.attention_level == AttentionLevel.FAIR:
            break_interval = 20
        elif context.attention_level == AttentionLevel.GOOD:
            break_interval = 25
        else:  # EXCELLENT
            break_interval = 30
        
        # Adjust for energy level
        if context.energy_level in [EnergyLevel.VERY_LOW, EnergyLevel.LOW]:
            break_interval = min(break_interval, 15)
        
        # Calculate break points
        breaks = []
        current_time = break_interval
        while current_time < total_time:
            breaks.append(current_time)
            current_time += break_interval
        
        return breaks
    
    def _create_difficulty_progression(self, context: StudyContext, num_phases: int) -> List[float]:
        """Create a difficulty progression for the session."""
        base_difficulty = self._calculate_recommended_difficulty(context)
        
        if num_phases == 1:
            return [base_difficulty]
        
        # Create progression based on energy level
        if context.energy_level in [EnergyLevel.VERY_LOW, EnergyLevel.LOW]:
            # Flat, easy progression
            return [base_difficulty * 0.8] * num_phases
        elif context.energy_level == EnergyLevel.MEDIUM:
            # Gradual increase
            progression = []
            for i in range(num_phases):
                difficulty = base_difficulty + (i * 0.1)
                progression.append(min(difficulty, 1.0))
            return progression
        else:
            # Start easy, peak in middle, then moderate
            if num_phases == 2:
                return [base_difficulty * 0.9, base_difficulty * 1.1]
            else:
                return [
                    base_difficulty * 0.8,  # Warmup
                    base_difficulty * 1.2,  # Peak
                    base_difficulty * 1.0   # Consolidation
                ]
    
    def _calculate_recommended_difficulty(self, context: StudyContext) -> float:
        """Calculate recommended difficulty based on context."""
        base_difficulty = context.preferred_difficulty
        
        # Adjust based on energy
        energy_adjustments = {
            EnergyLevel.VERY_LOW: -0.3,
            EnergyLevel.LOW: -0.2,
            EnergyLevel.MEDIUM: 0.0,
            EnergyLevel.HIGH: 0.1,
            EnergyLevel.VERY_HIGH: 0.2
        }
        
        base_difficulty += energy_adjustments.get(context.energy_level, 0.0)
        
        # Adjust based on attention
        attention_adjustments = {
            AttentionLevel.POOR: -0.2,
            AttentionLevel.FAIR: -0.1,
            AttentionLevel.GOOD: 0.0,
            AttentionLevel.EXCELLENT: 0.1
        }
        
        base_difficulty += attention_adjustments.get(context.attention_level, 0.0)
        
        # Adjust based on stress
        if context.stress_level >= 4:
            base_difficulty -= 0.2
        
        return max(0.1, min(1.0, base_difficulty))
    
    def _calculate_difficulty_range(self, context: StudyContext) -> tuple:
        """Calculate the difficulty range for card selection."""
        recommended = self._calculate_recommended_difficulty(context)
        tolerance = 0.2
        
        return (max(0.0, recommended - tolerance), min(1.0, recommended + tolerance))
    
    def _predict_session_accuracy(self, context: StudyContext, deck: Deck) -> float:
        """Predict session accuracy based on context."""
        base_accuracy = 0.75
        
        # Adjust based on energy
        if context.energy_level in [EnergyLevel.HIGH, EnergyLevel.VERY_HIGH]:
            base_accuracy += 0.1
        elif context.energy_level in [EnergyLevel.VERY_LOW, EnergyLevel.LOW]:
            base_accuracy -= 0.15
        
        # Adjust based on attention
        if context.attention_level == AttentionLevel.EXCELLENT:
            base_accuracy += 0.1
        elif context.attention_level == AttentionLevel.POOR:
            base_accuracy -= 0.2
        
        # Adjust based on environment
        if context.environment == StudyEnvironment.FOCUSED:
            base_accuracy += 0.05
        elif context.environment in [StudyEnvironment.NOISY, StudyEnvironment.DISTRACTED]:
            base_accuracy -= 0.15
        
        return max(0.3, min(1.0, base_accuracy))
    
    def _calculate_plan_confidence(self, context: StudyContext) -> float:
        """Calculate confidence in the study plan."""
        confidence = 0.5  # Base confidence
        
        # Higher confidence with better context
        if context.energy_level in [EnergyLevel.MEDIUM, EnergyLevel.HIGH]:
            confidence += 0.2
        
        if context.attention_level in [AttentionLevel.GOOD, AttentionLevel.EXCELLENT]:
            confidence += 0.2
        
        if context.environment in [StudyEnvironment.QUIET, StudyEnvironment.FOCUSED]:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _adapt_for_low_performance(self, plan: StudyPlan) -> StudyPlan:
        """Adapt plan for low performance."""
        # Reduce difficulty in remaining phases
        for phase in plan.session_phases:
            phase.difficulty_target *= 0.8
        
        # Adjust difficulty progression
        plan.difficulty_progression = [d * 0.8 for d in plan.difficulty_progression]
        
        return plan
    
    def _adapt_for_high_performance(self, plan: StudyPlan) -> StudyPlan:
        """Adapt plan for high performance."""
        # Increase difficulty in remaining phases
        for phase in plan.session_phases:
            phase.difficulty_target = min(1.0, phase.difficulty_target * 1.2)
        
        # Adjust difficulty progression
        plan.difficulty_progression = [min(1.0, d * 1.2) for d in plan.difficulty_progression]
        
        return plan
    
    def _adapt_for_low_engagement(self, plan: StudyPlan) -> StudyPlan:
        """Adapt plan for low engagement."""
        # Shorten phases and add more variety
        for phase in plan.session_phases:
            phase.duration = min(phase.duration, 15)
        
        # Add more frequent breaks
        plan.break_intervals = [i * 10 for i in range(1, plan.total_duration // 10)]
        
        return plan
    
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
        
        return recommendations
    
    def _generate_time_recommendations(self, context: StudyContext) -> List[ContextualRecommendation]:
        """Generate time-based recommendations."""
        recommendations = []
        
        if context.time_available < 15:
            rec = ContextualRecommendation(
                recommendation_type="time",
                title="Optimize Short Study Session",
                description="Limited time available - focus on high-impact activities.",
                confidence=0.9,
                suggested_actions=[
                    "Focus on review of familiar material",
                    "Use spaced repetition for maximum efficiency",
                    "Avoid starting new complex topics",
                    "Consider quick flashcard drills"
                ],
                expected_benefit="Maximum learning in minimal time",
                effort_required="low"
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_content_recommendations(self, context: StudyContext, deck: Deck) -> List[ContextualRecommendation]:
        """Generate content-based recommendations."""
        recommendations = []
        
        # Analyze deck difficulty distribution
        difficulties = [card.difficulty for card in deck.flashcards]
        if difficulties:
            avg_difficulty = sum(difficulties) / len(difficulties)
            recommended_difficulty = self._calculate_recommended_difficulty(context)
            
            if abs(avg_difficulty - recommended_difficulty) > 0.3:
                rec = ContextualRecommendation(
                    recommendation_type="content",
                    title="Adjust Content Difficulty",
                    description=f"Deck difficulty ({avg_difficulty:.1f}) may not match your current context.",
                    confidence=0.7,
                    suggested_actions=[
                        f"Focus on cards with difficulty around {recommended_difficulty:.1f}",
                        "Filter cards by difficulty level",
                        "Adjust study mode based on energy level"
                    ],
                    expected_benefit="Better alignment with current capabilities",
                    effort_required="low"
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _load_default_adaptation_rules(self) -> List[Dict[str, Any]]:
        """Load default adaptation rules."""
        return [
            {
                "name": "Low Energy Adaptation",
                "conditions": {"energy_level": [1, 2]},
                "adaptations": {"difficulty_multiplier": 0.8, "max_duration": 20}
            },
            {
                "name": "High Energy Optimization",
                "conditions": {"energy_level": [4, 5]},
                "adaptations": {"difficulty_multiplier": 1.2, "enable_challenges": True}
            },
            {
                "name": "Poor Attention Adjustment",
                "conditions": {"attention_level": [1, 2]},
                "adaptations": {"break_frequency": 15, "difficulty_multiplier": 0.9}
            },
            {
                "name": "Noisy Environment Compensation",
                "conditions": {"environment": ["noisy", "distracted"]},
                "adaptations": {"session_type": "review", "difficulty_multiplier": 0.8}
            }
        ]
