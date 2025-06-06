"""
Advanced tagging system for FlashGenie.

This module provides hierarchical tagging, auto-tagging based on content analysis,
and smart tag management for better organization of flashcards.
"""

import re
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import json
from pathlib import Path

from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck
from flashgenie.config import DATA_DIR


@dataclass
class TagHierarchy:
    """Represents a hierarchical tag structure."""
    name: str
    parent: Optional[str] = None
    children: Set[str] = field(default_factory=set)
    description: str = ""
    color: Optional[str] = None  # For future GUI use
    
    def get_full_path(self, tag_manager: 'TagManager') -> str:
        """Get the full hierarchical path of this tag."""
        if not self.parent:
            return self.name
        
        parent_tag = tag_manager.get_tag_hierarchy(self.parent)
        if parent_tag:
            return f"{parent_tag.get_full_path(tag_manager)} > {self.name}"
        return self.name


class TagManager:
    """
    Advanced tag management system with hierarchical organization and auto-tagging.
    """
    
    def __init__(self):
        """Initialize the tag manager."""
        self.tag_hierarchies: Dict[str, TagHierarchy] = {}
        self.tag_aliases: Dict[str, str] = {}  # alias -> canonical_name
        self.auto_tag_rules: List[Dict[str, Any]] = []
        self.tag_stats: Dict[str, int] = defaultdict(int)
        
        # Load existing tag data
        self.tags_file = DATA_DIR / "tag_hierarchies.json"
        self.load_tag_data()
        
        # Initialize common tag patterns
        self._initialize_common_patterns()
    
    def create_tag(self, name: str, parent: Optional[str] = None, 
                   description: str = "", color: Optional[str] = None) -> TagHierarchy:
        """
        Create a new tag with optional hierarchy.
        
        Args:
            name: Tag name
            parent: Parent tag name (for hierarchy)
            description: Tag description
            color: Optional color for GUI
            
        Returns:
            Created tag hierarchy
        """
        # Normalize tag name
        normalized_name = self._normalize_tag_name(name)
        
        # Check if tag already exists
        if normalized_name in self.tag_hierarchies:
            return self.tag_hierarchies[normalized_name]
        
        # Validate parent exists
        if parent and parent not in self.tag_hierarchies:
            raise ValueError(f"Parent tag '{parent}' does not exist")
        
        # Create tag
        tag = TagHierarchy(
            name=normalized_name,
            parent=parent,
            description=description,
            color=color
        )
        
        self.tag_hierarchies[normalized_name] = tag
        
        # Update parent's children
        if parent:
            self.tag_hierarchies[parent].children.add(normalized_name)
        
        # Save changes
        self.save_tag_data()
        
        return tag
    
    def create_hierarchical_tag(self, path: str, descriptions: Dict[str, str] = None) -> TagHierarchy:
        """
        Create a hierarchical tag from a path like "Science > Biology > Cell Structure".
        
        Args:
            path: Hierarchical path separated by " > "
            descriptions: Optional descriptions for each level
            
        Returns:
            The leaf tag in the hierarchy
        """
        descriptions = descriptions or {}
        parts = [part.strip() for part in path.split(">")]
        
        parent = None
        for part in parts:
            normalized_part = self._normalize_tag_name(part)
            
            if normalized_part not in self.tag_hierarchies:
                self.create_tag(
                    name=normalized_part,
                    parent=parent,
                    description=descriptions.get(part, "")
                )
            
            parent = normalized_part
        
        return self.tag_hierarchies[parent]
    
    def add_alias(self, alias: str, canonical_name: str) -> None:
        """
        Add an alias for a tag.
        
        Args:
            alias: Alternative name for the tag
            canonical_name: The canonical tag name
        """
        if canonical_name not in self.tag_hierarchies:
            raise ValueError(f"Canonical tag '{canonical_name}' does not exist")
        
        self.tag_aliases[self._normalize_tag_name(alias)] = canonical_name
        self.save_tag_data()
    
    def resolve_tag_name(self, name: str) -> str:
        """
        Resolve a tag name to its canonical form.
        
        Args:
            name: Tag name or alias
            
        Returns:
            Canonical tag name
        """
        normalized = self._normalize_tag_name(name)
        return self.tag_aliases.get(normalized, normalized)
    
    def get_tag_hierarchy(self, name: str) -> Optional[TagHierarchy]:
        """Get tag hierarchy by name."""
        canonical_name = self.resolve_tag_name(name)
        return self.tag_hierarchies.get(canonical_name)
    
    def get_all_children(self, tag_name: str) -> Set[str]:
        """Get all descendant tags of a given tag."""
        tag = self.get_tag_hierarchy(tag_name)
        if not tag:
            return set()
        
        children = set(tag.children)
        for child in tag.children:
            children.update(self.get_all_children(child))
        
        return children
    
    def get_tag_path(self, tag_name: str) -> List[str]:
        """Get the full path from root to the given tag."""
        tag = self.get_tag_hierarchy(tag_name)
        if not tag:
            return []
        
        path = [tag.name]
        while tag.parent:
            tag = self.get_tag_hierarchy(tag.parent)
            if tag:
                path.insert(0, tag.name)
            else:
                break
        
        return path
    
    def suggest_tags(self, question: str, answer: str, existing_tags: List[str] = None) -> List[str]:
        """
        Suggest tags based on content analysis.
        
        Args:
            question: Flashcard question
            answer: Flashcard answer
            existing_tags: Already assigned tags
            
        Returns:
            List of suggested tag names
        """
        existing_tags = existing_tags or []
        suggestions = set()
        
        # Combine question and answer for analysis
        content = f"{question} {answer}".lower()
        
        # Apply auto-tagging rules
        for rule in self.auto_tag_rules:
            if self._matches_rule(content, rule):
                suggestions.add(rule['tag'])
        
        # Remove already existing tags
        suggestions = suggestions - set(existing_tags)
        
        # Sort by relevance (frequency in content)
        suggestion_scores = []
        for tag in suggestions:
            score = self._calculate_tag_relevance(content, tag)
            suggestion_scores.append((tag, score))
        
        # Return top suggestions
        suggestion_scores.sort(key=lambda x: x[1], reverse=True)
        return [tag for tag, score in suggestion_scores[:5]]
    
    def auto_categorize(self, flashcard: Flashcard) -> List[str]:
        """
        Automatically categorize a flashcard based on content.
        
        Args:
            flashcard: Flashcard to categorize
            
        Returns:
            List of suggested tags
        """
        suggestions = self.suggest_tags(
            flashcard.question, 
            flashcard.answer, 
            flashcard.tags
        )
        
        # Filter to only include high-confidence suggestions
        high_confidence_tags = []
        content = f"{flashcard.question} {flashcard.answer}".lower()
        
        for tag in suggestions:
            confidence = self._calculate_tag_confidence(content, tag)
            if confidence > 0.7:  # High confidence threshold
                high_confidence_tags.append(tag)
        
        return high_confidence_tags
    
    def add_auto_tag_rule(self, patterns: List[str], tag: str, 
                         rule_type: str = "keyword") -> None:
        """
        Add an automatic tagging rule.
        
        Args:
            patterns: List of patterns to match
            tag: Tag to apply when pattern matches
            rule_type: Type of rule (keyword, regex, etc.)
        """
        rule = {
            'patterns': patterns,
            'tag': tag,
            'type': rule_type
        }
        self.auto_tag_rules.append(rule)
        self.save_tag_data()
    
    def get_tag_statistics(self) -> Dict[str, Any]:
        """Get statistics about tag usage."""
        return {
            'total_tags': len(self.tag_hierarchies),
            'total_aliases': len(self.tag_aliases),
            'total_rules': len(self.auto_tag_rules),
            'tag_usage': dict(self.tag_stats),
            'hierarchy_depth': self._calculate_max_depth(),
            'orphaned_tags': self._find_orphaned_tags()
        }
    
    def _normalize_tag_name(self, name: str) -> str:
        """Normalize tag name for consistency."""
        # Convert to lowercase, strip whitespace, replace spaces with underscores
        normalized = name.strip().lower()
        normalized = re.sub(r'\s+', '_', normalized)
        normalized = re.sub(r'[^\w\-_]', '', normalized)
        return normalized
    
    def _matches_rule(self, content: str, rule: Dict[str, Any]) -> bool:
        """Check if content matches an auto-tagging rule."""
        if rule['type'] == 'keyword':
            return any(pattern.lower() in content for pattern in rule['patterns'])
        elif rule['type'] == 'regex':
            return any(re.search(pattern, content, re.IGNORECASE) for pattern in rule['patterns'])
        return False
    
    def _calculate_tag_relevance(self, content: str, tag: str) -> float:
        """Calculate relevance score for a tag based on content."""
        tag_hierarchy = self.get_tag_hierarchy(tag)
        if not tag_hierarchy:
            return 0.0
        
        # Simple keyword matching for now
        tag_words = tag.replace('_', ' ').split()
        matches = sum(1 for word in tag_words if word in content)
        
        return matches / len(tag_words) if tag_words else 0.0
    
    def _calculate_tag_confidence(self, content: str, tag: str) -> float:
        """Calculate confidence score for auto-tagging."""
        # This is a simplified implementation
        # In practice, this could use more sophisticated NLP
        relevance = self._calculate_tag_relevance(content, tag)
        
        # Boost confidence for exact matches
        if tag.replace('_', ' ') in content:
            relevance += 0.3
        
        return min(1.0, relevance)
    
    def _calculate_max_depth(self) -> int:
        """Calculate maximum hierarchy depth."""
        max_depth = 0
        for tag_name in self.tag_hierarchies:
            depth = len(self.get_tag_path(tag_name))
            max_depth = max(max_depth, depth)
        return max_depth
    
    def _find_orphaned_tags(self) -> List[str]:
        """Find tags that are not used by any flashcards."""
        # This would need to be called with actual deck data
        # For now, return empty list
        return []
    
    def _initialize_common_patterns(self) -> None:
        """Initialize common auto-tagging patterns."""
        common_rules = [
            # Academic subjects
            (['math', 'mathematics', 'algebra', 'geometry', 'calculus'], 'mathematics'),
            (['science', 'physics', 'chemistry', 'biology'], 'science'),
            (['history', 'historical', 'war', 'ancient', 'medieval'], 'history'),
            (['language', 'grammar', 'vocabulary', 'literature'], 'language'),
            
            # Programming
            (['python', 'java', 'javascript', 'programming', 'code'], 'programming'),
            (['algorithm', 'data structure', 'computer science'], 'computer_science'),
            
            # Difficulty indicators
            (['basic', 'fundamental', 'introduction'], 'beginner'),
            (['advanced', 'complex', 'difficult'], 'advanced'),
            (['intermediate', 'moderate'], 'intermediate'),
        ]
        
        for patterns, tag in common_rules:
            if not any(rule['tag'] == tag for rule in self.auto_tag_rules):
                self.add_auto_tag_rule(patterns, tag, 'keyword')
    
    def save_tag_data(self) -> None:
        """Save tag data to file."""
        data = {
            'hierarchies': {
                name: {
                    'name': tag.name,
                    'parent': tag.parent,
                    'children': list(tag.children),
                    'description': tag.description,
                    'color': tag.color
                }
                for name, tag in self.tag_hierarchies.items()
            },
            'aliases': self.tag_aliases,
            'auto_tag_rules': self.auto_tag_rules,
            'tag_stats': dict(self.tag_stats)
        }
        
        self.tags_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tags_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_tag_data(self) -> None:
        """Load tag data from file."""
        if not self.tags_file.exists():
            return
        
        try:
            with open(self.tags_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load hierarchies
            for name, tag_data in data.get('hierarchies', {}).items():
                tag = TagHierarchy(
                    name=tag_data['name'],
                    parent=tag_data.get('parent'),
                    children=set(tag_data.get('children', [])),
                    description=tag_data.get('description', ''),
                    color=tag_data.get('color')
                )
                self.tag_hierarchies[name] = tag
            
            # Load aliases
            self.tag_aliases = data.get('aliases', {})
            
            # Load auto-tag rules
            self.auto_tag_rules = data.get('auto_tag_rules', [])
            
            # Load tag stats
            self.tag_stats = defaultdict(int, data.get('tag_stats', {}))
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load tag data: {e}")
            # Continue with empty data
