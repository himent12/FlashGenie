"""
Fuzzy matching utilities for intelligent typo handling in FlashGenie.

This module provides fuzzy string matching capabilities to handle user typos
during quiz sessions, making the learning experience more forgiving and user-friendly.
"""

from typing import List, Tuple, Optional, Dict, Any
import re
from dataclasses import dataclass
from enum import Enum


class MatchType(Enum):
    """Types of fuzzy matches."""
    EXACT = "exact"
    CASE_INSENSITIVE = "case_insensitive"
    MINOR_TYPO = "minor_typo"
    MODERATE_TYPO = "moderate_typo"
    MAJOR_TYPO = "major_typo"
    NO_MATCH = "no_match"


@dataclass
class FuzzyMatchResult:
    """Result of a fuzzy matching operation."""
    match_type: MatchType
    matched_answer: Optional[str]
    confidence: float  # 0.0 to 1.0
    distance: int  # Levenshtein distance
    suggestion: Optional[str] = None


class FuzzyMatcher:
    """
    Intelligent fuzzy matching for flashcard answers with typo tolerance.
    
    Provides configurable sensitivity levels and smart matching algorithms
    to handle common typing mistakes while maintaining accuracy.
    """
    
    def __init__(self, sensitivity: str = "medium"):
        """
        Initialize the fuzzy matcher.
        
        Args:
            sensitivity: Matching sensitivity ("strict", "medium", "lenient")
        """
        self.sensitivity = sensitivity
        self.config = self._get_sensitivity_config(sensitivity)
    
    def _get_sensitivity_config(self, sensitivity: str) -> Dict[str, Any]:
        """Get configuration based on sensitivity level."""
        configs = {
            "strict": {
                "minor_typo_threshold": 1,      # Max 1 character difference
                "moderate_typo_threshold": 2,   # Max 2 character difference
                "major_typo_threshold": 3,      # Max 3 character difference
                "length_ratio_threshold": 0.8,  # Answers must be 80% similar length
                "auto_accept_threshold": 0.95,  # Auto-accept if 95% confident
                "suggest_threshold": 0.7,       # Suggest if 70% confident
            },
            "medium": {
                "minor_typo_threshold": 2,      # Max 2 character difference
                "moderate_typo_threshold": 3,   # Max 3 character difference
                "major_typo_threshold": 5,      # Max 5 character difference
                "length_ratio_threshold": 0.6,  # Answers must be 60% similar length
                "auto_accept_threshold": 0.9,   # Auto-accept if 90% confident
                "suggest_threshold": 0.6,       # Suggest if 60% confident
            },
            "lenient": {
                "minor_typo_threshold": 3,      # Max 3 character difference
                "moderate_typo_threshold": 5,   # Max 5 character difference
                "major_typo_threshold": 7,      # Max 7 character difference
                "length_ratio_threshold": 0.4,  # Answers must be 40% similar length
                "auto_accept_threshold": 0.8,   # Auto-accept if 80% confident
                "suggest_threshold": 0.5,       # Suggest if 50% confident
            }
        }
        return configs.get(sensitivity, configs["medium"])
    
    def match_answer(self, user_input: str, valid_answers: List[str]) -> FuzzyMatchResult:
        """
        Find the best fuzzy match for user input against valid answers.
        
        Args:
            user_input: The user's input answer
            valid_answers: List of valid answers to match against
            
        Returns:
            FuzzyMatchResult with the best match found
        """
        user_input = user_input.strip()
        
        if not user_input or not valid_answers:
            return FuzzyMatchResult(
                match_type=MatchType.NO_MATCH,
                matched_answer=None,
                confidence=0.0,
                distance=float('inf')
            )
        
        best_match = None
        best_distance = float('inf')
        best_confidence = 0.0
        
        for valid_answer in valid_answers:
            match_result = self._match_single_answer(user_input, valid_answer)
            
            if match_result.confidence > best_confidence:
                best_match = match_result
                best_distance = match_result.distance
                best_confidence = match_result.confidence
        
        return best_match or FuzzyMatchResult(
            match_type=MatchType.NO_MATCH,
            matched_answer=None,
            confidence=0.0,
            distance=float('inf')
        )
    
    def _match_single_answer(self, user_input: str, valid_answer: str) -> FuzzyMatchResult:
        """Match user input against a single valid answer."""
        # Exact match
        if user_input == valid_answer:
            return FuzzyMatchResult(
                match_type=MatchType.EXACT,
                matched_answer=valid_answer,
                confidence=1.0,
                distance=0
            )
        
        # Case-insensitive match
        if user_input.lower() == valid_answer.lower():
            return FuzzyMatchResult(
                match_type=MatchType.CASE_INSENSITIVE,
                matched_answer=valid_answer,
                confidence=0.98,
                distance=0
            )
        
        # Fuzzy matching with Levenshtein distance
        distance = self._levenshtein_distance(user_input.lower(), valid_answer.lower())
        confidence = self._calculate_confidence(user_input, valid_answer, distance)
        
        # Determine match type based on distance and configuration
        match_type = self._determine_match_type(distance, len(valid_answer))
        
        # Generate suggestion if confidence is above threshold
        suggestion = None
        if confidence >= self.config["suggest_threshold"]:
            suggestion = f"Did you mean '{valid_answer}'?"
        
        return FuzzyMatchResult(
            match_type=match_type,
            matched_answer=valid_answer if match_type != MatchType.NO_MATCH else None,
            confidence=confidence,
            distance=distance,
            suggestion=suggestion
        )
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _calculate_confidence(self, user_input: str, valid_answer: str, distance: int) -> float:
        """Calculate confidence score for a match."""
        max_length = max(len(user_input), len(valid_answer))
        
        if max_length == 0:
            return 1.0
        
        # Basic confidence based on distance
        basic_confidence = 1.0 - (distance / max_length)
        
        # Length ratio penalty
        length_ratio = min(len(user_input), len(valid_answer)) / max_length
        if length_ratio < self.config["length_ratio_threshold"]:
            basic_confidence *= length_ratio / self.config["length_ratio_threshold"]
        
        # Bonus for common prefixes/suffixes
        prefix_bonus = self._calculate_prefix_bonus(user_input.lower(), valid_answer.lower())
        suffix_bonus = self._calculate_suffix_bonus(user_input.lower(), valid_answer.lower())
        
        confidence = basic_confidence + (prefix_bonus + suffix_bonus) * 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_prefix_bonus(self, s1: str, s2: str) -> float:
        """Calculate bonus for matching prefixes."""
        common_prefix = 0
        for i in range(min(len(s1), len(s2))):
            if s1[i] == s2[i]:
                common_prefix += 1
            else:
                break
        
        return common_prefix / max(len(s1), len(s2))
    
    def _calculate_suffix_bonus(self, s1: str, s2: str) -> float:
        """Calculate bonus for matching suffixes."""
        common_suffix = 0
        for i in range(1, min(len(s1), len(s2)) + 1):
            if s1[-i] == s2[-i]:
                common_suffix += 1
            else:
                break
        
        return common_suffix / max(len(s1), len(s2))
    
    def _determine_match_type(self, distance: int, answer_length: int) -> MatchType:
        """Determine the type of match based on distance and thresholds."""
        if distance <= self.config["minor_typo_threshold"]:
            return MatchType.MINOR_TYPO
        elif distance <= self.config["moderate_typo_threshold"]:
            return MatchType.MODERATE_TYPO
        elif distance <= self.config["major_typo_threshold"]:
            return MatchType.MAJOR_TYPO
        else:
            return MatchType.NO_MATCH
    
    def should_auto_accept(self, match_result: FuzzyMatchResult) -> bool:
        """Determine if a match should be automatically accepted."""
        return (match_result.confidence >= self.config["auto_accept_threshold"] and
                match_result.match_type in [MatchType.EXACT, MatchType.CASE_INSENSITIVE, MatchType.MINOR_TYPO])
    
    def should_suggest(self, match_result: FuzzyMatchResult) -> bool:
        """Determine if a suggestion should be offered to the user."""
        return (match_result.confidence >= self.config["suggest_threshold"] and
                match_result.match_type != MatchType.NO_MATCH and
                not self.should_auto_accept(match_result))
    
    def set_sensitivity(self, sensitivity: str) -> None:
        """Update the sensitivity level."""
        if sensitivity in ["strict", "medium", "lenient"]:
            self.sensitivity = sensitivity
            self.config = self._get_sensitivity_config(sensitivity)
        else:
            raise ValueError("Sensitivity must be 'strict', 'medium', or 'lenient'")


def create_fuzzy_matcher(sensitivity: str = "medium") -> FuzzyMatcher:
    """
    Factory function to create a FuzzyMatcher instance.
    
    Args:
        sensitivity: Matching sensitivity level
        
    Returns:
        Configured FuzzyMatcher instance
    """
    return FuzzyMatcher(sensitivity)
