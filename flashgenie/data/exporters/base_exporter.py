"""
Base exporter class for FlashGenie.

This module defines the abstract base class for all file exporters,
providing a common interface for data export functionality.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

from flashgenie.core.content_system.flashcard import Flashcard
from flashgenie.core.content_system.deck import Deck
from flashgenie.utils.exceptions import ExportError


class BaseExporter(ABC):
    """
    Abstract base class for all file exporters.
    
    This class defines the common interface that all exporters must implement
    and provides shared utility methods.
    """
    
    def __init__(self, encoding: str = 'utf-8'):
        """
        Initialize the exporter.
        
        Args:
            encoding: File encoding to use for writing files
        """
        self.encoding = encoding
        self.supported_extensions: List[str] = []
    
    @abstractmethod
    def export_deck(self, deck: Deck, file_path: Path, **kwargs) -> None:
        """
        Export a deck to a file.
        
        Args:
            deck: The deck to export
            file_path: Path where to save the exported file
            **kwargs: Additional exporter-specific options
            
        Raises:
            ExportError: If the deck cannot be exported
        """
        pass
    
    @abstractmethod
    def export_flashcards(self, flashcards: List[Flashcard], 
                         file_path: Path, **kwargs) -> None:
        """
        Export a list of flashcards to a file.
        
        Args:
            flashcards: List of flashcards to export
            file_path: Path where to save the exported file
            **kwargs: Additional exporter-specific options
            
        Raises:
            ExportError: If the flashcards cannot be exported
        """
        pass
    
    def can_export(self, file_path: Path) -> bool:
        """
        Check if this exporter can handle the given file extension.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if this exporter can handle the file extension
        """
        return file_path.suffix.lower() in self.supported_extensions
    
    def _ensure_directory(self, file_path: Path) -> None:
        """
        Ensure the directory for the file path exists.
        
        Args:
            file_path: Path to the file
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _validate_deck(self, deck: Deck) -> None:
        """
        Validate that a deck can be exported.
        
        Args:
            deck: The deck to validate
            
        Raises:
            ExportError: If the deck is invalid
        """
        if not deck:
            raise ExportError("Deck cannot be None")
        
        if not deck.flashcards:
            raise ExportError("Cannot export empty deck")
    
    def _validate_flashcards(self, flashcards: List[Flashcard]) -> None:
        """
        Validate that flashcards can be exported.
        
        Args:
            flashcards: List of flashcards to validate
            
        Raises:
            ExportError: If the flashcards are invalid
        """
        if not flashcards:
            raise ExportError("Cannot export empty flashcard list")
        
        for i, card in enumerate(flashcards):
            if not card.question.strip():
                raise ExportError(f"Flashcard {i} has empty question")
            if not card.answer.strip():
                raise ExportError(f"Flashcard {i} has empty answer")
    
    def get_export_stats(self, deck: Deck) -> Dict[str, Any]:
        """
        Get statistics about the deck to be exported.
        
        Args:
            deck: The deck to analyze
            
        Returns:
            Dictionary with export statistics
        """
        return {
            "total_cards": len(deck.flashcards),
            "deck_name": deck.name,
            "deck_description": deck.description,
            "tags": deck.tags,
            "created_at": deck.created_at.isoformat(),
            "modified_at": deck.modified_at.isoformat(),
        }
