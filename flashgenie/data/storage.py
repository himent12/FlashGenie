"""
Data storage and persistence layer for FlashGenie.

This module provides centralized data storage functionality,
managing deck persistence and data integrity.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from flashgenie.core.content_system.deck import Deck
from flashgenie.core.content_system.flashcard import Flashcard
from flashgenie.utils.exceptions import StorageError
from flashgenie.config import DECKS_DIR, DATA_DIR


class DataStorage:
    """
    Centralized data storage manager for FlashGenie.
    
    Handles saving, loading, and managing deck data with
    backup and recovery capabilities.
    """
    
    def __init__(self, storage_dir: Path = None):
        """
        Initialize the data storage manager.
        
        Args:
            storage_dir: Directory for storing data (uses default if None)
        """
        self.storage_dir = storage_dir or DECKS_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup directory
        self.backup_dir = self.storage_dir.parent / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def save_deck(self, deck: Deck, backup: bool = True) -> Path:
        """
        Save a deck to storage.
        
        Args:
            deck: The deck to save
            backup: Whether to create a backup of existing file
            
        Returns:
            Path where the deck was saved
            
        Raises:
            StorageError: If the deck cannot be saved
        """
        try:
            file_path = self.storage_dir / f"{deck.deck_id}.json"
            
            # Create backup if file exists and backup is requested
            if backup and file_path.exists():
                self._create_backup(file_path)
            
            # Update modification time
            deck.modified_at = datetime.now()
            
            # Save deck
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(deck.to_dict(), f, indent=2, ensure_ascii=False)
            
            return file_path
        
        except Exception as e:
            raise StorageError(f"Failed to save deck '{deck.name}': {e}")
    
    def load_deck(self, deck_id: str) -> Deck:
        """
        Load a deck from storage.
        
        Args:
            deck_id: ID of the deck to load
            
        Returns:
            Loaded deck
            
        Raises:
            StorageError: If the deck cannot be loaded
        """
        try:
            file_path = self.storage_dir / f"{deck_id}.json"
            
            if not file_path.exists():
                raise StorageError(f"Deck with ID '{deck_id}' not found")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return Deck.from_dict(data)
        
        except json.JSONDecodeError as e:
            raise StorageError(f"Invalid deck file format: {e}")
        except Exception as e:
            raise StorageError(f"Failed to load deck '{deck_id}': {e}")
    
    def load_deck_by_name(self, name: str) -> Optional[Deck]:
        """
        Load a deck by name.
        
        Args:
            name: Name of the deck to load
            
        Returns:
            Loaded deck or None if not found
        """
        for deck_info in self.list_decks():
            if deck_info["name"] == name:
                return self.load_deck(deck_info["deck_id"])
        return None
    
    def delete_deck(self, deck_id: str, backup: bool = True) -> bool:
        """
        Delete a deck from storage.
        
        Args:
            deck_id: ID of the deck to delete
            backup: Whether to create a backup before deletion
            
        Returns:
            True if deck was deleted, False if not found
            
        Raises:
            StorageError: If the deck cannot be deleted
        """
        try:
            file_path = self.storage_dir / f"{deck_id}.json"
            
            if not file_path.exists():
                return False
            
            # Create backup if requested
            if backup:
                self._create_backup(file_path, suffix="_deleted")
            
            # Delete file
            file_path.unlink()
            return True
        
        except Exception as e:
            raise StorageError(f"Failed to delete deck '{deck_id}': {e}")
    
    def list_decks(self) -> List[Dict[str, Any]]:
        """
        List all available decks with metadata.
        
        Returns:
            List of deck metadata dictionaries
        """
        decks = []
        
        for deck_file in self.storage_dir.glob("*.json"):
            try:
                with open(deck_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract basic metadata
                deck_info = {
                    "deck_id": data.get("deck_id"),
                    "name": data.get("name"),
                    "description": data.get("description", ""),
                    "card_count": len(data.get("flashcards", [])),
                    "created_at": data.get("created_at"),
                    "modified_at": data.get("modified_at"),
                    "tags": data.get("tags", []),
                    "file_path": deck_file,
                    "file_size": deck_file.stat().st_size
                }
                
                # Calculate due cards
                due_count = 0
                for card_data in data.get("flashcards", []):
                    try:
                        next_review = datetime.fromisoformat(card_data["next_review"])
                        if next_review <= datetime.now():
                            due_count += 1
                    except (KeyError, ValueError):
                        continue
                
                deck_info["due_count"] = due_count
                decks.append(deck_info)
            
            except (json.JSONDecodeError, KeyError):
                # Skip invalid files
                continue
        
        # Sort by modification date (newest first)
        return sorted(decks, key=lambda x: x["modified_at"], reverse=True)
    
    def search_decks(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for decks by name, description, or tags.
        
        Args:
            query: Search query
            
        Returns:
            List of matching deck metadata
        """
        query_lower = query.lower()
        all_decks = self.list_decks()
        
        matching_decks = []
        for deck in all_decks:
            # Search in name
            if query_lower in deck["name"].lower():
                matching_decks.append(deck)
                continue
            
            # Search in description
            if query_lower in deck["description"].lower():
                matching_decks.append(deck)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in deck["tags"]):
                matching_decks.append(deck)
                continue
        
        return matching_decks
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the storage.
        
        Returns:
            Dictionary with storage statistics
        """
        decks = self.list_decks()
        
        total_cards = sum(deck["card_count"] for deck in decks)
        total_size = sum(deck["file_size"] for deck in decks)
        
        # Calculate due cards
        total_due = sum(deck["due_count"] for deck in decks)
        
        return {
            "total_decks": len(decks),
            "total_cards": total_cards,
            "total_due_cards": total_due,
            "total_storage_size": total_size,
            "storage_directory": str(self.storage_dir),
            "backup_directory": str(self.backup_dir)
        }
    
    def _create_backup(self, file_path: Path, suffix: str = "_backup") -> Path:
        """
        Create a backup of a file.
        
        Args:
            file_path: Path to the file to backup
            suffix: Suffix to add to backup filename
            
        Returns:
            Path to the backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}{suffix}_{timestamp}.json"
        backup_path = self.backup_dir / backup_name
        
        # Copy file to backup location
        import shutil
        shutil.copy2(file_path, backup_path)
        
        return backup_path
    
    def cleanup_backups(self, days_to_keep: int = 30) -> int:
        """
        Clean up old backup files.
        
        Args:
            days_to_keep: Number of days of backups to keep
            
        Returns:
            Number of backup files removed
        """
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        removed_count = 0
        
        for backup_file in self.backup_dir.glob("*.json"):
            if backup_file.stat().st_mtime < cutoff_time:
                backup_file.unlink()
                removed_count += 1
        
        return removed_count
    
    def export_all_decks(self, export_path: Path) -> None:
        """
        Export all decks to a single backup file.
        
        Args:
            export_path: Path where to save the export
            
        Raises:
            StorageError: If the export cannot be created
        """
        try:
            all_decks = []
            
            for deck_info in self.list_decks():
                deck = self.load_deck(deck_info["deck_id"])
                all_decks.append(deck.to_dict())
            
            export_data = {
                "export_info": {
                    "format": "FlashGenie Complete Export",
                    "version": "1.0",
                    "exported_at": datetime.now().isoformat(),
                    "total_decks": len(all_decks)
                },
                "decks": all_decks
            }
            
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            raise StorageError(f"Failed to export all decks: {e}")
    
    def import_from_export(self, import_path: Path, 
                          overwrite: bool = False) -> List[str]:
        """
        Import decks from an export file.
        
        Args:
            import_path: Path to the export file
            overwrite: Whether to overwrite existing decks
            
        Returns:
            List of imported deck IDs
            
        Raises:
            StorageError: If the import cannot be completed
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "decks" not in data:
                raise StorageError("Invalid export file format")
            
            imported_deck_ids = []
            
            for deck_data in data["decks"]:
                deck = Deck.from_dict(deck_data)
                
                # Check if deck already exists
                existing_file = self.storage_dir / f"{deck.deck_id}.json"
                if existing_file.exists() and not overwrite:
                    # Generate new ID to avoid conflicts
                    import uuid
                    deck.deck_id = str(uuid.uuid4())
                
                # Save deck
                self.save_deck(deck, backup=False)
                imported_deck_ids.append(deck.deck_id)
            
            return imported_deck_ids
        
        except Exception as e:
            raise StorageError(f"Failed to import from export: {e}")
