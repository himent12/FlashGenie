"""
CSV file exporter for FlashGenie.

This module provides functionality to export flashcards and decks
to CSV format for data portability and backup.
"""

import csv
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from flashgenie.data.exporters.base_exporter import BaseExporter
from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck
from flashgenie.utils.exceptions import ExportError


class CSVExporter(BaseExporter):
    """
    Exporter for CSV format files.
    
    Exports flashcards and deck metadata to CSV format with
    customizable column selection and formatting.
    """
    
    def __init__(self, encoding: str = 'utf-8'):
        """Initialize the CSV exporter."""
        super().__init__(encoding)
        self.supported_extensions = ['.csv']
    
    def export_deck(self, deck: Deck, file_path: Path, **kwargs) -> None:
        """
        Export a deck to a CSV file.
        
        Args:
            deck: The deck to export
            file_path: Path where to save the CSV file
            **kwargs: Additional options:
                - include_metadata: Include flashcard metadata (default: False)
                - include_stats: Include performance statistics (default: False)
                - delimiter: CSV delimiter (default: ',')
                - include_deck_info: Include deck information as header (default: True)
                
        Raises:
            ExportError: If the deck cannot be exported
        """
        self._validate_deck(deck)
        self._ensure_directory(file_path)
        
        # Extract options
        include_metadata = kwargs.get('include_metadata', False)
        include_stats = kwargs.get('include_stats', False)
        delimiter = kwargs.get('delimiter', ',')
        include_deck_info = kwargs.get('include_deck_info', True)
        
        try:
            with open(file_path, 'w', newline='', encoding=self.encoding) as f:
                writer = csv.writer(f, delimiter=delimiter)
                
                # Write deck information as comments if requested
                if include_deck_info:
                    writer.writerow([f"# Deck: {deck.name}"])
                    writer.writerow([f"# Description: {deck.description}"])
                    writer.writerow([f"# Created: {deck.created_at.isoformat()}"])
                    writer.writerow([f"# Modified: {deck.modified_at.isoformat()}"])
                    writer.writerow([f"# Total Cards: {len(deck.flashcards)}"])
                    if deck.tags:
                        writer.writerow([f"# Tags: {', '.join(deck.tags)}"])
                    writer.writerow([])  # Empty row separator
                
                # Write header row
                headers = ['question', 'answer']
                
                if include_stats:
                    headers.extend([
                        'review_count', 'correct_count', 'accuracy',
                        'difficulty', 'ease_factor', 'last_reviewed', 'next_review'
                    ])
                
                if include_metadata:
                    headers.extend(['tags', 'created_at', 'card_id'])
                
                writer.writerow(headers)
                
                # Write flashcard data
                for card in deck.flashcards:
                    row = [card.question, card.answer]
                    
                    if include_stats:
                        row.extend([
                            card.review_count,
                            card.correct_count,
                            f"{card.accuracy:.2f}",
                            f"{card.difficulty:.2f}",
                            f"{card.ease_factor:.2f}",
                            card.last_reviewed.isoformat() if card.last_reviewed else '',
                            card.next_review.isoformat()
                        ])
                    
                    if include_metadata:
                        row.extend([
                            '; '.join(card.tags),
                            card.created_at.isoformat(),
                            card.card_id
                        ])
                    
                    writer.writerow(row)
        
        except Exception as e:
            raise ExportError(f"Failed to export deck to CSV: {e}")
    
    def export_flashcards(self, flashcards: List[Flashcard], 
                         file_path: Path, **kwargs) -> None:
        """
        Export a list of flashcards to a CSV file.
        
        Args:
            flashcards: List of flashcards to export
            file_path: Path where to save the CSV file
            **kwargs: Additional options (same as export_deck)
            
        Raises:
            ExportError: If the flashcards cannot be exported
        """
        self._validate_flashcards(flashcards)
        self._ensure_directory(file_path)
        
        # Create a temporary deck for export
        temp_deck = Deck(
            name="Exported Flashcards",
            description=f"Exported {len(flashcards)} flashcards",
            flashcards=flashcards
        )
        
        # Don't include deck info for standalone flashcard export
        kwargs['include_deck_info'] = kwargs.get('include_deck_info', False)
        
        self.export_deck(temp_deck, file_path, **kwargs)
    
    def export_performance_data(self, deck: Deck, file_path: Path) -> None:
        """
        Export detailed performance data for a deck.
        
        Args:
            deck: The deck to export performance data for
            file_path: Path where to save the CSV file
            
        Raises:
            ExportError: If the performance data cannot be exported
        """
        self._validate_deck(deck)
        self._ensure_directory(file_path)
        
        try:
            with open(file_path, 'w', newline='', encoding=self.encoding) as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'card_id', 'question', 'answer', 'created_at',
                    'review_count', 'correct_count', 'accuracy',
                    'difficulty', 'ease_factor', 'last_reviewed', 'next_review',
                    'days_since_created', 'days_since_last_review',
                    'is_due', 'tags'
                ])
                
                # Write performance data for each card
                now = datetime.now()
                for card in deck.flashcards:
                    days_since_created = (now - card.created_at).days
                    days_since_last_review = (
                        (now - card.last_reviewed).days 
                        if card.last_reviewed else None
                    )
                    
                    writer.writerow([
                        card.card_id,
                        card.question,
                        card.answer,
                        card.created_at.isoformat(),
                        card.review_count,
                        card.correct_count,
                        f"{card.accuracy:.2f}",
                        f"{card.difficulty:.2f}",
                        f"{card.ease_factor:.2f}",
                        card.last_reviewed.isoformat() if card.last_reviewed else '',
                        card.next_review.isoformat(),
                        days_since_created,
                        days_since_last_review or '',
                        card.is_due,
                        '; '.join(card.tags)
                    ])
        
        except Exception as e:
            raise ExportError(f"Failed to export performance data: {e}")
    
    def export_study_schedule(self, deck: Deck, file_path: Path, 
                             days_ahead: int = 30) -> None:
        """
        Export a study schedule showing when cards are due.
        
        Args:
            deck: The deck to create schedule for
            file_path: Path where to save the CSV file
            days_ahead: Number of days to include in schedule
            
        Raises:
            ExportError: If the schedule cannot be exported
        """
        self._validate_deck(deck)
        self._ensure_directory(file_path)
        
        try:
            from datetime import timedelta
            
            with open(file_path, 'w', newline='', encoding=self.encoding) as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'date', 'cards_due', 'card_ids', 'questions'
                ])
                
                # Generate schedule for each day
                start_date = datetime.now().date()
                for i in range(days_ahead + 1):
                    current_date = start_date + timedelta(days=i)
                    
                    # Find cards due on this date
                    due_cards = [
                        card for card in deck.flashcards
                        if card.next_review.date() == current_date
                    ]
                    
                    if due_cards:
                        card_ids = [card.card_id for card in due_cards]
                        questions = [card.question[:50] + "..." if len(card.question) > 50 
                                   else card.question for card in due_cards]
                        
                        writer.writerow([
                            current_date.isoformat(),
                            len(due_cards),
                            '; '.join(card_ids),
                            '; '.join(questions)
                        ])
                    else:
                        writer.writerow([
                            current_date.isoformat(),
                            0,
                            '',
                            ''
                        ])
        
        except Exception as e:
            raise ExportError(f"Failed to export study schedule: {e}")
    
    def get_export_preview(self, deck: Deck, max_rows: int = 5) -> List[List[str]]:
        """
        Get a preview of how the deck would look when exported.
        
        Args:
            deck: The deck to preview
            max_rows: Maximum number of rows to include in preview
            
        Returns:
            List of rows (each row is a list of strings)
        """
        self._validate_deck(deck)
        
        preview = []
        
        # Header row
        preview.append(['question', 'answer'])
        
        # Data rows
        for i, card in enumerate(deck.flashcards[:max_rows]):
            preview.append([card.question, card.answer])
        
        return preview
