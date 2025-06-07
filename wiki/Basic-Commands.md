# ⚡ Basic Commands

Essential FlashGenie commands to get you started with AI-powered learning.

## 🎯 **Core Commands**

### **create** - Create New Deck
```bash
# Create a basic deck
python -m flashgenie create "Spanish Vocabulary"

# With description
python -m flashgenie create "Biology Terms" "High school biology vocabulary"
```

### **add** - Add Flashcards
```bash
# Add cards interactively
python -m flashgenie add "Spanish Vocabulary"
```

### **list** - View Your Decks
```bash
# List all decks
python -m flashgenie list

# Detailed view
python -m flashgenie list --detailed
```

### **quiz** - Start Learning
```bash
# Basic quiz
python -m flashgenie quiz "Spanish Vocabulary"

# AI-powered adaptive mode
python -m flashgenie quiz "Biology Terms" --mode adaptive
```

## 🧠 **AI Commands**

### **plan** - Adaptive Study Planning
```bash
# Get an AI study plan
python -m flashgenie plan "Spanish Vocabulary" --time 20 --energy 3

# Full context
python -m flashgenie plan "Biology" --time 30 --energy 4 --environment quiet
```

### **velocity** - Learning Analytics
```bash
# Check your learning velocity
python -m flashgenie velocity "Spanish Vocabulary"

# With predictions
python -m flashgenie velocity "Biology" --predict
```

### **achievements** - View Progress
```bash
# See your achievements
python -m flashgenie achievements

# Check study streaks
python -m flashgenie achievements --streaks
```

## 📊 **Data Commands**

### **import** - Import Flashcards
```bash
# Import from CSV
python -m flashgenie import "Spanish Vocabulary" cards.csv

# With auto-tagging
python -m flashgenie import "Biology" terms.csv --auto-tag
```

### **export** - Export Data
```bash
# Export to CSV
python -m flashgenie export "Spanish Vocabulary" output.csv

# Export to JSON
python -m flashgenie export "Biology" data.json --format json
```

### **stats** - View Statistics
```bash
# Basic statistics
python -m flashgenie stats "Spanish Vocabulary"

# Detailed analytics
python -m flashgenie stats "Biology" --detailed
```

## 🔧 **Utility Commands**

### **help** - Get Help
```bash
# General help
python -m flashgenie --help

# Command-specific help
python -m flashgenie quiz --help
```

### **version** - Check Version
```bash
# Show version
python -m flashgenie --version
```

## 🎯 **Quick Workflow**

Here's a typical FlashGenie session:

```bash
# 1. Check what decks you have
python -m flashgenie list

# 2. Get an AI study plan
python -m flashgenie plan "My Deck" --time 20 --energy 3

# 3. Start studying with AI guidance
python -m flashgenie quiz "My Deck" --mode adaptive

# 4. Check your progress
python -m flashgenie achievements --recent
```

## 💡 **Pro Tips**

- **Use adaptive mode** for AI-optimized learning
- **Set realistic time limits** with `--time`
- **Be honest about energy levels** for better AI planning
- **Check achievements regularly** for motivation
- **Import CSV files** for bulk content addition

---

**Ready for more?** Explore the [Complete Command Reference](Complete-Command-Reference.md) for all available commands! 🧞‍♂️✨
