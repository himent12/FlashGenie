"""
AI Content Generator Plugin for FlashGenie

Provides AI-powered content generation for flashcards using local language models
and pattern-based generation techniques.
"""

import json
import random
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from flashgenie.core.plugin_system import AIEnhancementPlugin
from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck


class AIContentGeneratorPlugin(AIEnhancementPlugin):
    """AI-powered content generator for flashcards."""
    
    def initialize(self) -> None:
        """Initialize the AI content generator plugin."""
        self.require_permission(self.manifest.permissions[0])  # deck_read
        self.require_permission(self.manifest.permissions[1])  # deck_write
        self.require_permission(self.manifest.permissions[2])  # user_data
        
        self.logger.info("AI Content Generator plugin initialized")
        
        # Initialize content generation templates and patterns
        self._load_generation_templates()
        self._load_knowledge_patterns()
        
        # Simple AI model simulation (in real implementation, this would use actual ML models)
        self.model_type = self.get_setting("model_type", "simple")
        self.creativity_level = self.get_setting("creativity_level", 0.7)
        
        self.logger.info(f"AI model type: {self.model_type}, creativity: {self.creativity_level}")
    
    def cleanup(self) -> None:
        """Cleanup AI resources."""
        self.logger.info("AI Content Generator plugin cleaned up")
    
    def get_ai_capabilities(self) -> List[str]:
        """Get list of AI capabilities this plugin provides."""
        return [
            "generate_flashcards",
            "expand_topics",
            "create_variations",
            "difficulty_adaptation",
            "content_enhancement",
            "knowledge_gap_filling",
            "concept_explanation",
            "example_generation"
        ]
    
    def process_content(self, content: str, task: str, **kwargs) -> Dict[str, Any]:
        """Process content using AI capabilities."""
        self.logger.info(f"Processing content for task: {task}")
        
        try:
            if task == "generate_flashcards":
                return self._generate_flashcards_from_content(content, **kwargs)
            elif task == "expand_topics":
                return self._expand_topics(content, **kwargs)
            elif task == "create_variations":
                return self._create_variations(content, **kwargs)
            elif task == "enhance_content":
                return self._enhance_content(content, **kwargs)
            elif task == "explain_concept":
                return self._explain_concept(content, **kwargs)
            elif task == "generate_examples":
                return self._generate_examples(content, **kwargs)
            else:
                return {"error": f"Unknown task: {task}"}
        
        except Exception as e:
            self.logger.error(f"Content processing failed: {e}")
            return {"error": str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the AI model used."""
        return {
            "model_type": self.model_type,
            "version": "1.0.0",
            "capabilities": self.get_ai_capabilities(),
            "creativity_level": self.creativity_level,
            "local_processing": True,
            "privacy_safe": True,
            "description": "Local AI content generation using pattern-based and template-driven approaches"
        }
    
    def _load_generation_templates(self) -> None:
        """Load content generation templates."""
        self.templates = {
            "definition": [
                "What is {term}?",
                "Define {term}.",
                "Explain the concept of {term}.",
                "What does {term} mean?",
                "{term} refers to what?"
            ],
            "example": [
                "Give an example of {concept}.",
                "What is an example of {concept}?",
                "Provide a real-world example of {concept}.",
                "How would you demonstrate {concept}?",
                "Show {concept} in practice."
            ],
            "comparison": [
                "How does {term1} differ from {term2}?",
                "Compare {term1} and {term2}.",
                "What are the similarities between {term1} and {term2}?",
                "Contrast {term1} with {term2}.",
                "{term1} vs {term2}: what's the difference?"
            ],
            "application": [
                "How is {concept} used in {context}?",
                "What are the applications of {concept}?",
                "Where would you apply {concept}?",
                "How does {concept} work in practice?",
                "What problems does {concept} solve?"
            ],
            "process": [
                "What are the steps in {process}?",
                "How do you {action}?",
                "Describe the process of {process}.",
                "What is the procedure for {process}?",
                "Outline the {process} method."
            ]
        }
    
    def _load_knowledge_patterns(self) -> None:
        """Load knowledge domain patterns."""
        self.knowledge_patterns = {
            "science": {
                "question_types": ["definition", "example", "application", "process"],
                "keywords": ["theory", "law", "principle", "experiment", "hypothesis", "method"],
                "contexts": ["laboratory", "research", "nature", "technology", "medicine"]
            },
            "language": {
                "question_types": ["definition", "example", "comparison"],
                "keywords": ["word", "phrase", "grammar", "vocabulary", "meaning", "usage"],
                "contexts": ["conversation", "writing", "literature", "communication"]
            },
            "history": {
                "question_types": ["definition", "example", "comparison", "process"],
                "keywords": ["event", "period", "figure", "cause", "effect", "timeline"],
                "contexts": ["war", "politics", "culture", "society", "economy"]
            },
            "mathematics": {
                "question_types": ["definition", "example", "application", "process"],
                "keywords": ["formula", "theorem", "proof", "calculation", "equation", "function"],
                "contexts": ["algebra", "geometry", "calculus", "statistics", "logic"]
            }
        }
    
    def _generate_flashcards_from_content(self, content: str, **kwargs) -> Dict[str, Any]:
        """Generate flashcards from given content."""
        count = kwargs.get("count", self.get_setting("max_cards_per_batch", 10))
        difficulty_level = kwargs.get("difficulty", 0.5)
        topic = kwargs.get("topic", "general")
        
        # Analyze content to extract key concepts
        concepts = self._extract_concepts(content)
        
        if not concepts:
            return {"error": "No concepts found in content"}
        
        generated_cards = []
        
        for i in range(min(count, len(concepts) * 3)):  # Generate up to 3 cards per concept
            concept = random.choice(concepts)
            card_data = self._generate_single_card(concept, content, difficulty_level, topic)
            
            if card_data:
                generated_cards.append(card_data)
        
        return {
            "success": True,
            "generated_cards": generated_cards[:count],
            "concepts_found": len(concepts),
            "total_generated": len(generated_cards[:count])
        }
    
    def _extract_concepts(self, content: str) -> List[str]:
        """Extract key concepts from content."""
        # Simple concept extraction using patterns
        concepts = []
        
        # Look for definitions (X is Y, X refers to Y, etc.)
        definition_patterns = [
            r'(\w+(?:\s+\w+)*)\s+is\s+(?:a|an|the)?\s*([^.!?]+)',
            r'(\w+(?:\s+\w+)*)\s+refers\s+to\s+([^.!?]+)',
            r'(\w+(?:\s+\w+)*)\s+means\s+([^.!?]+)',
            r'(\w+(?:\s+\w+)*)\s*:\s*([^.!?]+)'
        ]
        
        for pattern in definition_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                concept = match[0].strip()
                if len(concept.split()) <= 3 and len(concept) > 2:  # Reasonable concept length
                    concepts.append(concept)
        
        # Look for capitalized terms (potential proper nouns/concepts)
        capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        concepts.extend([term for term in capitalized_terms if len(term.split()) <= 2])
        
        # Remove duplicates and common words
        stop_words = {'The', 'This', 'That', 'These', 'Those', 'When', 'Where', 'What', 'How', 'Why'}
        concepts = list(set([c for c in concepts if c not in stop_words]))
        
        return concepts[:20]  # Limit to top 20 concepts
    
    def _generate_single_card(self, concept: str, content: str, difficulty: float, topic: str) -> Optional[Dict[str, Any]]:
        """Generate a single flashcard for a concept."""
        # Determine question type based on creativity level and difficulty
        available_types = list(self.templates.keys())
        
        if difficulty < 0.3:
            # Easy questions - focus on definitions
            question_type = random.choice(["definition", "example"])
        elif difficulty > 0.7:
            # Hard questions - focus on application and comparison
            question_type = random.choice(["application", "comparison", "process"])
        else:
            # Medium questions - any type
            question_type = random.choice(available_types)
        
        # Generate question
        question_template = random.choice(self.templates[question_type])
        
        if question_type == "comparison" and "{term2}" in question_template:
            # Need a second term for comparison
            other_concepts = [c for c in self._extract_concepts(content) if c != concept]
            if not other_concepts:
                question_type = "definition"
                question_template = random.choice(self.templates[question_type])
            else:
                term2 = random.choice(other_concepts)
                question = question_template.format(term1=concept, term2=term2)
        else:
            question = question_template.format(
                term=concept,
                concept=concept,
                context=topic,
                process=concept,
                action=f"use {concept}"
            )
        
        # Generate answer based on content analysis
        answer = self._generate_answer(concept, content, question_type, difficulty)
        
        if not answer:
            return None
        
        # Generate tags
        tags = self._generate_tags(concept, topic, question_type)
        
        # Add explanation if enabled
        explanation = ""
        if self.get_setting("include_explanations", True):
            explanation = self._generate_explanation(concept, question_type)
        
        return {
            "question": question,
            "answer": answer,
            "tags": tags,
            "difficulty": difficulty,
            "explanation": explanation,
            "concept": concept,
            "question_type": question_type,
            "ai_generated": True
        }
    
    def _generate_answer(self, concept: str, content: str, question_type: str, difficulty: float) -> str:
        """Generate answer for a concept."""
        # Extract relevant sentences from content
        sentences = [s.strip() for s in content.split('.') if concept.lower() in s.lower()]
        
        if sentences:
            # Use content-based answer
            base_answer = sentences[0]
            
            # Enhance based on question type and difficulty
            if question_type == "definition":
                return f"{concept} is {base_answer.lower()}"
            elif question_type == "example":
                return f"An example of {concept} is: {base_answer}"
            elif question_type == "application":
                return f"{concept} is used in: {base_answer}"
            else:
                return base_answer
        else:
            # Generate generic answer
            generic_answers = {
                "definition": f"{concept} is a key concept in this domain.",
                "example": f"Examples of {concept} can be found in various contexts.",
                "application": f"{concept} has multiple practical applications.",
                "comparison": f"{concept} can be compared with related concepts.",
                "process": f"The process of {concept} involves several steps."
            }
            return generic_answers.get(question_type, f"This relates to {concept}.")
    
    def _generate_tags(self, concept: str, topic: str, question_type: str) -> List[str]:
        """Generate tags for the flashcard."""
        tags = ["ai-generated", question_type]
        
        # Add topic-based tags
        if topic and topic != "general":
            tags.append(topic.lower())
        
        # Add concept-based tags
        concept_words = concept.lower().split()
        tags.extend([word for word in concept_words if len(word) > 3])
        
        # Add domain-specific tags
        for domain, patterns in self.knowledge_patterns.items():
            if any(keyword in concept.lower() for keyword in patterns["keywords"]):
                tags.append(domain)
                break
        
        return list(set(tags))[:5]  # Limit to 5 tags
    
    def _generate_explanation(self, concept: str, question_type: str) -> str:
        """Generate explanation for the flashcard."""
        explanations = {
            "definition": f"This question tests your understanding of the basic definition of {concept}.",
            "example": f"This question asks you to provide concrete examples of {concept}.",
            "application": f"This question explores practical applications of {concept}.",
            "comparison": f"This question requires you to compare {concept} with related concepts.",
            "process": f"This question tests your knowledge of the steps involved in {concept}."
        }
        return explanations.get(question_type, f"This question relates to {concept}.")
    
    def _expand_topics(self, topic: str, **kwargs) -> Dict[str, Any]:
        """Expand a topic into related subtopics."""
        count = kwargs.get("count", 5)
        
        # Simple topic expansion using patterns
        expansions = []
        
        # Generate related topics
        prefixes = ["Introduction to", "Advanced", "Practical", "Theoretical", "Applied"]
        suffixes = ["Fundamentals", "Principles", "Applications", "Methods", "Techniques"]
        
        for i in range(count):
            if i < len(prefixes):
                expansion = f"{prefixes[i]} {topic}"
            else:
                expansion = f"{topic} {suffixes[i % len(suffixes)]}"
            
            expansions.append({
                "topic": expansion,
                "description": f"Detailed study of {expansion.lower()}",
                "estimated_cards": random.randint(10, 30),
                "difficulty": random.uniform(0.3, 0.8)
            })
        
        return {
            "success": True,
            "original_topic": topic,
            "expansions": expansions
        }
    
    def _create_variations(self, content: str, **kwargs) -> Dict[str, Any]:
        """Create variations of existing content."""
        variation_count = kwargs.get("count", 3)
        
        variations = []
        
        # Simple variation techniques
        techniques = [
            "Rephrase the question",
            "Change the difficulty level",
            "Add context",
            "Focus on different aspects",
            "Use different examples"
        ]
        
        for i in range(variation_count):
            technique = techniques[i % len(techniques)]
            variation = {
                "technique": technique,
                "content": f"Variation using {technique.lower()}: {content[:100]}...",
                "difficulty_change": random.choice([-0.1, 0.0, 0.1])
            }
            variations.append(variation)
        
        return {
            "success": True,
            "original_content": content[:100] + "...",
            "variations": variations
        }
    
    def _enhance_content(self, content: str, **kwargs) -> Dict[str, Any]:
        """Enhance existing content with additional information."""
        enhancements = [
            "Added contextual examples",
            "Included related concepts",
            "Provided memory aids",
            "Added difficulty progression",
            "Included practical applications"
        ]
        
        return {
            "success": True,
            "original_content": content,
            "enhanced_content": content + " [Enhanced with AI-generated context and examples]",
            "enhancements_applied": random.sample(enhancements, 3)
        }
    
    def _explain_concept(self, concept: str, **kwargs) -> Dict[str, Any]:
        """Generate explanation for a concept."""
        explanation_depth = kwargs.get("depth", "medium")
        
        explanations = {
            "basic": f"{concept} is a fundamental concept that requires understanding.",
            "medium": f"{concept} is an important concept with multiple applications and implications.",
            "advanced": f"{concept} is a complex concept that involves deep understanding of underlying principles and relationships."
        }
        
        return {
            "success": True,
            "concept": concept,
            "explanation": explanations.get(explanation_depth, explanations["medium"]),
            "depth": explanation_depth,
            "related_concepts": [f"Related to {concept}", f"Similar to {concept}", f"Opposite of {concept}"]
        }
    
    def _generate_examples(self, concept: str, **kwargs) -> Dict[str, Any]:
        """Generate examples for a concept."""
        example_count = kwargs.get("count", 3)
        
        examples = []
        for i in range(example_count):
            examples.append({
                "example": f"Example {i+1} of {concept}",
                "context": f"Real-world application in context {i+1}",
                "difficulty": random.uniform(0.2, 0.8)
            })
        
        return {
            "success": True,
            "concept": concept,
            "examples": examples,
            "total_generated": len(examples)
        }
