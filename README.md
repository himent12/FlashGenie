# 🧞‍♂️ FlashGenie v1.8.4

**Intelligent Flashcard Learning with Revolutionary Rich Terminal Interface and Enhanced Interactive Shell**

FlashGenie is an advanced flashcard application that combines proven spaced repetition algorithms with a stunning Rich Terminal UI. Learn more efficiently with adaptive difficulty adjustment, beautiful visual design, comprehensive accessibility features, and professional-grade performance monitoring.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.8.4-green.svg)](https://github.com/himent12/FlashGenie/releases)
[![Rich Terminal UI](https://img.shields.io/badge/terminal-rich_ui-brightgreen.svg)](https://github.com/himent12/FlashGenie)
[![Accessibility](https://img.shields.io/badge/accessibility-WCAG%202.1%20AA-blue.svg)](https://www.w3.org/WAI/WCAG21/AA/)

## ✨ **What Makes FlashGenie Special**

- 🎨 **Beautiful Rich Terminal UI** - Professional interface that rivals GUI applications
- 🧠 **Intelligent Spaced Repetition** - Scientifically-proven learning algorithms
- ♿ **Universal Accessibility** - Screen reader support, high contrast, audio feedback
- ⚡ **High Performance** - Real-time monitoring and intelligent optimization
- 🔧 **Developer Tools** - Comprehensive debugging and profiling capabilities
- 🌍 **Cross-Platform** - Works seamlessly on Windows, macOS, and Linux

## 🚀 **Quick Start**

### **Installation**
```bash
# Clone the repository
git clone https://github.com/himent12/FlashGenie.git
cd FlashGenie

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m flashgenie --version
```

### **Your First Deck**
```bash
# Get help with beautiful Rich Terminal UI
python -m flashgenie help

# Import flashcards from CSV
python -m flashgenie import my_cards.csv --name "My First Deck"

# View your decks with beautiful Rich UI
python -m flashgenie list

# Start learning
python -m flashgenie quiz "My First Deck"
```

### **Getting Help**
```bash
# Comprehensive help system with Rich UI
python -m flashgenie help

# Get help for specific commands
python -m flashgenie help import

# Search for commands
python -m flashgenie search quiz

# Browse commands by category
python -m flashgenie help deck_management
```

### **Example CSV Format**
```csv
question,answer,tags,difficulty
What is the capital of France?,Paris,"geography,europe",0.3
What is 2+2?,4,"math,basic",0.1
Who wrote Romeo and Juliet?,Shakespeare,"literature,drama",0.5
```

## 🎨 **Rich Terminal Interface**

FlashGenie v1.8.4 features a revolutionary Rich Terminal UI that transforms the command-line experience, now available in both standalone commands and the interactive shell:

## 🆘 **Comprehensive Help System**

FlashGenie includes an advanced help system with Rich Terminal UI that makes command discovery intuitive and accessible:

### **Smart Help Features**
- 🔍 **Searchable Commands** - Find any command with fuzzy search
- 📋 **Categorized Reference** - Commands organized by functionality
- 💡 **Contextual Help** - Relevant suggestions based on your task
- 🎨 **Rich Formatting** - Beautiful panels, tables, and syntax highlighting
- ♿ **Accessibility Support** - Screen reader compatible with ARIA-like markup
- 🎯 **Interactive Navigation** - Keyboard navigation and live search

### **Help Commands**
```bash
# Main help menu with categories and quick start
python -m flashgenie help

# Detailed help for any command
python -m flashgenie help import

# Search commands by name or description
python -m flashgenie search accessibility

# Browse commands by category
python -m flashgenie help developer
```

### **Rich Interactive Shell (v1.8.4)**
```bash
# Start interactive shell with Rich UI
python -m flashgenie

# All commands now use beautiful Rich formatting!
FlashGenie > help        # Rich help system
FlashGenie > list        # Rich deck tables
FlashGenie > search quiz # Rich search results
```

### **Beautiful Deck Listings**
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

### **Rich Import Process**
```
✅ Successfully imported 245 cards into deck 'Spanish Vocabulary'

╭─ 📊 Import Summary ─────────────────────────────────────────────────────────╮
│  Name: Spanish Vocabulary                                                   │
│  Cards: 245                                                                 │
│  File: spanish_vocab.csv                                                    │
│  Format: CSV                                                                │
╰─────────────────────────────────────────────────────────────────────────────╯
```

## 🧠 **Core Learning Features**

### **Intelligent Spaced Repetition**
- **Adaptive Algorithm**: Cards appear at optimal intervals based on your performance
- **Difficulty Adjustment**: Automatic difficulty scaling based on your success rate
- **Smart Scheduling**: Prioritizes cards you're most likely to forget
- **Progress Tracking**: Detailed analytics on your learning progress

### **Rich Content Support**
- **Multiple Formats**: Import from CSV, JSON, or create cards manually
- **Tags & Categories**: Organize cards with hierarchical tagging
- **Metadata**: Track creation dates, difficulty, and performance metrics
- **Flexible Structure**: Support for questions, answers, hints, and explanations

### **Study Modes**
- **Adaptive Quiz**: Intelligent card selection based on spaced repetition
- **Timed Sessions**: Practice with time constraints for exam preparation
- **Review Mode**: Focus on cards you've marked for review
- **Random Practice**: Shuffle through your deck for variety

## ♿ **Accessibility Features**

FlashGenie v1.8.4 includes comprehensive accessibility support:

### **Screen Reader Support**
- **Automatic Detection**: Supports NVDA, JAWS, VoiceOver, Orca, and Narrator
- **ARIA-like Markup**: Semantic markup for terminal content
- **Announcements**: Screen reader-friendly notifications and status updates
- **Keyboard Navigation**: Full Tab navigation and focus management

### **Visual Accessibility**
- **High Contrast Mode**: Enhanced visibility for users with visual impairments
- **Large Text Mode**: Configurable text size (1.0x to 2.0x scaling)
- **Reduced Motion**: Skip animations for users sensitive to motion
- **Color Accessibility**: Colorblind-friendly design with multiple indicators

### **Audio Feedback**
- **Cross-Platform Audio**: Sound cues on Windows, macOS, and Linux
- **Context-Aware Sounds**: Different tones for success, error, warning, navigation
- **Configurable Volume**: Adjustable audio feedback levels
- **Graceful Fallback**: System beep when advanced audio unavailable

## ⚡ **Performance & Developer Tools**

### **Real-Time Performance Monitoring**
```
╭─ ⚡ Performance Dashboard ──────────────────────────────────────────╮
│ Memory: 35.1 MB                                                   │
│ CPU: 12.5%                                                        │
│ Cache: 245/1000 (87.3% hit rate)                                  │
│ Objects: 40,333                                                   │
╰────────────────────────────────────────────────────────────────────╯
```

### **Developer Debug Console**
- **Performance Metrics**: Real-time CPU and memory monitoring
- **Function Profiling**: Execution time tracking and bottleneck analysis
- **Memory Analysis**: Usage tracking and leak detection
- **Object Inspector**: Deep property analysis and type information
- **Log Streaming**: Live log display with level-based filtering

### **Intelligent Optimization**
- **Automatic Caching**: LRU cache with TTL and automatic cleanup
- **Async Operations**: Non-blocking tasks with progress feedback
- **Resource Monitoring**: Background monitoring with minimal overhead
- **Memory Optimization**: Automatic garbage collection when thresholds exceeded

## 📋 **Command Reference**

### **Basic Commands**
```bash
# Deck Management
python -m flashgenie list                    # List all decks
python -m flashgenie import deck.csv         # Import from CSV
python -m flashgenie stats "Deck Name"       # Show deck statistics
python -m flashgenie export "Deck Name"      # Export deck data

# Study Sessions
python -m flashgenie quiz "Deck Name"        # Start adaptive quiz
python -m flashgenie quiz "Deck Name" --count 20  # Quiz with 20 cards
python -m flashgenie quiz "Deck Name" --timed     # Timed quiz session
```

### **Advanced Features**
```bash
# Accessibility
python -c "from flashgenie.interfaces.terminal import RichTerminalUI; ui = RichTerminalUI(); ui.enable_accessibility_mode('high_contrast')"

# Performance Monitoring
python -c "from flashgenie.interfaces.terminal import RichTerminalUI; ui = RichTerminalUI(); ui.show_performance_dashboard()"

# Debug Mode
python -c "from flashgenie.interfaces.terminal import RichTerminalUI; ui = RichTerminalUI(); ui.toggle_debug_mode()"
```

## 📦 **Installation & Setup**

### **System Requirements**
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Terminal**: Any modern terminal emulator
- **Memory**: 50MB free disk space
- **Dependencies**: Automatically installed via pip

### **Installation Steps**

#### **Option 1: Quick Install (Recommended)**
```bash
# Clone the repository
git clone https://github.com/himent12/FlashGenie.git
cd FlashGenie

# Install all dependencies (includes Rich Terminal UI)
pip install -r requirements.txt

# Verify installation
python -m flashgenie --version
```

#### **Option 2: Development Install**
```bash
# Clone and install in development mode
git clone https://github.com/himent12/FlashGenie.git
cd FlashGenie
pip install -e .

# Run tests to verify everything works
python -m pytest tests/
```

### **First Run**
```bash
# Test the Rich Terminal Interface
python -c "from flashgenie.interfaces.terminal import RichTerminalUI; ui = RichTerminalUI(); ui.show_success('FlashGenie v1.8.4 Ready!', 'Installation Complete')"

# Create your first deck
echo "question,answer,tags,difficulty
What is the capital of France?,Paris,geography,0.3
What is 2+2?,4,math,0.1" > sample.csv

python -m flashgenie import sample.csv --name "Sample Deck"
python -m flashgenie list
```

## 🔬 **Scientific Foundation**

FlashGenie is built on proven cognitive science research:

### **Spaced Repetition Algorithm**
- Based on the **Ebbinghaus Forgetting Curve** and **SM-2 algorithm**
- Optimizes review intervals to maximize long-term retention
- Adapts to individual learning patterns and performance

### **Adaptive Difficulty**
- Implements **Desirable Difficulties Theory** (Bjork, 1994)
- Automatically adjusts card difficulty based on performance
- Balances challenge and success for optimal learning

### **Metacognitive Learning**
- **Confidence-based assessment** improves self-awareness
- **Retrieval practice** strengthens memory consolidation
- **Interleaving** prevents overconfidence and improves transfer

## 🎯 **Usage Examples**

### **Basic Workflow**
```bash
# 1. Import your flashcards
python -m flashgenie import vocabulary.csv --name "Spanish Vocabulary"

# 2. View your decks
python -m flashgenie list

# 3. Start learning
python -m flashgenie quiz "Spanish Vocabulary"

# 4. Check your progress
python -m flashgenie stats "Spanish Vocabulary"
```

### **Advanced Features**
```bash
# Enable accessibility features
python -c "from flashgenie.interfaces.terminal import RichTerminalUI; ui = RichTerminalUI(); ui.enable_accessibility_mode('high_contrast')"

# Monitor performance
python -c "from flashgenie.interfaces.terminal import RichTerminalUI; ui = RichTerminalUI(); ui.show_performance_dashboard()"

# Export your progress
python -m flashgenie export "Spanish Vocabulary" --format json
```

### **CSV Import Format**
Your CSV files should follow this structure:
```csv
question,answer,tags,difficulty
"What is the capital of Spain?","Madrid","geography,europe",0.4
"¿Cómo estás?","How are you?","spanish,greetings",0.2
"Photosynthesis definition","Process by which plants make food","biology,science",0.7
```

**Columns:**
- `question` (required): The question or prompt
- `answer` (required): The correct answer
- `tags` (optional): Comma-separated tags for organization
- `difficulty` (optional): Difficulty level from 0.0 (easy) to 1.0 (hard)

## 🔧 **Technical Details**

### **Dependencies**
FlashGenie v1.8.4 includes these key dependencies:
```
rich>=13.7.0          # Beautiful terminal formatting
textual>=0.45.0       # Modern terminal interfaces
prompt-toolkit>=3.0.41 # Interactive command line
psutil>=5.9.6         # System monitoring
pandas>=1.5.0         # Data processing
colorama>=0.4.6       # Cross-platform colors
```

### **Architecture**
- **Modular Design**: Clean separation between core logic and UI
- **Rich Terminal UI**: 8 specialized modules for different UI aspects
- **Accessibility First**: Built-in support for screen readers and visual impairments
- **Performance Optimized**: Intelligent caching and resource monitoring
- **Cross-Platform**: Native support for Windows, macOS, and Linux

### **File Structure**
```
flashgenie/
├── core/                    # Core learning algorithms
├── data/                    # Data storage and import/export
├── interfaces/
│   ├── cli/                # Command-line interface
│   └── terminal/           # Rich Terminal UI (v1.8.4)
│       ├── rich_ui.py      # Main Rich UI
│       ├── themes.py       # Theme system
│       ├── widgets.py      # Interactive widgets
│       ├── accessibility.py # Accessibility features
│       └── performance_optimizer.py # Performance tools
└── utils/                  # Utilities and helpers
```

## 🤝 **Contributing**

We welcome contributions to FlashGenie! Here's how you can help:

### **Development Setup**
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/FlashGenie.git
cd FlashGenie

# Install development dependencies
pip install -r requirements.txt

# Run tests to ensure everything works
python -m pytest tests/

# Make your changes and submit a pull request
```

### **Areas for Contribution**
- 🐛 **Bug fixes** and performance improvements
- ✨ **New features** and Rich UI enhancements
- 📚 **Documentation** improvements and examples
- ♿ **Accessibility** features and testing
- 🧪 **Testing** and quality assurance
- 🌍 **Internationalization** and translations

### **Code Style**
- Follow PEP 8 Python style guidelines
- Use type hints for better code clarity
- Write comprehensive docstrings
- Add tests for new functionality
- Maintain Rich UI compatibility

## 📄 **License**

FlashGenie is open source software licensed under the [MIT License](LICENSE). This means you can:

- ✅ Use it for personal and commercial projects
- ✅ Modify and distribute the code
- ✅ Include it in proprietary software
- ✅ Sell applications that include FlashGenie

## 🙏 **Acknowledgments**

FlashGenie v1.8.4 builds upon decades of research in cognitive science and learning. Special thanks to:

- **Hermann Ebbinghaus** for foundational memory research and the forgetting curve
- **Piotr Wozniak** for the SM-2 spaced repetition algorithm
- **Robert Bjork** for desirable difficulties theory
- **The Rich library team** for making beautiful terminal interfaces possible
- **The open source community** for tools, inspiration, and contributions
- **Our contributors** who make FlashGenie better every day

## 📞 **Support & Community**

### **Get Help**
- 📖 **Documentation**: Check the docs/ folder for comprehensive guides
- 💬 **GitHub Discussions**: Community Q&A and feature requests
- 🐛 **GitHub Issues**: Bug reports and technical issues
- 📧 **Email**: Direct support for complex issues

### **Stay Connected**
- ⭐ **Star us on GitHub** to show your support
- 👀 **Watch releases** to stay updated with new features
- 🍴 **Fork the project** to contribute your improvements
- 📢 **Share FlashGenie** with fellow learners and developers

---

## 🌟 **FlashGenie v1.8.4 Highlights**

**Revolutionary Rich Terminal Interface with Enhanced Interactive Shell:**

- 🎨 **Beautiful Design**: Professional-grade terminal interface with Rich formatting everywhere
- 🎮 **Rich Interactive Shell**: Beautiful Rich UI now works in the interactive FlashGenie shell
- ♿ **Universal Access**: Comprehensive accessibility for screen readers and visual impairments
- ⚡ **High Performance**: Intelligent caching and real-time performance monitoring
- 🔧 **Developer Tools**: Advanced debugging, profiling, and development capabilities
- 🌍 **Cross-Platform**: Seamless experience on Windows, macOS, and Linux
- 🧠 **Smart Learning**: Proven spaced repetition algorithms for optimal retention
- 🆘 **Comprehensive Help**: Searchable command reference with Rich Terminal UI

**Transform your learning experience with FlashGenie v1.8.4 - Where beautiful design meets intelligent learning, now with Rich UI everywhere!** 🧞‍♂️✨

*Made with ❤️ by the FlashGenie community*
