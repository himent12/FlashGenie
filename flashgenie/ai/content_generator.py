"""
AI Content Generation System for FlashGenie v1.8.5 Phase 3.

This module provides AI-powered flashcard generation, smart content suggestions,
and intelligent difficulty prediction using various AI techniques.
"""

from typing import List, Dict, Any, Optional, Tuple
import re
import random
from datetime import datetime
from dataclasses import dataclass, field
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
    valid_answers: List[str] = field(default_factory=list)  # Multiple valid answers


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

        # First, try to detect if this is a file path and provide helpful guidance
        if self._is_likely_file_path(text):
            return self._generate_example_content(content_type, max_cards)

        # Get patterns for the content type
        patterns = self.content_patterns.get(content_type, [])

        # If no specific patterns, try general content extraction
        if not patterns:
            patterns = self._get_general_patterns()

        lines = text.split('\n')
        for line in lines:
            if len(generated) >= max_cards:
                break

            line = line.strip()
            if not line or len(line) < 5:  # Skip very short lines
                continue

            # Try patterns for this content type
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    question = match.group(1).strip()
                    answer = match.group(2).strip()

                    if len(question) > 3 and len(answer) > 3:
                        difficulty = self.predict_difficulty(question, answer)
                        tags = self._generate_tags_from_content(question, answer)

                        # Generate multiple valid answers for better flexibility
                        valid_answers = self._generate_multiple_answers(question, answer, content_type)

                        generated.append(GeneratedContent(
                            question=question,
                            answer=answer,
                            content_type=content_type,
                            confidence=0.8,  # Pattern matching confidence
                            difficulty=difficulty,
                            tags=tags,
                            source="pattern_matching",
                            valid_answers=valid_answers
                        ))
                        break

            # If no pattern matched, try to create content from the line itself
            if not generated or len(generated) < max_cards:
                generated_from_line = self._generate_from_single_line(line, content_type)
                if generated_from_line:
                    generated.extend(generated_from_line)

        # If still no content generated, provide examples
        if not generated:
            generated = self._generate_example_content(content_type, max_cards)

        return generated[:max_cards]
    
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

    def _is_likely_file_path(self, text: str) -> bool:
        """Check if the text looks like a file path."""
        text = text.strip()
        # Check for common file path indicators
        if any(indicator in text for indicator in ['.csv', '.txt', '.json', '/', '\\', 'assets', 'data']):
            return True
        # Check if it's very short and doesn't contain spaces (likely a filename)
        if len(text) < 50 and ' ' not in text and '.' in text:
            return True
        return False

    def _get_general_patterns(self) -> List[str]:
        """Get general patterns that work across content types."""
        return [
            r"(.+?)\s*[-–—]\s*(.+)",     # General dash separator
            r"(.+?):\s*(.+)",            # General colon separator
            r"(.+?)\s*=\s*(.+)",         # General equals separator
            r"(.+?)\s+is\s+(.+)",        # General "is" separator
            r"(.+?)\s+means\s+(.+)",     # General "means" separator
            r"What\s+(.+?)\?\s*(.+)",    # Question format
            r"(.+?)\s*\?\s*(.+)",        # Question mark separator
        ]

    def _generate_from_single_line(self, line: str, content_type: ContentType) -> List[GeneratedContent]:
        """Generate content from a single line of text."""
        generated = []

        # Skip very short lines
        if len(line) < 10:
            return generated

        # Try to create a question from the line
        if content_type == ContentType.FACTS:
            # Convert statements to questions
            if any(word in line.lower() for word in ['is', 'was', 'are', 'were', 'has', 'have']):
                question, answer = self._convert_statement_to_question(line)
                if question and answer:
                    valid_answers = self._generate_multiple_answers(question, answer, content_type)
                    generated.append(GeneratedContent(
                        question=question,
                        answer=answer,
                        content_type=content_type,
                        confidence=0.6,
                        difficulty=self.predict_difficulty(question, answer),
                        tags=self._generate_tags_from_content(question, answer),
                        source="statement_conversion",
                        valid_answers=valid_answers
                    ))

        elif content_type == ContentType.VOCABULARY:
            # Look for potential vocabulary words (capitalized words)
            words = re.findall(r'\b[A-Z][a-z]+\b', line)
            for word in words[:2]:  # Limit to 2 words per line
                question = f"What does {word} mean?"
                answer = f"[Definition of {word} - would be provided by user]"
                valid_answers = self._generate_multiple_answers(question, answer, content_type)
                generated.append(GeneratedContent(
                    question=question,
                    answer=answer,
                    content_type=content_type,
                    confidence=0.4,
                    difficulty=0.5,
                    tags=['vocabulary', word.lower()],
                    source="vocabulary_extraction",
                    valid_answers=valid_answers
                ))

        return generated

    def _convert_statement_to_question(self, statement: str) -> Tuple[Optional[str], Optional[str]]:
        """Convert a statement into a question-answer pair."""
        statement = statement.strip()

        # Pattern: "X is Y" -> "What is X?" / "Y"
        match = re.search(r'(.+?)\s+is\s+(.+)', statement, re.IGNORECASE)
        if match:
            subject = match.group(1).strip()
            predicate = match.group(2).strip()
            question = f"What is {subject}?"
            return question, predicate

        # Pattern: "X was Y" -> "What was X?" / "Y"
        match = re.search(r'(.+?)\s+was\s+(.+)', statement, re.IGNORECASE)
        if match:
            subject = match.group(1).strip()
            predicate = match.group(2).strip()
            question = f"What was {subject}?"
            return question, predicate

        # Pattern: "X has Y" -> "What does X have?" / "Y"
        match = re.search(r'(.+?)\s+has\s+(.+)', statement, re.IGNORECASE)
        if match:
            subject = match.group(1).strip()
            predicate = match.group(2).strip()
            question = f"What does {subject} have?"
            return question, predicate

        return None, None

    def _generate_example_content(self, content_type: ContentType, max_cards: int) -> List[GeneratedContent]:
        """Generate example content when no patterns match."""
        examples = {
            ContentType.FACTS: [
                ("What is the capital of France?", "Paris", ["geography", "europe"]),
                ("What is the speed of light?", "299,792,458 m/s", ["physics", "constants"]),
                ("What is the largest planet?", "Jupiter", ["astronomy", "planets"]),
            ],
            ContentType.VOCABULARY: [
                ("What does 'hello' mean?", "A greeting", ["vocabulary", "greetings"]),
                ("What does 'thank you' mean?", "Expression of gratitude", ["vocabulary", "politeness"]),
                ("What does 'please' mean?", "Polite request word", ["vocabulary", "politeness"]),
            ],
            ContentType.DEFINITIONS: [
                ("What is photosynthesis?", "Process by which plants make food from sunlight", ["biology", "plants"]),
                ("What is gravity?", "Force that attracts objects toward each other", ["physics", "forces"]),
                ("What is democracy?", "Government by the people", ["politics", "government"]),
            ],
            ContentType.FORMULAS: [
                ("Area of a circle?", "πr²", ["math", "geometry"]),
                ("Pythagorean theorem?", "a² + b² = c²", ["math", "geometry"]),
                ("Quadratic formula?", "x = (-b ± √(b²-4ac)) / 2a", ["math", "algebra"]),
            ],
            ContentType.QUESTIONS: [
                ("Who wrote Romeo and Juliet?", "William Shakespeare", ["literature", "shakespeare"]),
                ("When did World War II end?", "1945", ["history", "world-war"]),
                ("Who painted the Mona Lisa?", "Leonardo da Vinci", ["art", "renaissance"]),
            ]
        }

        example_set = examples.get(content_type, examples[ContentType.FACTS])
        generated = []

        for i, (question, answer, tags) in enumerate(example_set[:max_cards]):
            valid_answers = self._generate_multiple_answers(question, answer, content_type)
            generated.append(GeneratedContent(
                question=question,
                answer=answer,
                content_type=content_type,
                confidence=0.9,  # High confidence for examples
                difficulty=self.predict_difficulty(question, answer),
                tags=tags,
                explanation=f"Example {content_type.value} flashcard",
                source="examples",
                valid_answers=valid_answers
            ))

        return generated

    def _generate_multiple_answers(self, question: str, primary_answer: str, content_type: ContentType) -> List[str]:
        """
        Generate multiple valid answers for a question.

        Args:
            question: The question text
            primary_answer: The primary answer
            content_type: Type of content being generated

        Returns:
            List of valid answers including the primary answer
        """
        valid_answers = [primary_answer]

        # Generate variations based on content type
        if content_type == ContentType.VOCABULARY:
            # For vocabulary, add common variations
            variations = self._generate_vocabulary_variations(primary_answer)
            valid_answers.extend(variations)

        elif content_type == ContentType.DEFINITIONS:
            # For definitions, add simplified and expanded versions
            variations = self._generate_definition_variations(primary_answer)
            valid_answers.extend(variations)

        elif content_type == ContentType.FACTS:
            # For facts, add alternative phrasings
            variations = self._generate_fact_variations(primary_answer)
            valid_answers.extend(variations)

        elif content_type == ContentType.FORMULAS:
            # For formulas, add equivalent representations
            variations = self._generate_formula_variations(primary_answer)
            valid_answers.extend(variations)

        # Remove duplicates while preserving order
        seen = set()
        unique_answers = []
        for answer in valid_answers:
            answer_lower = answer.lower().strip()
            if answer_lower not in seen and answer.strip():
                seen.add(answer_lower)
                unique_answers.append(answer.strip())

        return unique_answers[:5]  # Limit to 5 valid answers

    def _generate_vocabulary_variations(self, answer: str) -> List[str]:
        """Generate variations for vocabulary answers."""
        variations = []

        # Add "A " or "An " prefix variations
        if not answer.lower().startswith(('a ', 'an ', 'the ')):
            if answer[0].lower() in 'aeiou':
                variations.append(f"An {answer.lower()}")
            else:
                variations.append(f"A {answer.lower()}")

        # Add variations without articles
        for article in ['a ', 'an ', 'the ']:
            if answer.lower().startswith(article):
                variations.append(answer[len(article):].strip())

        # Add capitalized version
        if answer != answer.capitalize():
            variations.append(answer.capitalize())

        return variations

    def _generate_definition_variations(self, answer: str) -> List[str]:
        """Generate variations for definition answers."""
        variations = []

        # Add "It is" prefix
        if not answer.lower().startswith(('it is', 'this is', 'that is')):
            variations.append(f"It is {answer.lower()}")

        # Add "The process of" for process definitions
        if 'process' in answer.lower() and not answer.lower().startswith('the process'):
            variations.append(f"The process of {answer.lower()}")

        # Add simplified version (remove extra words)
        simplified = re.sub(r'\b(that|which|who|where|when)\b.*', '', answer, flags=re.IGNORECASE).strip()
        if simplified != answer and len(simplified) > 3:
            variations.append(simplified)

        return variations

    def _generate_fact_variations(self, answer: str) -> List[str]:
        """Generate variations for factual answers."""
        variations = []

        # Add numeric variations (if contains numbers)
        if re.search(r'\d', answer):
            # Add version with commas in numbers
            number_with_commas = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1,', answer)
            if number_with_commas != answer:
                variations.append(number_with_commas)

            # Add version without commas
            number_without_commas = re.sub(r'(\d),(\d)', r'\1\2', answer)
            if number_without_commas != answer:
                variations.append(number_without_commas)

        # Add abbreviated versions for units
        unit_abbreviations = {
            'meters per second': 'm/s',
            'kilometers per hour': 'km/h',
            'degrees celsius': '°C',
            'degrees fahrenheit': '°F',
            'kilometers': 'km',
            'meters': 'm',
            'centimeters': 'cm',
            'millimeters': 'mm'
        }

        for full_unit, abbrev in unit_abbreviations.items():
            if full_unit in answer.lower():
                variations.append(answer.lower().replace(full_unit, abbrev))
            elif abbrev in answer:
                variations.append(answer.replace(abbrev, full_unit))

        return variations

    def _generate_formula_variations(self, answer: str) -> List[str]:
        """Generate variations for formula answers."""
        variations = []

        # Add variations with different spacing
        if ' ' in answer:
            variations.append(answer.replace(' ', ''))
        else:
            # Add spaced version for operators
            spaced = re.sub(r'([+\-*/=])', r' \1 ', answer)
            variations.append(spaced)

        # Add variations with different notation
        notation_variations = {
            '²': '^2',
            '³': '^3',
            '×': '*',
            '÷': '/',
            'π': 'pi'
        }

        for original, replacement in notation_variations.items():
            if original in answer:
                variations.append(answer.replace(original, replacement))
            elif replacement in answer:
                variations.append(answer.replace(replacement, original))

        return variations
