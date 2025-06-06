"""
CSV file importer for FlashGenie.

This module provides functionality to import flashcards from CSV files
with flexible column mapping and delimiter detection.
"""

import csv
from typing import List, Dict, Any, Optional
from pathlib import Path

from flashgenie.data.importers.base_importer import BaseImporter
from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck
from flashgenie.utils.exceptions import ImportError, ValidationError
from flashgenie.config import CSV_CONFIG


class CSVImporter(BaseImporter):
    """
    Importer for CSV format flashcard files.
    
    Supports various CSV formats with customizable column mapping
    and automatic delimiter detection.
    """
    
    def __init__(self, encoding: str = 'utf-8'):
        """Initialize the CSV importer."""
        super().__init__(encoding)
        self.supported_extensions = ['.csv']
        self.config = CSV_CONFIG.copy()
    
    def import_file(self, file_path: Path, **kwargs) -> Deck:
        """
        Import flashcards from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            **kwargs: Additional options:
                - delimiter: CSV delimiter (auto-detected if not provided)
                - question_column: Name or index of question column
                - answer_column: Name or index of answer column
                - deck_name: Name for the created deck
                - has_header: Whether the CSV has a header row
                
        Returns:
            Deck containing the imported flashcards
            
        Raises:
            ImportError: If the file cannot be imported
            ValidationError: If the CSV format is invalid
        """
        if not self.can_import(file_path):
            raise ImportError(f"Cannot import file: {file_path}")
        
        # Extract options
        delimiter = kwargs.get('delimiter')
        question_column = kwargs.get('question_column', self.config['question_column'])
        answer_column = kwargs.get('answer_column', self.config['answer_column'])
        deck_name = kwargs.get('deck_name')
        has_header = kwargs.get('has_header', True)
        
        try:
            # Auto-detect delimiter if not provided
            if delimiter is None:
                delimiter = self._detect_delimiter(file_path)
            
            # Read CSV file
            flashcards = []
            with open(file_path, 'r', encoding=self.encoding, newline='') as f:
                # Peek at first few lines to determine format
                sample = f.read(1024)
                f.seek(0)
                
                reader = csv.reader(f, delimiter=delimiter)
                
                # Handle header row
                if has_header:
                    headers = next(reader, None)
                    if headers is None:
                        raise ValidationError("CSV file is empty")
                    
                    # Map column names to indices
                    question_idx = self._get_column_index(headers, question_column)
                    answer_idx = self._get_column_index(headers, answer_column)
                else:
                    # Use column indices directly
                    question_idx = int(question_column) if isinstance(question_column, str) and question_column.isdigit() else 0
                    answer_idx = int(answer_column) if isinstance(answer_column, str) and answer_column.isdigit() else 1
                
                # Process data rows
                for row_num, row in enumerate(reader, start=2 if has_header else 1):
                    if len(row) < max(question_idx + 1, answer_idx + 1):
                        continue  # Skip rows with insufficient columns
                    
                    try:
                        question = row[question_idx].strip()
                        answer = row[answer_idx].strip()
                        
                        if question and answer:  # Skip empty rows
                            flashcard = self._create_flashcard(
                                question=question,
                                answer=answer,
                                metadata={'source_row': row_num, 'source_file': str(file_path)}
                            )
                            flashcards.append(flashcard)
                    
                    except (IndexError, ValidationError) as e:
                        # Log warning but continue processing
                        print(f"Warning: Skipping row {row_num}: {e}")
                        continue
            
            if not flashcards:
                raise ValidationError("No valid flashcards found in CSV file")
            
            # Create deck
            if deck_name is None:
                deck_name = file_path.stem
            
            deck = self._create_deck(
                flashcards=flashcards,
                name=deck_name,
                description=f"Imported from {file_path.name}",
                tags=['imported', 'csv']
            )
            
            return deck
        
        except Exception as e:
            if isinstance(e, (ImportError, ValidationError)):
                raise
            raise ImportError(f"Failed to import CSV file: {e}")
    
    def validate_file(self, file_path: Path) -> bool:
        """
        Validate that a CSV file can be imported.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            True if the file can be imported
        """
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                # Try to read first few lines
                sample = f.read(1024)
                if not sample.strip():
                    return False
                
                # Try to parse as CSV
                f.seek(0)
                delimiter = self._detect_delimiter(file_path)
                reader = csv.reader(f, delimiter=delimiter)
                
                # Check if we can read at least one row
                first_row = next(reader, None)
                if first_row is None or len(first_row) < 2:
                    return False
                
                return True
        
        except Exception:
            return False
    
    def _detect_delimiter(self, file_path: Path) -> str:
        """
        Auto-detect the CSV delimiter.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Detected delimiter
        """
        with open(file_path, 'r', encoding=self.encoding) as f:
            sample = f.read(1024)
            
            # Use csv.Sniffer to detect delimiter
            try:
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample, delimiters=',;\t|').delimiter
                return delimiter
            except csv.Error:
                # Fall back to default delimiter
                return self.config['default_delimiter']
    
    def _get_column_index(self, headers: List[str], column: Any) -> int:
        """
        Get the index of a column by name or index.
        
        Args:
            headers: List of header names
            column: Column name or index
            
        Returns:
            Column index
            
        Raises:
            ValidationError: If column is not found
        """
        if isinstance(column, int):
            if 0 <= column < len(headers):
                return column
            else:
                raise ValidationError(f"Column index {column} is out of range")
        
        elif isinstance(column, str):
            # Try to find by name (case-insensitive)
            for i, header in enumerate(headers):
                if header.lower() == column.lower():
                    return i
            
            # Try to parse as integer
            if column.isdigit():
                idx = int(column)
                if 0 <= idx < len(headers):
                    return idx
            
            raise ValidationError(f"Column '{column}' not found in headers: {headers}")
        
        else:
            raise ValidationError(f"Invalid column specification: {column}")
    
    def get_preview(self, file_path: Path, max_rows: int = 5) -> Dict[str, Any]:
        """
        Get a preview of the CSV file content.
        
        Args:
            file_path: Path to the CSV file
            max_rows: Maximum number of rows to preview
            
        Returns:
            Dictionary with preview information
        """
        try:
            delimiter = self._detect_delimiter(file_path)
            
            with open(file_path, 'r', encoding=self.encoding, newline='') as f:
                reader = csv.reader(f, delimiter=delimiter)
                
                rows = []
                for i, row in enumerate(reader):
                    if i >= max_rows:
                        break
                    rows.append(row)
                
                return {
                    'delimiter': delimiter,
                    'encoding': self.encoding,
                    'rows': rows,
                    'columns': len(rows[0]) if rows else 0,
                    'has_header': True,  # TODO: Implement header detection
                }
        
        except Exception as e:
            return {'error': str(e)}
    
    def suggest_column_mapping(self, file_path: Path) -> Dict[str, Any]:
        """
        Suggest column mapping for question and answer columns.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dictionary with suggested column mapping
        """
        try:
            delimiter = self._detect_delimiter(file_path)
            
            with open(file_path, 'r', encoding=self.encoding, newline='') as f:
                reader = csv.reader(f, delimiter=delimiter)
                headers = next(reader, None)
                
                if not headers:
                    return {'error': 'No headers found'}
                
                # Common question column names
                question_keywords = ['question', 'q', 'front', 'prompt', 'term']
                answer_keywords = ['answer', 'a', 'back', 'response', 'definition']
                
                question_column = None
                answer_column = None
                
                # Find best matches
                for i, header in enumerate(headers):
                    header_lower = header.lower()
                    
                    if question_column is None:
                        for keyword in question_keywords:
                            if keyword in header_lower:
                                question_column = i
                                break
                    
                    if answer_column is None:
                        for keyword in answer_keywords:
                            if keyword in header_lower:
                                answer_column = i
                                break
                
                # Default to first two columns if no matches found
                if question_column is None:
                    question_column = 0
                if answer_column is None:
                    answer_column = 1 if len(headers) > 1 else 0
                
                return {
                    'headers': headers,
                    'suggested_question_column': question_column,
                    'suggested_answer_column': answer_column,
                    'delimiter': delimiter
                }
        
        except Exception as e:
            return {'error': str(e)}
