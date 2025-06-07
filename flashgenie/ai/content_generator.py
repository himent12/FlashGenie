"""
AI Content Generation System for FlashGenie v1.8.5 Phase 3.

This module provides AI-powered flashcard generation, smart content suggestions,
and intelligent difficulty prediction using various AI techniques.
"""

from typing import List, Dict, Any, Optional, Tuple
import re
import random
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from flashgenie.core.content_system.flashcard import Flashcard
from flashgenie.core.content_system.deck import Deck


class ContentType(Enum):
    """Types of content that can be generated."""
    VOCABULARY = "vocabulary"
    DEFINITIONS = "definitions"
    FACTS = "facts"
    FORMULAS = "formulas"
    QUESTIONS = "questions"
    TRANSLATIONS = "translations"


class DifficultyLevel(Enum):
    """AI-predicted difficulty levels."""
    VERY_EASY = 0.1
    EASY = 0.3
    MEDIUM = 0.5
    HARD = 0.7
    VERY_HARD = 0.9


@dataclass
class GeneratedContent:
    """Container for AI-generated content."""
    question: str
    answer: str
    content_type: ContentType
    confidence: float
    difficulty: float
    tags: List[str]
    explanation: Optional[str] = None
    source: Optional[str] = None


class AIContentGenerator:
    """
    AI-powered content generation system.
    
    Provides intelligent flashcard generation, content suggestions,
    and difficulty prediction using various AI techniques.
    """
    
    def __init__(self):
        """Initialize the AI Content Generator."""
        self.content_patterns = self._initialize_content_patterns()
        self.difficulty_keywords = self._initialize_difficulty_keywords()
        self.subject_templates = self._initialize_subject_templates()
        
        # AI model configuration (placeholder for real AI integration)
        self.ai_enabled = False  # Would be True with real AI models
        self.confidence_threshold = 0.7
        self.max_generations_per_request = 50
    
    def generate_flashcards_from_text(self, text: str, content_type: ContentType = ContentType.FACTS,
                                    max_cards: int = 10) -> List[GeneratedContent]:
        """
        Generate flashcards from input text using AI analysis.
        
        Args:
            text: Input text to analyze and generate cards from
            content_type: Type of content to generate
            max_cards: Maximum number of cards to generate
            
        Returns:
            List of generated flashcard content
        """
        if self.ai_enabled:
            return self._generate_with_ai_model(text, content_type, max_cards)
        else:
            return self._generate_with_patterns(text, content_type, max_cards)
    
    def suggest_related_content(self, existing_cards: List[Flashcard], 
                              count: int = 5) -> List[GeneratedContent]:
        """
        Suggest related content based on existing flashcards.
        
        Args:
            existing_cards: List of existing flashcards to analyze
            count: Number of suggestions to generate
            
        Returns:
            List of suggested content
        """
        suggestions = []
        
        # Analyze existing cards for patterns
        topics = self._extract_topics_from_cards(existing_cards)
        difficulty_level = self._calculate_average_difficulty(existing_cards)
        
        # Generate related content
        for topic in topics[:count]:
            suggestion = self._generate_related_content(topic, difficulty_level)
            if suggestion:
                suggestions.append(suggestion)
        
        return suggestions
    
    def predict_difficulty(self, question: str, answer: str, context: Optional[str] = None) -> float:
        """
        Predict the difficulty level of a flashcard using AI analysis.
        
        Args:
            question: The question text
            answer: The answer text
            context: Optional context for better prediction
            
        Returns:
            Predicted difficulty level (0.0 to 1.0)
        """
        if self.ai_enabled:
            return self._predict_difficulty_with_ai(question, answer, context)
        else:
            return self._predict_difficulty_with_heuristics(question, answer)
    
    def generate_hints(self, flashcard: Flashcard) -> List[str]:
        """
        Generate helpful hints for a flashcard.
        
        Args:
            flashcard: Flashcard to generate hints for
            
        Returns:
            List of generated hints
        """
        hints = []
        
        # Generate different types of hints
        hints.extend(self._generate_letter_hints(flashcard.answer))
        hints.extend(self._generate_category_hints(flashcard))
        hints.extend(self._generate_context_hints(flashcard))
        
        return hints[:3]  # Return top 3 hints
    
    def enhance_existing_cards(self, cards: List[Flashcard]) -> List[Dict[str, Any]]:
        """
        Enhance existing flashcards with AI-generated improvements.
        
        Args:
            cards: List of flashcards to enhance
            
        Returns:
            List of enhancement suggestions
        """
        enhancements = []
        
        for card in cards:
            enhancement = {
                'card_id': card.card_id,
                'original_question': card.question,
                'original_answer': card.answer,
                'suggestions': []
            }
            
            # Generate various enhancements
            enhancement['suggestions'].extend(self._suggest_question_improvements(card))
            enhancement['suggestions'].extend(self._suggest_additional_context(card))
            enhancement['suggestions'].extend(self._suggest_better_tags(card))
            
            if enhancement['suggestions']:
                enhancements.append(enhancement)
        
        return enhancements
    
    def _initialize_content_patterns(self) -> Dict[ContentType, List[str]]:
        """Initialize content generation patterns."""
        return {
            ContentType.VOCABULARY: [
                r"(\w+)\s*[-–—]\s*(.+)",  # Word - definition
                r"(\w+):\s*(.+)",         # Word: definition
                r"(\w+)\s*\((.+)\)",      # Word (definition)
            ],
            ContentType.DEFINITIONS: [
                r"(.+?)\s+is\s+(.+)",     # X is Y
                r"(.+?)\s+means\s+(.+)",  # X means Y
                r"(.+?):\s*(.+)",         # Term: definition
            ],
            ContentType.FACTS: [
                r"(.+?)\s+was\s+(.+)",    # X was Y
                r"(.+?)\s+is\s+(.+)",     # X is Y
                r"(.+?)\s+has\s+(.+)",    # X has Y
            ],
            ContentType.FORMULAS: [
                r"(.+?)\s*=\s*(.+)",      # Formula = Expression
                r"(.+?)\s*:\s*(.+)",      # Name: Formula
            ]
        }
    
    def _initialize_difficulty_keywords(self) -> Dict[str, float]:
        """Initialize keywords that indicate difficulty levels."""
        return {
            # Easy indicators
            'basic': 0.2, 'simple': 0.2, 'elementary': 0.2, 'fundamental': 0.3,
            'common': 0.2, 'everyday': 0.2, 'beginner': 0.2,
            
            # Medium indicators
            'intermediate': 0.5, 'standard': 0.5, 'typical': 0.5, 'general': 0.4,
            'moderate': 0.5, 'average': 0.5,
            
            # Hard indicators
            'advanced': 0.7, 'complex': 0.8, 'complicated': 0.8, 'difficult': 0.8,
            'expert': 0.9, 'professional': 0.7, 'specialized': 0.8, 'technical': 0.7,
            'sophisticated': 0.8, 'intricate': 0.9
        }
    
    def _initialize_subject_templates(self) -> Dict[str, List[str]]:
        """Initialize subject-specific templates for content generation."""
        return {
            'math': [
                "What is the formula for {concept}?",
                "How do you calculate {concept}?",
                "What is {concept} in mathematics?",
                "Define {concept} in mathematical terms."
            ],
            'science': [
                "What is {concept}?",
                "How does {concept} work?",
                "What causes {concept}?",
                "Explain the process of {concept}."
            ],
            'history': [
                "When did {event} occur?",
                "Who was {person}?",
                "What happened during {event}?",
                "Why was {event} significant?"
            ],
            'language': [
                "What does {word} mean?",
                "How do you say {phrase} in {language}?",
                "What is the {language} word for {concept}?",
                "Translate {phrase}."
            ]
        }
    
    def _generate_with_patterns(self, text: str, content_type: ContentType, 
                              max_cards: int) -> List[GeneratedContent]:
        """Generate content using pattern matching (fallback method)."""
        generated = []
        patterns = self.content_patterns.get(content_type, [])
        
        lines = text.split('\n')
        for line in lines:
            if len(generated) >= max_cards:
                break
                
            line = line.strip()
            if not line:
                continue
            
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    question = match.group(1).strip()
                    answer = match.group(2).strip()
                    
                    if len(question) > 3 and len(answer) > 3:
                        difficulty = self.predict_difficulty(question, answer)
                        tags = self._generate_tags_from_content(question, answer)
                        
                        generated.append(GeneratedContent(
                            question=question,
                            answer=answer,
                            content_type=content_type,
                            confidence=0.8,  # Pattern matching confidence
                            difficulty=difficulty,
                            tags=tags,
                            source="pattern_matching"
                        ))
                        break
        
        return generated
    
    def _generate_with_ai_model(self, text: str, content_type: ContentType, 
                               max_cards: int) -> List[GeneratedContent]:
        """Generate content using AI model (placeholder for real AI integration)."""
        # This would integrate with actual AI models like GPT, Claude, etc.
        # For now, return enhanced pattern-based generation
        return self._generate_with_patterns(text, content_type, max_cards)
    
    def _extract_topics_from_cards(self, cards: List[Flashcard]) -> List[str]:
        """Extract topics from existing flashcards."""
        topics = set()
        
        for card in cards:
            # Extract topics from tags
            topics.update(card.tags)
            
            # Extract topics from question/answer content
            words = re.findall(r'\b[A-Z][a-z]+\b', card.question + ' ' + card.answer)
            topics.update(words[:3])  # Add up to 3 capitalized words
        
        return list(topics)[:10]  # Return top 10 topics
    
    def _calculate_average_difficulty(self, cards: List[Flashcard]) -> float:
        """Calculate average difficulty of existing cards."""
        if not cards:
            return 0.5
        
        difficulties = [getattr(card, 'difficulty', 0.5) for card in cards]
        return sum(difficulties) / len(difficulties)
    
    def _generate_related_content(self, topic: str, difficulty_level: float) -> Optional[GeneratedContent]:
        """Generate content related to a specific topic."""
        # Simple related content generation
        templates = [
            f"What is {topic}?",
            f"How does {topic} work?",
            f"Why is {topic} important?",
            f"What are the characteristics of {topic}?",
            f"How is {topic} used?"
        ]
        
        question = random.choice(templates)
        answer = f"[Related to {topic} - answer would be generated by AI]"
        
        return GeneratedContent(
            question=question,
            answer=answer,
            content_type=ContentType.FACTS,
            confidence=0.6,
            difficulty=difficulty_level,
            tags=[topic.lower(), 'ai_generated', 'related'],
            source="topic_expansion"
        )
    
    def _predict_difficulty_with_heuristics(self, question: str, answer: str) -> float:
        """Predict difficulty using heuristic analysis."""
        difficulty_score = 0.5  # Base difficulty
        
        # Length-based factors
        question_length = len(question.split())
        answer_length = len(answer.split())
        
        if question_length > 15:
            difficulty_score += 0.1
        if answer_length > 20:
            difficulty_score += 0.1
        
        # Keyword-based factors
        text = (question + ' ' + answer).lower()
        for keyword, weight in self.difficulty_keywords.items():
            if keyword in text:
                difficulty_score = max(difficulty_score, weight)
        
        # Complexity indicators
        if any(char in answer for char in ['(', ')', '[', ']', '{', '}', '=', '+', '-', '*', '/']):
            difficulty_score += 0.1
        
        if re.search(r'\d+', answer):  # Contains numbers
            difficulty_score += 0.05
        
        if len(re.findall(r'[A-Z]', answer)) > 3:  # Many capital letters
            difficulty_score += 0.05
        
        return min(1.0, max(0.0, difficulty_score))
    
    def _predict_difficulty_with_ai(self, question: str, answer: str, context: Optional[str]) -> float:
        """Predict difficulty using AI model (placeholder)."""
        # This would use actual AI models for difficulty prediction
        return self._predict_difficulty_with_heuristics(question, answer)
    
    def _generate_letter_hints(self, answer: str) -> List[str]:
        """Generate letter-based hints."""
        if len(answer) < 3:
            return []
        
        # First and last letter hint
        hint1 = answer[0] + '_' * (len(answer) - 2) + answer[-1]
        
        # First few letters hint
        hint2 = answer[:2] + '_' * (len(answer) - 2) if len(answer) > 3 else answer[0] + '_'
        
        return [f"Starts with '{answer[0]}' and ends with '{answer[-1]}'", 
                f"Begins with '{answer[:2]}'"]
    
    def _generate_category_hints(self, flashcard: Flashcard) -> List[str]:
        """Generate category-based hints."""
        hints = []
        
        if flashcard.tags:
            hints.append(f"This is related to {', '.join(flashcard.tags[:2])}")
        
        # Length hint
        word_count = len(flashcard.answer.split())
        if word_count == 1:
            hints.append("This is a single word")
        else:
            hints.append(f"This answer has {word_count} words")
        
        return hints
    
    def _generate_context_hints(self, flashcard: Flashcard) -> List[str]:
        """Generate context-based hints."""
        hints = []
        
        # Simple context hints based on question
        if '?' in flashcard.question:
            if 'who' in flashcard.question.lower():
                hints.append("This is a person")
            elif 'what' in flashcard.question.lower():
                hints.append("This is a thing or concept")
            elif 'when' in flashcard.question.lower():
                hints.append("This is a time or date")
            elif 'where' in flashcard.question.lower():
                hints.append("This is a place or location")
        
        return hints
    
    def _suggest_question_improvements(self, card: Flashcard) -> List[Dict[str, str]]:
        """Suggest improvements to question wording."""
        suggestions = []
        
        # Make questions more specific
        if len(card.question.split()) < 5:
            suggestions.append({
                'type': 'specificity',
                'suggestion': f"Consider making the question more specific: '{card.question}' could include more context"
            })
        
        # Add question words if missing
        if not any(word in card.question.lower() for word in ['what', 'who', 'when', 'where', 'why', 'how']):
            suggestions.append({
                'type': 'question_word',
                'suggestion': "Consider starting with a question word (What, Who, When, Where, Why, How)"
            })
        
        return suggestions
    
    def _suggest_additional_context(self, card: Flashcard) -> List[Dict[str, str]]:
        """Suggest additional context for better learning."""
        suggestions = []
        
        if not card.tags:
            suggestions.append({
                'type': 'tags',
                'suggestion': "Add tags to categorize this card and improve organization"
            })
        
        if len(card.answer.split()) == 1:
            suggestions.append({
                'type': 'context',
                'suggestion': "Consider adding more context or explanation to the answer"
            })
        
        return suggestions
    
    def _suggest_better_tags(self, card: Flashcard) -> List[Dict[str, str]]:
        """Suggest better tags for organization."""
        suggestions = []
        
        # Extract potential tags from content
        potential_tags = self._generate_tags_from_content(card.question, card.answer)
        existing_tags = set(card.tags)
        new_tags = [tag for tag in potential_tags if tag not in existing_tags]
        
        if new_tags:
            suggestions.append({
                'type': 'new_tags',
                'suggestion': f"Consider adding these tags: {', '.join(new_tags[:3])}"
            })
        
        return suggestions
    
    def _generate_tags_from_content(self, question: str, answer: str) -> List[str]:
        """Generate relevant tags from question and answer content."""
        tags = []
        text = (question + ' ' + answer).lower()
        
        # Subject-based tags
        subject_keywords = {
            'math': ['formula', 'equation', 'calculate', 'number', 'mathematics'],
            'science': ['theory', 'experiment', 'hypothesis', 'research', 'scientific'],
            'history': ['year', 'century', 'war', 'empire', 'historical'],
            'language': ['word', 'meaning', 'translation', 'language', 'grammar'],
            'geography': ['country', 'city', 'continent', 'ocean', 'mountain'],
            'biology': ['cell', 'organism', 'species', 'evolution', 'genetic']
        }
        
        for subject, keywords in subject_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(subject)
        
        # Difficulty-based tags
        if any(keyword in text for keyword in ['basic', 'simple', 'elementary']):
            tags.append('beginner')
        elif any(keyword in text for keyword in ['advanced', 'complex', 'expert']):
            tags.append('advanced')
        
        return tags[:5]  # Return up to 5 tags
