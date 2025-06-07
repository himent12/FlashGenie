"""
Smart collections system for FlashGenie.

This module provides dynamic collections that automatically group flashcards
based on various criteria like difficulty, performance, tags, and learning patterns.
"""

from typing import List, Dict, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path

from .flashcard import Flashcard
from .deck import Deck
from .tag_manager import TagManager
from flashgenie.config import DATA_DIR


class CollectionType(Enum):
    """Types of smart collections."""
    DIFFICULTY = "difficulty"
    PERFORMANCE = "performance"
    TAG_BASED = "tag_based"
    TEMPORAL = "temporal"
    CUSTOM = "custom"


@dataclass
class CollectionCriteria:
    """Criteria for smart collection filtering."""
    collection_type: CollectionType
    name: str
    description: str
    filters: Dict[str, Any] = field(default_factory=dict)
    auto_update: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: Optional[datetime] = None


class SmartCollection:
    """
    A smart collection that dynamically groups flashcards based on criteria.
    """
    
    def __init__(self, criteria: CollectionCriteria, tag_manager: TagManager = None):
        """
        Initialize a smart collection.
        
        Args:
            criteria: Collection criteria
            tag_manager: Tag manager for tag-based collections
        """
        self.criteria = criteria
        self.tag_manager = tag_manager or TagManager()
        self._cached_cards: List[Flashcard] = []
        self._cache_timestamp: Optional[datetime] = None
        self._cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
    
    def get_cards(self, deck: Deck, force_refresh: bool = False) -> List[Flashcard]:
        """
        Get cards that match the collection criteria.
        
        Args:
            deck: Deck to filter cards from
            force_refresh: Force refresh of cached results
            
        Returns:
            List of matching flashcards
        """
        # Check cache validity
        if (not force_refresh and self._cached_cards and self._cache_timestamp and 
            datetime.now() - self._cache_timestamp < self._cache_duration):
            return self._cached_cards
        
        # Filter cards based on criteria
        matching_cards = self._filter_cards(deck.flashcards)
        
        # Update cache
        self._cached_cards = matching_cards
        self._cache_timestamp = datetime.now()
        self.criteria.last_updated = datetime.now()
        
        return matching_cards
    
    def _filter_cards(self, cards: List[Flashcard]) -> List[Flashcard]:
        """Filter cards based on collection criteria."""
        if self.criteria.collection_type == CollectionType.DIFFICULTY:
            return self._filter_by_difficulty(cards)
        elif self.criteria.collection_type == CollectionType.PERFORMANCE:
            return self._filter_by_performance(cards)
        elif self.criteria.collection_type == CollectionType.TAG_BASED:
            return self._filter_by_tags(cards)
        elif self.criteria.collection_type == CollectionType.TEMPORAL:
            return self._filter_by_temporal(cards)
        elif self.criteria.collection_type == CollectionType.CUSTOM:
            return self._filter_by_custom(cards)
        else:
            return cards
    
    def _filter_by_difficulty(self, cards: List[Flashcard]) -> List[Flashcard]:
        """Filter cards by difficulty level."""
        min_difficulty = self.criteria.filters.get('min_difficulty', 0.0)
        max_difficulty = self.criteria.filters.get('max_difficulty', 1.0)
        
        return [
            card for card in cards
            if min_difficulty <= card.difficulty <= max_difficulty
        ]
    
    def _filter_by_performance(self, cards: List[Flashcard]) -> List[Flashcard]:
        """Filter cards by performance metrics."""
        filters = self.criteria.filters
        matching_cards = []
        
        for card in cards:
            # Skip cards with insufficient review data
            if card.review_count < filters.get('min_reviews', 1):
                continue
            
            # Accuracy filter
            if 'min_accuracy' in filters and card.accuracy < filters['min_accuracy']:
                continue
            if 'max_accuracy' in filters and card.accuracy > filters['max_accuracy']:
                continue
            
            # Response time filter
            if 'max_avg_response_time' in filters:
                if card.average_response_time > filters['max_avg_response_time']:
                    continue
            
            # Review count filter
            if 'min_review_count' in filters and card.review_count < filters['min_review_count']:
                continue
            if 'max_review_count' in filters and card.review_count > filters['max_review_count']:
                continue
            
            matching_cards.append(card)
        
        return matching_cards
    
    def _filter_by_tags(self, cards: List[Flashcard]) -> List[Flashcard]:
        """Filter cards by tag criteria."""
        required_tags = set(self.criteria.filters.get('required_tags', []))
        excluded_tags = set(self.criteria.filters.get('excluded_tags', []))
        any_of_tags = set(self.criteria.filters.get('any_of_tags', []))
        include_children = self.criteria.filters.get('include_children', True)
        
        matching_cards = []
        
        for card in cards:
            card_tags = set(card.tags)
            
            # Expand tags to include children if requested
            if include_children:
                expanded_tags = set(card_tags)
                for tag in card_tags:
                    children = self.tag_manager.get_all_children(tag)
                    expanded_tags.update(children)
                card_tags = expanded_tags
            
            # Check required tags
            if required_tags and not required_tags.issubset(card_tags):
                continue
            
            # Check excluded tags
            if excluded_tags and excluded_tags.intersection(card_tags):
                continue
            
            # Check any_of_tags
            if any_of_tags and not any_of_tags.intersection(card_tags):
                continue
            
            matching_cards.append(card)
        
        return matching_cards
    
    def _filter_by_temporal(self, cards: List[Flashcard]) -> List[Flashcard]:
        """Filter cards by temporal criteria."""
        now = datetime.now()
        filters = self.criteria.filters
        matching_cards = []
        
        for card in cards:
            # Due date filters
            if filters.get('due_only', False) and not card.is_due:
                continue
            
            if filters.get('not_due_only', False) and card.is_due:
                continue
            
            # Creation date filters
            if 'created_after' in filters:
                created_after = datetime.fromisoformat(filters['created_after'])
                if card.created_at < created_after:
                    continue
            
            if 'created_before' in filters:
                created_before = datetime.fromisoformat(filters['created_before'])
                if card.created_at > created_before:
                    continue
            
            # Last reviewed filters
            if 'reviewed_after' in filters and card.last_reviewed:
                reviewed_after = datetime.fromisoformat(filters['reviewed_after'])
                if card.last_reviewed < reviewed_after:
                    continue
            
            if 'reviewed_before' in filters and card.last_reviewed:
                reviewed_before = datetime.fromisoformat(filters['reviewed_before'])
                if card.last_reviewed > reviewed_before:
                    continue
            
            # Days since last review
            if 'min_days_since_review' in filters and card.last_reviewed:
                days_since = (now - card.last_reviewed).days
                if days_since < filters['min_days_since_review']:
                    continue
            
            matching_cards.append(card)
        
        return matching_cards
    
    def _filter_by_custom(self, cards: List[Flashcard]) -> List[Flashcard]:
        """Filter cards by custom criteria."""
        # This would allow for custom filter functions
        # For now, return all cards
        return cards
    
    def get_statistics(self, deck: Deck) -> Dict[str, Any]:
        """Get statistics about the collection."""
        cards = self.get_cards(deck)
        
        if not cards:
            return {
                'total_cards': 0,
                'collection_name': self.criteria.name,
                'collection_type': self.criteria.collection_type.value
            }
        
        # Calculate statistics
        total_cards = len(cards)
        due_cards = sum(1 for card in cards if card.is_due)
        avg_difficulty = sum(card.difficulty for card in cards) / total_cards if total_cards > 0 else 0.0
        avg_accuracy = sum(card.accuracy for card in cards if card.review_count > 0)
        reviewed_cards = sum(1 for card in cards if card.review_count > 0)
        
        if reviewed_cards > 0:
            avg_accuracy /= reviewed_cards
        else:
            avg_accuracy = 0.0
        
        return {
            'total_cards': total_cards,
            'due_cards': due_cards,
            'avg_difficulty': avg_difficulty,
            'avg_accuracy': avg_accuracy,
            'reviewed_cards': reviewed_cards,
            'collection_name': self.criteria.name,
            'collection_type': self.criteria.collection_type.value,
            'last_updated': self.criteria.last_updated.isoformat() if self.criteria.last_updated else None
        }


class SmartCollectionManager:
    """
    Manages multiple smart collections and provides predefined collections.
    """
    
    def __init__(self, tag_manager: TagManager = None):
        """Initialize the smart collection manager."""
        self.tag_manager = tag_manager or TagManager()
        self.collections: Dict[str, SmartCollection] = {}
        self.collections_file = DATA_DIR / "smart_collections.json"
        
        # Load existing collections
        self.load_collections()
        
        # Create default collections if none exist
        if not self.collections:
            self._create_default_collections()
    
    def create_collection(self, criteria: CollectionCriteria) -> SmartCollection:
        """Create a new smart collection."""
        collection = SmartCollection(criteria, self.tag_manager)
        self.collections[criteria.name] = collection
        self.save_collections()
        return collection
    
    def get_collection(self, name: str) -> Optional[SmartCollection]:
        """Get a collection by name."""
        return self.collections.get(name)
    
    def list_collections(self) -> List[str]:
        """List all collection names."""
        return list(self.collections.keys())
    
    def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        if name in self.collections:
            del self.collections[name]
            self.save_collections()
            return True
        return False
    
    def create_difficulty_collection(self, name: str, min_difficulty: float, 
                                   max_difficulty: float) -> SmartCollection:
        """Create a difficulty-based collection."""
        criteria = CollectionCriteria(
            collection_type=CollectionType.DIFFICULTY,
            name=name,
            description=f"Cards with difficulty between {min_difficulty:.1f} and {max_difficulty:.1f}",
            filters={
                'min_difficulty': min_difficulty,
                'max_difficulty': max_difficulty
            }
        )
        return self.create_collection(criteria)
    
    def create_performance_collection(self, name: str, min_accuracy: float = None,
                                    max_accuracy: float = None, 
                                    min_reviews: int = 3) -> SmartCollection:
        """Create a performance-based collection."""
        filters = {'min_reviews': min_reviews}
        description_parts = []
        
        if min_accuracy is not None:
            filters['min_accuracy'] = min_accuracy
            description_parts.append(f"accuracy >= {min_accuracy:.1%}")
        
        if max_accuracy is not None:
            filters['max_accuracy'] = max_accuracy
            description_parts.append(f"accuracy <= {max_accuracy:.1%}")
        
        description = f"Cards with {', '.join(description_parts)}" if description_parts else "Performance-based collection"
        
        criteria = CollectionCriteria(
            collection_type=CollectionType.PERFORMANCE,
            name=name,
            description=description,
            filters=filters
        )
        return self.create_collection(criteria)
    
    def create_tag_collection(self, name: str, required_tags: List[str] = None,
                            excluded_tags: List[str] = None,
                            any_of_tags: List[str] = None) -> SmartCollection:
        """Create a tag-based collection."""
        filters = {}
        description_parts = []
        
        if required_tags:
            filters['required_tags'] = required_tags
            description_parts.append(f"must have: {', '.join(required_tags)}")
        
        if excluded_tags:
            filters['excluded_tags'] = excluded_tags
            description_parts.append(f"must not have: {', '.join(excluded_tags)}")
        
        if any_of_tags:
            filters['any_of_tags'] = any_of_tags
            description_parts.append(f"any of: {', '.join(any_of_tags)}")
        
        description = f"Cards with tags - {'; '.join(description_parts)}" if description_parts else "Tag-based collection"
        
        criteria = CollectionCriteria(
            collection_type=CollectionType.TAG_BASED,
            name=name,
            description=description,
            filters=filters
        )
        return self.create_collection(criteria)
    
    def _create_default_collections(self) -> None:
        """Create default smart collections."""
        # Difficulty-based collections
        self.create_difficulty_collection("Easy Cards", 0.0, 0.3)
        self.create_difficulty_collection("Medium Cards", 0.3, 0.7)
        self.create_difficulty_collection("Hard Cards", 0.7, 1.0)
        
        # Performance-based collections
        self.create_performance_collection("Struggling Cards", max_accuracy=0.6)
        self.create_performance_collection("Mastered Cards", min_accuracy=0.9)
        
        # Temporal collections
        due_criteria = CollectionCriteria(
            collection_type=CollectionType.TEMPORAL,
            name="Due for Review",
            description="Cards that are due for review",
            filters={'due_only': True}
        )
        self.create_collection(due_criteria)
        
        recent_criteria = CollectionCriteria(
            collection_type=CollectionType.TEMPORAL,
            name="Recently Added",
            description="Cards added in the last 7 days",
            filters={
                'created_after': (datetime.now() - timedelta(days=7)).isoformat()
            }
        )
        self.create_collection(recent_criteria)
    
    def save_collections(self) -> None:
        """Save collections to file."""
        data = {}
        for name, collection in self.collections.items():
            criteria = collection.criteria
            data[name] = {
                'collection_type': criteria.collection_type.value,
                'name': criteria.name,
                'description': criteria.description,
                'filters': criteria.filters,
                'auto_update': criteria.auto_update,
                'created_at': criteria.created_at.isoformat(),
                'last_updated': criteria.last_updated.isoformat() if criteria.last_updated else None
            }
        
        self.collections_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.collections_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_collections(self) -> None:
        """Load collections from file."""
        if not self.collections_file.exists():
            return
        
        try:
            with open(self.collections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for name, collection_data in data.items():
                criteria = CollectionCriteria(
                    collection_type=CollectionType(collection_data['collection_type']),
                    name=collection_data['name'],
                    description=collection_data['description'],
                    filters=collection_data['filters'],
                    auto_update=collection_data.get('auto_update', True),
                    created_at=datetime.fromisoformat(collection_data['created_at']),
                    last_updated=datetime.fromisoformat(collection_data['last_updated']) if collection_data.get('last_updated') else None
                )
                
                collection = SmartCollection(criteria, self.tag_manager)
                self.collections[name] = collection
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Warning: Could not load smart collections: {e}")
            # Continue with empty collections
