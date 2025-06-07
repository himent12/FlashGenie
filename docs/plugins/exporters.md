# Exporter Plugin Development Guide

Exporter plugins enable FlashGenie to export flashcard data to various formats and external services. This guide covers creating robust exporter plugins for different output formats.

## Overview

Exporter plugins convert FlashGenie's internal flashcard data into external formats, enabling users to share, backup, or use their flashcards in other applications.

## Base Class: ExporterPlugin

All exporter plugins must inherit from `ExporterPlugin`:

```python
from flashgenie.core.plugin_system import ExporterPlugin
from flashgenie.core import Deck
from pathlib import Path
from typing import Dict, List, Any

class MyExporterPlugin(ExporterPlugin):
    def __init__(self):
        super().__init__()
        self.name = "my-exporter"
        self.version = "1.0.0"
        self.description = "Export to custom format"
    
    def can_export(self, deck: Deck, format_type: str) -> bool:
        """Check if this plugin can export in the given format."""
        return format_type in ['pdf', 'html']
    
    def export_data(self, deck: Deck, output_path: Path, format_type: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Export deck data to specified format."""
        # Implementation here
        pass
    
    def get_supported_formats(self) -> List[str]:
        """Return list of supported export formats."""
        return ['pdf', 'html']
```

## Required Methods

### `can_export(deck: Deck, format_type: str) -> bool`

Determines if the plugin can handle a specific export format:

```python
def can_export(self, deck: Deck, format_type: str) -> bool:
    """Check if this plugin can export in the given format."""
    # Check format support
    if format_type not in self.get_supported_formats():
        return False
    
    # Optional: Check deck compatibility
    if format_type == 'anki' and not deck.flashcards:
        return False
    
    return True
```

### `export_data(deck: Deck, output_path: Path, format_type: str, options: Dict[str, Any]) -> Dict[str, Any]`

Performs the actual export operation:

```python
def export_data(self, deck: Deck, output_path: Path, format_type: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Export deck data."""
    try:
        options = options or {}
        cards_exported = 0
        
        if format_type == 'pdf':
            cards_exported = self._export_pdf(deck, output_path, options)
        elif format_type == 'html':
            cards_exported = self._export_html(deck, output_path, options)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        return {
            "success": True,
            "cards_exported": cards_exported,
            "output_path": str(output_path),
            "format": format_type
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "cards_exported": 0
        }
```

### `get_supported_formats() -> List[str]`

Returns supported export formats:

```python
def get_supported_formats(self) -> List[str]:
    """Get list of supported export formats."""
    return ['pdf', 'html', 'csv', 'json']
```

## Complete Example: PDF Exporter

Here's a complete PDF exporter plugin:

```python
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from flashgenie.core.plugin_system import ExporterPlugin
from flashgenie.core import Deck

# External dependencies
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class PDFExporterPlugin(ExporterPlugin):
    def __init__(self):
        super().__init__()
        self.name = "pdf-exporter"
        self.version = "1.0.0"
        self.description = "Export flashcards to PDF format"
    
    def initialize(self):
        """Initialize the plugin."""
        self.logger.info("PDF Exporter plugin initialized")
        self.require_permission(Permission.FILE_WRITE)
        self.require_permission(Permission.DECK_READ)
    
    def can_export(self, deck: Deck, format_type: str) -> bool:
        """Check if this plugin can export in the given format."""
        return format_type == 'pdf' and len(deck.flashcards) > 0
    
    def export_data(self, deck: Deck, output_path: Path, format_type: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Export deck to PDF."""
        try:
            options = options or {}
            
            # Validate format
            if format_type != 'pdf':
                raise ValueError(f"Unsupported format: {format_type}")
            
            # Export based on layout style
            layout = options.get('layout', 'cards')
            
            if layout == 'cards':
                cards_exported = self._export_cards_layout(deck, output_path, options)
            elif layout == 'list':
                cards_exported = self._export_list_layout(deck, output_path, options)
            elif layout == 'study_guide':
                cards_exported = self._export_study_guide(deck, output_path, options)
            else:
                raise ValueError(f"Unsupported layout: {layout}")
            
            return {
                "success": True,
                "cards_exported": cards_exported,
                "output_path": str(output_path),
                "format": format_type,
                "layout": layout,
                "file_size": output_path.stat().st_size
            }
            
        except Exception as e:
            self.logger.error(f"PDF export failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "cards_exported": 0
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats."""
        return ['pdf']
    
    def _export_cards_layout(self, deck: Deck, output_path: Path, options: Dict[str, Any]) -> int:
        """Export in flashcard layout (one card per page)."""
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=options.get('page_size', letter),
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=18
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Title page
        if options.get('include_title', True):
            story.extend(self._create_title_page(deck, styles))
            story.append(PageBreak())
        
        # Export each card
        for i, card in enumerate(deck.flashcards):
            # Question page
            story.append(Paragraph(f"Card {i+1} - Question", styles['Heading2']))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(card.question, styles['Normal']))
            
            if options.get('include_tags', True) and card.tags:
                story.append(Spacer(1, 0.2*inch))
                tags_text = f"Tags: {', '.join(card.tags)}"
                story.append(Paragraph(tags_text, styles['Italic']))
            
            story.append(PageBreak())
            
            # Answer page
            story.append(Paragraph(f"Card {i+1} - Answer", styles['Heading2']))
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(card.answer, styles['Normal']))
            
            if options.get('include_metadata', False):
                story.append(Spacer(1, 0.2*inch))
                metadata = [
                    f"Difficulty: {card.difficulty:.1f}",
                    f"Created: {card.created_at.strftime('%Y-%m-%d')}",
                    f"Times Reviewed: {card.review_count}"
                ]
                for meta in metadata:
                    story.append(Paragraph(meta, styles['Italic']))
            
            if i < len(deck.flashcards) - 1:
                story.append(PageBreak())
        
        doc.build(story)
        return len(deck.flashcards)
    
    def _export_list_layout(self, deck: Deck, output_path: Path, options: Dict[str, Any]) -> int:
        """Export in list layout (Q&A pairs on same page)."""
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=options.get('page_size', letter),
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=18
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Title page
        if options.get('include_title', True):
            story.extend(self._create_title_page(deck, styles))
            story.append(PageBreak())
        
        # Export cards in list format
        for i, card in enumerate(deck.flashcards):
            # Card header
            story.append(Paragraph(f"Card {i+1}", styles['Heading3']))
            story.append(Spacer(1, 0.1*inch))
            
            # Question
            story.append(Paragraph("Question:", styles['Heading4']))
            story.append(Paragraph(card.question, styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            # Answer
            story.append(Paragraph("Answer:", styles['Heading4']))
            story.append(Paragraph(card.answer, styles['Normal']))
            
            # Tags and metadata
            if options.get('include_tags', True) and card.tags:
                story.append(Spacer(1, 0.1*inch))
                tags_text = f"Tags: {', '.join(card.tags)}"
                story.append(Paragraph(tags_text, styles['Italic']))
            
            story.append(Spacer(1, 0.3*inch))
            
            # Page break every N cards
            cards_per_page = options.get('cards_per_page', 3)
            if (i + 1) % cards_per_page == 0 and i < len(deck.flashcards) - 1:
                story.append(PageBreak())
        
        doc.build(story)
        return len(deck.flashcards)
    
    def _export_study_guide(self, deck: Deck, output_path: Path, options: Dict[str, Any]) -> int:
        """Export as study guide with questions and answers separated."""
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=options.get('page_size', letter),
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=18
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Title page
        if options.get('include_title', True):
            story.extend(self._create_title_page(deck, styles))
            story.append(PageBreak())
        
        # Questions section
        story.append(Paragraph("Study Questions", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        for i, card in enumerate(deck.flashcards):
            story.append(Paragraph(f"{i+1}. {card.question}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(PageBreak())
        
        # Answers section
        story.append(Paragraph("Answer Key", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        for i, card in enumerate(deck.flashcards):
            story.append(Paragraph(f"{i+1}. {card.answer}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        return len(deck.flashcards)
    
    def _create_title_page(self, deck: Deck, styles) -> List:
        """Create title page elements."""
        title_elements = []
        
        # Deck name
        title_elements.append(Paragraph(deck.name, styles['Title']))
        title_elements.append(Spacer(1, 0.3*inch))
        
        # Deck description
        if deck.description:
            title_elements.append(Paragraph(deck.description, styles['Normal']))
            title_elements.append(Spacer(1, 0.2*inch))
        
        # Statistics
        stats = [
            f"Total Cards: {len(deck.flashcards)}",
            f"Created: {deck.created_at.strftime('%Y-%m-%d')}",
            f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ]
        
        for stat in stats:
            title_elements.append(Paragraph(stat, styles['Normal']))
        
        return title_elements
    
    def get_export_options(self) -> Dict[str, Any]:
        """Get available export options for UI."""
        return {
            "layout": {
                "type": "select",
                "options": ["cards", "list", "study_guide"],
                "default": "cards",
                "description": "Layout style for the PDF"
            },
            "page_size": {
                "type": "select", 
                "options": ["letter", "a4"],
                "default": "letter",
                "description": "Page size for the PDF"
            },
            "include_title": {
                "type": "boolean",
                "default": True,
                "description": "Include title page"
            },
            "include_tags": {
                "type": "boolean",
                "default": True,
                "description": "Include card tags"
            },
            "include_metadata": {
                "type": "boolean",
                "default": False,
                "description": "Include card metadata"
            },
            "cards_per_page": {
                "type": "number",
                "default": 3,
                "min": 1,
                "max": 10,
                "description": "Cards per page (list layout only)"
            }
        }
```

## Plugin Manifest

Your `plugin.json` should specify exporter-specific settings:

```json
{
  "name": "pdf-exporter",
  "version": "1.0.0",
  "description": "Export flashcards to PDF with multiple layout options",
  "author": "Your Name",
  "license": "MIT",
  "type": "exporter",
  "entry_point": "PDFExporterPlugin",
  "permissions": ["file_write", "deck_read"],
  "dependencies": ["reportlab>=3.6.0"],
  "settings_schema": {
    "default_layout": {
      "type": "string",
      "default": "cards",
      "description": "Default PDF layout style"
    },
    "default_page_size": {
      "type": "string",
      "default": "letter",
      "description": "Default page size"
    }
  },
  "supported_formats": ["pdf"],
  "export_options": {
    "layout": ["cards", "list", "study_guide"],
    "page_size": ["letter", "a4"],
    "customizable": true
  },
  "flashgenie_version": ">=1.8.0"
}
```

## Testing Your Exporter

Create comprehensive tests in `test_plugin.py`:

```python
import unittest
import tempfile
from pathlib import Path
from flashgenie.core import Deck, Flashcard
from your_plugin import PDFExporterPlugin

class TestPDFExporter(unittest.TestCase):
    def setUp(self):
        self.plugin = PDFExporterPlugin()
        self.plugin.initialize()
        
        # Create test deck
        self.deck = Deck(name="Test Deck", description="Test deck for export")
        self.deck.add_flashcard(Flashcard(
            question="What is 2+2?",
            answer="4",
            tags=["math", "basic"]
        ))
        self.deck.add_flashcard(Flashcard(
            question="Capital of France?",
            answer="Paris",
            tags=["geography"]
        ))
    
    def test_can_export_pdf(self):
        """Test PDF export capability detection."""
        self.assertTrue(self.plugin.can_export(self.deck, 'pdf'))
        self.assertFalse(self.plugin.can_export(self.deck, 'html'))
    
    def test_export_cards_layout(self):
        """Test cards layout export."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            output_path = Path(f.name)
        
        result = self.plugin.export_data(
            self.deck, 
            output_path, 
            'pdf',
            {'layout': 'cards'}
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["cards_exported"], 2)
        self.assertTrue(output_path.exists())
        self.assertGreater(output_path.stat().st_size, 0)
        
        output_path.unlink()  # Clean up
    
    def test_export_with_options(self):
        """Test export with custom options."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            output_path = Path(f.name)
        
        options = {
            'layout': 'list',
            'include_tags': True,
            'cards_per_page': 2
        }
        
        result = self.plugin.export_data(self.deck, output_path, 'pdf', options)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["layout"], "list")
        
        output_path.unlink()  # Clean up

if __name__ == '__main__':
    unittest.main()
```

## Best Practices

### Output Quality
- Support multiple page sizes and orientations
- Use appropriate fonts and styling
- Handle long text gracefully
- Include proper page breaks

### Customization
- Provide layout options
- Allow styling customization
- Support different output qualities
- Enable selective content inclusion

### Performance
- Stream large exports
- Provide progress feedback
- Optimize memory usage
- Handle large decks efficiently

### Error Handling
- Validate output paths
- Handle file permission issues
- Gracefully handle formatting errors
- Provide meaningful error messages

## Advanced Features

### Template System
Support custom templates:

```python
def export_with_template(self, deck: Deck, output_path: Path, template_path: Path) -> Dict[str, Any]:
    """Export using custom template."""
    pass
```

### Batch Export
Export multiple decks:

```python
def export_multiple_decks(self, decks: List[Deck], output_dir: Path, format_type: str) -> Dict[str, Any]:
    """Export multiple decks to separate files."""
    pass
```

### Interactive Export
Provide export preview:

```python
def preview_export(self, deck: Deck, format_type: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Generate export preview."""
    pass
```

## Integration Examples

- **Anki Exporter**: Export to .apkg format
- **Quizlet Exporter**: Export to Quizlet-compatible format
- **Mobile App Exporter**: Export for mobile flashcard apps
- **Print Exporter**: Export optimized for printing
- **Web Exporter**: Export as interactive web pages

## Next Steps

- [Theme Plugin Guide](./themes.md)
- [Plugin UI Guidelines](../developer-guides/ui-guidelines.md)
- [Plugin Performance Guide](../developer-guides/performance.md)
