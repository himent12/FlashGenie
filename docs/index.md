# 🧞‍♂️ FlashGenie Documentation

Welcome to the comprehensive documentation for **FlashGenie v1.8.4** - the intelligent flashcard application with Rich Terminal UI and enhanced interactive shell that revolutionizes learning through adaptive spaced repetition, smart difficulty adjustment, and advanced organization features.

## 🚀 **What is FlashGenie?**

FlashGenie is more than just a flashcard app. It's an intelligent learning platform that adapts to your unique learning patterns, helping you master any subject more efficiently than traditional study methods.

### ✨ **Key Features**

=== "🧠 Smart Learning"

    **Adaptive Difficulty Adjustment**
    : Cards automatically adjust difficulty based on your performance, response time, and confidence levels
    
    **Enhanced Spaced Repetition**
    : Advanced SM-2 algorithm with confidence tracking for optimal review timing
    
    **Performance Analytics**
    : Comprehensive insights into your learning progress and patterns

=== "🏷️ Advanced Organization"

    **Hierarchical Tagging**
    : Organize knowledge with parent-child tag relationships (e.g., "Science > Biology > Cells")
    
    **Auto-Tagging**
    : AI-powered content analysis suggests relevant tags automatically
    
    **Smart Collections**
    : Dynamic card grouping by difficulty, performance, tags, and timing

=== "💻 Rich Terminal UI (v1.8.4)"

    **Rich Interactive Shell**
    : Beautiful Rich Terminal UI in both standalone and interactive modes

    **Enhanced Accessibility**
    : Screen reader support, high contrast, and keyboard navigation

    **Comprehensive Help System**
    : Searchable command reference with contextual assistance

    **Developer Tools**
    : Rich debug console and performance monitoring

## 🎯 **Quick Navigation**

<div class="grid cards" markdown>

-   :material-rocket-launch: **Getting Started**

    ---

    New to FlashGenie? Start here for installation, your first deck, and basic usage.

    [:octicons-arrow-right-24: User Guide](user-guide/getting-started.md)

-   :material-brain: **Smart Features**

    ---

    Learn about FlashGenie's intelligent features that adapt to your learning style.

    [:octicons-arrow-right-24: Smart Features](user-guide/smart-features.md)

-   :material-code-braces: **Developer Guide**

    ---

    Technical documentation for contributors and developers building on FlashGenie.

    [:octicons-arrow-right-24: Developer Guide](developer-guide/index.md)

-   :material-school: **Learning Science**

    ---

    Understand the research and science behind FlashGenie's learning algorithms.

    [:octicons-arrow-right-24: Learning Science](learning-science/index.md)

-   :material-puzzle: **Plugin System**

    ---

    Explore the complete plugin ecosystem with marketplace and development tools.

    [:octicons-arrow-right-24: Plugin Guide](plugins/README.md)

-   :material-palette: **Rich Terminal UI (v1.8.4)**

    ---

    Beautiful Rich Terminal UI with enhanced interactive shell and comprehensive help.

    [:octicons-arrow-right-24: Rich UI Guide](v1.8.4-rich-interactive-shell.md)

</div>

## 🎮 **Try FlashGenie Now**

### Installation

=== "Quick Install"

    ```bash
    git clone https://github.com/himent12/FlashGenie.git
    cd FlashGenie
    pip install -r requirements.txt
    python -m flashgenie
    ```

=== "With Sample Data"

    ```bash
    git clone https://github.com/himent12/FlashGenie.git
    cd FlashGenie
    pip install -r requirements.txt
    
    # Import sample flashcards
    python -m flashgenie import assets/sample_data/example_deck.csv --name "Sample Deck"
    
    # Start learning!
    python -m flashgenie quiz "Sample Deck"
    ```

### Your First Smart Study Session

=== "Rich Interactive Shell (v1.8.4)"

    ```bash
    # Start the beautiful Rich interactive shell
    python -m flashgenie

    # All commands now use Rich Terminal UI!
    FlashGenie > help                    # Rich help system
    FlashGenie > import my_flashcards.csv --name "My Study Deck"
    FlashGenie > list                    # Rich deck tables
    FlashGenie > quiz "My Study Deck"    # Start learning
    FlashGenie > stats                   # Rich analytics
    ```

=== "Standalone Commands"

    ```bash
    # 1. Import your flashcards
    python -m flashgenie import my_flashcards.csv --name "My Study Deck"

    # 2. Auto-tag for better organization
    python -m flashgenie autotag

    # 3. Start an adaptive quiz with confidence tracking
    python -m flashgenie quiz "My Study Deck"

    # 4. Explore smart collections
    python -m flashgenie collections

    # 5. View enhanced analytics
    python -m flashgenie stats
    ```

## 🌟 **What Makes FlashGenie Special**

!!! tip "Truly Adaptive Learning"

    Unlike traditional flashcard apps, FlashGenie learns from your behavior:
    
    - **Personalized difficulty curves** for each card
    - **Confidence-based scheduling** optimizes review timing  
    - **Performance pattern recognition** improves over time
    - **Real-time adjustments** with clear explanations

!!! info "Intelligent Organization"

    Advanced organization that scales with your learning:
    
    - **Hierarchical tagging** creates logical knowledge structures
    - **Auto-tagging** reduces manual organization work
    - **Smart collections** automatically group related content
    - **Dynamic filtering** finds exactly what you need

!!! success "Comprehensive Analytics"

    Deep insights into your learning process:
    
    - **Difficulty progression tracking** shows mastery development
    - **Performance trend analysis** identifies strengths and weaknesses
    - **Response time analytics** optimize study efficiency
    - **Confidence correlation** validates self-assessment accuracy

## 📊 **Learning in Action**

### Smart Difficulty Adjustment

```bash
# During quiz sessions, FlashGenie adapts in real-time:
Your answer: Paris
✓ Correct!

How confident were you? (1=Very Low, 2=Low, 3=Medium, 4=High, 5=Very High): 4

# System provides intelligent feedback:
Difficulty adjusted: Difficulty increased slightly based on high accuracy, fast response times
```

### Enhanced Analytics

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
```

## 🤝 **Community & Support**

<div class="grid cards" markdown>

-   :material-github: **GitHub Repository**

    ---

    Source code, issues, and contributions

    [:octicons-arrow-right-24: GitHub](https://github.com/himent12/FlashGenie)

-   :material-help-circle: **Get Help**

    ---

    Support, troubleshooting, and community discussions

    [:octicons-arrow-right-24: Support](community/support.md)

-   :material-account-group: **Contributing**

    ---

    Join our community of contributors and help improve FlashGenie

    [:octicons-arrow-right-24: Contributing](developer-guide/contributing.md)

-   :material-book-open: **Learning Science**

    ---

    Research and science behind FlashGenie's algorithms

    [:octicons-arrow-right-24: Research](learning-science/index.md)

</div>

## 🗺️ **What's Next?**

FlashGenie is actively developed with exciting features planned:

- **GUI Interface**: Modern desktop application with visual analytics
- **Web Version**: Browser-based interface with real-time sync  
- **Mobile Apps**: iOS and Android with offline capability
- **Advanced AI**: Machine learning for content generation and analysis
- **Collaboration**: Share decks and study with others

---

**Ready to transform your learning?** Start with our [Getting Started Guide](user-guide/getting-started.md) or dive into [Smart Features](user-guide/smart-features.md) to see what makes FlashGenie special! 🧞‍♂️✨
