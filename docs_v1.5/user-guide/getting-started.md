# 🚀 Getting Started with FlashGenie

Welcome to FlashGenie! This guide will help you install FlashGenie, create your first deck, and experience the power of intelligent spaced repetition learning.

## 📋 **Prerequisites**

Before installing FlashGenie, make sure you have:

- **Python 3.8 or higher** - [Download Python](https://python.org/downloads/)
- **Git** (optional but recommended) - [Download Git](https://git-scm.com/downloads/)
- **Terminal/Command Prompt** access
- **10-15 minutes** for setup and first session

!!! tip "Check Your Python Version"
    
    Open your terminal and run:
    ```bash
    python --version
    # or
    python3 --version
    ```
    
    You should see Python 3.8.0 or higher.

## 🔧 **Installation**

### Method 1: Git Clone (Recommended)

=== "Windows"

    ```cmd
    # Open Command Prompt or PowerShell
    git clone https://github.com/himent12/FlashGenie.git
    cd FlashGenie
    pip install -r requirements.txt
    ```

=== "macOS"

    ```bash
    # Open Terminal
    git clone https://github.com/himent12/FlashGenie.git
    cd FlashGenie
    pip3 install -r requirements.txt
    ```

=== "Linux"

    ```bash
    # Open Terminal
    git clone https://github.com/himent12/FlashGenie.git
    cd FlashGenie
    pip3 install -r requirements.txt
    ```

### Method 2: Download ZIP

1. Go to [FlashGenie GitHub](https://github.com/himent12/FlashGenie)
2. Click **"Code"** → **"Download ZIP"**
3. Extract the ZIP file
4. Open terminal in the extracted folder
5. Run: `pip install -r requirements.txt`

### Verify Installation

Test that FlashGenie is working:

```bash
python -m flashgenie --version
```

You should see: `FlashGenie 1.0.0`

!!! success "Installation Complete!"
    
    If you see the version number, FlashGenie is successfully installed! 🎉

## 🎮 **Your First FlashGenie Experience**

Let's start with the sample data to see FlashGenie in action:

### Step 1: Import Sample Data

```bash
# Import the included sample flashcards
python -m flashgenie import assets/sample_data/example_deck.csv --name "Sample Deck"
```

You should see:
```
Successfully imported 15 flashcards into deck 'Sample Deck'
```

### Step 2: Explore Smart Collections

```bash
# See how FlashGenie automatically organizes your cards
python -m flashgenie collections
```

This shows you FlashGenie's smart collections - dynamic groups that automatically categorize your cards!

### Step 3: Your First Intelligent Quiz

```bash
# Start an adaptive quiz session
python -m flashgenie quiz "Sample Deck"
```

During the quiz, you'll experience:

- **Adaptive questions** based on spaced repetition
- **Confidence ratings** (1-5 scale) that help FlashGenie learn about you
- **Real-time difficulty adjustments** with explanations
- **Smart feedback** that helps optimize your learning

!!! tip "During Your First Quiz"
    
    - Answer honestly - FlashGenie learns from your responses
    - Use confidence ratings - they help optimize your learning schedule
    - Pay attention to difficulty adjustments - they show FlashGenie adapting to you
    - Don't worry about perfect scores - the system optimizes for long-term retention

### Step 4: View Your Learning Analytics

```bash
# See detailed statistics about your learning
python -m flashgenie stats
```

This shows you comprehensive analytics including:
- Accuracy rates and trends
- Difficulty distribution
- Response time analysis
- Recent difficulty adjustments

## 📁 **Creating Your First Deck**

Now let's create a deck with your own flashcards!

### Supported File Formats

FlashGenie supports multiple formats with intelligent auto-detection:

=== "CSV Format"

    Create a file called `my_flashcards.csv`:
    
    ```csv
    question,answer,tags
    What is the capital of France?,Paris,"geography,europe"
    What does CPU stand for?,Central Processing Unit,"technology,computers"
    What is photosynthesis?,Process plants use to convert light to energy,"biology,science"
    ```

=== "TXT Format"

    Create a file called `my_flashcards.txt`:
    
    ```
    Q: What is the capital of Spain?
    A: Madrid
    
    Q: What does API stand for?
    A: Application Programming Interface
    
    Q: What is machine learning?
    A: A subset of AI that learns from data
    ```

=== "Advanced TXT Format"

    FlashGenie supports multiple TXT patterns:
    
    ```
    Question: What is quantum computing?
    Answer: Computing using quantum mechanical phenomena
    
    # Separator-based format
    What is blockchain?
    ---
    A distributed ledger technology
    
    # Simple format
    What is DNA?
    Deoxyribonucleic acid
    ```

### Import Your Deck

```bash
# Import your flashcards
python -m flashgenie import my_flashcards.csv --name "My Study Deck"

# Or import TXT format
python -m flashgenie import my_flashcards.txt --name "My Study Deck"
```

### Auto-Tag Your Cards

Let FlashGenie automatically suggest tags based on content:

```bash
# Load your deck
python -m flashgenie load "My Study Deck"

# Auto-tag cards based on content analysis
python -m flashgenie autotag
```

FlashGenie will analyze your card content and suggest relevant tags automatically!

## 🎯 **Understanding the CLI Interface**

FlashGenie uses a powerful command-line interface. Here are the essential commands:

### Interactive Mode

```bash
# Start interactive mode
python -m flashgenie

# You'll see:
FlashGenie > help
```

In interactive mode, you can use commands without the `python -m flashgenie` prefix.

### Essential Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `list` | Show all decks | `python -m flashgenie list` |
| `load <deck>` | Load a specific deck | `python -m flashgenie load "My Deck"` |
| `import <file>` | Import flashcards | `python -m flashgenie import cards.csv` |
| `quiz [mode]` | Start quiz session | `python -m flashgenie quiz` |
| `stats` | View statistics | `python -m flashgenie stats` |
| `collections` | Show smart collections | `python -m flashgenie collections` |
| `autotag` | Auto-tag current deck | `python -m flashgenie autotag` |
| `tags` | Manage tags | `python -m flashgenie tags` |
| `help` | Show help | `python -m flashgenie help` |

### Quiz Modes

FlashGenie offers several quiz modes:

- **`spaced`** (default): Intelligent spaced repetition with difficulty adjustment
- **`random`**: Questions in random order
- **`sequential`**: Questions in original order
- **`difficult`**: Focus on challenging cards first

```bash
# Examples
python -m flashgenie quiz                    # Default spaced repetition
python -m flashgenie quiz --mode random     # Random order
python -m flashgenie quiz --mode difficult  # Hard cards first
```

## 🧠 **Understanding Quiz Results**

During and after quizzes, FlashGenie provides rich feedback:

### During Quiz

```bash
Question: What is the capital of France?
Your answer: Paris
✓ Correct!

How confident were you? (1=Very Low, 2=Low, 3=Medium, 4=High, 5=Very High): 4

# FlashGenie may show:
Difficulty adjusted: Difficulty increased slightly based on high accuracy, fast response times
```

### After Quiz

```bash
Quiz Session Complete!
=====================================
Questions Answered: 10
Correct Answers: 8 (80%)
Average Response Time: 3.2 seconds
Session Duration: 5 minutes

Cards with Difficulty Adjustments: 3
- "What is photosynthesis?" - Difficulty decreased (struggling)
- "What is DNA?" - Difficulty increased (mastered)
```

### Understanding Difficulty Adjustments

FlashGenie automatically adjusts card difficulty based on:

- **Accuracy**: How often you get the card right
- **Response Time**: How quickly you answer
- **Confidence**: Your self-assessed confidence (1-5 scale)
- **Trends**: Whether you're improving or struggling

!!! info "Why Difficulty Matters"
    
    Difficulty adjustment ensures:
    - **Optimal Challenge**: Cards stay at the right difficulty level
    - **Efficient Learning**: Focus time on cards that need it
    - **Reduced Frustration**: Hard cards become easier over time
    - **Accelerated Progress**: Easy cards become more challenging

## 🎉 **Next Steps**

Congratulations! You've successfully:

- ✅ Installed FlashGenie
- ✅ Imported your first deck
- ✅ Experienced intelligent quizzing
- ✅ Seen smart difficulty adjustment in action
- ✅ Explored basic analytics

### What's Next?

<div class="grid cards" markdown>

-   :material-brain: **Explore Smart Features**

    ---

    Learn about hierarchical tagging, smart collections, and advanced analytics

    [:octicons-arrow-right-24: Smart Features](smart-features.md)

-   :material-speedometer: **Advanced Usage**

    ---

    Master advanced workflows and power-user features

    [:octicons-arrow-right-24: Advanced Usage](advanced-usage.md)

-   :material-lightbulb: **Best Practices**

    ---

    Learn evidence-based strategies for effective learning

    [:octicons-arrow-right-24: Best Practices](best-practices.md)

-   :material-help-circle: **Need Help?**

    ---

    Troubleshooting and community support

    [:octicons-arrow-right-24: Troubleshooting](troubleshooting.md)

</div>

## 🔧 **Troubleshooting Installation**

### Common Issues

!!! warning "Python Version Error"
    
    **Error**: `python: command not found`
    
    **Solution**: Try `python3` instead of `python`, or install Python from [python.org](https://python.org)

!!! warning "Permission Error"
    
    **Error**: `Permission denied` or `Access denied`
    
    **Solution**: 
    - On Windows: Run Command Prompt as Administrator
    - On macOS/Linux: Use `pip3 install --user -r requirements.txt`

!!! warning "Module Not Found"
    
    **Error**: `ModuleNotFoundError: No module named 'pandas'`
    
    **Solution**: Ensure you ran `pip install -r requirements.txt` in the FlashGenie directory

### Getting Help

If you're still having issues:

1. Check our [Troubleshooting Guide](troubleshooting.md)
2. Search [GitHub Issues](https://github.com/himent12/FlashGenie/issues)
3. Ask for help in [GitHub Discussions](https://github.com/himent12/FlashGenie/discussions)
4. Email us: [huckflower@gmail.com](mailto:huckflower@gmail.com)

---

**Ready to dive deeper?** Continue to [Smart Features](smart-features.md) to discover what makes FlashGenie truly intelligent! 🧞‍♂️✨
