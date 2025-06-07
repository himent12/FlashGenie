"""
Intelligent Content Recommender for FlashGenie v1.5

This module implements AI-powered content suggestions that recommend new flashcards,
identify content gaps, and suggest study materials based on learning patterns.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import math
from pathlib import Path
from collections import Counter

from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck
from flashgenie.core.tag_manager import TagManager


class SuggestionType(Enum):
    """Types of content suggestions."""
    NEW_CARD = "new_card"  # Suggest new flashcard content
    RELATED_TOPIC = "related_topic"  # Suggest related topics to study
    PREREQUISITE = "prerequisite"  # Suggest prerequisite knowledge
    ADVANCED = "advanced"  # Suggest advanced topics
    REVIEW = "review"  # Suggest cards for review
    WEAK_AREA = "weak_area"  # Suggest focus on weak areas


class ContentSource(Enum):
    """Sources for content suggestions."""
    PATTERN_ANALYSIS = "pattern_analysis"  # Based on existing content patterns
    KNOWLEDGE_GRAPH = "knowledge_graph"  # Based on knowledge relationships
    DIFFICULTY_PROGRESSION = "difficulty_progression"  # Based on difficulty gaps
    USER_PERFORMANCE = "user_performance"  # Based on performance analysis
    EXTERNAL_RESOURCES = "external_resources"  # From external knowledge bases


@dataclass
class CardSuggestion:
    """A suggestion for a new flashcard."""
    suggested_question: str
    suggested_answer: str
    confidence_score: float  # 0.0 to 1.0
    reasoning: str
    suggested_tags: Set[str]
    estimated_difficulty: float
    source: ContentSource
    related_cards: List[str] = field(default_factory=list)  # Related card IDs
    
    def generate_card(self) -> Flashcard:
        """Generate a flashcard from this suggestion."""
        return Flashcard(
            question=self.suggested_question,
            answer=self.suggested_answer,
            tags=self.suggested_tags,
            difficulty=self.estimated_difficulty
        )


@dataclass
class TopicSuggestion:
    """A suggestion for a topic to study."""
    topic_name: str
    description: str
    confidence_score: float
    reasoning: str
    suggested_tags: Set[str]
    estimated_card_count: int
    priority_score: float  # Higher = more important
    source: ContentSource


@dataclass
class ContentGap:
    """An identified gap in content coverage."""
    gap_type: str  # "missing_basics", "difficulty_jump", "isolated_topic"
    description: str
    severity: float  # 0.0 to 1.0
    affected_tags: Set[str]
    suggested_actions: List[str]
    related_cards: List[str] = field(default_factory=list)


@dataclass
class LearningGoals:
    """User's learning goals and preferences."""
    target_topics: Set[str] = field(default_factory=set)
    difficulty_preference: float = 0.5  # 0.0 = easy, 1.0 = hard
    learning_pace: str = "moderate"  # slow, moderate, fast
    focus_areas: Set[str] = field(default_factory=set)
    avoid_topics: Set[str] = field(default_factory=set)
    time_constraints: Optional[int] = None  # minutes per day


class ContentRecommendationEngine:
    """
    AI-powered content recommendation system.
    
    This engine analyzes existing content and learning patterns to:
    - Suggest new flashcards to fill knowledge gaps
    - Recommend related topics for expanded learning
    - Identify prerequisite knowledge that's missing
    - Suggest optimal difficulty progression
    - Recommend external resources and materials
    """
    
    def __init__(self, tag_manager: TagManager, data_path: Optional[str] = None):
        self.tag_manager = tag_manager
        self.data_path = Path(data_path or "data/content_recommendations")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Knowledge bases and patterns
        self.content_patterns = self._load_content_patterns()
        self.topic_relationships = self._load_topic_relationships()
        self.difficulty_progressions = self._load_difficulty_progressions()
        
        # User preferences
        self.learning_goals = self._load_learning_goals()
        
        # Suggestion history
        self.suggestion_history: List[Dict[str, Any]] = []
    
    def suggest_new_cards(
        self, 
        deck: Deck, 
        count: int = 5,
        focus_areas: Optional[Set[str]] = None
    ) -> List[CardSuggestion]:
        """
        Suggest new flashcards based on existing content and gaps.
        
        Args:
            deck: The current deck
            count: Number of suggestions to generate
            focus_areas: Optional specific areas to focus on
            
        Returns:
            List of card suggestions
        """
        suggestions = []
        
        # Analyze existing content
        content_analysis = self._analyze_deck_content(deck)
        
        # Identify content gaps
        gaps = self._identify_content_gaps(deck, content_analysis)
        
        # Generate suggestions for each gap type
        for gap in gaps[:count]:
            if gap.gap_type == "missing_basics":
                card_suggestions = self._suggest_basic_cards(gap, deck)
            elif gap.gap_type == "difficulty_jump":
                card_suggestions = self._suggest_bridge_cards(gap, deck)
            elif gap.gap_type == "isolated_topic":
                card_suggestions = self._suggest_connecting_cards(gap, deck)
            else:
                card_suggestions = self._suggest_general_cards(gap, deck)
            
            suggestions.extend(card_suggestions)
        
        # Filter and rank suggestions
        filtered_suggestions = self._filter_suggestions(suggestions, deck, focus_areas)
        ranked_suggestions = self._rank_suggestions(filtered_suggestions, deck)
        
        return ranked_suggestions[:count]
    
    def suggest_related_topics(
        self, 
        deck: Deck, 
        count: int = 3
    ) -> List[TopicSuggestion]:
        """
        Suggest related topics for expanded learning.
        
        Args:
            deck: The current deck
            count: Number of topic suggestions
            
        Returns:
            List of topic suggestions
        """
        # Get current topics from deck
        current_topics = set()
        for card in deck.flashcards:
            current_topics.update(card.tags)
        
        # Find related topics
        related_topics = self._find_related_topics(current_topics)
        
        # Score and rank topics
        topic_suggestions = []
        for topic, relationship_strength in related_topics.items():
            if topic not in current_topics:
                suggestion = TopicSuggestion(
                    topic_name=topic,
                    description=f"Related to your current studies in {', '.join(list(current_topics)[:3])}",
                    confidence_score=relationship_strength,
                    reasoning=f"Strong relationship with existing topics (strength: {relationship_strength:.2f})",
                    suggested_tags={topic},
                    estimated_card_count=self._estimate_topic_card_count(topic),
                    priority_score=relationship_strength,
                    source=ContentSource.KNOWLEDGE_GRAPH
                )
                topic_suggestions.append(suggestion)
        
        # Sort by priority and return top suggestions
        topic_suggestions.sort(key=lambda x: x.priority_score, reverse=True)
        return topic_suggestions[:count]
    
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
        difficulty_analysis = self._analyze_difficulty_distribution(deck)
        
        # Check for difficulty jumps that might indicate missing prerequisites
        if difficulty_analysis["has_difficulty_gaps"]:
            for gap in difficulty_analysis["gaps"]:
                prereq_topics = self._suggest_prerequisite_topics(gap, deck)
                prerequisites.extend(prereq_topics)
        
        # Check for isolated high-difficulty cards
        isolated_cards = self._find_isolated_difficult_cards(deck)
        for card in isolated_cards:
            prereq_topics = self._suggest_prerequisites_for_card(card, deck)
            prerequisites.extend(prereq_topics)
        
        return prerequisites
    
    def recommend_study_sequence(self, deck: Deck) -> List[Dict[str, Any]]:
        """
        Recommend an optimal study sequence for the deck.
        
        Args:
            deck: The deck to analyze
            
        Returns:
            List of study phases with recommended focus
        """
        # Analyze current mastery levels by topic
        topic_mastery = self._analyze_topic_mastery(deck)
        
        # Create study phases
        phases = []
        
        # Phase 1: Foundation topics (low mastery, low difficulty)
        foundation_topics = [
            topic for topic, data in topic_mastery.items()
            if data["mastery_level"] < 0.3 and data["avg_difficulty"] < 0.5
        ]
        
        if foundation_topics:
            phases.append({
                "phase": "Foundation",
                "description": "Build strong foundations in basic concepts",
                "topics": foundation_topics,
                "estimated_duration": len(foundation_topics) * 3,  # 3 days per topic
                "focus": "accuracy and understanding"
            })
        
        # Phase 2: Core topics (medium mastery, medium difficulty)
        core_topics = [
            topic for topic, data in topic_mastery.items()
            if 0.3 <= data["mastery_level"] < 0.7 and 0.3 <= data["avg_difficulty"] < 0.7
        ]
        
        if core_topics:
            phases.append({
                "phase": "Core Development",
                "description": "Develop proficiency in main topics",
                "topics": core_topics,
                "estimated_duration": len(core_topics) * 5,  # 5 days per topic
                "focus": "consistency and application"
            })
        
        # Phase 3: Advanced topics (any mastery, high difficulty)
        advanced_topics = [
            topic for topic, data in topic_mastery.items()
            if data["avg_difficulty"] >= 0.7
        ]
        
        if advanced_topics:
            phases.append({
                "phase": "Advanced Mastery",
                "description": "Master challenging concepts",
                "topics": advanced_topics,
                "estimated_duration": len(advanced_topics) * 7,  # 7 days per topic
                "focus": "deep understanding and retention"
            })
        
        return phases
    
    def _analyze_deck_content(self, deck: Deck) -> Dict[str, Any]:
        """Analyze the content structure of a deck."""
        analysis = {
            "total_cards": len(deck.flashcards),
            "topics": set(),
            "difficulty_distribution": {},
            "tag_frequency": Counter(),
            "content_patterns": {},
            "mastery_levels": {}
        }
        
        # Collect basic statistics
        difficulties = []
        for card in deck.flashcards:
            analysis["topics"].update(card.tags)
            analysis["tag_frequency"].update(card.tags)
            difficulties.append(card.difficulty)
        
        # Difficulty distribution
        if difficulties:
            analysis["difficulty_distribution"] = {
                "mean": sum(difficulties) / len(difficulties),
                "min": min(difficulties),
                "max": max(difficulties),
                "std": self._calculate_std(difficulties)
            }
        
        # Content patterns (simplified)
        analysis["content_patterns"] = self._extract_content_patterns(deck)
        
        return analysis
    
    def _identify_content_gaps(self, deck: Deck, analysis: Dict[str, Any]) -> List[ContentGap]:
        """Identify gaps in content coverage."""
        gaps = []
        
        # Check for missing basic concepts
        basic_gaps = self._find_missing_basics(deck, analysis)
        gaps.extend(basic_gaps)
        
        # Check for difficulty jumps
        difficulty_gaps = self._find_difficulty_jumps(deck, analysis)
        gaps.extend(difficulty_gaps)
        
        # Check for isolated topics
        isolation_gaps = self._find_isolated_topics(deck, analysis)
        gaps.extend(isolation_gaps)
        
        return gaps
    
    def _find_missing_basics(self, deck: Deck, analysis: Dict[str, Any]) -> List[ContentGap]:
        """Find missing basic concepts."""
        gaps = []
        
        # Look for topics with only high-difficulty cards
        for topic in analysis["topics"]:
            topic_cards = [card for card in deck.flashcards if topic in card.tags]
            if topic_cards:
                avg_difficulty = sum(card.difficulty for card in topic_cards) / len(topic_cards)
                if avg_difficulty > 0.7 and len(topic_cards) < 5:
                    gap = ContentGap(
                        gap_type="missing_basics",
                        description=f"Topic '{topic}' lacks basic/introductory content",
                        severity=0.8,
                        affected_tags={topic},
                        suggested_actions=[
                            f"Add basic concepts for {topic}",
                            f"Create introductory cards for {topic}",
                            f"Review fundamentals of {topic}"
                        ]
                    )
                    gaps.append(gap)
        
        return gaps
    
    def _find_difficulty_jumps(self, deck: Deck, analysis: Dict[str, Any]) -> List[ContentGap]:
        """Find difficulty jumps that need bridging content."""
        gaps = []
        
        # Group cards by topic and analyze difficulty progression
        for topic in analysis["topics"]:
            topic_cards = [card for card in deck.flashcards if topic in card.tags]
            if len(topic_cards) >= 3:
                difficulties = sorted([card.difficulty for card in topic_cards])
                
                # Look for large gaps in difficulty
                for i in range(len(difficulties) - 1):
                    gap_size = difficulties[i + 1] - difficulties[i]
                    if gap_size > 0.3:  # Significant difficulty jump
                        gap = ContentGap(
                            gap_type="difficulty_jump",
                            description=f"Large difficulty jump in '{topic}' from {difficulties[i]:.2f} to {difficulties[i+1]:.2f}",
                            severity=gap_size,
                            affected_tags={topic},
                            suggested_actions=[
                                f"Add intermediate-level cards for {topic}",
                                f"Create bridge content between difficulty levels",
                                f"Break down complex concepts into smaller steps"
                            ]
                        )
                        gaps.append(gap)
        
        return gaps
    
    def _find_isolated_topics(self, deck: Deck, analysis: Dict[str, Any]) -> List[ContentGap]:
        """Find topics that are isolated from others."""
        gaps = []
        
        # Find topics with very few cards
        for topic, count in analysis["tag_frequency"].items():
            if count <= 2:  # Very few cards for this topic
                gap = ContentGap(
                    gap_type="isolated_topic",
                    description=f"Topic '{topic}' has insufficient content ({count} cards)",
                    severity=0.6,
                    affected_tags={topic},
                    suggested_actions=[
                        f"Expand content for {topic}",
                        f"Add more examples and variations for {topic}",
                        f"Connect {topic} to related concepts"
                    ]
                )
                gaps.append(gap)
        
        return gaps
    
    def _suggest_basic_cards(self, gap: ContentGap, deck: Deck) -> List[CardSuggestion]:
        """Suggest basic cards for a topic."""
        suggestions = []
        topic = list(gap.affected_tags)[0]
        
        # Generate basic question patterns
        basic_patterns = [
            f"What is {topic}?",
            f"Define {topic}",
            f"What are the key characteristics of {topic}?",
            f"Why is {topic} important?",
            f"What are the basic principles of {topic}?"
        ]
        
        for pattern in basic_patterns[:2]:  # Limit to 2 suggestions per gap
            suggestion = CardSuggestion(
                suggested_question=pattern,
                suggested_answer=f"[Basic definition/explanation of {topic}]",
                confidence_score=0.7,
                reasoning=f"Basic foundational knowledge needed for {topic}",
                suggested_tags={topic, "basics", "definition"},
                estimated_difficulty=0.2,
                source=ContentSource.PATTERN_ANALYSIS
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def _suggest_bridge_cards(self, gap: ContentGap, deck: Deck) -> List[CardSuggestion]:
        """Suggest cards to bridge difficulty gaps."""
        suggestions = []
        topic = list(gap.affected_tags)[0]
        
        # Find the difficulty levels that need bridging
        topic_cards = [card for card in deck.flashcards if topic in card.tags]
        difficulties = sorted([card.difficulty for card in topic_cards])
        
        # Suggest intermediate-level content
        for i in range(len(difficulties) - 1):
            if difficulties[i + 1] - difficulties[i] > 0.3:
                intermediate_difficulty = (difficulties[i] + difficulties[i + 1]) / 2
                
                suggestion = CardSuggestion(
                    suggested_question=f"[Intermediate question about {topic}]",
                    suggested_answer=f"[Intermediate-level explanation of {topic}]",
                    confidence_score=0.6,
                    reasoning=f"Bridge content needed between difficulty levels {difficulties[i]:.2f} and {difficulties[i+1]:.2f}",
                    suggested_tags={topic, "intermediate"},
                    estimated_difficulty=intermediate_difficulty,
                    source=ContentSource.DIFFICULTY_PROGRESSION
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _suggest_connecting_cards(self, gap: ContentGap, deck: Deck) -> List[CardSuggestion]:
        """Suggest cards to connect isolated topics."""
        suggestions = []
        topic = list(gap.affected_tags)[0]
        
        # Find related topics in the deck
        all_topics = set()
        for card in deck.flashcards:
            all_topics.update(card.tags)
        
        related_topics = self._find_related_topics({topic})
        
        for related_topic, strength in list(related_topics.items())[:2]:
            if related_topic in all_topics:
                suggestion = CardSuggestion(
                    suggested_question=f"How does {topic} relate to {related_topic}?",
                    suggested_answer=f"[Explanation of relationship between {topic} and {related_topic}]",
                    confidence_score=strength,
                    reasoning=f"Connect isolated topic {topic} to existing topic {related_topic}",
                    suggested_tags={topic, related_topic, "relationships"},
                    estimated_difficulty=0.5,
                    source=ContentSource.KNOWLEDGE_GRAPH
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _suggest_general_cards(self, gap: ContentGap, deck: Deck) -> List[CardSuggestion]:
        """Suggest general cards for unspecified gaps."""
        suggestions = []
        topic = list(gap.affected_tags)[0] if gap.affected_tags else "general"
        
        suggestion = CardSuggestion(
            suggested_question=f"[Question about {topic}]",
            suggested_answer=f"[Answer about {topic}]",
            confidence_score=0.5,
            reasoning=f"General content suggestion for {topic}",
            suggested_tags={topic},
            estimated_difficulty=0.5,
            source=ContentSource.PATTERN_ANALYSIS
        )
        suggestions.append(suggestion)
        
        return suggestions
    
    def _filter_suggestions(
        self, 
        suggestions: List[CardSuggestion], 
        deck: Deck,
        focus_areas: Optional[Set[str]]
    ) -> List[CardSuggestion]:
        """Filter suggestions based on criteria."""
        filtered = []
        
        for suggestion in suggestions:
            # Filter by focus areas if specified
            if focus_areas and not suggestion.suggested_tags.intersection(focus_areas):
                continue
            
            # Filter out suggestions too similar to existing cards
            if not self._is_suggestion_novel(suggestion, deck):
                continue
            
            filtered.append(suggestion)
        
        return filtered
    
    def _rank_suggestions(self, suggestions: List[CardSuggestion], deck: Deck) -> List[CardSuggestion]:
        """Rank suggestions by relevance and quality."""
        def suggestion_score(suggestion: CardSuggestion) -> float:
            score = suggestion.confidence_score
            
            # Boost score for high-priority topics
            if any(tag in self.learning_goals.target_topics for tag in suggestion.suggested_tags):
                score += 0.2
            
            # Boost score for appropriate difficulty
            difficulty_match = 1.0 - abs(suggestion.estimated_difficulty - self.learning_goals.difficulty_preference)
            score += difficulty_match * 0.1
            
            return score
        
        return sorted(suggestions, key=suggestion_score, reverse=True)
    
    def _is_suggestion_novel(self, suggestion: CardSuggestion, deck: Deck) -> bool:
        """Check if a suggestion is novel (not too similar to existing cards)."""
        # Simple novelty check - can be enhanced with NLP similarity
        for card in deck.flashcards:
            if (suggestion.suggested_question.lower() in card.question.lower() or
                card.question.lower() in suggestion.suggested_question.lower()):
                return False
        return True
    
    # Helper methods for analysis
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    def _extract_content_patterns(self, deck: Deck) -> Dict[str, Any]:
        """Extract content patterns from the deck."""
        patterns = {
            "question_types": Counter(),
            "answer_lengths": [],
            "common_words": Counter()
        }
        
        for card in deck.flashcards:
            # Analyze question types
            if card.question.startswith("What"):
                patterns["question_types"]["what"] += 1
            elif card.question.startswith("How"):
                patterns["question_types"]["how"] += 1
            elif card.question.startswith("Why"):
                patterns["question_types"]["why"] += 1
            else:
                patterns["question_types"]["other"] += 1
            
            # Analyze answer lengths
            patterns["answer_lengths"].append(len(card.answer.split()))
            
            # Extract common words (simplified)
            words = re.findall(r'\w+', card.question.lower() + " " + card.answer.lower())
            patterns["common_words"].update(words)
        
        return patterns
    
    def _find_related_topics(self, topics: Set[str]) -> Dict[str, float]:
        """Find topics related to the given topics."""
        # Simplified relationship finding - would use knowledge graphs in practice
        related = {}
        
        for topic in topics:
            # Use tag hierarchy to find related topics
            hierarchy = self.tag_manager.get_tag_hierarchy(topic)
            if hierarchy:
                if hierarchy.parent:
                    related[hierarchy.parent] = 0.8
                for child in self.tag_manager.get_child_tags(topic):
                    related[child] = 0.7
        
        return related
    
    def _estimate_topic_card_count(self, topic: str) -> int:
        """Estimate how many cards a topic might need."""
        # Simple estimation - can be enhanced with topic complexity analysis
        return 10  # Default estimate
    
    def _analyze_difficulty_distribution(self, deck: Deck) -> Dict[str, Any]:
        """Analyze difficulty distribution for gaps."""
        difficulties = [card.difficulty for card in deck.flashcards]
        if not difficulties:
            return {"has_difficulty_gaps": False, "gaps": []}
        
        # Simple gap detection
        sorted_difficulties = sorted(set(difficulties))
        gaps = []
        
        for i in range(len(sorted_difficulties) - 1):
            gap_size = sorted_difficulties[i + 1] - sorted_difficulties[i]
            if gap_size > 0.3:
                gaps.append({
                    "start": sorted_difficulties[i],
                    "end": sorted_difficulties[i + 1],
                    "size": gap_size
                })
        
        return {
            "has_difficulty_gaps": len(gaps) > 0,
            "gaps": gaps,
            "distribution": {
                "min": min(difficulties),
                "max": max(difficulties),
                "mean": sum(difficulties) / len(difficulties)
            }
        }
    
    def _find_isolated_difficult_cards(self, deck: Deck) -> List[Flashcard]:
        """Find cards that are much harder than others in their topic."""
        isolated = []
        
        # Group cards by topic
        topic_cards = {}
        for card in deck.flashcards:
            for tag in card.tags:
                if tag not in topic_cards:
                    topic_cards[tag] = []
                topic_cards[tag].append(card)
        
        # Find isolated difficult cards
        for topic, cards in topic_cards.items():
            if len(cards) >= 3:
                difficulties = [card.difficulty for card in cards]
                mean_difficulty = sum(difficulties) / len(difficulties)
                
                for card in cards:
                    if card.difficulty > mean_difficulty + 0.4:  # Much harder than average
                        isolated.append(card)
        
        return isolated
    
    def _suggest_prerequisite_topics(self, gap: Dict[str, Any], deck: Deck) -> List[TopicSuggestion]:
        """Suggest prerequisite topics for a difficulty gap."""
        # Simplified prerequisite suggestion
        suggestions = []
        
        suggestion = TopicSuggestion(
            topic_name="Prerequisites",
            description=f"Foundational knowledge for difficulty range {gap['start']:.2f}-{gap['end']:.2f}",
            confidence_score=0.6,
            reasoning="Difficulty gap indicates missing prerequisites",
            suggested_tags={"prerequisites", "foundations"},
            estimated_card_count=5,
            priority_score=gap['size'],
            source=ContentSource.DIFFICULTY_PROGRESSION
        )
        suggestions.append(suggestion)
        
        return suggestions
    
    def _suggest_prerequisites_for_card(self, card: Flashcard, deck: Deck) -> List[TopicSuggestion]:
        """Suggest prerequisites for a specific difficult card."""
        suggestions = []
        
        for tag in card.tags:
            suggestion = TopicSuggestion(
                topic_name=f"Prerequisites for {tag}",
                description=f"Foundational knowledge needed for {tag}",
                confidence_score=0.5,
                reasoning=f"Card '{card.question[:50]}...' appears isolated and difficult",
                suggested_tags={f"{tag}_prerequisites", "foundations"},
                estimated_card_count=3,
                priority_score=card.difficulty,
                source=ContentSource.USER_PERFORMANCE
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def _analyze_topic_mastery(self, deck: Deck) -> Dict[str, Dict[str, Any]]:
        """Analyze mastery levels by topic."""
        topic_data = {}
        
        # Group cards by topic
        for card in deck.flashcards:
            for tag in card.tags:
                if tag not in topic_data:
                    topic_data[tag] = {
                        "cards": [],
                        "total_reviews": 0,
                        "total_correct": 0,
                        "difficulties": []
                    }
                
                topic_data[tag]["cards"].append(card)
                topic_data[tag]["total_reviews"] += card.review_count
                topic_data[tag]["total_correct"] += card.correct_count
                topic_data[tag]["difficulties"].append(card.difficulty)
        
        # Calculate mastery metrics
        for tag, data in topic_data.items():
            if data["total_reviews"] > 0:
                accuracy = data["total_correct"] / data["total_reviews"]
            else:
                accuracy = 0.0
            
            avg_difficulty = sum(data["difficulties"]) / len(data["difficulties"])
            
            # Simple mastery calculation
            mastery_level = accuracy * (1.0 - avg_difficulty)  # Higher accuracy, lower difficulty = higher mastery
            
            topic_data[tag]["mastery_level"] = mastery_level
            topic_data[tag]["accuracy"] = accuracy
            topic_data[tag]["avg_difficulty"] = avg_difficulty
            topic_data[tag]["card_count"] = len(data["cards"])
        
        return topic_data
    
    def _load_content_patterns(self) -> Dict[str, Any]:
        """Load learned content patterns."""
        return {}  # Placeholder
    
    def _load_topic_relationships(self) -> Dict[str, Any]:
        """Load topic relationship data."""
        return {}  # Placeholder
    
    def _load_difficulty_progressions(self) -> Dict[str, Any]:
        """Load difficulty progression patterns."""
        return {}  # Placeholder
    
    def _load_learning_goals(self) -> LearningGoals:
        """Load user learning goals."""
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
            except Exception:
                pass
        
        return LearningGoals()
