# 🧞‍♂️ FlashGenie v1.8.5 Documentation

Welcome to the comprehensive documentation for **FlashGenie v1.8.5** - the ultimate flashcard learning system with beautiful Rich Terminal UI, comprehensive analytics, and intelligent AI-powered content generation that revolutionizes learning through adaptive spaced repetition, smart difficulty adjustment, and advanced AI features.

## 🚀 **What is FlashGenie?**

FlashGenie v1.8.5 is the most advanced flashcard learning system available. It's an intelligent learning platform that combines beautiful Rich Terminal UI, comprehensive analytics, and AI-powered content generation to adapt to your unique learning patterns, helping you master any subject more efficiently than ever before.

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

=== "🎮 Rich Quiz Interface (v1.8.5 Phase 1)"

    **Beautiful Quiz Sessions**
    : Interactive quiz experience with Rich Terminal UI formatting

    **Multiple Quiz Modes**
    : Spaced repetition, random, sequential, and difficult-first modes

    **Real-time Progress Tracking**
    : Visual progress bars and completion indicators

    **Confidence Assessment**
    : User confidence rating system with adaptive difficulty

=== "📊 Rich Statistics Dashboard (v1.8.5 Phase 2)"

    **Comprehensive Analytics**
    : Detailed learning insights with Rich data visualization

    **Global Statistics**
    : Cross-deck analytics and library overview

    **Learning Trends**
    : Progress tracking over time with predictions

    **Performance Analysis**
    : Response times, accuracy, and improvement areas

=== "🤖 AI Content Generation (v1.8.5 Phase 3)"

    **AI-Powered Generation**
    : Intelligent flashcard creation from text

    **Smart Difficulty Prediction**
    : AI assessment of card complexity

    **Content Suggestions**
    : Related topic generation based on existing cards

    **Automatic Enhancement**
    : AI recommendations for improving existing flashcards

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

-   :material-gamepad-variant: **Rich Quiz Interface (v1.8.5)**

    ---

    Beautiful, interactive quiz sessions with Rich Terminal UI and multiple modes.

    [:octicons-arrow-right-24: Rich Quiz Guide](v1.8.5-rich-quiz-interface.md)

-   :material-chart-line: **Rich Statistics Dashboard (v1.8.5)**

    ---

    Comprehensive learning analytics with Rich data visualization and insights.

    [:octicons-arrow-right-24: Statistics Guide](v1.8.5-statistics-dashboard.md)

-   :material-robot: **AI Content Generation (v1.8.5)**

    ---

    Intelligent flashcard creation and enhancement with AI-powered features.

    [:octicons-arrow-right-24: AI Features Guide](v1.8.5-ai-content-generation.md)

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

=== "Rich Interactive Shell (v1.8.5)"

    ```bash
    # Start the beautiful Rich interactive shell with AI features
    python -m flashgenie

    # All commands now use Rich Terminal UI!
    FlashGenie > help                    # Rich help system
    FlashGenie > import my_flashcards.csv --name "My Study Deck"
    FlashGenie > list                    # Rich deck tables

    # v1.8.5 New Features:
    FlashGenie > quiz                    # Rich quiz interface
    FlashGenie > stats --detailed        # Rich statistics dashboard
    FlashGenie > ai                      # AI features overview
    FlashGenie > generate                # AI flashcard generation
    FlashGenie > suggest                 # AI content suggestions
    FlashGenie > enhance                 # AI card enhancement
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

FlashGenie v1.8.5 delivers revolutionary AI-powered learning! Future development includes:

- **Real AI Model Integration**: GPT, Claude, or other AI model integration
- **GUI Interface**: Modern desktop application with visual analytics
- **Web Version**: Browser-based interface with real-time sync
- **Mobile Apps**: iOS and Android with offline capability
- **Advanced AI Features**: Personalized learning paths and recommendations
- **Collaboration**: Share decks and study with others

---

**Ready to transform your learning?** Start with our [Getting Started Guide](user-guide/getting-started.md) or dive into [Smart Features](user-guide/smart-features.md) to see what makes FlashGenie special! 🧞‍♂️✨
