"""
Main content recommendation engine.

This module provides the main ContentRecommender class that coordinates
all content recommendation functionality.
"""

from typing import List, Dict, Optional, Set, Any
from pathlib import Path
import json

from ..content_system.deck import Deck
from ..content_system.tag_manager import TagManager
from .models import (
    CardSuggestion, TopicSuggestion, ContentGap, LearningGoals, 
    RecommendationContext, StudyPhase
)
from .analyzers import ContentAnalyzer
from .generators import SuggestionGenerator


class ContentRecommender:
    """
    Main content recommendation engine.
    
    This class coordinates content analysis and suggestion generation to provide
    intelligent recommendations for flashcard content.
    """
    
    def __init__(self, tag_manager: TagManager, data_path: Optional[str] = None):
        """
        Initialize the content recommender.
        
        Args:
            tag_manager: Tag manager for handling tag relationships
            data_path: Optional path for storing recommendation data
        """
        self.tag_manager = tag_manager
        self.data_path = Path(data_path or "data/content_recommendations")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.analyzer = ContentAnalyzer()
        self.generator = SuggestionGenerator()
        
        # Load user preferences and history
        self.learning_goals = self._load_learning_goals()
        self.suggestion_history: List[Dict[str, Any]] = []
    
    def suggest_cards(
        self, 
        deck: Deck, 
        count: int = 5,
        context: Optional[RecommendationContext] = None
    ) -> List[CardSuggestion]:
        """
        Suggest new flashcards based on existing content and gaps.
        
        Args:
            deck: The current deck
            count: Number of suggestions to generate
            context: Optional context for recommendations
            
        Returns:
            List of card suggestions
        """
        # Analyze existing content
        content_analysis = self.analyzer.analyze_deck_content(deck)
        
        # Identify content gaps
        gaps = self.analyzer.identify_content_gaps(deck, content_analysis)
        
        # Generate suggestions for each gap type
        suggestions = []
        for gap in gaps[:count]:
            if gap.gap_type == "missing_basics":
                card_suggestions = self.generator.suggest_basic_cards(gap, deck)
            elif gap.gap_type == "difficulty_jump":
                card_suggestions = self.generator.suggest_bridge_cards(gap, deck)
            elif gap.gap_type == "isolated_topic":
                card_suggestions = self.generator.suggest_connecting_cards(gap, deck)
            else:
                card_suggestions = self.generator.suggest_general_cards(gap, deck)
            
            suggestions.extend(card_suggestions)
        
        # Filter and rank suggestions
        filtered_suggestions = self._filter_suggestions(suggestions, deck, context)
        ranked_suggestions = self._rank_suggestions(filtered_suggestions, deck, context)
        
        # Record suggestions in history
        self._record_suggestions(ranked_suggestions[:count])
        
        return ranked_suggestions[:count]
    
    def suggest_topics(
        self, 
        deck: Deck, 
        count: int = 3,
        context: Optional[RecommendationContext] = None
    ) -> List[TopicSuggestion]:
        """
        Suggest related topics for expanded learning.
        
        Args:
            deck: The current deck
            count: Number of topic suggestions
            context: Optional context for recommendations
            
        Returns:
            List of topic suggestions
        """
        # Get current topics from deck
        current_topics = set()
        for card in deck.flashcards:
            current_topics.update(card.tags)
        
        # Generate topic suggestions
        suggestions = self.generator.suggest_related_topics(current_topics, count)
        
        # Apply context filtering if provided
        if context and context.focus_areas:
            suggestions = [
                s for s in suggestions 
                if any(area in s.suggested_tags for area in context.focus_areas)
            ]
        
        return suggestions[:count]
    
    def identify_content_gaps(self, deck: Deck) -> List[ContentGap]:
        """
        Identify gaps in content coverage.
        
        Args:
            deck: The deck to analyze
            
        Returns:
            List of identified content gaps
        """
        content_analysis = self.analyzer.analyze_deck_content(deck)
        return self.analyzer.identify_content_gaps(deck, content_analysis)
    
    def identify_prerequisite_gaps(self, deck: Deck) -> List[TopicSuggestion]:
        """
        Identify missing prerequisite knowledge.
        
        Args:
            deck: The current deck
            
        Returns:
            List of prerequisite topic suggestions
        """
        prerequisites = []
        
        # Analyze difficulty distribution
        difficulty_analysis = self.analyzer.analyze_difficulty_distribution(deck)
        
        # Check for difficulty jumps that might indicate missing prerequisites
        if difficulty_analysis["has_difficulty_gaps"]:
            for gap in difficulty_analysis["gaps"]:
                prereq_topics = self.generator.suggest_prerequisite_topics(gap, deck)
                prerequisites.extend(prereq_topics)
        
        # Check for isolated high-difficulty cards
        isolated_cards = self.analyzer.find_isolated_difficult_cards(deck)
        for card in isolated_cards:
            prereq_topics = self.generator.suggest_prerequisites_for_card(card, deck)
            prerequisites.extend(prereq_topics)
        
        return prerequisites
    
    def recommend_study_sequence(self, deck: Deck) -> List[StudyPhase]:
        """
        Recommend an optimal study sequence for the deck.
        
        Args:
            deck: The deck to analyze
            
        Returns:
            List of study phases with recommended focus
        """
        # Analyze current mastery levels by topic
        topic_mastery = self.analyzer.analyze_topic_mastery(deck)
        
        # Create study phases
        phases = []
        
        # Phase 1: Foundation topics (low mastery, low difficulty)
        foundation_topics = [
            topic for topic, data in topic_mastery.items()
            if data["mastery_level"] < 0.3 and data["avg_difficulty"] < 0.5
        ]
        
        if foundation_topics:
            phases.append(StudyPhase(
                phase="Foundation",
                description="Build strong foundations in basic concepts",
                topics=foundation_topics,
                estimated_duration=len(foundation_topics) * 3,  # 3 days per topic
                focus="accuracy and understanding",
                priority=1
            ))
        
        # Phase 2: Core topics (medium mastery, medium difficulty)
        core_topics = [
            topic for topic, data in topic_mastery.items()
            if 0.3 <= data["mastery_level"] < 0.7 and 0.3 <= data["avg_difficulty"] < 0.7
        ]
        
        if core_topics:
            phases.append(StudyPhase(
                phase="Core Development",
                description="Develop proficiency in main topics",
                topics=core_topics,
                estimated_duration=len(core_topics) * 5,  # 5 days per topic
                focus="consistency and application",
                priority=2
            ))
        
        # Phase 3: Advanced topics (any mastery, high difficulty)
        advanced_topics = [
            topic for topic, data in topic_mastery.items()
            if data["avg_difficulty"] >= 0.7
        ]
        
        if advanced_topics:
            phases.append(StudyPhase(
                phase="Advanced Mastery",
                description="Master challenging concepts",
                topics=advanced_topics,
                estimated_duration=len(advanced_topics) * 7,  # 7 days per topic
                focus="deep understanding and retention",
                priority=3
            ))
        
        return phases
    
    def _filter_suggestions(
        self, 
        suggestions: List[CardSuggestion], 
        deck: Deck,
        context: Optional[RecommendationContext] = None
    ) -> List[CardSuggestion]:
        """Filter suggestions based on context and preferences."""
        filtered = []
        
        for suggestion in suggestions:
            # Skip if suggestion is too similar to existing cards
            if self._is_duplicate_suggestion(suggestion, deck):
                continue
            
            # Apply context filters
            if context:
                if context.focus_areas and not (suggestion.suggested_tags & context.focus_areas):
                    continue
                
                if context.difficulty_preference:
                    # Filter by difficulty preference
                    difficulty_diff = abs(suggestion.estimated_difficulty - context.difficulty_preference)
                    if difficulty_diff > 0.4:  # Too far from preferred difficulty
                        continue
            
            # Apply learning goals
            if self.learning_goals:
                if self.learning_goals.avoid_topics & suggestion.suggested_tags:
                    continue
                
                if (self.learning_goals.target_topics and 
                    not (self.learning_goals.target_topics & suggestion.suggested_tags)):
                    continue
            
            filtered.append(suggestion)
        
        return filtered
    
    def _rank_suggestions(
        self, 
        suggestions: List[CardSuggestion], 
        deck: Deck,
        context: Optional[RecommendationContext] = None
    ) -> List[CardSuggestion]:
        """Rank suggestions by relevance and quality."""
        def score_suggestion(suggestion: CardSuggestion) -> float:
            score = suggestion.confidence_score
            
            # Boost score for focus areas
            if context and context.focus_areas:
                if suggestion.suggested_tags & context.focus_areas:
                    score += 0.2
            
            # Boost score for target topics
            if self.learning_goals and self.learning_goals.target_topics:
                if suggestion.suggested_tags & self.learning_goals.target_topics:
                    score += 0.3
            
            # Adjust for difficulty preference
            if context and context.difficulty_preference:
                difficulty_match = 1 - abs(suggestion.estimated_difficulty - context.difficulty_preference)
                score *= difficulty_match
            
            return score
        
        # Sort by score (descending)
        suggestions.sort(key=score_suggestion, reverse=True)
        return suggestions
    
    def _is_duplicate_suggestion(self, suggestion: CardSuggestion, deck: Deck) -> bool:
        """Check if suggestion is too similar to existing cards."""
        for card in deck.flashcards:
            # Simple similarity check based on question text
            if suggestion.suggested_question.lower() in card.question.lower():
                return True
            if card.question.lower() in suggestion.suggested_question.lower():
                return True
        return False
    
    def _record_suggestions(self, suggestions: List[CardSuggestion]) -> None:
        """Record suggestions in history for learning."""
        for suggestion in suggestions:
            self.suggestion_history.append({
                "timestamp": "now",  # In real implementation, use datetime
                "question": suggestion.suggested_question,
                "tags": list(suggestion.suggested_tags),
                "confidence": suggestion.confidence_score,
                "source": suggestion.source.value
            })
    
    def _load_learning_goals(self) -> Optional[LearningGoals]:
        """Load user learning goals from storage."""
        goals_file = self.data_path / "learning_goals.json"
        if goals_file.exists():
            try:
                with open(goals_file, 'r') as f:
                    data = json.load(f)
                return LearningGoals(
                    target_topics=set(data.get("target_topics", [])),
                    difficulty_preference=data.get("difficulty_preference", 0.5),
                    learning_pace=data.get("learning_pace", "moderate"),
                    focus_areas=set(data.get("focus_areas", [])),
                    avoid_topics=set(data.get("avoid_topics", [])),
                    time_constraints=data.get("time_constraints")
                )
            except (json.JSONDecodeError, KeyError):
                pass
        
        return None
    
    def save_learning_goals(self, goals: LearningGoals) -> None:
        """Save user learning goals to storage."""
        goals_file = self.data_path / "learning_goals.json"
        data = {
            "target_topics": list(goals.target_topics),
            "difficulty_preference": goals.difficulty_preference,
            "learning_pace": goals.learning_pace,
            "focus_areas": list(goals.focus_areas),
            "avoid_topics": list(goals.avoid_topics),
            "time_constraints": goals.time_constraints
        }
        
        with open(goals_file, 'w') as f:
            json.dump(data, f, indent=2)
