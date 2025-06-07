"""
Base importer class for FlashGenie.

This module defines the abstract base class for all file importers,
providing a common interface and validation functionality.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

from flashgenie.core.content_system.flashcard import Flashcard
from flashgenie.core.content_system.deck import Deck
from flashgenie.utils.exceptions import ImportError, ValidationError


class BaseImporter(ABC):
    """
    Abstract base class for all file importers.
    
    This class defines the common interface that all importers must implement
    and provides shared validation and utility methods.
    """
    
    def __init__(self, encoding: str = 'utf-8'):
        """
        Initialize the importer.
        
        Args:
            encoding: File encoding to use for reading files
        """
        self.encoding = encoding
        self.supported_extensions: List[str] = []
    
    @abstractmethod
    def import_file(self, file_path: Path, **kwargs) -> Deck:
        """
        Import flashcards from a file.
        
        Args:
            file_path: Path to the file to import
            **kwargs: Additional importer-specific options
            
        Returns:
            Deck containing the imported flashcards
            
        Raises:
            ImportError: If the file cannot be imported
            ValidationError: If the file format is invalid
        """
        pass
    
    @abstractmethod
    def validate_file(self, file_path: Path) -> bool:
        """
        Validate that a file can be imported by this importer.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if the file can be imported, False otherwise
        """
        pass
    
    def can_import(self, file_path: Path) -> bool:
        """
        Check if this importer can handle the given file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this importer can handle the file
        """
        if not file_path.exists():
            return False
        
        # Check file extension
        if file_path.suffix.lower() not in self.supported_extensions:
            return False
        
        # Validate file format
        try:
            return self.validate_file(file_path)
        except Exception:
            return False
    
    def _validate_flashcard_data(self, question: str, answer: str) -> None:
        """
        Validate flashcard question and answer data.
        
        Args:
            question: The question text
            answer: The answer text
            
        Raises:
            ValidationError: If the data is invalid
        """
        if not question or not question.strip():
            raise ValidationError("Question cannot be empty")
        
        if not answer or not answer.strip():
            raise ValidationError("Answer cannot be empty")
        
        if len(question.strip()) > 1000:
            raise ValidationError("Question is too long (max 1000 characters)")
        
        if len(answer.strip()) > 1000:
            raise ValidationError("Answer is too long (max 1000 characters)")
    
    def _create_flashcard(self, question: str, answer: str, 
                         tags: Optional[List[str]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Flashcard:
        """
        Create a flashcard with validation.
        
        Args:
            question: The question text
            answer: The answer text
            tags: Optional list of tags
            metadata: Optional metadata dictionary
            
        Returns:
            Created flashcard
            
        Raises:
            ValidationError: If the data is invalid
        """
        # Validate data
        self._validate_flashcard_data(question, answer)
        
        # Create flashcard
        return Flashcard(
            question=question.strip(),
            answer=answer.strip(),
            tags=tags or [],
            metadata=metadata or {}
        )
    
    def _create_deck(self, flashcards: List[Flashcard], 
                    name: str = None, 
                    description: str = "",
                    tags: Optional[List[str]] = None) -> Deck:
        """
        Create a deck from flashcards.
        
        Args:
            flashcards: List of flashcards
            name: Deck name (auto-generated if None)
            description: Deck description
            tags: Optional list of tags
            
        Returns:
            Created deck
        """
        if not flashcards:
            raise ValidationError("Cannot create deck with no flashcards")
        
        if name is None:
            name = f"Imported Deck ({len(flashcards)} cards)"
        
        deck = Deck(
            name=name,
            description=description,
            tags=tags or [],
            flashcards=flashcards
        )
        
        return deck
    
    def get_import_stats(self, deck: Deck) -> Dict[str, Any]:
        """
        Get statistics about the imported deck.
        
        Args:
            deck: The imported deck
            
        Returns:
            Dictionary with import statistics
        """
        return {
            "total_cards": len(deck.flashcards),
            "deck_name": deck.name,
            "deck_description": deck.description,
            "tags": deck.tags,
            "created_at": deck.created_at.isoformat(),
        }
