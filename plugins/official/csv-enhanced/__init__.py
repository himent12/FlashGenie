"""
Enhanced CSV Importer Plugin for FlashGenie

Provides advanced CSV import capabilities with intelligent column mapping,
content validation, encoding detection, and auto-tagging features.
"""

import csv
import chardet
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import re

from flashgenie.core.plugin_system import ImporterPlugin
from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck
from flashgenie.data.storage import DataStorage


class EnhancedCSVImporter(ImporterPlugin):
    """Enhanced CSV importer with advanced features."""
    
    def initialize(self) -> None:
        """Initialize the CSV importer plugin."""
        self.require_permission(self.manifest.permissions[0])  # file_read
        self.require_permission(self.manifest.permissions[1])  # deck_write
        
        self.logger.info("Enhanced CSV importer plugin initialized")
        
        # Column mapping patterns
        self.column_patterns = {
            'question': [
                r'question', r'q', r'front', r'prompt', r'term', r'word',
                r'english', r'definition', r'concept', r'key'
            ],
            'answer': [
                r'answer', r'a', r'back', r'response', r'translation', r'meaning',
                r'spanish', r'french', r'german', r'value', r'explanation'
            ],
            'tags': [
                r'tags', r'tag', r'category', r'categories', r'topic', r'topics',
                r'subject', r'type', r'group', r'classification'
            ],
            'difficulty': [
                r'difficulty', r'level', r'hard', r'easy', r'complexity'
            ],
            'notes': [
                r'notes', r'note', r'comment', r'comments', r'hint', r'hints',
                r'explanation', r'context', r'example'
            ]
        }
        
        # Supported encodings to try
        self.encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'iso-8859-1']
    
    def cleanup(self) -> None:
        """Cleanup importer resources."""
        self.logger.info("Enhanced CSV importer plugin cleaned up")
    
    def can_import(self, file_path: Path) -> bool:
        """Check if this plugin can import the given file."""
        if not file_path.exists():
            return False
        
        # Check file extension
        if file_path.suffix.lower() not in ['.csv', '.tsv']:
            return False
        
        # Try to read first few lines to validate CSV format
        try:
            encoding = self._detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding) as f:
                # Try to parse first few lines
                sample = f.read(1024)
                sniffer = csv.Sniffer()
                sniffer.sniff(sample)
                return True
        except Exception:
            return False
    
    def import_data(self, file_path: Path, deck_name: str) -> Dict[str, Any]:
        """Import data from CSV file and return import results."""
        self.logger.info(f"Starting enhanced CSV import from {file_path}")
        
        try:
            # Detect encoding
            encoding = self._detect_encoding(file_path)
            self.logger.info(f"Detected encoding: {encoding}")
            
            # Read CSV file
            df = self._read_csv_file(file_path, encoding)
            
            # Map columns intelligently
            column_mapping = self._map_columns(df.columns.tolist())
            self.logger.info(f"Column mapping: {column_mapping}")
            
            # Validate and process data
            processed_data = self._process_data(df, column_mapping, file_path)
            
            # Create or load deck
            storage = DataStorage()
            deck = storage.load_deck_by_name(deck_name)
            if deck is None:
                deck = Deck(deck_name, f"Imported from {file_path.name}")
            
            # Import flashcards
            import_stats = self._import_flashcards(deck, processed_data)
            
            # Save deck
            storage.save_deck(deck)
            
            # Prepare results
            results = {
                'success': True,
                'deck_name': deck_name,
                'file_path': str(file_path),
                'encoding': encoding,
                'column_mapping': column_mapping,
                'total_rows': len(df),
                'imported_cards': import_stats['imported'],
                'skipped_cards': import_stats['skipped'],
                'duplicate_cards': import_stats['duplicates'],
                'validation_errors': import_stats['errors'],
                'auto_tags': import_stats['auto_tags']
            }
            
            self.logger.info(f"Import completed: {import_stats['imported']} cards imported")
            return results
            
        except Exception as e:
            self.logger.error(f"Import failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path)
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return ['.csv', '.tsv']
    
    def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding."""
        if not self.get_setting("auto_detect_encoding", True):
            return 'utf-8'
        
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                
                if confidence > 0.7 and encoding:
                    return encoding
        except Exception:
            pass
        
        # Fallback: try common encodings
        for encoding in self.encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1000)  # Try to read first 1KB
                    return encoding
            except UnicodeDecodeError:
                continue
        
        return 'utf-8'  # Final fallback
    
    def _read_csv_file(self, file_path: Path, encoding: str) -> pd.DataFrame:
        """Read CSV file with intelligent delimiter detection."""
        # Detect delimiter
        with open(file_path, 'r', encoding=encoding) as f:
            sample = f.read(1024)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
        
        # Read with pandas
        df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        
        return df
    
    def _map_columns(self, columns: List[str]) -> Dict[str, str]:
        """Intelligently map CSV columns to flashcard fields."""
        mapping = {}
        
        if not self.get_setting("smart_column_mapping", True):
            # Use exact matches only
            for col in columns:
                if col in ['question', 'answer', 'tags', 'difficulty', 'notes']:
                    mapping[col] = col
            return mapping
        
        # Smart mapping using patterns
        for field, patterns in self.column_patterns.items():
            for col in columns:
                for pattern in patterns:
                    if re.search(pattern, col, re.IGNORECASE):
                        mapping[col] = field
                        break
                if col in mapping:
                    break
        
        # Ensure we have at least question and answer
        if 'question' not in mapping.values() and columns:
            mapping[columns[0]] = 'question'
        
        if 'answer' not in mapping.values() and len(columns) > 1:
            # Find the second unmapped column
            for col in columns[1:]:
                if col not in mapping:
                    mapping[col] = 'answer'
                    break
        
        return mapping
    
    def _process_data(self, df: pd.DataFrame, column_mapping: Dict[str, str], file_path: Path) -> List[Dict[str, Any]]:
        """Process and validate CSV data."""
        processed_data = []
        
        # Generate auto-tags from filename if enabled
        auto_tags = []
        if self.get_setting("auto_tag_from_filename", True):
            filename_tags = self._generate_filename_tags(file_path)
            auto_tags.extend(filename_tags)
        
        for index, row in df.iterrows():
            try:
                # Extract fields based on mapping
                card_data = {}
                
                for csv_col, field in column_mapping.items():
                    if csv_col in row and pd.notna(row[csv_col]):
                        value = str(row[csv_col]).strip()
                        if value:
                            card_data[field] = value
                
                # Validate required fields
                if 'question' not in card_data or 'answer' not in card_data:
                    continue
                
                # Process tags
                tags = set(auto_tags)
                if 'tags' in card_data:
                    tag_str = card_data['tags']
                    # Split by common delimiters
                    for delimiter in [',', ';', '|', '\n']:
                        if delimiter in tag_str:
                            tags.update([t.strip() for t in tag_str.split(delimiter)])
                            break
                    else:
                        tags.add(tag_str.strip())
                
                card_data['tags'] = list(tags)
                
                # Process difficulty
                if 'difficulty' in card_data:
                    try:
                        difficulty = float(card_data['difficulty'])
                        card_data['difficulty'] = max(0.0, min(1.0, difficulty))
                    except ValueError:
                        # Try to parse text difficulty
                        diff_text = card_data['difficulty'].lower()
                        if 'easy' in diff_text:
                            card_data['difficulty'] = 0.2
                        elif 'medium' in diff_text or 'normal' in diff_text:
                            card_data['difficulty'] = 0.5
                        elif 'hard' in diff_text or 'difficult' in diff_text:
                            card_data['difficulty'] = 0.8
                        else:
                            card_data['difficulty'] = 0.5
                else:
                    card_data['difficulty'] = 0.5  # Default difficulty
                
                # Validate content if enabled
                if self.get_setting("validate_content", True):
                    if not self._validate_card_content(card_data):
                        continue
                
                card_data['row_index'] = index
                processed_data.append(card_data)
                
            except Exception as e:
                self.logger.warning(f"Error processing row {index}: {e}")
                continue
        
        return processed_data
    
    def _generate_filename_tags(self, file_path: Path) -> List[str]:
        """Generate tags from filename."""
        filename = file_path.stem
        
        # Remove common prefixes/suffixes
        filename = re.sub(r'^(flashcards?|cards?|deck|study)[-_]?', '', filename, flags=re.IGNORECASE)
        filename = re.sub(r'[-_]?(flashcards?|cards?|deck|study)$', '', filename, flags=re.IGNORECASE)
        
        # Split by common delimiters and clean
        tags = []
        for delimiter in ['-', '_', ' ']:
            if delimiter in filename:
                parts = filename.split(delimiter)
                tags.extend([part.strip().lower() for part in parts if part.strip()])
                break
        else:
            tags.append(filename.lower())
        
        # Filter out common words and short tags
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        tags = [tag for tag in tags if len(tag) > 2 and tag not in stop_words]
        
        return tags[:3]  # Limit to 3 auto-generated tags
    
    def _validate_card_content(self, card_data: Dict[str, Any]) -> bool:
        """Validate flashcard content."""
        question = card_data.get('question', '')
        answer = card_data.get('answer', '')
        
        # Check minimum length
        if len(question.strip()) < 3 or len(answer.strip()) < 1:
            return False
        
        # Check for suspicious content
        suspicious_patterns = [
            r'^[0-9]+$',  # Only numbers
            r'^[^a-zA-Z]*$',  # No letters
            r'^\s*$',  # Only whitespace
        ]
        
        for pattern in suspicious_patterns:
            if re.match(pattern, question) or re.match(pattern, answer):
                return False
        
        return True
    
    def _import_flashcards(self, deck: Deck, processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Import flashcards into deck."""
        stats = {
            'imported': 0,
            'skipped': 0,
            'duplicates': 0,
            'errors': 0,
            'auto_tags': set()
        }
        
        skip_duplicates = self.get_setting("skip_duplicates", True)
        existing_questions = {card.question.lower() for card in deck.flashcards} if skip_duplicates else set()
        
        for card_data in processed_data:
            try:
                question = card_data['question']
                answer = card_data['answer']
                
                # Check for duplicates
                if skip_duplicates and question.lower() in existing_questions:
                    stats['duplicates'] += 1
                    continue
                
                # Create flashcard
                flashcard = Flashcard(question, answer)
                flashcard.tags.update(card_data.get('tags', []))
                flashcard.difficulty = card_data.get('difficulty', 0.5)
                
                # Add notes if present
                if 'notes' in card_data:
                    # Store notes in a custom attribute (could be extended in future)
                    flashcard.metadata = {'notes': card_data['notes']}
                
                deck.add_flashcard(flashcard)
                existing_questions.add(question.lower())
                stats['imported'] += 1
                stats['auto_tags'].update(card_data.get('tags', []))
                
            except Exception as e:
                self.logger.error(f"Error creating flashcard: {e}")
                stats['errors'] += 1
        
        stats['auto_tags'] = list(stats['auto_tags'])
        return stats
