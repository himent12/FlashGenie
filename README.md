# 🧞‍♂️ FlashGenie v1.0

**FlashGenie** is an intelligent flashcard application that uses advanced spaced repetition algorithms and AI-powered features to optimize your learning experience. Create, study, and master any subject with scientifically-proven learning techniques enhanced by smart difficulty adjustment and advanced organization tools.

## ✨ Key Features

### 🧠 **Intelligent Learning**
- **Smart Difficulty Auto-Adjustment**: Cards automatically adapt to your performance
- **Advanced Spaced Repetition**: Enhanced SM-2 algorithm with confidence tracking
- **Performance Analytics**: Comprehensive learning insights and progress tracking
- **Confidence-Based Learning**: 1-5 scale confidence ratings optimize review timing

### 🏷️ **Advanced Organization**
- **Hierarchical Tagging**: Organize with parent-child tag relationships (e.g., "Science > Biology > Cells")
- **Auto-Tagging**: AI-powered content analysis suggests relevant tags automatically
- **Smart Collections**: Dynamic card grouping by difficulty, performance, tags, and timing
- **Intelligent Search**: Find cards and decks with advanced filtering

### 📁 **Flexible Data Management**
- **Multiple Import Formats**: CSV, TXT with auto-detection and format recognition
- **Comprehensive Export**: JSON, CSV with full metadata preservation
- **Offline-First**: All data stays local and private
- **Cross-Platform**: Works on Windows, macOS, and Linux

### 💻 **Rich Interface**
- **Interactive CLI**: Full-featured terminal interface with colors and progress tracking
- **Command Mode**: Direct command execution for automation
- **Real-Time Feedback**: Immediate difficulty adjustments and explanations
- **Comprehensive Help**: Built-in guidance and examples

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/himent12/FlashGenie.git
   cd FlashGenie
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run FlashGenie**:
   ```bash
   python -m flashgenie
   ```

### Your First Intelligent Study Session

1. **Import flashcards** with automatic tagging:
   ```bash
   python -m flashgenie import flashcards.csv --name "My Study Deck"
   ```

2. **Auto-tag your cards**:
   ```bash
   python -m flashgenie autotag
   ```

3. **Start an adaptive quiz**:
   ```bash
   python -m flashgenie quiz "My Study Deck"
   ```

4. **Explore smart collections**:
   ```bash
   python -m flashgenie collections
   ```

## 🎯 Smart Features in Action

### 🧠 Adaptive Difficulty
```bash
# During quiz sessions, FlashGenie asks for confidence:
Your answer: Paris
✓ Correct!

How confident were you? (1=Very Low, 2=Low, 3=Medium, 4=High, 5=Very High): 4

# System provides real-time feedback:
Difficulty adjusted: Difficulty increased slightly based on high accuracy, fast response times
```

### 🏷️ Intelligent Organization
```bash
# Create hierarchical tags
python -m flashgenie tags create "Languages > Spanish > Grammar > Verbs"

# Auto-tag your entire deck
python -m flashgenie autotag
# ✓ Added tags to 23 cards

# Explore smart collections
python -m flashgenie collections
# Shows: Easy Cards, Hard Cards, Struggling Cards, Mastered Cards, Due for Review, etc.
```

### 📊 Enhanced Analytics
```bash
python -m flashgenie stats

# Enhanced Statistics: Spanish Vocabulary
# =====================================
# Total Cards: 150        Due for Review: 23
# Reviewed Cards: 89       Average Accuracy: 73.2%
# Total Reviews: 342       Average Difficulty: 0.52
# Avg Response Time: 3.2s
#
# Difficulty Distribution:
# Easy (0.0-0.33): 45 cards
# Medium (0.33-0.67): 78 cards  
# Hard (0.67-1.0): 27 cards
#
# Recent Difficulty Adjustments: 12 cards
#   ¿Cómo estás?... - Difficulty increased based on high accuracy
#   subjunctive mood... - Difficulty decreased based on low accuracy
```

## 📚 Complete Command Reference

### Core Commands
```bash
# Deck Management
python -m flashgenie list                    # List all decks
python -m flashgenie load "Deck Name"       # Load a specific deck
python -m flashgenie import file.csv        # Import flashcards

# Intelligent Study
python -m flashgenie quiz [mode]            # Start adaptive quiz with confidence tracking
python -m flashgenie stats                  # Enhanced statistics with difficulty tracking

# Smart Organization  
python -m flashgenie collections            # Show smart collections and statistics
python -m flashgenie autotag               # Auto-tag cards in current deck
python -m flashgenie tags                  # Manage hierarchical tags
python -m flashgenie tags create <path>    # Create hierarchical tags
python -m flashgenie tags suggest          # Suggest tags for untagged cards
```

### Quiz Modes
- **spaced** (default): Adaptive spaced repetition with difficulty adjustment
- **random**: Questions in random order
- **sequential**: Questions in original order  
- **difficult**: Focus on challenging cards first

### Smart Collections
FlashGenie automatically creates intelligent collections:
- **Easy Cards**: Low difficulty cards (0.0-0.3)
- **Medium Cards**: Moderate difficulty cards (0.3-0.7)
- **Hard Cards**: High difficulty cards (0.7-1.0)
- **Struggling Cards**: Cards with low accuracy
- **Mastered Cards**: Cards with high accuracy
- **Due for Review**: Cards needing attention
- **Recently Added**: Cards added in the last 7 days

## 📁 Supported File Formats

### CSV Format with Auto-Detection
```csv
question,answer,tags
What is the capital of France?,Paris,"geography,europe"
What does CPU stand for?,Central Processing Unit,"technology,computers"
```

### TXT Format with Multiple Patterns
```
Q: What is the capital of Spain?
A: Madrid

Question: What does API stand for?
Answer: Application Programming Interface

# Also supports separator-based formats:
What is photosynthesis?
---
The process by which plants convert light energy into chemical energy
```

## 🧠 Advanced Learning Science

### Enhanced Spaced Repetition
FlashGenie's algorithm considers multiple factors:
- **Performance History**: Accuracy trends over time
- **Response Speed**: How quickly you answer
- **Confidence Levels**: Your self-assessed confidence (1-5 scale)
- **Difficulty Progression**: Dynamic adjustment based on mastery
- **Content Similarity**: Learning from related cards

### Intelligent Difficulty Adjustment
The system automatically:
- **Increases difficulty** for cards you answer quickly and confidently
- **Decreases difficulty** for cards you struggle with
- **Maintains optimal challenge** to maximize retention
- **Provides explanations** for all adjustments
- **Tracks history** of difficulty changes

### Smart Content Analysis
Auto-tagging recognizes:
- **Academic subjects**: mathematics, science, history, literature
- **Programming concepts**: algorithms, data structures, languages
- **Difficulty levels**: basic, intermediate, advanced
- **Content types**: definitions, formulas, procedures, facts

## 🛠️ Architecture & Extensibility

### Modular Design
```
FlashGenie/
├── flashgenie/
│   ├── core/                 # Business logic and algorithms
│   │   ├── flashcard.py      # Enhanced flashcard with tracking
│   │   ├── deck.py           # Deck management with collections
│   │   ├── spaced_repetition.py  # SM-2 algorithm
│   │   ├── difficulty_analyzer.py  # Smart difficulty adjustment
│   │   ├── tag_manager.py    # Hierarchical tagging system
│   │   ├── smart_collections.py   # Dynamic collections
│   │   └── quiz_engine.py    # Enhanced quiz with confidence
│   ├── data/                 # Import/export/storage
│   ├── interfaces/           # User interfaces (CLI implemented)
│   └── utils/                # Utilities and helpers
├── docs/                     # Comprehensive documentation
└── assets/                   # Sample data and resources
```

### Future-Ready
- **GUI-Ready**: Core designed for graphical interfaces
- **API-Ready**: Classes structured for REST API integration
- **Plugin Architecture**: Extensible for custom features
- **Database-Ready**: Easy migration from JSON to SQL databases

## 📖 Documentation

- **[User Guide](docs/user_guide.md)**: Complete usage instructions with examples
- **[Developer Guide](docs/developer_guide.md)**: Technical documentation and contribution guidelines
- **[New Features Guide](docs/new_features.md)**: Detailed documentation of smart features

## 🎯 What Makes FlashGenie Special

### 🧠 **Truly Adaptive Learning**
Unlike traditional flashcard apps, FlashGenie learns from your behavior:
- **Personalized difficulty curves** for each card
- **Confidence-based scheduling** optimizes review timing
- **Performance pattern recognition** improves over time
- **Real-time adjustments** with clear explanations

### 🏷️ **Intelligent Organization**
Advanced organization that scales with your learning:
- **Hierarchical tagging** creates logical knowledge structures
- **Auto-tagging** reduces manual organization work
- **Smart collections** automatically group related content
- **Dynamic filtering** finds exactly what you need

### 📊 **Comprehensive Analytics**
Deep insights into your learning process:
- **Difficulty progression tracking** shows mastery development
- **Performance trend analysis** identifies strengths and weaknesses
- **Response time analytics** optimize study efficiency
- **Confidence correlation** validates self-assessment accuracy

## 🗺️ Roadmap

### ✅ **Version 1.0 (Current)**
- Smart difficulty auto-adjustment with confidence tracking
- Advanced hierarchical tagging with auto-categorization
- Smart collections with multiple criteria types
- Enhanced CLI with comprehensive command set
- Comprehensive analytics and progress tracking

### 🔄 **Planned Features**
- **GUI Interface**: Modern desktop application with visual analytics
- **Web Version**: Browser-based interface with real-time sync
- **Mobile Apps**: iOS and Android with offline capability
- **Advanced AI**: Machine learning for content generation and analysis
- **Collaboration**: Share decks and study with others
- **Cloud Sync**: Optional cloud backup and synchronization

## 🤝 Contributing

We welcome contributions! FlashGenie is built with extensibility in mind.

### Development Setup
```bash
git clone https://github.com/himent12/FlashGenie.git
cd FlashGenie
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m flashgenie
```

### Areas for Contribution
- **New import formats** (Anki, Quizlet, etc.)
- **Enhanced algorithms** (custom spaced repetition variants)
- **GUI development** (Tkinter, PyQt, or web-based)
- **Mobile apps** (React Native, Flutter)
- **Advanced analytics** (machine learning insights)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Spaced Repetition Research**: Hermann Ebbinghaus and Piotr Wozniak
- **SM-2 Algorithm**: SuperMemo methodology
- **Learning Science**: Cognitive psychology research on memory and retention
- **Open Source Community**: Python ecosystem and contributors

## 📞 Support & Community

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/himent12/FlashGenie/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/himent12/FlashGenie/discussions)
- 📚 **Documentation**: [User Guide](docs/user_guide.md) and [Developer Guide](docs/developer_guide.md)
- 🤝 **Contributing**: See [Developer Guide](docs/developer_guide.md) for contribution guidelines

---

**Transform your learning with FlashGenie's intelligent, adaptive flashcard system!** 🧞‍♂️✨

*FlashGenie v1.0 - Where artificial intelligence meets learning science to create the ultimate study companion.*
