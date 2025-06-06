# FlashGenie Developer Guide

This guide provides information for developers who want to contribute to FlashGenie or understand its architecture.

## Architecture Overview

FlashGenie follows a modular architecture with clear separation of concerns:

```
flashgenie/
├── core/           # Business logic and data models
├── data/           # Data handling (import/export/storage)
├── interfaces/     # User interfaces (CLI/GUI/Web)
├── utils/          # Utility functions and helpers
└── config.py       # Configuration settings
```

## Core Components

### Data Models

- **Flashcard**: Individual flashcard with spaced repetition data
- **Deck**: Collection of flashcards with metadata
- **QuizSession**: Manages quiz state and progress
- **PerformanceTracker**: Tracks learning statistics

### Algorithms

- **SpacedRepetitionAlgorithm**: Implements SM-2 algorithm
- **QuizEngine**: Orchestrates quiz sessions and learning

### Data Layer

- **Importers**: Handle various file formats (CSV, TXT, future: Anki, Quizlet)
- **Exporters**: Export data in multiple formats
- **Storage**: Persistent data management with JSON files

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/himent12/FlashGenie.git
   cd FlashGenie
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv flashgenie_env
   source flashgenie_env/bin/activate  # On Windows: flashgenie_env\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Run tests**:
   ```bash
   pytest
   ```

## Code Style and Standards

### Python Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write comprehensive docstrings for all classes and functions
- Maximum line length: 88 characters (Black formatter)

### Documentation

- Use Google-style docstrings
- Include examples in docstrings where helpful
- Keep README and documentation up to date

### Testing

- Write unit tests for all new functionality
- Aim for >90% code coverage
- Use pytest for testing framework
- Place tests in `tests/` directory mirroring source structure

## Adding New Features

### Adding a New Importer

1. Create new importer class inheriting from `BaseImporter`
2. Implement required methods: `import_file()` and `validate_file()`
3. Add to `__init__.py` exports
4. Write comprehensive tests
5. Update documentation

Example:
```python
from flashgenie.data.importers.base_importer import BaseImporter

class MyImporter(BaseImporter):
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.myformat']
    
    def import_file(self, file_path, **kwargs):
        # Implementation here
        pass
    
    def validate_file(self, file_path):
        # Validation logic here
        pass
```

### Adding a New Quiz Mode

1. Add new mode to `QuizMode` enum
2. Implement selection logic in `QuizEngine._select_next_flashcard()`
3. Add command-line support
4. Write tests
5. Update documentation

### Adding New Statistics

1. Extend `PerformanceTracker` with new metrics
2. Update `PerformanceMetrics` dataclass if needed
3. Add visualization/display logic
4. Write tests

## Database Schema (Future)

Currently using JSON files, but planning SQLite migration:

```sql
-- Planned database schema
CREATE TABLE decks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP,
    modified_at TIMESTAMP
);

CREATE TABLE flashcards (
    id TEXT PRIMARY KEY,
    deck_id TEXT REFERENCES decks(id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    difficulty REAL,
    ease_factor REAL,
    review_count INTEGER,
    correct_count INTEGER,
    last_reviewed TIMESTAMP,
    next_review TIMESTAMP,
    created_at TIMESTAMP
);

CREATE TABLE quiz_sessions (
    id TEXT PRIMARY KEY,
    deck_id TEXT REFERENCES decks(id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    total_questions INTEGER,
    correct_answers INTEGER
);
```

## API Design Principles

### Error Handling

- Use custom exceptions from `utils.exceptions`
- Provide meaningful error messages
- Log errors appropriately
- Fail gracefully with user-friendly messages

### Configuration

- Use `config.py` for all configuration
- Support environment variable overrides
- Provide sensible defaults
- Document all configuration options

### Logging

- Use structured logging with appropriate levels
- Log performance metrics for optimization
- Include context in log messages
- Rotate log files to prevent disk space issues

## Testing Strategy

### Unit Tests

- Test individual components in isolation
- Mock external dependencies
- Test both success and failure cases
- Use parameterized tests for multiple scenarios

### Integration Tests

- Test component interactions
- Test file I/O operations
- Test complete workflows
- Use temporary directories for file tests

### Performance Tests

- Benchmark critical algorithms
- Test with large datasets
- Monitor memory usage
- Profile slow operations

## Contributing Guidelines

### Pull Request Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes with tests
4. Run full test suite: `pytest`
5. Update documentation
6. Submit pull request with clear description

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New functionality has tests
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact considered

### Issue Reporting

When reporting bugs:
- Include Python version and OS
- Provide minimal reproduction case
- Include error messages and stack traces
- Describe expected vs actual behavior

## Future Architecture Plans

### GUI Implementation

- Use Tkinter for cross-platform compatibility
- Implement MVC pattern
- Support themes and customization
- Maintain feature parity with CLI

### Web Interface

- Consider Flask or FastAPI for backend
- RESTful API design
- Progressive Web App (PWA) support
- Real-time updates with WebSockets

### Mobile App

- Cross-platform with React Native or Flutter
- Offline synchronization
- Push notifications for study reminders
- Touch-optimized interface

### Cloud Features

- Optional cloud synchronization
- Shared deck marketplace
- Collaborative study groups
- Progress analytics dashboard

## Performance Considerations

### Memory Usage

- Lazy loading for large decks
- Efficient data structures
- Memory profiling for optimization
- Garbage collection awareness

### File I/O

- Streaming for large files
- Atomic file operations
- Backup and recovery mechanisms
- Compression for storage efficiency

### Algorithm Optimization

- Efficient sorting and filtering
- Caching for repeated calculations
- Batch operations where possible
- Profiling critical paths

## Security Considerations

### Data Privacy

- Local-first approach
- No telemetry without consent
- Secure file handling
- Input validation and sanitization

### Future Cloud Features

- End-to-end encryption
- Secure authentication
- GDPR compliance
- Data export capabilities

## Release Process

### Version Management

- Semantic versioning (MAJOR.MINOR.PATCH)
- Changelog maintenance
- Git tags for releases
- Automated version bumping

### Distribution

- PyPI package distribution
- GitHub releases
- Documentation updates
- Migration guides for breaking changes

## Getting Help

### Development Questions

- Check existing issues on GitHub
- Review this developer guide
- Look at existing code examples
- Ask questions in discussions

### Contributing

- Start with "good first issue" labels
- Join development discussions
- Propose new features via issues
- Help with documentation and testing

Thank you for contributing to FlashGenie! 🚀
