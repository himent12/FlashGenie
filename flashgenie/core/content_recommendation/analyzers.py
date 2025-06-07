"""
Content analysis utilities for the recommendation system.

This module provides functions to analyze deck content and identify patterns.
"""

from typing import Dict, List, Set, Any
from collections import Counter
import math

from ..content_system.deck import Deck
from .models import ContentGap, ContentAnalysis


class ContentAnalyzer:
    """Analyzes deck content to identify patterns and gaps."""
    
    def __init__(self):
        """Initialize the content analyzer."""
        pass
    
    def analyze_deck_content(self, deck: Deck) -> ContentAnalysis:
        """
        Analyze the content structure of a deck.
        
        Args:
            deck: The deck to analyze
            
        Returns:
            ContentAnalysis object with analysis results
        """
        topics = set()
        tag_frequency = Counter()
        difficulties = []
        
        # Collect basic statistics
        for card in deck.flashcards:
            topics.update(card.tags)
            tag_frequency.update(card.tags)
            difficulties.append(card.difficulty)
        
        # Calculate difficulty distribution
        difficulty_distribution = {}
        if difficulties:
            difficulty_distribution = {
                "mean": sum(difficulties) / len(difficulties),
                "min": min(difficulties),
                "max": max(difficulties),
                "std": self._calculate_std(difficulties)
            }
        
        # Extract content patterns
        content_patterns = self._extract_content_patterns(deck)
        
        # Calculate mastery levels by topic
        mastery_levels = self._calculate_topic_mastery(deck)
        
        return ContentAnalysis(
            total_cards=len(deck.flashcards),
            topics=topics,
            difficulty_distribution=difficulty_distribution,
            tag_frequency=dict(tag_frequency),
            content_patterns=content_patterns,
            mastery_levels=mastery_levels
        )
    
    def identify_content_gaps(self, deck: Deck, analysis: ContentAnalysis) -> List[ContentGap]:
        """
        Identify gaps in content coverage.
        
        Args:
            deck: The deck to analyze
            analysis: Pre-computed content analysis
            
        Returns:
            List of identified content gaps
        """
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
    
    def analyze_topic_mastery(self, deck: Deck) -> Dict[str, Dict[str, float]]:
        """
        Analyze mastery levels by topic.
        
        Args:
            deck: The deck to analyze
            
        Returns:
            Dictionary mapping topics to mastery data
        """
        topic_data = {}
        
        # Group cards by topic
        for card in deck.flashcards:
            for tag in card.tags:
                if tag not in topic_data:
                    topic_data[tag] = {
                        "cards": [],
                        "total_reviews": 0,
                        "correct_reviews": 0,
                        "difficulties": []
                    }
                
                topic_data[tag]["cards"].append(card)
                topic_data[tag]["total_reviews"] += card.review_count
                topic_data[tag]["correct_reviews"] += card.correct_count
                topic_data[tag]["difficulties"].append(card.difficulty)
        
        # Calculate mastery metrics
        mastery_analysis = {}
        for topic, data in topic_data.items():
            card_count = len(data["cards"])
            avg_difficulty = sum(data["difficulties"]) / card_count if card_count > 0 else 0
            
            # Calculate mastery level (0.0 to 1.0)
            if data["total_reviews"] > 0:
                accuracy = data["correct_reviews"] / data["total_reviews"]
                # Adjust for difficulty - harder topics need higher accuracy for same mastery
                mastery_level = accuracy * (1 - avg_difficulty * 0.3)
            else:
                mastery_level = 0.0
            
            mastery_analysis[topic] = {
                "mastery_level": mastery_level,
                "card_count": card_count,
                "avg_difficulty": avg_difficulty,
                "accuracy": data["correct_reviews"] / data["total_reviews"] if data["total_reviews"] > 0 else 0,
                "total_reviews": data["total_reviews"]
            }
        
        return mastery_analysis
    
    def analyze_difficulty_distribution(self, deck: Deck) -> Dict[str, Any]:
        """
        Analyze the difficulty distribution of cards.
        
        Args:
            deck: The deck to analyze
            
        Returns:
            Dictionary with difficulty analysis
        """
        difficulties = [card.difficulty for card in deck.flashcards]
        
        if not difficulties:
            return {"has_difficulty_gaps": False, "gaps": []}
        
        # Sort difficulties to find gaps
        sorted_difficulties = sorted(set(difficulties))
        
        gaps = []
        for i in range(len(sorted_difficulties) - 1):
            gap_size = sorted_difficulties[i + 1] - sorted_difficulties[i]
            if gap_size > 0.3:  # Significant gap
                gaps.append({
                    "start": sorted_difficulties[i],
                    "end": sorted_difficulties[i + 1],
                    "size": gap_size
                })
        
        return {
            "has_difficulty_gaps": len(gaps) > 0,
            "gaps": gaps,
            "distribution": {
                "easy": len([d for d in difficulties if d < 0.3]),
                "medium": len([d for d in difficulties if 0.3 <= d <= 0.7]),
                "hard": len([d for d in difficulties if d > 0.7])
            }
        }
    
    def find_isolated_difficult_cards(self, deck: Deck) -> List:
        """
        Find cards that are significantly more difficult than related cards.
        
        Args:
            deck: The deck to analyze
            
        Returns:
            List of isolated difficult cards
        """
        isolated_cards = []
        
        # Group cards by tags
        tag_groups = {}
        for card in deck.flashcards:
            for tag in card.tags:
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(card)
        
        # Find cards that are much harder than their tag group average
        for tag, cards in tag_groups.items():
            if len(cards) >= 3:  # Need enough cards for comparison
                difficulties = [card.difficulty for card in cards]
                avg_difficulty = sum(difficulties) / len(difficulties)
                std_difficulty = self._calculate_std(difficulties)
                
                for card in cards:
                    # Card is isolated if it's more than 2 standard deviations above average
                    if card.difficulty > avg_difficulty + 2 * std_difficulty:
                        isolated_cards.append(card)
        
        return isolated_cards
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation of a list of values."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)
    
    def _extract_content_patterns(self, deck: Deck) -> Dict[str, Any]:
        """Extract patterns from deck content."""
        patterns = {
            "question_types": Counter(),
            "answer_lengths": [],
            "common_words": Counter(),
            "tag_combinations": Counter()
        }
        
        for card in deck.flashcards:
            # Analyze question types (simplified)
            question = card.question.lower()
            if question.startswith("what"):
                patterns["question_types"]["what"] += 1
            elif question.startswith("how"):
                patterns["question_types"]["how"] += 1
            elif question.startswith("why"):
                patterns["question_types"]["why"] += 1
            elif question.startswith("when"):
                patterns["question_types"]["when"] += 1
            else:
                patterns["question_types"]["other"] += 1
            
            # Answer length
            patterns["answer_lengths"].append(len(card.answer.split()))
            
            # Common words (simplified)
            words = card.question.lower().split() + card.answer.lower().split()
            patterns["common_words"].update(words)
            
            # Tag combinations
            if len(card.tags) > 1:
                tag_combo = tuple(sorted(card.tags))
                patterns["tag_combinations"][tag_combo] += 1
        
        return patterns
    
    def _calculate_topic_mastery(self, deck: Deck) -> Dict[str, float]:
        """Calculate mastery level for each topic."""
        topic_mastery = {}
        
        # Group cards by topic and calculate mastery
        for card in deck.flashcards:
            for tag in card.tags:
                if tag not in topic_mastery:
                    topic_mastery[tag] = []
                
                # Simple mastery calculation based on accuracy and review count
                if card.review_count > 0:
                    accuracy = card.correct_count / card.review_count
                    # Weight by review count (more reviews = more reliable)
                    weighted_mastery = accuracy * min(card.review_count / 5, 1.0)
                    topic_mastery[tag].append(weighted_mastery)
                else:
                    topic_mastery[tag].append(0.0)
        
        # Average mastery per topic
        for tag in topic_mastery:
            if topic_mastery[tag]:
                topic_mastery[tag] = sum(topic_mastery[tag]) / len(topic_mastery[tag])
            else:
                topic_mastery[tag] = 0.0
        
        return topic_mastery
    
    def _find_missing_basics(self, deck: Deck, analysis: ContentAnalysis) -> List[ContentGap]:
        """Find missing basic concepts."""
        gaps = []
        
        # Look for topics with only high-difficulty cards
        for topic in analysis.topics:
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
    
    def _find_difficulty_jumps(self, deck: Deck, analysis: ContentAnalysis) -> List[ContentGap]:
        """Find difficulty jumps that need bridging content."""
        gaps = []
        
        # Group cards by topic and analyze difficulty progression
        for topic in analysis.topics:
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
    
    def _find_isolated_topics(self, deck: Deck, analysis: ContentAnalysis) -> List[ContentGap]:
        """Find topics that are isolated from others."""
        gaps = []
        
        # Find topics with very few cards
        for topic, count in analysis.tag_frequency.items():
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
