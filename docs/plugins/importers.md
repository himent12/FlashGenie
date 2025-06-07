# Importer Plugin Development Guide

Importer plugins allow FlashGenie to import flashcard data from various external sources and file formats. This guide covers everything you need to know to create robust importer plugins.

## Overview

Importer plugins extend FlashGenie's ability to read and convert flashcard data from different sources into the native FlashGenie format. They handle file parsing, data validation, and format conversion.

## Base Class: ImporterPlugin

All importer plugins must inherit from `ImporterPlugin`:

```python
from flashgenie.core.plugin_system import ImporterPlugin
from pathlib import Path
from typing import Dict, List, Any

class MyImporterPlugin(ImporterPlugin):
    def __init__(self):
        super().__init__()
        self.name = "my-importer"
        self.version = "1.0.0"
        self.description = "Import from custom format"
    
    def can_import(self, file_path: Path) -> bool:
        """Check if this plugin can import the given file."""
        return file_path.suffix.lower() in ['.csv', '.txt']
    
    def import_data(self, file_path: Path, deck_name: str) -> Dict[str, Any]:
        """Import data from file and return results."""
        # Implementation here
        pass
    
    def get_supported_formats(self) -> List[str]:
        """Return list of supported file extensions."""
        return ['.csv', '.txt']
```

## Required Methods

### `can_import(file_path: Path) -> bool`

Determines if the plugin can handle a specific file:

```python
def can_import(self, file_path: Path) -> bool:
    """Check if this plugin can import the given file."""
    # Check file extension
    if file_path.suffix.lower() not in ['.csv', '.xlsx']:
        return False
    
    # Optional: Check file content/headers
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            # Check for expected headers or format markers
            return 'question' in first_line.lower()
    except:
        return False
```

### `import_data(file_path: Path, deck_name: str) -> Dict[str, Any]`

Performs the actual import operation:

```python
def import_data(self, file_path: Path, deck_name: str) -> Dict[str, Any]:
    """Import data from file."""
    try:
        cards_imported = 0
        errors = []
        
        # Parse the file
        with open(file_path, 'r', encoding='utf-8') as f:
            # Your parsing logic here
            for line_num, line in enumerate(f, 1):
                try:
                    # Parse each line/record
                    card_data = self._parse_line(line)
                    
                    # Create flashcard
                    self._create_flashcard(deck_name, card_data)
                    cards_imported += 1
                    
                except Exception as e:
                    errors.append(f"Line {line_num}: {str(e)}")
        
        return {
            "success": True,
            "cards_imported": cards_imported,
            "errors": errors,
            "deck_name": deck_name
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "cards_imported": 0
        }
```

### `get_supported_formats() -> List[str]`

Returns supported file formats:

```python
def get_supported_formats(self) -> List[str]:
    """Get list of supported file formats."""
    return ['.csv', '.tsv', '.xlsx', '.json']
```

## Complete Example: CSV Importer

Here's a complete CSV importer plugin:

```python
import csv
from pathlib import Path
from typing import Dict, List, Any
from flashgenie.core.plugin_system import ImporterPlugin
from flashgenie.core import Flashcard, Deck

class CSVImporterPlugin(ImporterPlugin):
    def __init__(self):
        super().__init__()
        self.name = "csv-importer"
        self.version = "1.0.0"
        self.description = "Import flashcards from CSV files"
    
    def initialize(self):
        """Initialize the plugin."""
        self.logger.info("CSV Importer plugin initialized")
        self.require_permission(Permission.FILE_READ)
        self.require_permission(Permission.DECK_WRITE)
    
    def can_import(self, file_path: Path) -> bool:
        """Check if this plugin can import the given file."""
        if file_path.suffix.lower() != '.csv':
            return False
        
        try:
            # Check if file has expected structure
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                
                if not headers:
                    return False
                
                # Look for question/answer columns
                headers_lower = [h.lower().strip() for h in headers]
                has_question = any('question' in h for h in headers_lower)
                has_answer = any('answer' in h for h in headers_lower)
                
                return has_question and has_answer
                
        except Exception:
            return False
    
    def import_data(self, file_path: Path, deck_name: str) -> Dict[str, Any]:
        """Import data from CSV file."""
        try:
            cards_imported = 0
            errors = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Validate headers
                if not reader.fieldnames:
                    return {
                        "success": False,
                        "error": "CSV file has no headers",
                        "cards_imported": 0
                    }
                
                # Find question and answer columns
                question_col = self._find_column(reader.fieldnames, ['question', 'front', 'q'])
                answer_col = self._find_column(reader.fieldnames, ['answer', 'back', 'a'])
                
                if not question_col or not answer_col:
                    return {
                        "success": False,
                        "error": "Could not find question and answer columns",
                        "cards_imported": 0
                    }
                
                # Create or get deck
                deck = self._get_or_create_deck(deck_name)
                
                # Process each row
                for row_num, row in enumerate(reader, 2):  # Start at 2 (header is row 1)
                    try:
                        question = row.get(question_col, '').strip()
                        answer = row.get(answer_col, '').strip()
                        
                        if not question or not answer:
                            errors.append(f"Row {row_num}: Empty question or answer")
                            continue
                        
                        # Extract tags if present
                        tags = self._extract_tags(row)
                        
                        # Extract difficulty if present
                        difficulty = self._extract_difficulty(row)
                        
                        # Create flashcard
                        flashcard = Flashcard(
                            question=question,
                            answer=answer,
                            tags=tags,
                            difficulty=difficulty
                        )
                        
                        deck.add_flashcard(flashcard)
                        cards_imported += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                
                # Save deck
                deck.save()
                
                return {
                    "success": True,
                    "cards_imported": cards_imported,
                    "errors": errors,
                    "deck_name": deck_name,
                    "total_rows_processed": row_num - 1
                }
                
        except Exception as e:
            self.logger.error(f"CSV import failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "cards_imported": 0
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return ['.csv']
    
    def _find_column(self, fieldnames: List[str], possible_names: List[str]) -> str:
        """Find column name from possible alternatives."""
        fieldnames_lower = [f.lower().strip() for f in fieldnames]
        
        for name in possible_names:
            for i, field in enumerate(fieldnames_lower):
                if name in field:
                    return fieldnames[i]
        return None
    
    def _extract_tags(self, row: Dict[str, str]) -> List[str]:
        """Extract tags from row data."""
        tags = []
        
        # Look for tags column
        for key, value in row.items():
            if 'tag' in key.lower() and value:
                # Split by common delimiters
                tag_list = value.replace(',', ';').replace('|', ';').split(';')
                tags.extend([tag.strip() for tag in tag_list if tag.strip()])
        
        return tags
    
    def _extract_difficulty(self, row: Dict[str, str]) -> float:
        """Extract difficulty from row data."""
        for key, value in row.items():
            if 'difficulty' in key.lower() or 'level' in key.lower():
                try:
                    # Try to parse as float (0.0 to 1.0)
                    diff = float(value)
                    return max(0.0, min(1.0, diff))
                except ValueError:
                    # Try to parse as integer (1-5 scale)
                    try:
                        diff_int = int(value)
                        return max(0.0, min(1.0, (diff_int - 1) / 4))
                    except ValueError:
                        pass
        
        return 0.5  # Default difficulty
    
    def _get_or_create_deck(self, deck_name: str) -> Deck:
        """Get existing deck or create new one."""
        # This would integrate with FlashGenie's deck management
        # For now, create a new deck
        return Deck(name=deck_name)
```

## Plugin Manifest

Your `plugin.json` should specify importer-specific settings:

```json
{
  "name": "csv-importer",
  "version": "1.0.0",
  "description": "Import flashcards from CSV files with flexible column mapping",
  "author": "Your Name",
  "license": "MIT",
  "type": "importer",
  "entry_point": "CSVImporterPlugin",
  "permissions": ["file_read", "deck_write"],
  "dependencies": ["pandas>=1.5.0"],
  "settings_schema": {
    "default_difficulty": {
      "type": "number",
      "default": 0.5,
      "description": "Default difficulty for imported cards"
    },
    "auto_detect_tags": {
      "type": "boolean",
      "default": true,
      "description": "Automatically detect and extract tags"
    },
    "skip_empty_cards": {
      "type": "boolean", 
      "default": true,
      "description": "Skip cards with empty questions or answers"
    }
  },
  "supported_formats": [".csv", ".tsv"],
  "flashgenie_version": ">=1.8.0"
}
```

## Testing Your Importer

Create comprehensive tests in `test_plugin.py`:

```python
import unittest
import tempfile
import csv
from pathlib import Path
from your_plugin import CSVImporterPlugin

class TestCSVImporter(unittest.TestCase):
    def setUp(self):
        self.plugin = CSVImporterPlugin()
        self.plugin.initialize()
    
    def test_can_import_valid_csv(self):
        """Test detection of valid CSV files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['Question', 'Answer'])
            writer.writerow(['What is 2+2?', '4'])
            csv_path = Path(f.name)
        
        self.assertTrue(self.plugin.can_import(csv_path))
        csv_path.unlink()  # Clean up
    
    def test_import_basic_csv(self):
        """Test basic CSV import functionality."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['Question', 'Answer', 'Tags'])
            writer.writerow(['What is 2+2?', '4', 'math;basic'])
            writer.writerow(['Capital of France?', 'Paris', 'geography'])
            csv_path = Path(f.name)
        
        result = self.plugin.import_data(csv_path, "Test Deck")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["cards_imported"], 2)
        self.assertEqual(len(result["errors"]), 0)
        
        csv_path.unlink()  # Clean up

if __name__ == '__main__':
    unittest.main()
```

## Best Practices

### Error Handling
- Gracefully handle malformed files
- Provide detailed error messages with line numbers
- Continue processing after non-fatal errors

### Performance
- Use streaming for large files
- Implement progress callbacks for long operations
- Cache parsed data when possible

### User Experience
- Support common file formats and naming conventions
- Provide preview functionality
- Allow column mapping customization

### Data Validation
- Validate required fields
- Sanitize input data
- Handle encoding issues gracefully

## Advanced Features

### Custom Column Mapping
Allow users to map columns to flashcard fields:

```python
def import_with_mapping(self, file_path: Path, deck_name: str, column_mapping: Dict[str, str]) -> Dict[str, Any]:
    """Import with custom column mapping."""
    # Use provided mapping instead of auto-detection
    pass
```

### Batch Processing
Support importing multiple files:

```python
def import_batch(self, file_paths: List[Path], deck_name: str) -> Dict[str, Any]:
    """Import multiple files into a single deck."""
    pass
```

### Preview Mode
Allow users to preview import results:

```python
def preview_import(self, file_path: Path, max_rows: int = 10) -> Dict[str, Any]:
    """Preview import results without creating cards."""
    pass
```

## Integration Examples

- **Anki Importer**: Import .apkg files
- **Quizlet Importer**: Import from Quizlet exports
- **Google Sheets Importer**: Import from Google Sheets
- **Notion Importer**: Import from Notion databases
- **PDF Importer**: Extract Q&A from PDF files

## Next Steps

- [Exporter Plugin Guide](./exporters.md)
- [Plugin Testing Guide](../developer-guides/testing.md)
- [Plugin Security Guide](../developer-guides/security.md)
