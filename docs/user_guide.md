# FlashGenie User Guide

Welcome to FlashGenie! This guide will help you get started with creating, managing, and studying flashcards using our intelligent spaced repetition system.

## Getting Started

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/himent12/FlashGenie.git
   cd FlashGenie
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run FlashGenie:
   ```bash
   python -m flashgenie
   ```

### First Steps

1. **Import your first deck**: Use the `import` command to load flashcards from a CSV or TXT file
2. **Start studying**: Use the `quiz` command to begin a spaced repetition session
3. **Track progress**: Use the `stats` command to monitor your learning progress

## Importing Flashcards

### CSV Format

Create a CSV file with `question` and `answer` columns:

```csv
question,answer
What is the capital of France?,Paris
What does CPU stand for?,Central Processing Unit
```

### TXT Format

Create a text file with Q: and A: prefixes:

```
Q: What is the capital of Spain?
A: Madrid

Q: What does API stand for?
A: Application Programming Interface
```

### Import Commands

```bash
# Import from file
flashgenie import flashcards.csv

# Import with custom name
flashgenie import flashcards.csv --name "My Study Deck"
```

## Quiz Modes

FlashGenie offers several quiz modes to suit different learning styles:

- **Spaced Repetition** (default): Uses scientific algorithms to optimize review timing
- **Random**: Questions in random order
- **Sequential**: Questions in original order
- **Difficult**: Focuses on cards you find challenging

### Starting a Quiz

```bash
# Start with default spaced repetition
flashgenie quiz

# Specify mode
flashgenie quiz --mode random

# Quiz specific deck
flashgenie quiz "My Deck Name"
```

## Commands Reference

### Interactive Mode

Start FlashGenie without arguments to enter interactive mode:

```bash
python -m flashgenie
```

Available commands in interactive mode:
- `help` - Show available commands
- `list` - List all decks
- `load <deck_name>` - Load a specific deck
- `import <file_path>` - Import flashcards
- `quiz [mode]` - Start quiz session
- `stats` - Show deck statistics
- `exit` - Exit FlashGenie

### Command Line Mode

```bash
# List all decks
flashgenie list

# Show detailed deck information
flashgenie list --detailed

# Show statistics
flashgenie stats "Deck Name"

# Export deck
flashgenie export "Deck Name" output.csv
```

## Understanding Spaced Repetition

FlashGenie uses the SM-2 algorithm to optimize when you review each card:

- **New cards**: Reviewed immediately
- **Easy cards**: Longer intervals between reviews
- **Difficult cards**: More frequent reviews
- **Forgotten cards**: Reset to shorter intervals

### Performance Factors

The algorithm considers:
- **Response accuracy**: Whether you answered correctly
- **Response time**: How quickly you answered
- **Historical performance**: Your past performance with the card

## Tips for Effective Learning

1. **Study regularly**: Consistent daily sessions are more effective than cramming
2. **Be honest**: Mark answers as incorrect if you weren't confident
3. **Use quality ratings**: The algorithm works better with accurate feedback
4. **Review due cards**: Focus on cards that are due for review
5. **Create good cards**: Clear, specific questions work best

## Troubleshooting

### Common Issues

**Import fails with encoding error**:
- Try saving your file with UTF-8 encoding
- Check for special characters in your text

**No cards due for review**:
- This is normal! It means you're learning effectively
- Import new cards or wait for existing cards to become due

**Quiz seems too easy/hard**:
- The algorithm adapts to your performance over time
- Be patient and provide honest feedback

### Getting Help

- Use the `help` command for quick reference
- Check the documentation in the `docs/` folder
- Report issues on GitHub: https://github.com/himent12/FlashGenie

## Advanced Features

### Deck Management

- **Tags**: Organize decks with descriptive tags
- **Search**: Find decks by name, description, or tags
- **Statistics**: Track learning progress over time

### Data Export

Export your progress and flashcards:

```bash
# Export as CSV
flashgenie export "My Deck" backup.csv

# Export as JSON (preserves all metadata)
flashgenie export "My Deck" backup.json --format json
```

### Performance Tracking

Monitor your learning with detailed statistics:
- Overall accuracy rates
- Learning streaks
- Time spent studying
- Cards mastered over time

## What's Next?

FlashGenie is actively developed with exciting features planned:

- **GUI Interface**: User-friendly graphical interface
- **Web Version**: Study anywhere with a web browser
- **Mobile App**: Take your flashcards on the go
- **Advanced Analytics**: Detailed learning insights
- **Collaboration**: Share decks with friends and classmates

Happy studying with FlashGenie! 🧞‍♂️
