"""
JSON file exporter for FlashGenie.

This module provides functionality to export flashcards and decks
to JSON format for complete data preservation and backup.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from flashgenie.data.exporters.base_exporter import BaseExporter
from flashgenie.core.content_system.flashcard import Flashcard
from flashgenie.core.content_system.deck import Deck
from flashgenie.utils.exceptions import ExportError


class JSONExporter(BaseExporter):
    """
    Exporter for JSON format files.
    
    Exports complete flashcard and deck data to JSON format,
    preserving all metadata and relationships.
    """
    
    def __init__(self, encoding: str = 'utf-8'):
        """Initialize the JSON exporter."""
        super().__init__(encoding)
        self.supported_extensions = ['.json']
    
    def export_deck(self, deck: Deck, file_path: Path, **kwargs) -> None:
        """
        Export a deck to a JSON file.
        
        Args:
            deck: The deck to export
            file_path: Path where to save the JSON file
            **kwargs: Additional options:
                - indent: JSON indentation (default: 2)
                - include_metadata: Include all metadata (default: True)
                - compact: Use compact format (default: False)
                
        Raises:
            ExportError: If the deck cannot be exported
        """
        self._validate_deck(deck)
        self._ensure_directory(file_path)
        
        # Extract options
        indent = kwargs.get('indent', 2)
        include_metadata = kwargs.get('include_metadata', True)
        compact = kwargs.get('compact', False)
        
        if compact:
            indent = None
        
        try:
            # Prepare export data
            export_data = {
                "export_info": {
                    "format": "FlashGenie JSON Export",
                    "version": "1.0",
                    "exported_at": datetime.now().isoformat(),
                    "exporter": "JSONExporter"
                },
                "deck": deck.to_dict()
            }
            
            # Remove metadata if not requested
            if not include_metadata:
                export_data["deck"]["metadata"] = {}
                for card_data in export_data["deck"]["flashcards"]:
                    card_data["metadata"] = {}
            
            # Write to file
            with open(file_path, 'w', encoding=self.encoding) as f:
                json.dump(export_data, f, indent=indent, ensure_ascii=False)
        
        except Exception as e:
            raise ExportError(f"Failed to export deck to JSON: {e}")
    
    def export_flashcards(self, flashcards: List[Flashcard], 
                         file_path: Path, **kwargs) -> None:
        """
        Export a list of flashcards to a JSON file.
        
        Args:
            flashcards: List of flashcards to export
            file_path: Path where to save the JSON file
            **kwargs: Additional options (same as export_deck)
            
        Raises:
            ExportError: If the flashcards cannot be exported
        """
        self._validate_flashcards(flashcards)
        self._ensure_directory(file_path)
        
        # Extract options
        indent = kwargs.get('indent', 2)
        include_metadata = kwargs.get('include_metadata', True)
        compact = kwargs.get('compact', False)
        
        if compact:
            indent = None
        
        try:
            # Prepare export data
            export_data = {
                "export_info": {
                    "format": "FlashGenie JSON Export",
                    "version": "1.0",
                    "exported_at": datetime.now().isoformat(),
                    "exporter": "JSONExporter",
                    "type": "flashcards_only"
                },
                "flashcards": [card.to_dict() for card in flashcards]
            }
            
            # Remove metadata if not requested
            if not include_metadata:
                for card_data in export_data["flashcards"]:
                    card_data["metadata"] = {}
            
            # Write to file
            with open(file_path, 'w', encoding=self.encoding) as f:
                json.dump(export_data, f, indent=indent, ensure_ascii=False)
        
        except Exception as e:
            raise ExportError(f"Failed to export flashcards to JSON: {e}")
    
    def export_multiple_decks(self, decks: List[Deck], file_path: Path, 
                             **kwargs) -> None:
        """
        Export multiple decks to a single JSON file.
        
        Args:
            decks: List of decks to export
            file_path: Path where to save the JSON file
            **kwargs: Additional options (same as export_deck)
            
        Raises:
            ExportError: If the decks cannot be exported
        """
        if not decks:
            raise ExportError("Cannot export empty deck list")
        
        for deck in decks:
            self._validate_deck(deck)
        
        self._ensure_directory(file_path)
        
        # Extract options
        indent = kwargs.get('indent', 2)
        include_metadata = kwargs.get('include_metadata', True)
        compact = kwargs.get('compact', False)
        
        if compact:
            indent = None
        
        try:
            # Prepare export data
            export_data = {
                "export_info": {
                    "format": "FlashGenie JSON Export",
                    "version": "1.0",
                    "exported_at": datetime.now().isoformat(),
                    "exporter": "JSONExporter",
                    "type": "multiple_decks",
                    "deck_count": len(decks)
                },
                "decks": [deck.to_dict() for deck in decks]
            }
            
            # Remove metadata if not requested
            if not include_metadata:
                for deck_data in export_data["decks"]:
                    deck_data["metadata"] = {}
                    for card_data in deck_data["flashcards"]:
                        card_data["metadata"] = {}
            
            # Write to file
            with open(file_path, 'w', encoding=self.encoding) as f:
                json.dump(export_data, f, indent=indent, ensure_ascii=False)
        
        except Exception as e:
            raise ExportError(f"Failed to export multiple decks to JSON: {e}")
    
    def export_backup(self, decks: List[Deck], file_path: Path) -> None:
        """
        Export a complete backup of all decks with full metadata.
        
        Args:
            decks: List of all decks to backup
            file_path: Path where to save the backup file
            
        Raises:
            ExportError: If the backup cannot be created
        """
        if not decks:
            raise ExportError("Cannot create backup with no decks")
        
        self._ensure_directory(file_path)
        
        try:
            # Calculate backup statistics
            total_cards = sum(len(deck.flashcards) for deck in decks)
            total_reviews = sum(
                sum(card.review_count for card in deck.flashcards)
                for deck in decks
            )
            
            # Prepare backup data
            backup_data = {
                "backup_info": {
                    "format": "FlashGenie Complete Backup",
                    "version": "1.0",
                    "created_at": datetime.now().isoformat(),
                    "total_decks": len(decks),
                    "total_cards": total_cards,
                    "total_reviews": total_reviews
                },
                "decks": [deck.to_dict() for deck in decks],
                "metadata": {
                    "backup_type": "complete",
                    "includes_performance_data": True,
                    "includes_metadata": True
                }
            }
            
            # Write backup file
            with open(file_path, 'w', encoding=self.encoding) as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            raise ExportError(f"Failed to create backup: {e}")
    
    def export_anki_format(self, deck: Deck, file_path: Path) -> None:
        """
        Export deck in Anki-compatible JSON format.
        
        Args:
            deck: The deck to export
            file_path: Path where to save the Anki-format file
            
        Raises:
            ExportError: If the deck cannot be exported in Anki format
        """
        self._validate_deck(deck)
        self._ensure_directory(file_path)
        
        try:
            # Convert to Anki-like format
            anki_data = {
                "name": deck.name,
                "description": deck.description,
                "notes": []
            }
            
            for card in deck.flashcards:
                note = {
                    "fields": [card.question, card.answer],
                    "tags": card.tags,
                    "guid": card.card_id
                }
                anki_data["notes"].append(note)
            
            # Write to file
            with open(file_path, 'w', encoding=self.encoding) as f:
                json.dump(anki_data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            raise ExportError(f"Failed to export in Anki format: {e}")
    
    def validate_json_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate a JSON export file and return information about it.
        
        Args:
            file_path: Path to the JSON file to validate
            
        Returns:
            Dictionary with validation results and file information
        """
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                data = json.load(f)
            
            # Check if it's a FlashGenie export
            if "export_info" in data:
                export_info = data["export_info"]
                
                result = {
                    "valid": True,
                    "format": export_info.get("format", "Unknown"),
                    "version": export_info.get("version", "Unknown"),
                    "exported_at": export_info.get("exported_at"),
                    "type": export_info.get("type", "single_deck")
                }
                
                # Count content
                if "deck" in data:
                    result["deck_count"] = 1
                    result["card_count"] = len(data["deck"].get("flashcards", []))
                elif "decks" in data:
                    result["deck_count"] = len(data["decks"])
                    result["card_count"] = sum(
                        len(deck.get("flashcards", [])) for deck in data["decks"]
                    )
                elif "flashcards" in data:
                    result["deck_count"] = 0
                    result["card_count"] = len(data["flashcards"])
                
                return result
            
            else:
                return {
                    "valid": False,
                    "error": "Not a FlashGenie export file"
                }
        
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": f"Invalid JSON: {e}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {e}"
            }
