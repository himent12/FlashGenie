# ⚡ Advanced Usage

Master FlashGenie's power-user features and advanced workflows to maximize your learning efficiency. This guide covers sophisticated techniques for experienced users.

## 🎯 **Advanced Study Workflows**

### Multi-Deck Study Sessions

Combine multiple decks for comprehensive study sessions:

```bash
# Load multiple decks in sequence
python -m flashgenie quiz "Spanish Vocabulary" "Spanish Grammar" "Spanish Culture"

# Or use interactive mode for complex workflows
python -m flashgenie
FlashGenie > load "Spanish Vocabulary"
FlashGenie > quiz --mode spaced --limit 20
FlashGenie > load "Spanish Grammar" 
FlashGenie > quiz --mode difficult --limit 10
FlashGenie > stats
```

### Targeted Review Strategies

=== "🎯 Weakness-Focused Study"

    ```bash
    # Focus on struggling cards across all decks
    python -m flashgenie quiz --collection "Struggling Cards" --all-decks
    
    # Study cards with specific difficulty range
    python -m flashgenie quiz --difficulty-range 0.7-1.0
    
    # Review cards not seen in X days
    python -m flashgenie quiz --not-reviewed-since 7
    ```

=== "🚀 Mastery Acceleration"

    ```bash
    # Challenge yourself with hard cards when confident
    python -m flashgenie quiz --mode difficult --confidence-threshold 4
    
    # Progressive difficulty increase
    python -m flashgenie quiz --adaptive-difficulty --aggression 1.5
    
    # Mastery verification sessions
    python -m flashgenie quiz --mastery-check --accuracy-threshold 0.95
    ```

=== "⏰ Time-Optimized Sessions"

    ```bash
    # Quick 5-minute review sessions
    python -m flashgenie quiz --time-limit 300 --priority due
    
    # Intensive 30-minute deep study
    python -m flashgenie quiz --time-limit 1800 --mode mixed
    
    # Micro-sessions for busy schedules
    python -m flashgenie quiz --card-limit 5 --quick-mode
    ```

### Custom Study Algorithms

Create personalized study patterns:

```bash
# Custom spaced repetition intervals
python -m flashgenie config set spaced_repetition.easy_multiplier 2.5
python -m flashgenie config set spaced_repetition.hard_multiplier 1.2

# Adjust confidence weighting
python -m flashgenie config set difficulty.confidence_weight 0.4
python -m flashgenie config set difficulty.response_time_weight 0.3

# Fine-tune difficulty adjustment sensitivity
python -m flashgenie config set difficulty.max_change_per_review 0.15
python -m flashgenie config set difficulty.min_reviews_for_adjustment 5
```

## 🏗️ **Advanced Data Management**

### Bulk Operations

Efficiently manage large collections of flashcards:

```bash
# Bulk import with preprocessing
python -m flashgenie import *.csv --merge-duplicates --auto-tag --validate

# Batch export with filtering
python -m flashgenie export --tags "mathematics,advanced" --format json --include-stats

# Mass tag operations
python -m flashgenie tags apply "science" --to-cards-matching "biology|chemistry|physics"
python -m flashgenie tags remove "outdated" --from-all-cards
```

### Data Transformation

Transform and clean your flashcard data:

```bash
# Normalize card formatting
python -m flashgenie transform --normalize-text --fix-encoding --trim-whitespace

# Split complex cards
python -m flashgenie transform --split-long-answers --max-length 200

# Merge similar cards
python -m flashgenie transform --merge-duplicates --similarity-threshold 0.85
```

### Advanced Import Strategies

=== "📊 Spreadsheet Integration"

    ```bash
    # Import with column mapping
    python -m flashgenie import data.xlsx \
        --question-column "Question Text" \
        --answer-column "Answer Text" \
        --tags-column "Categories" \
        --difficulty-column "Initial Difficulty"
    
    # Import with conditional logic
    python -m flashgenie import data.csv \
        --filter "difficulty > 0.5" \
        --transform "tags = tags.lower().split(';')"
    ```

=== "🔄 Automated Imports"

    ```bash
    # Watch directory for new files
    python -m flashgenie watch-import ./study_materials/ \
        --auto-tag --notify-on-import
    
    # Scheduled imports
    python -m flashgenie schedule-import \
        --source "https://example.com/daily_vocab.csv" \
        --frequency daily \
        --time "08:00"
    ```

=== "🌐 Web Scraping"

    ```bash
    # Import from web sources (future feature)
    python -m flashgenie import-web \
        --url "https://quizlet.com/set/123456" \
        --format quizlet \
        --auto-tag
    ```

## 🔧 **Performance Optimization**

### Memory Management

Optimize FlashGenie for large datasets:

```bash
# Configure memory limits
python -m flashgenie config set memory.max_cards_in_memory 10000
python -m flashgenie config set memory.cache_size_mb 512

# Enable lazy loading for large decks
python -m flashgenie config set performance.lazy_loading true
python -m flashgenie config set performance.batch_size 100
```

### Database Optimization

Improve performance with database tuning:

```bash
# Rebuild indexes for faster queries
python -m flashgenie maintenance rebuild-indexes

# Optimize storage
python -m flashgenie maintenance compact-database

# Analyze performance
python -m flashgenie maintenance analyze-performance --report
```

### Caching Strategies

Configure intelligent caching:

```bash
# Smart collection caching
python -m flashgenie config set cache.collections.ttl 300  # 5 minutes
python -m flashgenie config set cache.collections.max_size 50

# Statistics caching
python -m flashgenie config set cache.stats.enabled true
python -m flashgenie config set cache.stats.refresh_interval 60
```

## 📊 **Advanced Analytics**

### Custom Metrics

Create personalized learning metrics:

```bash
# Define custom performance indicators
python -m flashgenie analytics create-metric "weekly_velocity" \
    --formula "cards_learned / days * 7" \
    --description "Cards learned per week"

# Track learning streaks
python -m flashgenie analytics create-metric "study_streak" \
    --formula "consecutive_study_days" \
    --goal 30

# Monitor difficulty progression
python -m flashgenie analytics create-metric "difficulty_trend" \
    --formula "avg(difficulty_changes[-7:])" \
    --description "Recent difficulty trend"
```

### Data Export and Analysis

Export data for external analysis:

```bash
# Export comprehensive learning data
python -m flashgenie export-analytics \
    --format csv \
    --include-sessions \
    --include-difficulty-history \
    --date-range "2024-01-01:2024-12-31"

# Generate learning reports
python -m flashgenie report generate \
    --type "monthly_progress" \
    --format pdf \
    --include-charts

# Export for research
python -m flashgenie export-research \
    --anonymize \
    --format json \
    --include-metadata
```

### Predictive Analytics

Leverage FlashGenie's predictive capabilities:

```bash
# Predict mastery timelines
python -m flashgenie predict mastery-timeline \
    --deck "Spanish Vocabulary" \
    --confidence-interval 0.95

# Forecast study requirements
python -m flashgenie predict study-time \
    --goal "90% accuracy" \
    --available-time "30min/day"

# Identify at-risk cards
python -m flashgenie predict struggling-cards \
    --threshold 0.7 \
    --lookahead-days 14
```

## 🔌 **Integration and Automation**

### Command Line Scripting

Automate FlashGenie workflows:

```bash
#!/bin/bash
# Daily study routine script

# Morning vocabulary review
python -m flashgenie quiz "Daily Vocabulary" \
    --mode spaced \
    --time-limit 600 \
    --auto-confidence

# Update statistics
python -m flashgenie stats --export daily_stats_$(date +%Y%m%d).json

# Auto-tag new cards
python -m flashgenie autotag --all-decks

# Backup data
python -m flashgenie backup create --compress --encrypt
```

### API Integration

Use FlashGenie programmatically:

```python
# Python API usage
from flashgenie import FlashGenie, Deck, Flashcard

# Initialize FlashGenie
fg = FlashGenie()

# Create deck programmatically
deck = Deck("API Created Deck")
deck.add_card(Flashcard("API Question", "API Answer"))

# Run automated quiz
session = fg.start_quiz_session(deck, mode="spaced")
results = session.run_automated(confidence_strategy="adaptive")

# Analyze results
analytics = fg.get_analytics(deck)
print(f"Session accuracy: {analytics.session_accuracy}")
```

### External Tool Integration

Connect FlashGenie with other tools:

=== "📚 Study Apps"

    ```bash
    # Sync with Anki
    python -m flashgenie sync anki \
        --export-to-anki \
        --preserve-scheduling
    
    # Import from Quizlet
    python -m flashgenie import quizlet \
        --set-id 123456789 \
        --include-images
    ```

=== "📊 Analytics Tools"

    ```bash
    # Export to Google Sheets
    python -m flashgenie export google-sheets \
        --sheet-id "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms" \
        --auto-update
    
    # Send to analytics platform
    python -m flashgenie export analytics-platform \
        --platform mixpanel \
        --api-key $MIXPANEL_KEY
    ```

=== "🔔 Notifications"

    ```bash
    # Study reminders
    python -m flashgenie notifications setup \
        --type study-reminder \
        --time "19:00" \
        --message "Time for your daily review!"
    
    # Progress notifications
    python -m flashgenie notifications setup \
        --type milestone \
        --trigger "accuracy > 0.9" \
        --message "Great job! You've mastered this deck!"
    ```

## 🛠️ **Customization and Extensions**

### Custom Algorithms

Implement your own learning algorithms:

```python
# Custom difficulty adjustment algorithm
from flashgenie.core.difficulty_analyzer import DifficultyAnalyzer

class CustomDifficultyAnalyzer(DifficultyAnalyzer):
    def calculate_adjustment(self, card, performance):
        # Your custom logic here
        adjustment = super().calculate_adjustment(card, performance)
        
        # Add custom factors
        if card.has_tag("difficult_subject"):
            adjustment *= 0.8  # Slower difficulty increase
        
        return adjustment

# Register custom algorithm
python -m flashgenie config set algorithms.difficulty_analyzer "CustomDifficultyAnalyzer"
```

### Plugin Development

Create FlashGenie plugins:

```python
# Example plugin: Study streak tracker
from flashgenie.plugins import BasePlugin

class StudyStreakPlugin(BasePlugin):
    def on_quiz_complete(self, session):
        streak = self.calculate_streak(session.user)
        if streak > self.get_best_streak():
            self.notify_new_record(streak)
    
    def calculate_streak(self, user):
        # Implementation here
        pass

# Install plugin
python -m flashgenie plugins install study-streak-tracker
```

### Configuration Management

Advanced configuration techniques:

```bash
# Environment-specific configs
python -m flashgenie config create-profile "work" \
    --copy-from default \
    --set "study.session_length=15" \
    --set "difficulty.aggression=0.8"

# Configuration versioning
python -m flashgenie config backup --name "pre_experiment"
python -m flashgenie config restore "pre_experiment"

# Shared team configurations
python -m flashgenie config export team_config.json
python -m flashgenie config import team_config.json --merge
```

## 🔍 **Debugging and Troubleshooting**

### Performance Debugging

Identify and resolve performance issues:

```bash
# Profile quiz performance
python -m flashgenie debug profile-quiz \
    --deck "Large Deck" \
    --duration 300 \
    --output profile_report.html

# Memory usage analysis
python -m flashgenie debug memory-usage \
    --track-allocations \
    --report-top 20

# Database query optimization
python -m flashgenie debug slow-queries \
    --threshold 100ms \
    --explain-plans
```

### Data Integrity Checks

Ensure your data is consistent:

```bash
# Comprehensive data validation
python -m flashgenie validate \
    --check-duplicates \
    --check-orphaned-tags \
    --check-invalid-dates \
    --fix-issues

# Backup verification
python -m flashgenie backup verify \
    --file backup_20241201.fgb \
    --deep-check

# Migration validation
python -m flashgenie migrate validate \
    --from-version 1.0.0 \
    --to-version 1.5.0 \
    --dry-run
```

### Advanced Logging

Configure detailed logging for troubleshooting:

```bash
# Enable debug logging
python -m flashgenie config set logging.level DEBUG
python -m flashgenie config set logging.file flashgenie_debug.log

# Component-specific logging
python -m flashgenie config set logging.components.difficulty_analyzer DEBUG
python -m flashgenie config set logging.components.quiz_engine INFO

# Performance logging
python -m flashgenie config set logging.performance.enabled true
python -m flashgenie config set logging.performance.threshold 100ms
```

## 🎯 **Power User Tips**

### Keyboard Shortcuts and Aliases

Speed up your workflow:

```bash
# Create command aliases
alias fgq="python -m flashgenie quiz"
alias fgs="python -m flashgenie stats"
alias fgl="python -m flashgenie list"

# Bash completion
python -m flashgenie completion bash >> ~/.bashrc
source ~/.bashrc

# Quick deck switching
export FG_DEFAULT_DECK="Daily Review"
python -m flashgenie quiz  # Uses default deck
```

### Batch Processing

Process multiple operations efficiently:

```bash
# Batch quiz sessions
python -m flashgenie batch-quiz \
    --decks "Deck1,Deck2,Deck3" \
    --mode spaced \
    --time-per-deck 10 \
    --auto-confidence

# Bulk statistics generation
python -m flashgenie batch-stats \
    --all-decks \
    --format csv \
    --output stats_$(date +%Y%m%d).csv
```

### Advanced Search and Filtering

Find exactly what you need:

```bash
# Complex card queries
python -m flashgenie search \
    --query "tags:mathematics AND difficulty:>0.7 AND accuracy:<0.6" \
    --sort-by "last_reviewed" \
    --limit 20

# Regex-based searches
python -m flashgenie search \
    --regex-question "^What is.*\?" \
    --regex-answer ".*definition.*" \
    --case-insensitive
```

---

**Ready to explore the science behind FlashGenie?** Continue to [Best Practices](best-practices.md) for evidence-based learning strategies! 🧞‍♂️✨
