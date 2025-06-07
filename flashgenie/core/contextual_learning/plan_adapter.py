"""
Plan adaptation utilities for the contextual learning system.

This module provides functions to adapt study plans in real-time.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from .models import StudyPlan, StudyPhase


class PlanAdapter:
    """Adapts study plans in real-time based on performance."""
    
    def __init__(self):
        """Initialize the plan adapter."""
        self.logger = logging.getLogger(__name__)
        self.adaptation_thresholds = {
            "low_accuracy": 0.6,
            "high_accuracy": 0.9,
            "low_engagement": 2.0,
            "high_engagement": 4.5,
            "slow_speed": 0.7,
            "fast_speed": 1.5
        }
    
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
        try:
            # Extract performance metrics
            current_accuracy = performance_data.get("accuracy", 0.75)
            current_speed = performance_data.get("speed", 1.0)
            current_engagement = performance_data.get("engagement", 3.0)
            cards_completed = performance_data.get("cards_completed", 0)
            time_elapsed = performance_data.get("time_elapsed", 0)
            
            self.logger.debug(f"Adapting plan based on performance: accuracy={current_accuracy:.2f}, "
                            f"speed={current_speed:.2f}, engagement={current_engagement:.1f}")
            
            # Create adapted plan
            adapted_plan = self._create_adapted_plan_copy(current_plan)
            
            # Apply adaptations based on performance
            if current_accuracy < self.adaptation_thresholds["low_accuracy"]:
                adapted_plan = self._adapt_for_low_performance(adapted_plan, performance_data)
            elif current_accuracy > self.adaptation_thresholds["high_accuracy"]:
                adapted_plan = self._adapt_for_high_performance(adapted_plan, performance_data)
            
            if current_engagement < self.adaptation_thresholds["low_engagement"]:
                adapted_plan = self._adapt_for_low_engagement(adapted_plan, performance_data)
            elif current_engagement > self.adaptation_thresholds["high_engagement"]:
                adapted_plan = self._adapt_for_high_engagement(adapted_plan, performance_data)
            
            if current_speed < self.adaptation_thresholds["slow_speed"]:
                adapted_plan = self._adapt_for_slow_pace(adapted_plan, performance_data)
            elif current_speed > self.adaptation_thresholds["fast_speed"]:
                adapted_plan = self._adapt_for_fast_pace(adapted_plan, performance_data)
            
            # Update plan metadata
            adapted_plan.confidence_score = self._recalculate_confidence(adapted_plan, performance_data)
            
            self.logger.info(f"Plan adapted successfully with confidence: {adapted_plan.confidence_score:.2f}")
            return adapted_plan
            
        except Exception as e:
            self.logger.error(f"Error adapting plan: {e}")
            return current_plan  # Return original plan if adaptation fails
    
    def _create_adapted_plan_copy(self, original_plan: StudyPlan) -> StudyPlan:
        """Create a copy of the plan for adaptation."""
        return StudyPlan(
            plan_id=original_plan.plan_id + "_adapted",
            created_at=datetime.now(),
            context=original_plan.context,
            total_duration=original_plan.total_duration,
            session_phases=original_plan.session_phases.copy(),
            recommended_cards=original_plan.recommended_cards.copy(),
            focus_topics=original_plan.focus_topics.copy(),
            difficulty_range=original_plan.difficulty_range,
            break_intervals=original_plan.break_intervals.copy(),
            difficulty_progression=original_plan.difficulty_progression.copy(),
            estimated_completion=original_plan.estimated_completion,
            predicted_accuracy=original_plan.predicted_accuracy,
            confidence_score=original_plan.confidence_score
        )
    
    def _adapt_for_low_performance(self, plan: StudyPlan, performance_data: Dict[str, Any]) -> StudyPlan:
        """Adapt plan for low performance."""
        self.logger.debug("Adapting for low performance")
        
        # Reduce difficulty in remaining phases
        for phase in plan.session_phases:
            phase.difficulty_target = max(0.1, phase.difficulty_target * 0.8)
            phase.description += " (Difficulty reduced due to low accuracy)"
        
        # Adjust difficulty progression
        plan.difficulty_progression = [max(0.1, d * 0.8) for d in plan.difficulty_progression]
        
        # Add more breaks
        if len(plan.break_intervals) > 0:
            # Add breaks between existing ones
            new_breaks = []
            for i, break_time in enumerate(plan.break_intervals):
                new_breaks.append(break_time)
                if i < len(plan.break_intervals) - 1:
                    # Add break halfway to next break
                    next_break = plan.break_intervals[i + 1]
                    mid_break = (break_time + next_break) // 2
                    new_breaks.append(mid_break)
            plan.break_intervals = new_breaks
        
        # Reduce predicted accuracy
        plan.predicted_accuracy = max(0.3, plan.predicted_accuracy * 0.9)
        
        return plan
    
    def _adapt_for_high_performance(self, plan: StudyPlan, performance_data: Dict[str, Any]) -> StudyPlan:
        """Adapt plan for high performance."""
        self.logger.debug("Adapting for high performance")
        
        # Increase difficulty in remaining phases
        for phase in plan.session_phases:
            phase.difficulty_target = min(1.0, phase.difficulty_target * 1.2)
            phase.description += " (Difficulty increased due to high accuracy)"
        
        # Adjust difficulty progression
        plan.difficulty_progression = [min(1.0, d * 1.2) for d in plan.difficulty_progression]
        
        # Potentially extend session if time allows
        if plan.total_duration < plan.context.time_available:
            extension = min(15, plan.context.time_available - plan.total_duration)
            plan.total_duration += extension
            plan.estimated_completion += extension
            
            # Add an additional practice phase
            if extension >= 10:
                additional_phase = StudyPhase(
                    phase_name="Bonus Challenge",
                    duration=extension,
                    description="Additional challenging practice",
                    phase_type="practice",
                    difficulty_target=min(1.0, max(plan.difficulty_progression) * 1.1)
                )
                plan.session_phases.append(additional_phase)
        
        # Increase predicted accuracy
        plan.predicted_accuracy = min(1.0, plan.predicted_accuracy * 1.1)
        
        return plan
    
    def _adapt_for_low_engagement(self, plan: StudyPlan, performance_data: Dict[str, Any]) -> StudyPlan:
        """Adapt plan for low engagement."""
        self.logger.debug("Adapting for low engagement")
        
        # Shorten phases and add more variety
        for phase in plan.session_phases:
            phase.duration = min(phase.duration, 15)
            phase.description += " (Shortened to maintain engagement)"
        
        # Add more frequent breaks
        plan.break_intervals = [i * 10 for i in range(1, plan.total_duration // 10)]
        
        # Vary difficulty more to add interest
        if len(plan.difficulty_progression) > 1:
            # Add some variation to difficulty progression
            for i in range(len(plan.difficulty_progression)):
                if i % 2 == 0:
                    plan.difficulty_progression[i] = max(0.1, plan.difficulty_progression[i] * 0.9)
                else:
                    plan.difficulty_progression[i] = min(1.0, plan.difficulty_progression[i] * 1.1)
        
        return plan
    
    def _adapt_for_high_engagement(self, plan: StudyPlan, performance_data: Dict[str, Any]) -> StudyPlan:
        """Adapt plan for high engagement."""
        self.logger.debug("Adapting for high engagement")
        
        # Extend phases slightly since user is engaged
        for phase in plan.session_phases:
            if phase.duration < 30:
                phase.duration = min(phase.duration + 5, 30)
                phase.description += " (Extended due to high engagement)"
        
        # Reduce break frequency
        if len(plan.break_intervals) > 1:
            # Keep every other break
            plan.break_intervals = plan.break_intervals[::2]
        
        return plan
    
    def _adapt_for_slow_pace(self, plan: StudyPlan, performance_data: Dict[str, Any]) -> StudyPlan:
        """Adapt plan for slow pace."""
        self.logger.debug("Adapting for slow pace")
        
        # Reduce number of cards if possible
        if len(plan.recommended_cards) > 5:
            # Keep only the most important cards (first 80%)
            keep_count = int(len(plan.recommended_cards) * 0.8)
            plan.recommended_cards = plan.recommended_cards[:keep_count]
        
        # Adjust time estimates
        plan.estimated_completion = int(plan.estimated_completion * 1.2)
        
        # Add note about pacing
        for phase in plan.session_phases:
            phase.description += " (Take your time - quality over speed)"
        
        return plan
    
    def _adapt_for_fast_pace(self, plan: StudyPlan, performance_data: Dict[str, Any]) -> StudyPlan:
        """Adapt plan for fast pace."""
        self.logger.debug("Adapting for fast pace")
        
        # Add more cards if available and time permits
        cards_completed = performance_data.get("cards_completed", 0)
        time_elapsed = performance_data.get("time_elapsed", 0)
        
        if time_elapsed > 0:
            current_rate = cards_completed / time_elapsed  # cards per minute
            remaining_time = plan.total_duration - time_elapsed
            potential_additional_cards = int(current_rate * remaining_time * 0.5)  # Conservative estimate
            
            # Could add more cards here if we had access to the deck
            # For now, just note the fast pace
            for phase in plan.session_phases:
                phase.description += " (Great pace - consider bonus material)"
        
        # Reduce estimated completion time
        plan.estimated_completion = int(plan.estimated_completion * 0.9)
        
        return plan
    
    def _recalculate_confidence(self, plan: StudyPlan, performance_data: Dict[str, Any]) -> float:
        """Recalculate plan confidence based on performance."""
        base_confidence = plan.confidence_score
        
        # Adjust based on how well performance matches predictions
        current_accuracy = performance_data.get("accuracy", 0.75)
        predicted_accuracy = plan.predicted_accuracy
        
        accuracy_diff = abs(current_accuracy - predicted_accuracy)
        
        if accuracy_diff < 0.1:
            # Prediction was accurate, increase confidence
            base_confidence = min(1.0, base_confidence + 0.1)
        elif accuracy_diff > 0.2:
            # Prediction was off, decrease confidence
            base_confidence = max(0.1, base_confidence - 0.1)
        
        return base_confidence
    
    def suggest_immediate_actions(self, performance_data: Dict[str, Any]) -> List[str]:
        """
        Suggest immediate actions based on current performance.
        
        Args:
            performance_data: Real-time performance data
            
        Returns:
            List of immediate action suggestions
        """
        suggestions = []
        
        current_accuracy = performance_data.get("accuracy", 0.75)
        current_engagement = performance_data.get("engagement", 3.0)
        current_speed = performance_data.get("speed", 1.0)
        
        if current_accuracy < 0.5:
            suggestions.append("🎯 Take a moment to review the material before continuing")
            suggestions.append("📚 Consider switching to easier cards")
        
        if current_engagement < 2.0:
            suggestions.append("☕ Take a short break to refresh")
            suggestions.append("🎵 Try changing your environment or adding background music")
        
        if current_speed < 0.5:
            suggestions.append("⏰ Don't rush - focus on understanding over speed")
            suggestions.append("🧘 Take deep breaths and maintain steady pace")
        
        if current_accuracy > 0.9 and current_speed > 1.2:
            suggestions.append("🚀 Great performance! Consider tackling harder material")
            suggestions.append("📈 You're ready for more challenging concepts")
        
        return suggestions[:3]  # Return top 3 suggestions
