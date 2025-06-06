"""
Deck management for FlashGenie.

This module defines the Deck class that manages collections of flashcards,
including metadata, filtering, and persistence operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Iterator
from dataclasses import dataclass, field
import uuid
import json
from pathlib import Path

from flashgenie.core.flashcard import Flashcard
from flashgenie.config import DECKS_DIR


@dataclass
class Deck:
    """
    Represents a collection of flashcards with metadata and management capabilities.
    
    Attributes:
        name: Human-readable name for the deck
        deck_id: Unique identifier for the deck
        description: Optional description of the deck
        created_at: When the deck was created
        modified_at: When the deck was last modified
        tags: Tags for categorization
        flashcards: List of flashcards in the deck
        metadata: Additional metadata dictionary
    """
    
    name: str
    deck_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    flashcards: List[Flashcard] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate deck data after initialization."""
        if not self.name.strip():
            raise ValueError("Deck name cannot be empty")
    
    @property
    def size(self) -> int:
        """Get the number of flashcards in the deck."""
        return len(self.flashcards)
    
    @property
    def due_cards(self) -> List[Flashcard]:
        """Get all cards that are due for review."""
        return [card for card in self.flashcards if card.is_due]
    
    @property
    def due_count(self) -> int:
        """Get the number of cards due for review."""
        return len(self.due_cards)
    
    @property
    def average_accuracy(self) -> float:
        """Calculate the average accuracy across all cards."""
        if not self.flashcards:
            return 0.0
        
        total_accuracy = sum(card.accuracy for card in self.flashcards)
        return total_accuracy / len(self.flashcards)
    
    def add_flashcard(self, flashcard: Flashcard) -> None:
        """
        Add a flashcard to the deck.
        
        Args:
            flashcard: The flashcard to add
        """
        if flashcard not in self.flashcards:
            self.flashcards.append(flashcard)
            self.modified_at = datetime.now()
    
    def remove_flashcard(self, card_id: str) -> bool:
        """
        Remove a flashcard from the deck by ID.
        
        Args:
            card_id: The ID of the card to remove
            
        Returns:
            True if card was removed, False if not found
        """
        for i, card in enumerate(self.flashcards):
            if card.card_id == card_id:
                del self.flashcards[i]
                self.modified_at = datetime.now()
                return True
        return False
    
    def get_flashcard(self, card_id: str) -> Optional[Flashcard]:
        """
        Get a flashcard by ID.
        
        Args:
            card_id: The ID of the card to retrieve
            
        Returns:
            The flashcard if found, None otherwise
        """
        for card in self.flashcards:
            if card.card_id == card_id:
                return card
        return None
    
    def filter_by_tags(self, tags: List[str]) -> List[Flashcard]:
        """
        Filter flashcards by tags.
        
        Args:
            tags: List of tags to filter by
            
        Returns:
            List of flashcards that have any of the specified tags
        """
        return [
            card for card in self.flashcards
            if any(tag in card.tags for tag in tags)
        ]
    
    def get_cards_by_difficulty(self, min_difficulty: float = 0.0, 
                               max_difficulty: float = 1.0) -> List[Flashcard]:
        """
        Get cards within a difficulty range.
        
        Args:
            min_difficulty: Minimum difficulty (0.0 to 1.0)
            max_difficulty: Maximum difficulty (0.0 to 1.0)
            
        Returns:
            List of flashcards within the difficulty range
        """
        return [
            card for card in self.flashcards
            if min_difficulty <= card.difficulty <= max_difficulty
        ]
    
    def shuffle_cards(self) -> None:
        """Shuffle the order of flashcards in the deck."""
        import random
        random.shuffle(self.flashcards)
        self.modified_at = datetime.now()
    
    def sort_by_difficulty(self, reverse: bool = False) -> None:
        """
        Sort flashcards by difficulty.
        
        Args:
            reverse: If True, sort from hardest to easiest
        """
        self.flashcards.sort(key=lambda card: card.difficulty, reverse=reverse)
        self.modified_at = datetime.now()
    
    def sort_by_due_date(self) -> None:
        """Sort flashcards by next review date (due cards first)."""
        self.flashcards.sort(key=lambda card: card.next_review)
        self.modified_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert deck to dictionary for serialization."""
        return {
            "deck_id": self.deck_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "tags": self.tags,
            "flashcards": [card.to_dict() for card in self.flashcards],
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Deck":
        """Create deck from dictionary."""
        # Parse datetime fields
        created_at = datetime.fromisoformat(data["created_at"])
        modified_at = datetime.fromisoformat(data["modified_at"])
        
        # Create flashcards
        flashcards = [
            Flashcard.from_dict(card_data) 
            for card_data in data.get("flashcards", [])
        ]
        
        return cls(
            deck_id=data["deck_id"],
            name=data["name"],
            description=data.get("description", ""),
            created_at=created_at,
            modified_at=modified_at,
            tags=data.get("tags", []),
            flashcards=flashcards,
            metadata=data.get("metadata", {}),
        )
    
    def save(self, file_path: Optional[Path] = None) -> Path:
        """
        Save the deck to a JSON file.
        
        Args:
            file_path: Optional custom file path
            
        Returns:
            Path where the deck was saved
        """
        if file_path is None:
            file_path = DECKS_DIR / f"{self.deck_id}.json"
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        
        return file_path
    
    @classmethod
    def load(cls, file_path: Path) -> "Deck":
        """
        Load a deck from a JSON file.
        
        Args:
            file_path: Path to the deck file
            
        Returns:
            Loaded deck instance
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def list_saved_decks(cls) -> List[Dict[str, Any]]:
        """
        List all saved decks with basic metadata.
        
        Returns:
            List of dictionaries with deck metadata
        """
        decks = []
        for deck_file in DECKS_DIR.glob("*.json"):
            try:
                with open(deck_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    decks.append({
                        "deck_id": data["deck_id"],
                        "name": data["name"],
                        "description": data.get("description", ""),
                        "size": len(data.get("flashcards", [])),
                        "created_at": data["created_at"],
                        "modified_at": data["modified_at"],
                        "file_path": deck_file,
                    })
            except (json.JSONDecodeError, KeyError):
                # Skip invalid deck files
                continue
        
        return sorted(decks, key=lambda x: x["modified_at"], reverse=True)
    
    def __len__(self) -> int:
        """Return the number of flashcards in the deck."""
        return len(self.flashcards)
    
    def __iter__(self) -> Iterator[Flashcard]:
        """Iterate over flashcards in the deck."""
        return iter(self.flashcards)
    
    def __str__(self) -> str:
        """String representation of the deck."""
        return f"Deck('{self.name}', {len(self.flashcards)} cards)"
    
    def __repr__(self) -> str:
        """Detailed string representation of the deck."""
        return (f"Deck(id={self.deck_id}, name='{self.name}', "
                f"size={len(self.flashcards)}, due={self.due_count})")
