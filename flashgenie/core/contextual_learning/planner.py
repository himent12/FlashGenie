"""
Study planning utilities for the contextual learning system.

This module provides functions to create adaptive study plans based on context.
Refactored for better maintainability and smaller file size.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import logging

from ..content_system.deck import Deck
from .models import StudyContext, StudyPlan, ContextualRecommendation
from .session_planner import SessionPlanner
from .recommendation_generator import RecommendationGenerator
from .plan_adapter import PlanAdapter


class StudyPlanner:
    """Creates adaptive study plans based on context."""
    
    def __init__(self):
        """Initialize the study planner."""
        self.session_planner = SessionPlanner()
        self.recommendation_generator = RecommendationGenerator()
        self.plan_adapter = PlanAdapter()
        
        self.logger = logging.getLogger(__name__)
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
        try:
            plan_id = str(uuid.uuid4())
            
            self.logger.info(f"Creating study plan for deck '{deck.name}' with {context.time_available} minutes")
            
            # Calculate optimal session structure
            session_phases = self.session_planner.plan_session_phases(deck, context)
            
            # Select appropriate cards
            recommended_cards = self.session_planner.select_cards(deck, context)
            
            # Determine focus topics
            focus_topics = self.session_planner.determine_focus_topics(deck, context)
            
            # Calculate break intervals
            break_intervals = self.session_planner.calculate_break_intervals(context)
            
            # Create difficulty progression
            difficulty_progression = self.session_planner.create_difficulty_progression(
                context, len(session_phases)
            )
            
            # Calculate difficulty range
            difficulty_range = self.session_planner.calculate_difficulty_range(context)
            
            # Estimate session metrics
            session_metrics = self.session_planner.estimate_session_metrics(context, deck)
            
            # Calculate total duration and completion time
            estimated_completion = sum(phase.duration for phase in session_phases)
            
            plan = StudyPlan(
                plan_id=plan_id,
                created_at=datetime.now(),
                context=context,
                total_duration=estimated_completion,
                session_phases=session_phases,
                recommended_cards=recommended_cards,
                focus_topics=focus_topics,
                difficulty_range=difficulty_range,
                break_intervals=break_intervals,
                difficulty_progression=difficulty_progression,
                estimated_completion=estimated_completion,
                predicted_accuracy=session_metrics["predicted_accuracy"],
                confidence_score=session_metrics["plan_confidence"]
            )
            
            self.logger.info(f"Study plan created successfully: {len(session_phases)} phases, "
                           f"{len(recommended_cards)} cards, confidence: {plan.confidence_score:.2f}")
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Error creating study plan: {e}")
            return self._create_fallback_plan(deck, context)
    
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
            self.logger.debug("Adapting study plan based on real-time performance")
            return self.plan_adapter.adapt_plan_realtime(current_plan, performance_data)
        except Exception as e:
            self.logger.error(f"Error adapting plan: {e}")
            return current_plan
    
    def generate_recommendations(self, context: StudyContext, deck: Deck) -> List[ContextualRecommendation]:
        """
        Generate contextual recommendations for study optimization.
        
        Args:
            context: Study context
            deck: Deck to study
            
        Returns:
            List of contextual recommendations
        """
        try:
            self.logger.debug("Generating contextual recommendations")
            recommendations = self.recommendation_generator.generate_recommendations(context, deck)
            self.logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []
    
    def get_session_tips(self, context: StudyContext) -> List[str]:
        """
        Get quick tips for the current session.
        
        Args:
            context: Study context
            
        Returns:
            List of quick tips
        """
        try:
            return self.recommendation_generator.generate_session_tips(context)
        except Exception as e:
            self.logger.error(f"Error generating session tips: {e}")
            return ["💡 Focus on understanding over speed", "📚 Take breaks when needed"]
    
    def suggest_immediate_actions(self, performance_data: Dict[str, Any]) -> List[str]:
        """
        Suggest immediate actions based on current performance.
        
        Args:
            performance_data: Real-time performance data
            
        Returns:
            List of immediate action suggestions
        """
        try:
            return self.plan_adapter.suggest_immediate_actions(performance_data)
        except Exception as e:
            self.logger.error(f"Error suggesting immediate actions: {e}")
            return []
    
    def validate_plan(self, plan: StudyPlan) -> Dict[str, Any]:
        """
        Validate a study plan for feasibility and quality.
        
        Args:
            plan: Study plan to validate
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        try:
            # Check time constraints
            if plan.total_duration > plan.context.time_available:
                validation["errors"].append(
                    f"Plan duration ({plan.total_duration} min) exceeds available time "
                    f"({plan.context.time_available} min)"
                )
                validation["valid"] = False
            
            # Check phase durations
            for i, phase in enumerate(plan.session_phases):
                if phase.duration <= 0:
                    validation["errors"].append(f"Phase {i+1} has invalid duration: {phase.duration}")
                    validation["valid"] = False
                elif phase.duration < 5:
                    validation["warnings"].append(f"Phase {i+1} is very short ({phase.duration} min)")
            
            # Check difficulty progression
            if len(plan.difficulty_progression) != len(plan.session_phases):
                validation["errors"].append("Difficulty progression doesn't match number of phases")
                validation["valid"] = False
            
            # Check for reasonable number of cards
            if len(plan.recommended_cards) == 0:
                validation["warnings"].append("No cards recommended for study")
            elif len(plan.recommended_cards) > plan.context.time_available * 2:
                validation["warnings"].append("Very high number of cards for available time")
            
            # Suggestions for improvement
            if plan.confidence_score < 0.5:
                validation["suggestions"].append("Consider adjusting context factors to improve plan quality")
            
            if len(plan.break_intervals) == 0 and plan.total_duration > 30:
                validation["suggestions"].append("Consider adding breaks for longer sessions")
            
        except Exception as e:
            validation["errors"].append(f"Validation error: {e}")
            validation["valid"] = False
        
        return validation
    
    def _create_fallback_plan(self, deck: Deck, context: StudyContext) -> StudyPlan:
        """Create a simple fallback plan when main planning fails."""
        self.logger.warning("Creating fallback study plan")
        
        from .models import StudyPhase
        
        # Simple single-phase plan
        phase = StudyPhase(
            phase_name="Basic Study Session",
            duration=min(context.time_available, 30),
            description="Basic study session with mixed content",
            phase_type="mixed",
            difficulty_target=0.5
        )
        
        # Select a few cards
        recommended_cards = [card.card_id for card in deck.flashcards[:10]]
        
        return StudyPlan(
            plan_id=str(uuid.uuid4()),
            created_at=datetime.now(),
            context=context,
            total_duration=phase.duration,
            session_phases=[phase],
            recommended_cards=recommended_cards,
            focus_topics=[],
            difficulty_range=(0.3, 0.7),
            break_intervals=[],
            difficulty_progression=[0.5],
            estimated_completion=phase.duration,
            predicted_accuracy=0.7,
            confidence_score=0.3
        )
    
    def _load_default_adaptation_rules(self) -> Dict[str, Any]:
        """Load default adaptation rules."""
        return {
            "accuracy_thresholds": {
                "low": 0.6,
                "high": 0.9
            },
            "engagement_thresholds": {
                "low": 2.0,
                "high": 4.5
            },
            "speed_thresholds": {
                "slow": 0.7,
                "fast": 1.5
            },
            "adaptation_factors": {
                "difficulty_reduction": 0.8,
                "difficulty_increase": 1.2,
                "phase_shortening": 0.8,
                "break_frequency_increase": 1.5
            }
        }
    
    def update_adaptation_rules(self, new_rules: Dict[str, Any]) -> None:
        """
        Update adaptation rules.
        
        Args:
            new_rules: Dictionary with new adaptation rules
        """
        try:
            self.adaptation_rules.update(new_rules)
            
            # Update thresholds in plan adapter
            if "accuracy_thresholds" in new_rules:
                thresholds = new_rules["accuracy_thresholds"]
                if "low" in thresholds:
                    self.plan_adapter.adaptation_thresholds["low_accuracy"] = thresholds["low"]
                if "high" in thresholds:
                    self.plan_adapter.adaptation_thresholds["high_accuracy"] = thresholds["high"]
            
            self.logger.info("Adaptation rules updated successfully")
            
        except Exception as e:
            self.logger.error(f"Error updating adaptation rules: {e}")
    
    def get_plan_summary(self, plan: StudyPlan) -> Dict[str, Any]:
        """
        Get a summary of the study plan.
        
        Args:
            plan: Study plan to summarize
            
        Returns:
            Dictionary with plan summary
        """
        try:
            return {
                "plan_id": plan.plan_id,
                "total_duration": plan.total_duration,
                "phase_count": len(plan.session_phases),
                "card_count": len(plan.recommended_cards),
                "focus_topics": plan.focus_topics[:3],  # Top 3
                "difficulty_range": f"{plan.difficulty_range[0]:.1f}-{plan.difficulty_range[1]:.1f}",
                "predicted_accuracy": f"{plan.predicted_accuracy:.1%}",
                "confidence": f"{plan.confidence_score:.1%}",
                "break_count": len(plan.break_intervals),
                "phases": [
                    {
                        "name": phase.phase_name,
                        "duration": phase.duration,
                        "type": phase.phase_type,
                        "difficulty": phase.difficulty_target
                    }
                    for phase in plan.session_phases
                ]
            }
        except Exception as e:
            self.logger.error(f"Error generating plan summary: {e}")
            return {"error": "Unable to generate plan summary"}
