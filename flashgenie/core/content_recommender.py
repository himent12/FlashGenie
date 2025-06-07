"""
Content Recommender for FlashGenie.

This module provides the main ContentRecommender class that serves as the
public interface for content recommendation functionality.
"""

from typing import List, Dict, Optional, Set, Any

from .content_system.deck import Deck
from .content_system.tag_manager import TagManager
from .content_recommendation.engine import ContentRecommender as Engine
from .content_recommendation.models import (
    CardSuggestion, TopicSuggestion, ContentGap, LearningGoals, 
    RecommendationContext, StudyPhase
)


class ContentRecommender:
    """
    Main interface for content recommendation functionality.
    
    This class provides a simplified interface to the content recommendation
    system while maintaining backward compatibility.
    """
    
    def __init__(self, tag_manager: TagManager, data_path: Optional[str] = None):
        """
        Initialize the content recommender.
        
        Args:
            tag_manager: Tag manager for handling tag relationships
            data_path: Optional path for storing recommendation data
        """
        self.engine = Engine(tag_manager, data_path)
    
    def suggest_cards(
        self, 
        deck: Deck, 
        count: int = 5,
        focus_areas: Optional[Set[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest new flashcards based on existing content and gaps.
        
        Args:
            deck: The current deck
            count: Number of suggestions to generate
            focus_areas: Optional specific areas to focus on
            
        Returns:
            List of card suggestions as dictionaries
        """
        context = None
        if focus_areas:
            context = RecommendationContext(focus_areas=focus_areas)
        
        suggestions = self.engine.suggest_cards(deck, count, context)
        
        # Convert to dictionary format for backward compatibility
        return [
            {
                "question": s.suggested_question,
                "answer": s.suggested_answer,
                "confidence": s.confidence_score,
                "reason": s.reasoning,
                "tags": list(s.suggested_tags),
                "difficulty": s.estimated_difficulty,
                "source": s.source.value
            }
            for s in suggestions
        ]
    
    def suggest_topics(self, deck: Deck, count: int = 3) -> List[Dict[str, Any]]:
        """
        Suggest related topics for expanded learning.
        
        Args:
            deck: The current deck
            count: Number of topic suggestions
            
        Returns:
            List of topic suggestions as dictionaries
        """
        suggestions = self.engine.suggest_topics(deck, count)
        
        # Convert to dictionary format for backward compatibility
        return [
            {
                "name": s.topic_name,
                "description": s.description,
                "confidence": s.confidence_score,
                "reason": s.reasoning,
                "tags": list(s.suggested_tags),
                "estimated_cards": s.estimated_card_count,
                "priority": s.priority_score,
                "source": s.source.value
            }
            for s in suggestions
        ]
    
    def identify_content_gaps(self, deck: Deck) -> List[Dict[str, Any]]:
        """
        Identify gaps in content coverage.
        
        Args:
            deck: The deck to analyze
            
        Returns:
            List of identified content gaps as dictionaries
        """
        gaps = self.engine.identify_content_gaps(deck)
        
        # Convert to dictionary format for backward compatibility
        return [
            {
                "type": gap.gap_type,
                "description": gap.description,
                "severity": gap.severity,
                "affected_tags": list(gap.affected_tags),
                "suggested_actions": gap.suggested_actions,
                "related_cards": gap.related_cards
            }
            for gap in gaps
        ]
    
    def get_study_recommendations(self, deck: Deck) -> Dict[str, Any]:
        """
        Get comprehensive study recommendations for a deck.
        
        Args:
            deck: The deck to analyze
            
        Returns:
            Dictionary with various recommendations
        """
        # Get card suggestions
        card_suggestions = self.suggest_cards(deck, 5)
        
        # Get topic suggestions
        topic_suggestions = self.suggest_topics(deck, 3)
        
        # Get content gaps
        content_gaps = self.identify_content_gaps(deck)
        
        # Get study sequence
        study_phases = self.engine.recommend_study_sequence(deck)
        study_sequence = [
            {
                "phase": phase.phase,
                "description": phase.description,
                "topics": phase.topics,
                "duration": phase.estimated_duration,
                "focus": phase.focus,
                "priority": phase.priority
            }
            for phase in study_phases
        ]
        
        # Get prerequisite gaps
        prerequisite_suggestions = self.engine.identify_prerequisite_gaps(deck)
        prerequisites = [
            {
                "name": s.topic_name,
                "description": s.description,
                "confidence": s.confidence_score,
                "reason": s.reasoning,
                "estimated_cards": s.estimated_card_count,
                "priority": s.priority_score
            }
            for s in prerequisite_suggestions
        ]
        
        return {
            "card_suggestions": card_suggestions,
            "topic_suggestions": topic_suggestions,
            "content_gaps": content_gaps,
            "study_sequence": study_sequence,
            "prerequisites": prerequisites,
            "summary": {
                "total_suggestions": len(card_suggestions),
                "gaps_identified": len(content_gaps),
                "study_phases": len(study_sequence),
                "prerequisites_needed": len(prerequisites)
            }
        }
    
    def set_learning_goals(
        self,
        target_topics: Optional[Set[str]] = None,
        difficulty_preference: float = 0.5,
        learning_pace: str = "moderate",
        focus_areas: Optional[Set[str]] = None,
        avoid_topics: Optional[Set[str]] = None,
        time_constraints: Optional[int] = None
    ) -> None:
        """
        Set user learning goals and preferences.
        
        Args:
            target_topics: Topics the user wants to focus on
            difficulty_preference: Preferred difficulty level (0.0 = easy, 1.0 = hard)
            learning_pace: Learning pace (slow, moderate, fast)
            focus_areas: Areas to focus recommendations on
            avoid_topics: Topics to avoid in recommendations
            time_constraints: Daily time available for study (minutes)
        """
        goals = LearningGoals(
            target_topics=target_topics or set(),
            difficulty_preference=difficulty_preference,
            learning_pace=learning_pace,
            focus_areas=focus_areas or set(),
            avoid_topics=avoid_topics or set(),
            time_constraints=time_constraints
        )
        
        self.engine.save_learning_goals(goals)
    
    def get_learning_goals(self) -> Optional[Dict[str, Any]]:
        """
        Get current learning goals.
        
        Returns:
            Dictionary with current learning goals or None
        """
        goals = self.engine.learning_goals
        if goals:
            return {
                "target_topics": list(goals.target_topics),
                "difficulty_preference": goals.difficulty_preference,
                "learning_pace": goals.learning_pace,
                "focus_areas": list(goals.focus_areas),
                "avoid_topics": list(goals.avoid_topics),
                "time_constraints": goals.time_constraints
            }
        return None
    
    def analyze_deck_content(self, deck: Deck) -> Dict[str, Any]:
        """
        Analyze deck content and provide insights.
        
        Args:
            deck: The deck to analyze
            
        Returns:
            Dictionary with content analysis results
        """
        analysis = self.engine.analyzer.analyze_deck_content(deck)
        
        return {
            "total_cards": analysis.total_cards,
            "topics": list(analysis.topics),
            "difficulty_distribution": analysis.difficulty_distribution,
            "tag_frequency": analysis.tag_frequency,
            "mastery_levels": analysis.mastery_levels,
            "insights": {
                "most_common_topics": sorted(
                    analysis.tag_frequency.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:5],
                "difficulty_range": {
                    "min": analysis.difficulty_distribution.get("min", 0),
                    "max": analysis.difficulty_distribution.get("max", 1),
                    "average": analysis.difficulty_distribution.get("mean", 0.5)
                },
                "topic_count": len(analysis.topics),
                "coverage_assessment": self._assess_coverage(analysis)
            }
        }
    
    def _assess_coverage(self, analysis) -> str:
        """Assess the coverage quality of the deck."""
        if analysis.total_cards < 10:
            return "Limited - Consider adding more cards"
        elif len(analysis.topics) < 3:
            return "Narrow - Consider expanding topic coverage"
        elif analysis.difficulty_distribution.get("std", 0) < 0.1:
            return "Uniform - Good difficulty distribution"
        elif analysis.difficulty_distribution.get("std", 0) > 0.3:
            return "Varied - Wide range of difficulties"
        else:
            return "Balanced - Good overall coverage"
