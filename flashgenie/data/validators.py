"""
Data validation utilities for FlashGenie.

This module provides validation functions for flashcard data,
import/export operations, and data integrity checks.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck
from flashgenie.utils.exceptions import ValidationError


class DataValidator:
    """
    Validator for flashcard and deck data.
    
    Provides comprehensive validation for data integrity,
    format compliance, and content quality.
    """
    
    def __init__(self):
        """Initialize the data validator."""
        self.max_question_length = 1000
        self.max_answer_length = 1000
        self.max_deck_name_length = 100
        self.max_tag_length = 50
        self.max_tags_per_item = 20
    
    def validate_flashcard(self, flashcard: Flashcard) -> List[str]:
        """
        Validate a flashcard and return any issues found.
        
        Args:
            flashcard: The flashcard to validate
            
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        # Validate question
        if not flashcard.question or not flashcard.question.strip():
            issues.append("Question cannot be empty")
        elif len(flashcard.question) > self.max_question_length:
            issues.append(f"Question too long (max {self.max_question_length} characters)")
        
        # Validate answer
        if not flashcard.answer or not flashcard.answer.strip():
            issues.append("Answer cannot be empty")
        elif len(flashcard.answer) > self.max_answer_length:
            issues.append(f"Answer too long (max {self.max_answer_length} characters)")
        
        # Validate difficulty
        if not 0.0 <= flashcard.difficulty <= 1.0:
            issues.append("Difficulty must be between 0.0 and 1.0")
        
        # Validate ease factor
        if flashcard.ease_factor < 1.3:
            issues.append("Ease factor must be at least 1.3")
        
        # Validate review counts
        if flashcard.review_count < 0:
            issues.append("Review count cannot be negative")
        
        if flashcard.correct_count < 0:
            issues.append("Correct count cannot be negative")
        
        if flashcard.correct_count > flashcard.review_count:
            issues.append("Correct count cannot exceed review count")
        
        # Validate tags
        tag_issues = self.validate_tags(flashcard.tags)
        issues.extend(tag_issues)
        
        return issues
    
    def validate_deck(self, deck: Deck) -> List[str]:
        """
        Validate a deck and return any issues found.
        
        Args:
            deck: The deck to validate
            
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        # Validate deck name
        if not deck.name or not deck.name.strip():
            issues.append("Deck name cannot be empty")
        elif len(deck.name) > self.max_deck_name_length:
            issues.append(f"Deck name too long (max {self.max_deck_name_length} characters)")
        
        # Validate flashcards
        if not deck.flashcards:
            issues.append("Deck cannot be empty")
        else:
            # Check for duplicate card IDs
            card_ids = [card.card_id for card in deck.flashcards]
            if len(card_ids) != len(set(card_ids)):
                issues.append("Deck contains duplicate card IDs")
            
            # Validate each flashcard
            for i, card in enumerate(deck.flashcards):
                card_issues = self.validate_flashcard(card)
                for issue in card_issues:
                    issues.append(f"Card {i + 1}: {issue}")
        
        # Validate tags
        tag_issues = self.validate_tags(deck.tags)
        issues.extend(tag_issues)
        
        return issues
    
    def validate_tags(self, tags: List[str]) -> List[str]:
        """
        Validate a list of tags.
        
        Args:
            tags: List of tags to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if len(tags) > self.max_tags_per_item:
            issues.append(f"Too many tags (max {self.max_tags_per_item})")
        
        for i, tag in enumerate(tags):
            if not tag or not tag.strip():
                issues.append(f"Tag {i + 1} cannot be empty")
            elif len(tag) > self.max_tag_length:
                issues.append(f"Tag {i + 1} too long (max {self.max_tag_length} characters)")
            elif not self._is_valid_tag_format(tag):
                issues.append(f"Tag {i + 1} contains invalid characters")
        
        # Check for duplicates
        if len(tags) != len(set(tags)):
            issues.append("Duplicate tags found")
        
        return issues
    
    def _is_valid_tag_format(self, tag: str) -> bool:
        """
        Check if a tag has valid format.
        
        Args:
            tag: Tag to check
            
        Returns:
            True if tag format is valid
        """
        # Allow alphanumeric, spaces, hyphens, underscores
        return re.match(r'^[a-zA-Z0-9\s\-_]+$', tag) is not None
    
    def validate_import_data(self, data: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Validate imported flashcard data.
        
        Args:
            data: List of (question, answer) tuples
            
        Returns:
            Dictionary with validation results
        """
        valid_cards = []
        invalid_cards = []
        
        for i, (question, answer) in enumerate(data):
            issues = []
            
            # Validate question
            if not question or not question.strip():
                issues.append("Empty question")
            elif len(question) > self.max_question_length:
                issues.append("Question too long")
            
            # Validate answer
            if not answer or not answer.strip():
                issues.append("Empty answer")
            elif len(answer) > self.max_answer_length:
                issues.append("Answer too long")
            
            if issues:
                invalid_cards.append({
                    "row": i + 1,
                    "question": question,
                    "answer": answer,
                    "issues": issues
                })
            else:
                valid_cards.append((question.strip(), answer.strip()))
        
        return {
            "valid_count": len(valid_cards),
            "invalid_count": len(invalid_cards),
            "valid_cards": valid_cards,
            "invalid_cards": invalid_cards,
            "success_rate": len(valid_cards) / len(data) if data else 0.0
        }
    
    def check_data_integrity(self, deck: Deck) -> Dict[str, Any]:
        """
        Perform comprehensive data integrity check on a deck.
        
        Args:
            deck: The deck to check
            
        Returns:
            Dictionary with integrity check results
        """
        results = {
            "overall_status": "healthy",
            "issues": [],
            "warnings": [],
            "statistics": {}
        }
        
        # Basic validation
        validation_issues = self.validate_deck(deck)
        if validation_issues:
            results["issues"].extend(validation_issues)
            results["overall_status"] = "issues_found"
        
        # Check for potential data quality issues
        warnings = []
        
        # Check for very short questions/answers
        short_questions = sum(1 for card in deck.flashcards if len(card.question.strip()) < 5)
        short_answers = sum(1 for card in deck.flashcards if len(card.answer.strip()) < 2)
        
        if short_questions > 0:
            warnings.append(f"{short_questions} cards have very short questions")
        
        if short_answers > 0:
            warnings.append(f"{short_answers} cards have very short answers")
        
        # Check for duplicate content
        questions = [card.question.strip().lower() for card in deck.flashcards]
        duplicate_questions = len(questions) - len(set(questions))
        
        if duplicate_questions > 0:
            warnings.append(f"{duplicate_questions} duplicate questions found")
        
        # Check for cards that haven't been reviewed
        unreviewed_cards = sum(1 for card in deck.flashcards if card.review_count == 0)
        if unreviewed_cards == len(deck.flashcards):
            warnings.append("No cards have been reviewed yet")
        
        results["warnings"] = warnings
        
        # Calculate statistics
        if deck.flashcards:
            accuracies = [card.accuracy for card in deck.flashcards if card.review_count > 0]
            difficulties = [card.difficulty for card in deck.flashcards]
            
            results["statistics"] = {
                "total_cards": len(deck.flashcards),
                "reviewed_cards": len(accuracies),
                "average_accuracy": sum(accuracies) / len(accuracies) if accuracies else 0.0,
                "average_difficulty": sum(difficulties) / len(difficulties),
                "due_cards": len(deck.due_cards),
                "unreviewed_cards": unreviewed_cards
            }
        
        return results
    
    def suggest_improvements(self, deck: Deck) -> List[str]:
        """
        Suggest improvements for a deck.
        
        Args:
            deck: The deck to analyze
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        if not deck.flashcards:
            return ["Add some flashcards to the deck"]
        
        # Check review status
        unreviewed = sum(1 for card in deck.flashcards if card.review_count == 0)
        if unreviewed > 0:
            suggestions.append(f"Review {unreviewed} unreviewed cards")
        
        # Check due cards
        due_count = len(deck.due_cards)
        if due_count > 0:
            suggestions.append(f"Study {due_count} cards that are due for review")
        
        # Check for difficult cards
        difficult_cards = [card for card in deck.flashcards if card.difficulty > 0.7]
        if difficult_cards:
            suggestions.append(f"Focus on {len(difficult_cards)} difficult cards")
        
        # Check for low accuracy cards
        low_accuracy_cards = [
            card for card in deck.flashcards 
            if card.review_count > 2 and card.accuracy < 0.5
        ]
        if low_accuracy_cards:
            suggestions.append(f"Review {len(low_accuracy_cards)} cards with low accuracy")
        
        # Check deck organization
        if not deck.tags:
            suggestions.append("Add tags to organize the deck")
        
        if not deck.description:
            suggestions.append("Add a description to the deck")
        
        return suggestions
