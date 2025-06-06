"""
Text file importer for FlashGenie.

This module provides functionality to import flashcards from formatted
text files with various question/answer patterns.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from flashgenie.data.importers.base_importer import BaseImporter
from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck
from flashgenie.utils.exceptions import ImportError, ValidationError
from flashgenie.config import TXT_CONFIG


class TXTImporter(BaseImporter):
    """
    Importer for text format flashcard files.
    
    Supports various text formats including:
    - Q: question / A: answer
    - Question? / Answer
    - Custom prefixes and separators
    """
    
    def __init__(self, encoding: str = 'utf-8'):
        """Initialize the TXT importer."""
        super().__init__(encoding)
        self.supported_extensions = ['.txt', '.text']
        self.config = TXT_CONFIG.copy()
    
    def import_file(self, file_path: Path, **kwargs) -> Deck:
        """
        Import flashcards from a text file.
        
        Args:
            file_path: Path to the text file
            **kwargs: Additional options:
                - question_prefix: Prefix for question lines (default: "Q:")
                - answer_prefix: Prefix for answer lines (default: "A:")
                - separator: Alternative separator pattern
                - deck_name: Name for the created deck
                - auto_detect: Whether to auto-detect format
                
        Returns:
            Deck containing the imported flashcards
            
        Raises:
            ImportError: If the file cannot be imported
            ValidationError: If the text format is invalid
        """
        if not self.can_import(file_path):
            raise ImportError(f"Cannot import file: {file_path}")
        
        # Extract options
        question_prefix = kwargs.get('question_prefix', self.config['question_prefix'])
        answer_prefix = kwargs.get('answer_prefix', self.config['answer_prefix'])
        separator = kwargs.get('separator')
        deck_name = kwargs.get('deck_name')
        auto_detect = kwargs.get('auto_detect', True)
        
        try:
            # Read file content
            with open(file_path, 'r', encoding=self.encoding) as f:
                content = f.read()
            
            if not content.strip():
                raise ValidationError("Text file is empty")
            
            # Auto-detect format if requested
            if auto_detect:
                detected_format = self._detect_format(content)
                if detected_format:
                    question_prefix = detected_format.get('question_prefix', question_prefix)
                    answer_prefix = detected_format.get('answer_prefix', answer_prefix)
                    separator = detected_format.get('separator', separator)
            
            # Parse flashcards based on format
            if separator:
                flashcards = self._parse_with_separator(content, separator)
            else:
                flashcards = self._parse_with_prefixes(content, question_prefix, answer_prefix)
            
            if not flashcards:
                raise ValidationError("No valid flashcards found in text file")
            
            # Create deck
            if deck_name is None:
                deck_name = file_path.stem
            
            deck = self._create_deck(
                flashcards=flashcards,
                name=deck_name,
                description=f"Imported from {file_path.name}",
                tags=['imported', 'txt']
            )
            
            return deck
        
        except Exception as e:
            if isinstance(e, (ImportError, ValidationError)):
                raise
            raise ImportError(f"Failed to import text file: {e}")
    
    def validate_file(self, file_path: Path) -> bool:
        """
        Validate that a text file can be imported.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            True if the file can be imported
        """
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                content = f.read(1024)  # Read first 1KB
                
                if not content.strip():
                    return False
                
                # Check if content contains recognizable patterns
                return self._detect_format(content) is not None
        
        except Exception:
            return False
    
    def _detect_format(self, content: str) -> Optional[Dict[str, str]]:
        """
        Auto-detect the text file format.
        
        Args:
            content: File content to analyze
            
        Returns:
            Dictionary with detected format parameters or None
        """
        lines = content.split('\n')
        
        # Pattern 1: Q: / A: format
        q_a_pattern = re.compile(r'^Q\s*:\s*(.+)', re.IGNORECASE)
        a_pattern = re.compile(r'^A\s*:\s*(.+)', re.IGNORECASE)
        
        q_count = sum(1 for line in lines if q_a_pattern.match(line.strip()))
        a_count = sum(1 for line in lines if a_pattern.match(line.strip()))
        
        if q_count > 0 and a_count > 0 and abs(q_count - a_count) <= 1:
            return {
                'question_prefix': 'Q:',
                'answer_prefix': 'A:',
                'format': 'prefix'
            }
        
        # Pattern 2: Question / Answer format
        question_pattern = re.compile(r'^Question\s*:\s*(.+)', re.IGNORECASE)
        answer_pattern = re.compile(r'^Answer\s*:\s*(.+)', re.IGNORECASE)
        
        q_count = sum(1 for line in lines if question_pattern.match(line.strip()))
        a_count = sum(1 for line in lines if answer_pattern.match(line.strip()))
        
        if q_count > 0 and a_count > 0 and abs(q_count - a_count) <= 1:
            return {
                'question_prefix': 'Question:',
                'answer_prefix': 'Answer:',
                'format': 'prefix'
            }
        
        # Pattern 3: Separator-based format (e.g., --- or ===)
        separators = ['---', '===', '***', '|||']
        for sep in separators:
            sep_count = content.count(sep)
            if sep_count > 0:
                # Check if separator creates reasonable chunks
                chunks = content.split(sep)
                if len(chunks) > 1 and all(chunk.strip() for chunk in chunks):
                    return {
                        'separator': sep,
                        'format': 'separator'
                    }
        
        # Pattern 4: Empty line separation
        if '\n\n' in content:
            chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
            if len(chunks) >= 2 and len(chunks) % 2 == 0:
                return {
                    'separator': '\n\n',
                    'format': 'separator'
                }
        
        return None
    
    def _parse_with_prefixes(self, content: str, 
                           question_prefix: str, 
                           answer_prefix: str) -> List[Flashcard]:
        """
        Parse text content using question and answer prefixes.
        
        Args:
            content: File content
            question_prefix: Prefix for question lines
            answer_prefix: Prefix for answer lines
            
        Returns:
            List of flashcards
        """
        flashcards = []
        lines = content.split('\n')
        
        # Create regex patterns for prefixes
        q_pattern = re.compile(rf'^{re.escape(question_prefix)}\s*(.+)', re.IGNORECASE)
        a_pattern = re.compile(rf'^{re.escape(answer_prefix)}\s*(.+)', re.IGNORECASE)
        
        current_question = None
        line_num = 0
        
        for line in lines:
            line_num += 1
            line = line.strip()
            
            if not line:
                continue
            
            # Check for question
            q_match = q_pattern.match(line)
            if q_match:
                current_question = q_match.group(1).strip()
                continue
            
            # Check for answer
            a_match = a_pattern.match(line)
            if a_match and current_question:
                answer = a_match.group(1).strip()
                
                try:
                    flashcard = self._create_flashcard(
                        question=current_question,
                        answer=answer,
                        metadata={'source_line': line_num}
                    )
                    flashcards.append(flashcard)
                except ValidationError:
                    # Skip invalid flashcards
                    pass
                
                current_question = None
        
        return flashcards
    
    def _parse_with_separator(self, content: str, separator: str) -> List[Flashcard]:
        """
        Parse text content using a separator pattern.
        
        Args:
            content: File content
            separator: Separator pattern
            
        Returns:
            List of flashcards
        """
        flashcards = []
        
        # Split content by separator
        chunks = [chunk.strip() for chunk in content.split(separator) if chunk.strip()]
        
        # Process chunks in pairs
        for i in range(0, len(chunks) - 1, 2):
            if i + 1 < len(chunks):
                question = chunks[i].strip()
                answer = chunks[i + 1].strip()
                
                try:
                    flashcard = self._create_flashcard(
                        question=question,
                        answer=answer,
                        metadata={'source_chunk': i // 2 + 1}
                    )
                    flashcards.append(flashcard)
                except ValidationError:
                    # Skip invalid flashcards
                    continue
        
        return flashcards
    
    def get_preview(self, file_path: Path, max_lines: int = 20) -> Dict[str, Any]:
        """
        Get a preview of the text file content.
        
        Args:
            file_path: Path to the text file
            max_lines: Maximum number of lines to preview
            
        Returns:
            Dictionary with preview information
        """
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line.rstrip('\n\r'))
                
                content = '\n'.join(lines)
                detected_format = self._detect_format(content)
                
                return {
                    'encoding': self.encoding,
                    'lines': lines,
                    'total_lines': len(lines),
                    'detected_format': detected_format,
                }
        
        except Exception as e:
            return {'error': str(e)}
    
    def suggest_format_options(self, file_path: Path) -> Dict[str, Any]:
        """
        Suggest format options for the text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Dictionary with suggested format options
        """
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                content = f.read()
            
            detected_format = self._detect_format(content)
            
            # Count potential flashcards with different formats
            formats = []
            
            # Test Q:/A: format
            q_a_cards = len(self._parse_with_prefixes(content, 'Q:', 'A:'))
            if q_a_cards > 0:
                formats.append({
                    'name': 'Q: / A: Format',
                    'question_prefix': 'Q:',
                    'answer_prefix': 'A:',
                    'estimated_cards': q_a_cards
                })
            
            # Test Question:/Answer: format
            qa_cards = len(self._parse_with_prefixes(content, 'Question:', 'Answer:'))
            if qa_cards > 0:
                formats.append({
                    'name': 'Question: / Answer: Format',
                    'question_prefix': 'Question:',
                    'answer_prefix': 'Answer:',
                    'estimated_cards': qa_cards
                })
            
            # Test separator formats
            separators = ['---', '===', '***', '\n\n']
            for sep in separators:
                sep_cards = len(self._parse_with_separator(content, sep))
                if sep_cards > 0:
                    formats.append({
                        'name': f'Separator Format ({repr(sep)})',
                        'separator': sep,
                        'estimated_cards': sep_cards
                    })
            
            return {
                'detected_format': detected_format,
                'available_formats': formats,
                'recommended': max(formats, key=lambda x: x['estimated_cards']) if formats else None
            }
        
        except Exception as e:
            return {'error': str(e)}
