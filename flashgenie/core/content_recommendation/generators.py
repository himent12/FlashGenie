"""
Content suggestion generators for the recommendation system.

This module provides functions to generate specific types of content suggestions.
"""

from typing import List, Set, Dict, Any
from ..content_system.deck import Deck
from .models import (
    CardSuggestion, TopicSuggestion, ContentGap, ContentSource
)


class SuggestionGenerator:
    """Generates various types of content suggestions."""
    
    def __init__(self):
        """Initialize the suggestion generator."""
        self.basic_question_patterns = [
            "What is {topic}?",
            "Define {topic}",
            "What are the key characteristics of {topic}?",
            "Why is {topic} important?",
            "What are the basic principles of {topic}?"
        ]
        
        self.intermediate_patterns = [
            "How does {topic} work?",
            "What are the applications of {topic}?",
            "Compare {topic} with related concepts",
            "What are the advantages and disadvantages of {topic}?",
            "How is {topic} used in practice?"
        ]
        
        self.advanced_patterns = [
            "Analyze the implications of {topic}",
            "Evaluate the effectiveness of {topic}",
            "What are the limitations of {topic}?",
            "How might {topic} evolve in the future?",
            "What are the ethical considerations of {topic}?"
        ]
    
    def suggest_basic_cards(self, gap: ContentGap, deck: Deck) -> List[CardSuggestion]:
        """
        Suggest basic cards for a topic.
        
        Args:
            gap: The content gap to address
            deck: The current deck
            
        Returns:
            List of basic card suggestions
        """
        suggestions = []
        topic = list(gap.affected_tags)[0]
        
        # Generate basic question patterns
        for pattern in self.basic_question_patterns[:2]:  # Limit to 2 suggestions per gap
            question = pattern.format(topic=topic)
            suggestion = CardSuggestion(
                suggested_question=question,
                suggested_answer=f"[Basic definition/explanation of {topic}]",
                confidence_score=0.7,
                reasoning=f"Basic foundational knowledge needed for {topic}",
                suggested_tags={topic, "basics", "definition"},
                estimated_difficulty=0.2,
                source=ContentSource.PATTERN_ANALYSIS
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def suggest_bridge_cards(self, gap: ContentGap, deck: Deck) -> List[CardSuggestion]:
        """
        Suggest cards to bridge difficulty gaps.
        
        Args:
            gap: The content gap to address
            deck: The current deck
            
        Returns:
            List of bridge card suggestions
        """
        suggestions = []
        topic = list(gap.affected_tags)[0]
        
        # Find the difficulty levels that need bridging
        topic_cards = [card for card in deck.flashcards if topic in card.tags]
        difficulties = sorted([card.difficulty for card in topic_cards])
        
        # Suggest intermediate-level content
        for i in range(len(difficulties) - 1):
            if difficulties[i + 1] - difficulties[i] > 0.3:
                intermediate_difficulty = (difficulties[i] + difficulties[i + 1]) / 2
                
                # Choose appropriate pattern based on difficulty level
                if intermediate_difficulty < 0.5:
                    pattern = self.intermediate_patterns[0]  # "How does {topic} work?"
                else:
                    pattern = self.intermediate_patterns[1]  # "What are the applications of {topic}?"
                
                question = pattern.format(topic=topic)
                suggestion = CardSuggestion(
                    suggested_question=question,
                    suggested_answer=f"[Intermediate-level explanation of {topic}]",
                    confidence_score=0.6,
                    reasoning=f"Bridge content needed between difficulty levels {difficulties[i]:.2f} and {difficulties[i+1]:.2f}",
                    suggested_tags={topic, "intermediate"},
                    estimated_difficulty=intermediate_difficulty,
                    source=ContentSource.DIFFICULTY_PROGRESSION
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def suggest_connecting_cards(self, gap: ContentGap, deck: Deck) -> List[CardSuggestion]:
        """
        Suggest cards to connect isolated topics.
        
        Args:
            gap: The content gap to address
            deck: The current deck
            
        Returns:
            List of connecting card suggestions
        """
        suggestions = []
        topic = list(gap.affected_tags)[0]
        
        # Find related topics in the deck
        all_topics = set()
        for card in deck.flashcards:
            all_topics.update(card.tags)
        
        # Find potential connections (simplified - in real implementation, 
        # this would use a knowledge graph or semantic similarity)
        related_topics = self._find_simple_related_topics(topic, all_topics)
        
        for related_topic in list(related_topics)[:2]:  # Limit to 2 connections
            suggestion = CardSuggestion(
                suggested_question=f"How does {topic} relate to {related_topic}?",
                suggested_answer=f"[Explanation of relationship between {topic} and {related_topic}]",
                confidence_score=0.5,
                reasoning=f"Connect isolated topic {topic} with existing topic {related_topic}",
                suggested_tags={topic, related_topic, "connections"},
                estimated_difficulty=0.5,
                source=ContentSource.KNOWLEDGE_GRAPH
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def suggest_general_cards(self, gap: ContentGap, deck: Deck) -> List[CardSuggestion]:
        """
        Suggest general cards for unspecified gaps.
        
        Args:
            gap: The content gap to address
            deck: The current deck
            
        Returns:
            List of general card suggestions
        """
        suggestions = []
        topic = list(gap.affected_tags)[0]
        
        # Generate a general suggestion
        suggestion = CardSuggestion(
            suggested_question=f"[Question about {topic}]",
            suggested_answer=f"[Answer about {topic}]",
            confidence_score=0.4,
            reasoning=f"General content expansion for {topic}",
            suggested_tags={topic},
            estimated_difficulty=0.5,
            source=ContentSource.PATTERN_ANALYSIS
        )
        suggestions.append(suggestion)
        
        return suggestions
    
    def suggest_related_topics(self, current_topics: Set[str], count: int = 3) -> List[TopicSuggestion]:
        """
        Suggest related topics for expanded learning.
        
        Args:
            current_topics: Set of current topics in the deck
            count: Number of topic suggestions to generate
            
        Returns:
            List of topic suggestions
        """
        suggestions = []
        
        # Simple topic relationship mapping (in real implementation, 
        # this would be more sophisticated)
        topic_relationships = self._get_topic_relationships()
        
        related_topics = {}
        for topic in current_topics:
            if topic in topic_relationships:
                for related, strength in topic_relationships[topic].items():
                    if related not in current_topics:
                        if related not in related_topics:
                            related_topics[related] = 0
                        related_topics[related] += strength
        
        # Create suggestions for top related topics
        sorted_topics = sorted(related_topics.items(), key=lambda x: x[1], reverse=True)
        
        for topic, strength in sorted_topics[:count]:
            suggestion = TopicSuggestion(
                topic_name=topic,
                description=f"Related to your current studies in {', '.join(list(current_topics)[:3])}",
                confidence_score=min(strength, 1.0),
                reasoning=f"Strong relationship with existing topics (strength: {strength:.2f})",
                suggested_tags={topic},
                estimated_card_count=self._estimate_topic_card_count(topic),
                priority_score=strength,
                source=ContentSource.KNOWLEDGE_GRAPH
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def suggest_prerequisite_topics(self, gap: Dict[str, Any], deck: Deck) -> List[TopicSuggestion]:
        """
        Suggest prerequisite topics for a difficulty gap.
        
        Args:
            gap: The difficulty gap information
            deck: The current deck
            
        Returns:
            List of prerequisite topic suggestions
        """
        suggestions = []
        
        # Find topics that might need prerequisites
        high_difficulty_cards = [
            card for card in deck.flashcards 
            if card.difficulty >= gap.get("start", 0.7)
        ]
        
        # Extract topics from high-difficulty cards
        high_difficulty_topics = set()
        for card in high_difficulty_cards:
            high_difficulty_topics.update(card.tags)
        
        # Suggest prerequisites for these topics
        prerequisite_map = self._get_prerequisite_map()
        
        for topic in high_difficulty_topics:
            if topic in prerequisite_map:
                for prereq in prerequisite_map[topic]:
                    # Check if prerequisite is already covered
                    prereq_covered = any(
                        prereq in card.tags for card in deck.flashcards
                    )
                    
                    if not prereq_covered:
                        suggestion = TopicSuggestion(
                            topic_name=prereq,
                            description=f"Prerequisite knowledge for {topic}",
                            confidence_score=0.8,
                            reasoning=f"Required foundation for understanding {topic}",
                            suggested_tags={prereq, "prerequisite"},
                            estimated_card_count=3,
                            priority_score=0.9,
                            source=ContentSource.KNOWLEDGE_GRAPH
                        )
                        suggestions.append(suggestion)
        
        return suggestions
    
    def suggest_prerequisites_for_card(self, card, deck: Deck) -> List[TopicSuggestion]:
        """
        Suggest prerequisites for a specific difficult card.
        
        Args:
            card: The difficult card
            deck: The current deck
            
        Returns:
            List of prerequisite topic suggestions
        """
        suggestions = []
        
        # Simple heuristic: suggest basic versions of the card's topics
        for tag in card.tags:
            basic_topic = f"{tag}_basics"
            
            # Check if basics are already covered
            basics_covered = any(
                basic_topic in existing_card.tags or "basics" in existing_card.tags
                for existing_card in deck.flashcards
                if tag in existing_card.tags
            )
            
            if not basics_covered:
                suggestion = TopicSuggestion(
                    topic_name=basic_topic,
                    description=f"Basic concepts for {tag}",
                    confidence_score=0.7,
                    reasoning=f"Foundation needed for difficult {tag} concepts",
                    suggested_tags={tag, "basics"},
                    estimated_card_count=2,
                    priority_score=0.8,
                    source=ContentSource.DIFFICULTY_PROGRESSION
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _find_simple_related_topics(self, topic: str, all_topics: Set[str]) -> Set[str]:
        """Find topics that might be related to the given topic."""
        related = set()
        
        # Simple heuristic: topics with similar words
        topic_words = set(topic.lower().split())
        
        for other_topic in all_topics:
            if other_topic != topic:
                other_words = set(other_topic.lower().split())
                # If topics share words, they might be related
                if topic_words & other_words:
                    related.add(other_topic)
        
        return related
    
    def _get_topic_relationships(self) -> Dict[str, Dict[str, float]]:
        """Get a simple topic relationship mapping."""
        # This is a simplified example - in practice, this would be loaded from
        # a knowledge base or learned from data
        return {
            "python": {"programming": 0.9, "algorithms": 0.7, "data_structures": 0.8},
            "programming": {"python": 0.9, "java": 0.8, "algorithms": 0.9},
            "algorithms": {"programming": 0.9, "data_structures": 0.9, "complexity": 0.8},
            "mathematics": {"algebra": 0.8, "calculus": 0.7, "statistics": 0.6},
            "biology": {"chemistry": 0.7, "genetics": 0.8, "ecology": 0.6},
        }
    
    def _get_prerequisite_map(self) -> Dict[str, List[str]]:
        """Get a mapping of topics to their prerequisites."""
        return {
            "calculus": ["algebra", "trigonometry"],
            "algorithms": ["programming", "mathematics"],
            "machine_learning": ["statistics", "programming", "linear_algebra"],
            "organic_chemistry": ["general_chemistry", "atomic_structure"],
            "genetics": ["biology", "chemistry"],
        }
    
    def _estimate_topic_card_count(self, topic: str) -> int:
        """Estimate how many cards a topic might need."""
        # Simple heuristic based on topic complexity
        complex_topics = ["machine_learning", "quantum_physics", "organic_chemistry"]
        medium_topics = ["programming", "calculus", "biology"]
        
        if topic in complex_topics:
            return 10
        elif topic in medium_topics:
            return 6
        else:
            return 3
