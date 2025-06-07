"""
Session planning utilities for the contextual learning system.

This module provides functions to plan study sessions based on context.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ..content_system.deck import Deck
from .models import (
    StudyContext, StudyPhase, EnergyLevel, AttentionLevel, StudyEnvironment
)


class SessionPlanner:
    """Plans study sessions based on context."""
    
    def __init__(self):
        """Initialize the session planner."""
        pass
    
    def plan_session_phases(self, deck: Deck, context: StudyContext) -> List[StudyPhase]:
        """
        Plan the phases of a study session.
        
        Args:
            deck: The deck to study
            context: Current study context
            
        Returns:
            List of study phases
        """
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
    
    def select_cards(self, deck: Deck, context: StudyContext) -> List[str]:
        """
        Select appropriate cards based on context.
        
        Args:
            deck: The deck to study
            context: Current study context
            
        Returns:
            List of recommended card IDs
        """
        recommended_difficulty = self._calculate_recommended_difficulty(context)
        
        # Filter cards by difficulty range
        difficulty_tolerance = 0.2
        suitable_cards = [
            card.card_id for card in deck.flashcards
            if abs(card.difficulty - recommended_difficulty) <= difficulty_tolerance
        ]
        
        # If focus areas specified, prioritize those
        if context.focus_areas:
            focus_cards = [
                card.card_id for card in deck.flashcards
                if any(tag in context.focus_areas for tag in card.tags)
            ]
            # Combine with suitable cards
            suitable_cards = list(set(suitable_cards) & set(focus_cards))
        
        # Prioritize due cards
        due_cards = [
            card.card_id for card in deck.flashcards
            if card.is_due and card.card_id in suitable_cards
        ]
        
        # Combine due cards with other suitable cards
        if due_cards:
            # Start with due cards, then add others
            remaining_cards = [cid for cid in suitable_cards if cid not in due_cards]
            suitable_cards = due_cards + remaining_cards
        
        # Limit number of cards based on time available
        max_cards = context.time_available // 2  # Rough estimate: 2 minutes per card
        
        return suitable_cards[:max_cards]
    
    def determine_focus_topics(self, deck: Deck, context: StudyContext) -> List[str]:
        """
        Determine focus topics based on context.
        
        Args:
            deck: The deck to study
            context: Current study context
            
        Returns:
            List of focus topics
        """
        if context.focus_areas:
            return list(context.focus_areas)
        
        # Auto-determine based on deck analysis
        all_tags = set()
        tag_frequency = {}
        
        for card in deck.flashcards:
            for tag in card.tags:
                all_tags.add(tag)
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
        
        # Sort tags by frequency and difficulty
        sorted_tags = sorted(
            tag_frequency.items(),
            key=lambda x: (x[1], self._get_tag_difficulty(deck, x[0])),
            reverse=True
        )
        
        # Return top 5 most relevant tags
        return [tag for tag, _ in sorted_tags[:5]]
    
    def calculate_break_intervals(self, context: StudyContext) -> List[int]:
        """
        Calculate when to take breaks.
        
        Args:
            context: Current study context
            
        Returns:
            List of break time points (in minutes)
        """
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
        elif context.energy_level == EnergyLevel.VERY_HIGH:
            break_interval = min(break_interval + 10, 40)
        
        # Adjust for environment
        if context.environment in [StudyEnvironment.NOISY, StudyEnvironment.DISTRACTED]:
            break_interval = min(break_interval, 12)
        
        # Calculate break points
        breaks = []
        current_time = break_interval
        while current_time < total_time:
            breaks.append(current_time)
            current_time += break_interval
        
        return breaks
    
    def create_difficulty_progression(self, context: StudyContext, num_phases: int) -> List[float]:
        """
        Create a difficulty progression for the session.
        
        Args:
            context: Current study context
            num_phases: Number of study phases
            
        Returns:
            List of difficulty levels for each phase
        """
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
        elif context.stress_level <= 2:
            base_difficulty += 0.1
        
        # Adjust based on environment
        if context.environment == StudyEnvironment.FOCUSED:
            base_difficulty += 0.1
        elif context.environment in [StudyEnvironment.NOISY, StudyEnvironment.DISTRACTED]:
            base_difficulty -= 0.2
        
        return max(0.1, min(1.0, base_difficulty))
    
    def _get_tag_difficulty(self, deck: Deck, tag: str) -> float:
        """Get average difficulty for cards with a specific tag."""
        tag_cards = [card for card in deck.flashcards if tag in card.tags]
        if not tag_cards:
            return 0.5
        
        return sum(card.difficulty for card in tag_cards) / len(tag_cards)
    
    def calculate_difficulty_range(self, context: StudyContext) -> tuple:
        """Calculate the difficulty range for card selection."""
        recommended = self._calculate_recommended_difficulty(context)
        
        # Adjust tolerance based on context
        if context.energy_level in [EnergyLevel.VERY_LOW, EnergyLevel.LOW]:
            tolerance = 0.15  # Narrower range for low energy
        elif context.energy_level == EnergyLevel.VERY_HIGH:
            tolerance = 0.3   # Wider range for high energy
        else:
            tolerance = 0.2   # Standard range
        
        return (max(0.0, recommended - tolerance), min(1.0, recommended + tolerance))
    
    def estimate_session_metrics(self, context: StudyContext, deck: Deck) -> Dict[str, float]:
        """
        Estimate session metrics based on context.
        
        Args:
            context: Current study context
            deck: The deck to study
            
        Returns:
            Dictionary with estimated metrics
        """
        # Predict accuracy
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
        
        predicted_accuracy = max(0.3, min(1.0, base_accuracy))
        
        # Calculate confidence
        confidence = 0.5  # Base confidence
        
        # Higher confidence with better context
        if context.energy_level in [EnergyLevel.MEDIUM, EnergyLevel.HIGH]:
            confidence += 0.2
        
        if context.attention_level in [AttentionLevel.GOOD, AttentionLevel.EXCELLENT]:
            confidence += 0.2
        
        if context.environment in [StudyEnvironment.QUIET, StudyEnvironment.FOCUSED]:
            confidence += 0.1
        
        plan_confidence = min(1.0, confidence)
        
        return {
            "predicted_accuracy": predicted_accuracy,
            "plan_confidence": plan_confidence,
            "estimated_cards_per_minute": self._estimate_cards_per_minute(context),
            "estimated_retention_rate": self._estimate_retention_rate(context)
        }
    
    def _estimate_cards_per_minute(self, context: StudyContext) -> float:
        """Estimate cards per minute based on context."""
        base_rate = 0.5  # 30 seconds per card
        
        # Adjust based on energy and attention
        if context.energy_level == EnergyLevel.VERY_HIGH and context.attention_level == AttentionLevel.EXCELLENT:
            base_rate *= 1.5
        elif context.energy_level in [EnergyLevel.VERY_LOW, EnergyLevel.LOW]:
            base_rate *= 0.7
        
        # Adjust based on environment
        if context.environment in [StudyEnvironment.NOISY, StudyEnvironment.DISTRACTED]:
            base_rate *= 0.8
        
        return base_rate
    
    def _estimate_retention_rate(self, context: StudyContext) -> float:
        """Estimate retention rate based on context."""
        base_retention = 0.8
        
        # Better retention with good conditions
        if context.energy_level in [EnergyLevel.HIGH, EnergyLevel.VERY_HIGH]:
            base_retention += 0.1
        
        if context.attention_level in [AttentionLevel.GOOD, AttentionLevel.EXCELLENT]:
            base_retention += 0.1
        
        if context.environment == StudyEnvironment.FOCUSED:
            base_retention += 0.05
        
        # Lower retention with poor conditions
        if context.stress_level >= 4:
            base_retention -= 0.15
        
        return max(0.5, min(1.0, base_retention))
