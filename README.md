# FlashGenie v1.5 🧞‍♂️

**The AI-Powered Intelligent Spaced Repetition Learning Platform**

FlashGenie v1.5 transforms traditional flashcard studying into an intelligent, adaptive, and engaging learning experience. Powered by cutting-edge AI algorithms and grounded in cognitive science research, FlashGenie adapts to your learning patterns, predicts your progress, and optimizes your study sessions for maximum efficiency.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.5.0-green.svg)](https://github.com/himent12/FlashGenie/releases)

## ✨ **What's New in v1.5**

### 🧠 **AI-Powered Learning Intelligence**
- **Adaptive Study Sessions**: Context-aware study planning that adapts to your time, energy, and environment
- **Learning Velocity Tracking**: Predictive analytics that forecast your mastery timeline
- **Contextual Learning Engine**: Dynamic adaptation based on device, environment, and attention level
- **Knowledge Graph Visualization**: Visual representation of your learning progress and concept relationships
- **Gamification System**: Comprehensive achievement system with streaks, challenges, and rewards
- **Intelligent Content Suggestions**: AI-powered recommendations for new cards and study strategies

### 📚 **Enhanced Core Features**
- **Smart Spaced Repetition**: Enhanced algorithms with personalized intervals
- **Advanced Difficulty Analysis**: Multi-factor difficulty adjustment with confidence weighting
- **Hierarchical Tag Management**: Sophisticated content organization with auto-tagging
- **Smart Collections**: Dynamic grouping with advanced filtering and analytics
- **Comprehensive Analytics**: Deep learning insights with velocity tracking and predictions

## 🚀 **Key Features**

### **🎯 Intelligent Learning**
- **Adaptive Study Planning**: AI creates optimal study sessions based on your context
- **Predictive Analytics**: Forecasts learning progress and mastery timelines
- **Context Awareness**: Adapts to your environment, device, and attention level
- **Smart Difficulty**: Multi-factor difficulty adjustment with performance analysis
- **Personalized Intervals**: Spaced repetition optimized for your learning patterns

### **📊 Advanced Analytics**
- **Learning Velocity**: Track cards per day, mastery rate, and study efficiency
- **Progress Visualization**: Knowledge graphs showing concept relationships and mastery
- **Performance Insights**: Detailed analytics with trends and recommendations
- **Bottleneck Identification**: Find cards that slow your progress
- **Mastery Prediction**: AI-powered timeline forecasts with confidence intervals

### **🎮 Gamification & Motivation**
- **Achievement System**: 20+ achievements across different categories
- **Study Streaks**: Daily, weekly, accuracy, and perfect streaks
- **Level Progression**: Earn points and level up as you learn
- **Challenge System**: Time-limited challenges and competitions
- **Progress Rewards**: Visual feedback and celebration of milestones

### **💡 Smart Content Management**
- **AI Content Suggestions**: Intelligent recommendations for new flashcards
- **Gap Analysis**: Identifies missing knowledge and prerequisite concepts
- **Related Topic Discovery**: Suggests related topics for expanded learning
- **Auto-tagging**: Intelligent content analysis with hierarchical organization
- **Import/Export**: Support for multiple formats with metadata preservation

## 📦 **Installation**

### **Requirements**
- Python 3.8 or higher
- 50MB free disk space
- Terminal/Command prompt access

### **Quick Install**
```bash
# Clone the repository
git clone https://github.com/himent12/FlashGenie.git
cd FlashGenie

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m flashgenie --version
```

### **Alternative Installation**
```bash
# Install from PyPI (when available)
pip install flashgenie

# Or install in development mode
pip install -e .
```

## 🎯 **Quick Start Guide**

### **1. Create Your First Deck**
```bash
# Create a new deck
python -m flashgenie create "Spanish Vocabulary" "Learn Spanish words and phrases"

# Import flashcards from CSV
python -m flashgenie import "Spanish Vocabulary" my_cards.csv

# Or create cards interactively
python -m flashgenie add "Spanish Vocabulary"
```

### **2. Start Learning with AI**
```bash
# Get an adaptive study plan
python -m flashgenie plan "Spanish Vocabulary" --time 30 --energy 4

# Start an intelligent quiz session
python -m flashgenie quiz "Spanish Vocabulary" --mode adaptive

# Quick mobile session
python -m flashgenie plan "Spanish Vocabulary" --time 10 --environment mobile
```

### **3. Track Your Progress**
```bash
# View comprehensive statistics
python -m flashgenie stats "Spanish Vocabulary"

# Analyze learning velocity
python -m flashgenie velocity "Spanish Vocabulary" --predict

# Generate knowledge graph
python -m flashgenie graph "Spanish Vocabulary" --export graph.html
```

### **4. Get AI Recommendations**
```bash
# Get content suggestions
python -m flashgenie suggest "Spanish Vocabulary" --cards 5

# Find related topics
python -m flashgenie suggest "Spanish Vocabulary" --topics

# Identify knowledge gaps
python -m flashgenie suggest "Spanish Vocabulary" --gaps
```

### **5. Track Achievements**
```bash
# View your achievements
python -m flashgenie achievements

# Check study streaks
python -m flashgenie achievements --streaks

# See progress towards goals
python -m flashgenie achievements --progress
```

## 🎮 **Complete Command Reference**

### **Core Commands**
| Command | Description | Example |
|---------|-------------|---------|
| `create` | Create a new deck | `python -m flashgenie create "Math Facts"` |
| `import` | Import flashcards | `python -m flashgenie import "Deck" cards.csv` |
| `quiz` | Start a quiz session | `python -m flashgenie quiz "Deck" --mode adaptive` |
| `stats` | View statistics | `python -m flashgenie stats "Deck"` |
| `list` | List all decks | `python -m flashgenie list` |
| `export` | Export deck data | `python -m flashgenie export "Deck" output.json` |

### **AI-Powered Commands**
| Command | Description | Example |
|---------|-------------|---------|
| `plan` | Create adaptive study plan | `python -m flashgenie plan "Deck" --time 30` |
| `velocity` | Analyze learning velocity | `python -m flashgenie velocity "Deck" --predict` |
| `graph` | Generate knowledge graph | `python -m flashgenie graph "Deck" --export graph.json` |
| `achievements` | View achievements | `python -m flashgenie achievements --streaks` |
| `suggest` | Get AI recommendations | `python -m flashgenie suggest "Deck" --gaps` |

## 📊 **Usage Examples**

### **Adaptive Study Session**
```bash
# Morning study session
python -m flashgenie plan "Biology" --time 45 --energy 5 --environment quiet

# Quick commute review
python -m flashgenie plan "Vocabulary" --time 15 --energy 3 --environment mobile

# Evening focused study
python -m flashgenie plan "Math" --time 60 --energy 4 --environment quiet
```

### **Learning Analytics**
```bash
# Comprehensive analysis
python -m flashgenie velocity "Spanish" --predict --trends

# Export learning data
python -m flashgenie export "Spanish" learning_data.json --format json

# Generate visual knowledge map
python -m flashgenie graph "Spanish" --export knowledge_map.html --format html
```

### **Content Management**
```bash
# Import with auto-tagging
python -m flashgenie import "History" timeline.csv --auto-tag

# Get personalized suggestions
python -m flashgenie suggest "Chemistry" --cards 10 --topics

# Identify weak areas
python -m flashgenie suggest "Physics" --gaps
```

## 🔬 **Scientific Foundation**

FlashGenie v1.5 is built on proven cognitive science research:

- **Spaced Repetition**: Based on Ebbinghaus forgetting curve and SM-2 algorithm
- **Adaptive Difficulty**: Implements desirable difficulties theory (Bjork, 1994)
- **Context-Dependent Learning**: Leverages environmental context research
- **Metacognition**: Confidence-based learning and self-assessment
- **Knowledge Graphs**: Semantic network theory and concept mapping
- **Gamification**: Motivation and engagement research

## 📚 **Documentation**

### **Complete Documentation**
- **[User Guide](docs/user-guide/)**: Comprehensive learning paths for all users
- **[Developer Guide](docs/developer-guide/)**: API reference and contribution guidelines
- **[Learning Science](docs/learning-science/)**: Research foundation and effectiveness

### **Quick References**
- **[Getting Started](docs/user-guide/getting-started.md)**: Step-by-step setup and first use
- **[Smart Features](docs/user-guide/smart-features.md)**: AI-powered capabilities
- **[Advanced Usage](docs/user-guide/advanced-usage.md)**: Power-user techniques
- **[API Reference](docs/developer-guide/api-reference.md)**: Complete technical documentation

## 🤝 **Contributing**

We welcome contributions from the community! FlashGenie is open source and thrives on collaboration.

### **How to Contribute**
1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following our coding standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request** with a clear description

### **Development Setup**
```bash
# Clone your fork
git clone https://github.com/yourusername/FlashGenie.git
cd FlashGenie

# Install development dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt

# Run tests
python -m pytest tests/

# Build documentation
mkdocs serve
```

### **Contribution Areas**
- 🐛 **Bug fixes** and performance improvements
- ✨ **New features** and AI enhancements
- 📚 **Documentation** improvements and translations
- 🧪 **Testing** and quality assurance
- 🎨 **UI/UX** improvements and accessibility
- 🔬 **Research** integration and algorithm improvements

## 📄 **License**

FlashGenie is open source software licensed under the [MIT License](LICENSE). This means you can:

- ✅ Use it for personal and commercial projects
- ✅ Modify and distribute the code
- ✅ Include it in proprietary software
- ✅ Sell applications that include FlashGenie

## 🙏 **Acknowledgments**

FlashGenie v1.5 builds upon decades of research in cognitive science, spaced repetition, and learning analytics. We thank:

- **Hermann Ebbinghaus** for foundational memory research
- **Piotr Wozniak** for the SM-2 algorithm
- **Robert Bjork** for desirable difficulties theory
- **The open source community** for tools and inspiration
- **Our contributors** who make FlashGenie better every day

## 📞 **Support & Community**

### **Get Help**
- 📖 **Documentation**: Comprehensive guides and tutorials
- 💬 **GitHub Discussions**: Community Q&A and feature requests
- 🐛 **GitHub Issues**: Bug reports and technical issues
- 📧 **Email**: Direct support for complex issues

### **Stay Connected**
- ⭐ **Star us on GitHub** to show your support
- 👀 **Watch releases** to stay updated
- 🍴 **Fork the project** to contribute
- 📢 **Share FlashGenie** with fellow learners

---

**Transform your learning with FlashGenie v1.5 - Where AI meets education!** 🧞‍♂️✨

*Made with ❤️ by the FlashGenie community*
