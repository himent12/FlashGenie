# 🧞‍♂️ FlashGenie v1.8.4 - Complete Command Reference

**Comprehensive guide to all FlashGenie commands with Rich Terminal UI**

This document provides detailed information about every command available in FlashGenie v1.8.4, including syntax, parameters, examples, and expected output with the Rich Terminal Interface and Enhanced Interactive Shell.

## 📋 **Table of Contents**

- [🔰 Basic Commands](#-basic-commands)
- [📚 Deck Management](#-deck-management)
- [📁 Import/Export](#-importexport)
- [🎯 Study Sessions](#-study-sessions)
- [📊 Analytics & Statistics](#-analytics--statistics)
- [♿ Accessibility](#-accessibility)
- [🔧 Developer Tools](#-developer-tools)
- [⚡ Performance](#-performance)
- [🔍 Search & Help](#-search--help)

---

## 🔰 **Basic Commands**

### `help` - Show Help Information

**Syntax:**
```bash
python -m flashgenie help [command|category]
```

**Description:**
Display comprehensive help information with Rich Terminal UI formatting. Shows main help menu, specific command details, or category information.

**Parameters:**
- `command` (optional): Specific command to get help for
- `category` (optional): Command category to explore

**Examples:**
```bash
# Show main help menu
python -m flashgenie help

# Get help for specific command
python -m flashgenie help import

# Show commands in category
python -m flashgenie help deck_management
```

**Expected Output:**
```
╭─ Welcome to FlashGenie ─────────────────────────────────────────╮
│ 🧞‍♂️ FlashGenie v1.8.4 - Command Reference                      │
╰─────────────────────────────────────────────────────────────────╯

╭─ 🚀 Quick Start ───────────────────────────────────────────────╮
│ 🚀 Quick Start Commands                                        │
│                                                                 │
│   Get help: python -m flashgenie help                          │
│   List decks: python -m flashgenie list                        │
│   Import deck: python -m flashgenie import deck.csv --name...  │
╰─────────────────────────────────────────────────────────────────╯
```

**Aliases:** `--help`, `-h`

---

### `version` - Version Information

**Syntax:**
```bash
python -m flashgenie version
```

**Description:**
Display FlashGenie version, system information, and Rich Terminal UI status.

**Examples:**
```bash
python -m flashgenie version
```

**Expected Output:**
```
╭─ 🧞‍♂️ FlashGenie Version Information ─────────────────────────────╮
│ Version: 1.8.3                                                 │
│ Rich Terminal UI: ✅ Enabled                                   │
│ Python: 3.9.7                                                  │
│ Platform: Windows 10                                           │
│ Accessibility: ✅ Available                                    │
╰─────────────────────────────────────────────────────────────────╯
```

**Aliases:** `--version`, `-v`

---

## 📚 **Deck Management**

### `list` - List All Decks

**Syntax:**
```bash
python -m flashgenie list [--format FORMAT] [--sort FIELD]
```

**Description:**
Display all flashcard decks in a beautiful Rich table with statistics and summary information.

**Parameters:**
- `--format` (optional): Output format (table, json, csv) - default: table
- `--sort` (optional): Sort by field (name, cards, created, modified) - default: name

**Examples:**
```bash
# List all decks with Rich table
python -m flashgenie list

# List decks sorted by card count
python -m flashgenie list --sort cards

# Export deck list as JSON
python -m flashgenie list --format json
```

**Expected Output:**
```
                            📚 Your Flashcard Decks                             
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ Name                  ┃ Cards     ┃ Created           ┃ Modified         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ Spanish Vocabulary    │ 245       │ 2025-06-01        │ 2025-06-07       │
│ Math Formulas         │ 89        │ 2025-05-15        │ 2025-06-05       │
│ History Timeline      │ 156       │ 2025-05-20        │ 2025-06-03       │
└────────────────────────┴────────────┴────────────────────┴───────────────────┘

╭─ 📊 Library Summary ────────────────────────────────────────────────────────╮
│  Total Decks: 3                                                            │
│  Total Cards: 490                                                          │
│  Average Cards per Deck: 163.3                                             │
│  Most Recent: Spanish Vocabulary (2025-06-07)                              │
╰─────────────────────────────────────────────────────────────────────────────╯
```

**Aliases:** `ls`

---

### `create` - Create New Deck

**Syntax:**
```bash
python -m flashgenie create NAME [--description DESC] [--tags TAGS]
```

**Description:**
Create a new empty flashcard deck with optional description and tags.

**Parameters:**
- `NAME` (required): Name of the new deck
- `--description` (optional): Deck description
- `--tags` (optional): Comma-separated tags

**Examples:**
```bash
# Create basic deck
python -m flashgenie create "Spanish Vocabulary"

# Create deck with description
python -m flashgenie create "Math Formulas" --description "Basic algebra and geometry"

# Create deck with tags
python -m flashgenie create "History" --tags "world-war,20th-century"
```

**Expected Output:**
```
✅ Successfully created deck 'Spanish Vocabulary'

╭─ 📚 New Deck Created ──────────────────────────────────────────────────────╮
│  Name: Spanish Vocabulary                                                  │
│  Description: None                                                         │
│  Cards: 0                                                                  │
│  Created: 2025-06-07 14:30:25                                              │
╰─────────────────────────────────────────────────────────────────────────────╯

💡 Next steps:
  • Import cards: python -m flashgenie import deck.csv --name "Spanish Vocabulary"
  • Add cards manually: python -m flashgenie add "Spanish Vocabulary"
```

---

### `delete` - Delete Deck

**Syntax:**
```bash
python -m flashgenie delete DECK_NAME [--confirm] [--backup]
```

**Description:**
Delete a flashcard deck with confirmation prompt. Optionally create backup before deletion.

**Parameters:**
- `DECK_NAME` (required): Name of deck to delete
- `--confirm` (optional): Skip confirmation prompt
- `--backup` (optional): Create backup before deletion

**Examples:**
```bash
# Delete with confirmation
python -m flashgenie delete "Old Deck"

# Delete without confirmation
python -m flashgenie delete "Test Deck" --confirm

# Delete with backup
python -m flashgenie delete "Archive Deck" --backup
```

**Expected Output:**
```
⚠️  Are you sure you want to delete deck 'Old Deck'? (y/N): y

✅ Successfully deleted deck 'Old Deck'

╭─ 🗑️ Deck Deleted ──────────────────────────────────────────────────────────╮
│  Name: Old Deck                                                            │
│  Cards Deleted: 45                                                         │
│  Backup Created: ❌                                                        │
│  Deleted: 2025-06-07 14:35:12                                              │
╰─────────────────────────────────────────────────────────────────────────────╯
```

**Aliases:** `remove`, `rm`

---

## 📁 **Import/Export**

### `import` - Import Flashcards

**Syntax:**
```bash
python -m flashgenie import FILE --name NAME [--format FORMAT] [--encoding ENC]
```

**Description:**
Import flashcards from various file formats with Rich progress indicators and validation.

**Parameters:**
- `FILE` (required): Path to file to import
- `--name` (required): Name for the new deck
- `--format` (optional): File format (csv, json, anki) - auto-detected if not specified
- `--encoding` (optional): File encoding (utf-8, latin-1) - default: utf-8

**Examples:**
```bash
# Import CSV file
python -m flashgenie import vocabulary.csv --name "Spanish Vocabulary"

# Import JSON with specific encoding
python -m flashgenie import cards.json --name "Math" --encoding utf-8

# Import Anki deck
python -m flashgenie import deck.apkg --name "Anki Import" --format anki
```

**Expected Output:**
```
📁 Importing from vocabulary.csv...

╭─ 📊 Import Progress ────────────────────────────────────────────────────────╮
│ ████████████████████████████████████████ 100% (245/245 cards)             │
│ Validating cards... ✅                                                     │
│ Processing tags... ✅                                                      │
│ Saving to database... ✅                                                   │
╰─────────────────────────────────────────────────────────────────────────────╯

✅ Successfully imported 245 cards into deck 'Spanish Vocabulary'

╭─ 📊 Import Summary ─────────────────────────────────────────────────────────╮
│  Name: Spanish Vocabulary                                                   │
│  Cards: 245                                                                 │
│  File: vocabulary.csv                                                       │
│  Format: CSV                                                                │
│  Encoding: utf-8                                                            │
│  Import Time: 2.3 seconds                                                   │
╰─────────────────────────────────────────────────────────────────────────────╯
```

---

### `export` - Export Flashcards

**Syntax:**
```bash
python -m flashgenie export DECK_NAME [--format FORMAT] [--output FILE] [--include-stats]
```

**Description:**
Export flashcard deck to various formats with optional statistics inclusion.

**Parameters:**
- `DECK_NAME` (required): Name of deck to export
- `--format` (optional): Export format (csv, json, anki, pdf) - default: csv
- `--output` (optional): Output file path - auto-generated if not specified
- `--include-stats` (optional): Include learning statistics in export

**Examples:**
```bash
# Export to CSV
python -m flashgenie export "Spanish Vocabulary"

# Export to JSON with stats
python -m flashgenie export "Math" --format json --include-stats

# Export to specific file
python -m flashgenie export "History" --output backup.csv
```

**Expected Output:**
```
📤 Exporting deck 'Spanish Vocabulary'...

╭─ 📊 Export Progress ────────────────────────────────────────────────────────╮
│ ████████████████████████████████████████ 100% (245/245 cards)             │
│ Formatting data... ✅                                                      │
│ Writing file... ✅                                                         │
╰─────────────────────────────────────────────────────────────────────────────╯

✅ Successfully exported 245 cards to 'spanish_vocabulary_2025-06-07.csv'

╭─ 📊 Export Summary ─────────────────────────────────────────────────────────╮
│  Deck: Spanish Vocabulary                                                   │
│  Cards: 245                                                                 │
│  Format: CSV                                                                │
│  File: spanish_vocabulary_2025-06-07.csv                                    │
│  Size: 45.2 KB                                                              │
│  Export Time: 1.1 seconds                                                   │
╰─────────────────────────────────────────────────────────────────────────────╯
```

---

## 🎯 **Study Sessions**

### `quiz` - Start Quiz Session

**Syntax:**
```bash
python -m flashgenie quiz DECK_NAME [--count N] [--timed] [--mode MODE] [--difficulty LEVEL]
```

**Description:**
Start an adaptive quiz session with spaced repetition algorithm and Rich Terminal UI.

**Parameters:**
- `DECK_NAME` (required): Name of deck to quiz
- `--count` (optional): Number of cards to quiz (default: adaptive)
- `--timed` (optional): Enable timed mode
- `--mode` (optional): Quiz mode (adaptive, review, random) - default: adaptive
- `--difficulty` (optional): Filter by difficulty (easy, medium, hard)

**Examples:**
```bash
# Start adaptive quiz
python -m flashgenie quiz "Spanish Vocabulary"

# Timed quiz with 20 cards
python -m flashgenie quiz "Math" --count 20 --timed

# Review difficult cards only
python -m flashgenie quiz "History" --mode review --difficulty hard
```

**Expected Output:**
```
╭─ 🎯 Quiz Session: Spanish Vocabulary ──────────────────────────────────────╮
│ Progress: ████████░░░░░░░░░░░░ 8/20 (40%)  ⏱️  03:45  💯 85%              │
│                                                                             │
│ ┌─ Question 8/20 ────────────────────────────────────────────────────────┐ │
│ │  🇪🇸 ¿Cómo se dice "hello" en español?                                 │ │
│ │  💡 Hint: Common greeting                                              │ │
│ │  🏷️  Tags: greetings, basic                                           │ │
│ │  ⭐ Difficulty: ●●○○○                                                 │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│ 📊 Session Stats:  ✅ 6  ❌ 2  ⏭️  0  ⚡ 2.3 cards/min                   │
╰─────────────────────────────────────────────────────────────────────────────╯

Your answer: _
```

**Aliases:** `study`, `practice`

---

## 📊 **Analytics & Statistics**

### `stats` - Show Statistics

**Syntax:**
```bash
python -m flashgenie stats [DECK_NAME] [--detailed] [--timeframe DAYS] [--export FILE]
```

**Description:**
Display comprehensive learning statistics with Rich charts and tables.

**Parameters:**
- `DECK_NAME` (optional): Specific deck to analyze (default: all decks)
- `--detailed` (optional): Show detailed analytics
- `--timeframe` (optional): Analysis timeframe in days (default: 30)
- `--export` (optional): Export statistics to file

**Examples:**
```bash
# Show overall statistics
python -m flashgenie stats

# Detailed stats for specific deck
python -m flashgenie stats "Spanish Vocabulary" --detailed

# Stats for last 7 days
python -m flashgenie stats --timeframe 7
```

**Expected Output:**
```
╭─ 📊 FlashGenie Statistics ─────────────────────────────────────────────────╮
│                                                                             │
│ 📚 Library Overview                                                         │
│   Total Decks: 3                                                           │
│   Total Cards: 490                                                         │
│   Cards Mastered: 234 (47.8%)                                              │
│   Cards Learning: 189 (38.6%)                                              │
│   Cards New: 67 (13.7%)                                                    │
│                                                                             │
│ 🎯 Study Performance (Last 30 Days)                                        │
│   Study Sessions: 15                                                       │
│   Cards Reviewed: 1,245                                                    │
│   Average Accuracy: 78.5%                                                  │
│   Study Time: 12h 34m                                                      │
│   Average Session: 50m                                                     │
│                                                                             │
│ 📈 Progress Trends                                                          │
│   Daily Average: 41.5 cards                                                │
│   Weekly Growth: +12.3%                                                    │
│   Retention Rate: 85.2%                                                    │
│   Learning Velocity: 2.1 cards/min                                         │
╰─────────────────────────────────────────────────────────────────────────────╯
```

**Aliases:** `statistics`, `analytics`

---

## ♿ **Accessibility**

### `accessibility` - Configure Accessibility

**Syntax:**
```bash
python -m flashgenie accessibility [--enable MODE] [--disable MODE] [--status] [--test]
```

**Description:**
Configure accessibility features including screen reader support, high contrast, and audio feedback.

**Parameters:**
- `--enable` (optional): Enable accessibility mode (screen_reader, high_contrast, large_text, audio)
- `--disable` (optional): Disable accessibility mode
- `--status` (optional): Show current accessibility status
- `--test` (optional): Test accessibility features

**Examples:**
```bash
# Show accessibility status
python -m flashgenie accessibility --status

# Enable high contrast mode
python -m flashgenie accessibility --enable high_contrast

# Enable screen reader support
python -m flashgenie accessibility --enable screen_reader

# Test accessibility features
python -m flashgenie accessibility --test
```

**Expected Output:**
```
╭─ ♿ Accessibility Settings ────────────────────────────────────────────────╮
│                                                                             │
│ Current Settings:                                                           │
│   Screen Reader: ✅ Enabled (NVDA detected)                               │
│   High Contrast: ✅ Enabled                                               │
│   Large Text: ❌ Disabled                                                 │
│   Audio Feedback: ✅ Enabled                                              │
│   Text Size: 1.0x                                                          │
│                                                                             │
│ Detected Screen Readers:                                                    │
│   • NVDA (Active)                                                           │
│   • Narrator (Available)                                                   │
│                                                                             │
│ [ANNOUNCEMENT] Accessibility status displayed                               │
╰─────────────────────────────────────────────────────────────────────────────╯
```

**Aliases:** `a11y`

---

## 🔧 **Developer Tools**

### `debug` - Debug Mode

**Syntax:**
```bash
python -m flashgenie debug [--enable] [--disable] [--console] [--level LEVEL]
```

**Description:**
Enable debug mode with performance monitoring, logging, and developer console.

**Parameters:**
- `--enable` (optional): Enable debug mode
- `--disable` (optional): Disable debug mode
- `--console` (optional): Show debug console
- `--level` (optional): Debug level (debug, info, warning, error)

**Examples:**
```bash
# Enable debug mode
python -m flashgenie debug --enable

# Show debug console
python -m flashgenie debug --console

# Set debug level
python -m flashgenie debug --enable --level debug
```

**Expected Output:**
```
╭─ 🐛 Debug Console - FlashGenie v1.8.3 ─────────────────────────────────────╮
│  ┌─ 📊 Performance Metrics ───────────────────────────────────────────────┐ │
│  │ CPU Usage: 12.5%                                                       │ │
│  │ Memory: 45.2 MB ↑                                                      │ │
│  │ Average Memory: 43.1 MB                                                │ │
│  │                                                                         │ │
│  │ Slowest Functions:                                                      │ │
│  │   quiz_engine.get_next_question: 0.023s                                │ │
│  │   deck_manager.load_deck: 0.015s                                       │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│  ┌─ 📝 Recent Logs ────────────────────────────────────────────────────────┐ │
│  │ [14:23:45] INFO     Quiz session started                               │ │
│  │ [14:23:47] DEBUG    Card selected: id=123, difficulty=0.6              │ │
│  │ [14:23:52] WARNING  Slow query detected (>50ms)                        │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
╰─────────────────────────────────────────────────────────────────────────────╯
```

**Permissions:** Developer

---

## ⚡ **Performance**

### `performance` - Performance Tools

**Syntax:**
```bash
python -m flashgenie performance [--dashboard] [--optimize] [--monitor] [--profile COMMAND]
```

**Description:**
Performance monitoring, optimization, and profiling tools with real-time dashboard.

**Parameters:**
- `--dashboard` (optional): Show performance dashboard
- `--optimize` (optional): Run performance optimization
- `--monitor` (optional): Start performance monitoring
- `--profile` (optional): Profile specific command

**Examples:**
```bash
# Show performance dashboard
python -m flashgenie performance --dashboard

# Optimize performance
python -m flashgenie performance --optimize

# Profile import command
python -m flashgenie performance --profile "import deck.csv --name Test"
```

**Expected Output:**
```
╭─ ⚡ Performance Dashboard ──────────────────────────────────────────────────╮
│ Memory: 35.1 MB                                                           │
│ CPU: 12.5%                                                                │
│ Cache: 245/1000 (87.3% hit rate)                                          │
│ Objects: 40,333                                                           │
│                                                                            │
│ 📊 Recent Performance:                                                     │
│   Import Speed: 245 cards/2.3s (106.5 cards/s)                           │
│   Quiz Response: 0.023s average                                           │
│   Memory Growth: +2.1 MB/hour                                             │
│   Cache Efficiency: 87.3% hit rate                                        │
╰────────────────────────────────────────────────────────────────────────────╯
```

**Permissions:** Developer

---

## 🔍 **Search & Help**

### `search` - Search Commands

**Syntax:**
```bash
python -m flashgenie search QUERY [--category CAT] [--exact]
```

**Description:**
Search through all available commands by name, description, or examples.

**Parameters:**
- `QUERY` (required): Search term or phrase
- `--category` (optional): Limit search to specific category
- `--exact` (optional): Exact match only

**Examples:**
```bash
# Search for import commands
python -m flashgenie search import

# Search in specific category
python -m flashgenie search stats --category analytics

# Exact match search
python -m flashgenie search "quiz" --exact
```

**Expected Output:**
```
╭─ 🔍 Search Results for 'import' ──────────────────────────────────────────╮
│ Found 3 matching commands                                                  │
│                                                                            │
│   🔧 import (import_export)                                               │
│      Import flashcards from CSV, JSON, or other formats with Rich...      │
│                                                                            │
│   🔧 create (deck_management)                                             │
│      Create a new flashcard deck                                          │
│                                                                            │
│   🔧 export (import_export)                                               │
│      Export flashcard deck to various formats                             │
│                                                                            │
│ 💡 Use 'help COMMAND' for detailed information                            │
╰────────────────────────────────────────────────────────────────────────────╯
```

---

## 📝 **CSV Import Format**

When importing flashcards, use this CSV format:

```csv
question,answer,tags,difficulty
"What is the capital of France?","Paris","geography,europe",0.3
"¿Cómo estás?","How are you?","spanish,greetings",0.2
"Photosynthesis definition","Process by which plants make food","biology,science",0.7
```

**Columns:**
- `question` (required): The question or prompt
- `answer` (required): The correct answer
- `tags` (optional): Comma-separated tags for organization
- `difficulty` (optional): Difficulty level from 0.0 (easy) to 1.0 (hard)

---

## 🎯 **Quick Reference**

**Most Common Commands:**
```bash
python -m flashgenie help                    # Show help
python -m flashgenie list                    # List decks
python -m flashgenie import deck.csv --name "My Deck"  # Import
python -m flashgenie quiz "My Deck"          # Start quiz
python -m flashgenie stats                   # View statistics
```

**Accessibility:**
```bash
python -m flashgenie accessibility --enable high_contrast
python -m flashgenie accessibility --enable screen_reader
```

**Developer Tools:**
```bash
python -m flashgenie debug --enable          # Debug mode
python -m flashgenie performance --dashboard # Performance
```

---

*For more information, use `python -m flashgenie help` or visit the [FlashGenie documentation](../README.md).*
