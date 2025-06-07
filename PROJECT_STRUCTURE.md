# FlashGenie v1.5 Project Structure

This document outlines the clean, professional directory structure of FlashGenie v1.5.

## 📁 **Root Directory**

```
FlashGenie/
├── 📄 README.md                    # Main project documentation
├── 📄 CHANGELOG.md                 # Version history and changes
├── 📄 LICENSE                      # MIT License
├── 📄 setup.py                     # Python package setup
├── 📄 requirements.txt             # Python dependencies
├── 📄 mkdocs.yml                   # Documentation configuration
├── 📄 docs-requirements.txt        # Documentation build dependencies
├── 📄 .gitignore                   # Git ignore patterns
├── 📄 PROJECT_STRUCTURE.md         # This file
├── 📁 flashgenie/                  # Main application package
├── 📁 docs/                        # Professional documentation
├── 📁 assets/                      # Sample data and resources
└── 📁 data/                        # User data directory (gitignored)
```

## 🧞‍♂️ **FlashGenie Package** (`flashgenie/`)

```
flashgenie/
├── 📄 __init__.py                  # Package initialization
├── 📄 __main__.py                  # Entry point for python -m flashgenie
├── 📄 main.py                      # Main CLI application
├── 📄 config.py                    # Application configuration
├── 📁 core/                        # Core business logic
├── 📁 data/                        # Data management
├── 📁 interfaces/                  # User interfaces
└── 📁 utils/                       # Utility functions
```

### **Core Module** (`flashgenie/core/`)

```
core/
├── 📄 __init__.py
├── 📄 flashcard.py                 # Flashcard data model
├── 📄 deck.py                      # Deck management
├── 📄 spaced_repetition.py         # SM-2 algorithm implementation
├── 📄 difficulty_analyzer.py       # Smart difficulty adjustment
├── 📄 quiz_engine.py               # Quiz session management
├── 📄 performance_tracker.py       # Learning analytics
├── 📄 tag_manager.py               # Hierarchical tagging system
├── 📄 smart_collections.py         # Dynamic card collections
├── 📄 adaptive_study_planner.py    # AI-powered study planning
├── 📄 learning_velocity_tracker.py # Learning velocity analytics
├── 📄 contextual_learning_engine.py # Context-aware adaptation
├── 📄 knowledge_graph.py           # Knowledge visualization
├── 📄 achievement_system.py        # Gamification and achievements
└── 📄 content_recommender.py       # AI content suggestions
```

### **Data Management** (`flashgenie/data/`)

```
data/
├── 📄 __init__.py
├── 📄 storage.py                   # Data persistence layer
├── 📁 importers/                   # File import modules
│   ├── 📄 __init__.py
│   ├── 📄 base_importer.py
│   ├── 📄 csv_importer.py
│   └── 📄 txt_importer.py
└── 📁 exporters/                   # File export modules
    ├── 📄 __init__.py
    ├── 📄 base_exporter.py
    ├── 📄 csv_exporter.py
    └── 📄 json_exporter.py
```

### **User Interfaces** (`flashgenie/interfaces/`)

```
interfaces/
├── 📄 __init__.py
└── 📁 cli/                         # Command-line interface
    ├── 📄 __init__.py
    ├── 📄 terminal_ui.py           # Interactive terminal UI
    ├── 📄 commands.py              # CLI command handlers
    └── 📄 formatters.py            # Output formatting
```

### **Utilities** (`flashgenie/utils/`)

```
utils/
├── 📄 __init__.py
├── 📄 exceptions.py                # Custom exception classes
├── 📄 logging_config.py            # Logging configuration
├── 📄 validators.py                # Input validation
└── 📄 helpers.py                   # General utility functions
```

## 📚 **Documentation** (`docs/`)

```
docs/
├── 📄 index.md                     # Documentation homepage
├── 📁 user-guide/                  # User documentation
│   ├── 📄 index.md
│   ├── 📄 getting-started.md
│   ├── 📄 smart-features.md
│   └── 📄 advanced-usage.md
├── 📁 developer-guide/             # Developer documentation
│   ├── 📄 index.md
│   └── 📄 api-reference.md
├── 📁 learning-science/            # Research and methodology
│   └── 📄 index.md
├── 📁 community/                   # Community resources
├── 📁 analytics/                   # Analytics documentation
├── 📁 stylesheets/                 # Custom CSS
│   └── 📄 extra.css
└── 📁 javascripts/                 # Custom JavaScript
    └── 📄 mathjax.js
```

## 🎯 **Assets** (`assets/`)

```
assets/
└── 📁 sample_data/                 # Sample flashcard data
    ├── 📄 spanish_vocabulary.csv
    ├── 📄 programming_concepts.csv
    └── 📄 science_facts.txt
```

## 💾 **Data Directory** (`data/`)

*Note: This directory is gitignored and created automatically*

```
data/
├── 📁 decks/                       # User flashcard decks
├── 📁 exports/                     # Exported data files
├── 📁 imports/                     # Imported data files
├── 📁 backups/                     # Automatic backups
├── 📁 sessions/                    # Study session data
├── 📁 achievements/                # Achievement progress
├── 📁 velocity_tracking/           # Learning velocity data
├── 📁 knowledge_graph/             # Knowledge graph data
├── 📁 content_recommendations/     # AI recommendations
├── 📁 contextual_learning/         # Context adaptation data
└── 📁 study_planning/              # Study plan data
```

## 🎯 **Key Design Principles**

### **1. Separation of Concerns**
- **Core**: Business logic and algorithms
- **Data**: Persistence and file handling
- **Interfaces**: User interaction
- **Utils**: Shared utilities

### **2. Modularity**
- Each module has a single responsibility
- Clean interfaces between modules
- Easy to test and maintain

### **3. Extensibility**
- Plugin-ready architecture
- Clear extension points
- Minimal coupling between components

### **4. Professional Standards**
- Consistent naming conventions
- Comprehensive documentation
- Proper error handling
- Type hints throughout

### **5. User Privacy**
- All user data stored locally
- No external dependencies for core functionality
- Clear data organization

## 🚀 **Getting Started**

1. **Installation**: `pip install -r requirements.txt`
2. **Run**: `python -m flashgenie`
3. **Documentation**: `mkdocs serve` (requires `pip install -r docs-requirements.txt`)
4. **Development**: See `docs/developer-guide/`

## 📝 **File Naming Conventions**

- **Python files**: `snake_case.py`
- **Documentation**: `kebab-case.md`
- **Directories**: `snake_case/` or `kebab-case/`
- **Constants**: `UPPER_CASE`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`

This structure ensures FlashGenie v1.5 maintains professional standards suitable for open source distribution, educational use, and commercial applications.
