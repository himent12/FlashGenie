# 📚 API Reference

Complete technical documentation for FlashGenie's classes, methods, and interfaces. This reference is auto-generated from docstrings and provides comprehensive coverage of the public API.

## 🎯 **API Overview**

FlashGenie's API is organized into several key modules:

- **[Core Classes](#core-classes)**: Fundamental flashcard and deck management
- **[Smart Features](#smart-features)**: Intelligent learning algorithms
- **[Data Management](#data-management)**: Storage and persistence
- **[User Interface](#user-interface)**: CLI and interaction components
- **[Utilities](#utilities)**: Helper functions and tools

## 🧠 **Core Classes**

### Flashcard

The fundamental unit of learning in FlashGenie.

```python
class Flashcard:
    """
    Represents a single flashcard with question, answer, and learning metadata.
    
    Attributes:
        question (str): The question or prompt
        answer (str): The correct answer
        tags (Set[str]): Associated tags for organization
        difficulty (float): Current difficulty level (0.0-1.0)
        created_at (datetime): Creation timestamp
        last_reviewed (Optional[datetime]): Last review timestamp
        review_count (int): Number of times reviewed
        correct_count (int): Number of correct answers
        response_times (List[float]): Recent response times
        confidence_ratings (List[int]): Recent confidence ratings (1-5)
        difficulty_history (List[float]): History of difficulty changes
    """
    
    def __init__(
        self, 
        question: str, 
        answer: str, 
        tags: Optional[Set[str]] = None,
        difficulty: float = 0.5
    ) -> None:
        """
        Initialize a new flashcard.
        
        Args:
            question: The question text
            answer: The answer text
            tags: Optional set of tags
            difficulty: Initial difficulty (default: 0.5)
        """
    
    def mark_reviewed(
        self, 
        correct: bool, 
        quality: int, 
        response_time: float,
        confidence: int
    ) -> None:
        """
        Record a review session for this card.
        
        Args:
            correct: Whether the answer was correct
            quality: Quality rating (0-5) for spaced repetition
            response_time: Time taken to answer in seconds
            confidence: Confidence rating (1-5)
        """
    
    def calculate_accuracy(self) -> float:
        """
        Calculate the accuracy rate for this card.
        
        Returns:
            Accuracy as a float between 0.0 and 1.0
        """
    
    def get_average_response_time(self) -> float:
        """
        Get the average response time for recent reviews.
        
        Returns:
            Average response time in seconds
        """
    
    def is_due_for_review(self) -> bool:
        """
        Check if this card is due for review based on spaced repetition.
        
        Returns:
            True if the card should be reviewed
        """
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to this card."""
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from this card."""
    
    def has_tag(self, tag: str) -> bool:
        """Check if this card has a specific tag."""
```

### Deck

A collection of flashcards with metadata and management capabilities.

```python
class Deck:
    """
    Represents a collection of flashcards with associated metadata.
    
    Attributes:
        name (str): Deck name
        description (str): Deck description
        flashcards (List[Flashcard]): List of flashcards
        tags (Set[str]): Deck-level tags
        created_at (datetime): Creation timestamp
        last_studied (Optional[datetime]): Last study session
        total_reviews (int): Total number of reviews across all cards
    """
    
    def __init__(
        self, 
        name: str, 
        description: str = "",
        flashcards: Optional[List[Flashcard]] = None
    ) -> None:
        """
        Initialize a new deck.
        
        Args:
            name: Deck name
            description: Optional description
            flashcards: Optional initial flashcards
        """
    
    def add_flashcard(self, flashcard: Flashcard) -> None:
        """Add a flashcard to this deck."""
    
    def remove_flashcard(self, flashcard: Flashcard) -> None:
        """Remove a flashcard from this deck."""
    
    def get_flashcard_by_id(self, card_id: str) -> Optional[Flashcard]:
        """Get a flashcard by its ID."""
    
    def get_cards_by_tag(self, tag: str) -> List[Flashcard]:
        """Get all cards with a specific tag."""
    
    def get_due_cards(self) -> List[Flashcard]:
        """Get all cards due for review."""
    
    def get_cards_by_difficulty(
        self, 
        min_difficulty: float = 0.0,
        max_difficulty: float = 1.0
    ) -> List[Flashcard]:
        """Get cards within a difficulty range."""
    
    def calculate_statistics(self) -> DeckStatistics:
        """Calculate comprehensive deck statistics."""
    
    def auto_tag_cards(self, tag_manager: 'TagManager') -> int:
        """
        Automatically tag cards based on content analysis.
        
        Returns:
            Number of cards that received new tags
        """
```

## 🧠 **Smart Features**

### DifficultyAnalyzer

Intelligent difficulty adjustment based on performance analysis.

```python
class DifficultyAnalyzer:
    """
    Analyzes flashcard performance and suggests difficulty adjustments.
    
    This class implements FlashGenie's smart difficulty adjustment algorithm,
    considering multiple factors including accuracy, response time, confidence,
    and learning trends.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the difficulty analyzer.
        
        Args:
            config: Optional configuration parameters
        """
    
    def analyze_card_performance(
        self, 
        card: Flashcard
    ) -> PerformanceAnalysis:
        """
        Analyze the performance metrics for a specific card.
        
        Args:
            card: The flashcard to analyze
            
        Returns:
            Comprehensive performance analysis
        """
    
    def suggest_difficulty_adjustment(
        self, 
        performance: PerformanceAnalysis
    ) -> DifficultyAdjustment:
        """
        Suggest a difficulty adjustment based on performance analysis.
        
        Args:
            performance: Performance analysis results
            
        Returns:
            Suggested difficulty adjustment with explanation
        """
    
    def apply_difficulty_adjustment(
        self, 
        card: Flashcard, 
        adjustment: DifficultyAdjustment
    ) -> None:
        """
        Apply a difficulty adjustment to a card.
        
        Args:
            card: The flashcard to adjust
            adjustment: The adjustment to apply
        """
    
    def get_adjustment_explanation(
        self, 
        adjustment: DifficultyAdjustment
    ) -> str:
        """
        Get a human-readable explanation for a difficulty adjustment.
        
        Args:
            adjustment: The difficulty adjustment
            
        Returns:
            Explanation string for the user
        """
```

### TagManager

Hierarchical tagging system with auto-categorization capabilities.

```python
class TagManager:
    """
    Manages hierarchical tags and auto-tagging functionality.
    
    Supports parent-child tag relationships, tag aliases, and automatic
    content-based tag suggestions.
    """
    
    def __init__(self, storage_path: Optional[str] = None) -> None:
        """
        Initialize the tag manager.
        
        Args:
            storage_path: Optional path for tag hierarchy storage
        """
    
    def create_tag(
        self, 
        name: str, 
        parent: Optional[str] = None,
        description: str = "",
        aliases: Optional[List[str]] = None
    ) -> TagHierarchy:
        """
        Create a new tag with optional hierarchy.
        
        Args:
            name: Tag name
            parent: Optional parent tag name
            description: Tag description
            aliases: Optional list of aliases
            
        Returns:
            Created tag hierarchy object
        """
    
    def get_tag_hierarchy(self, tag: str) -> Optional[TagHierarchy]:
        """Get the hierarchy information for a tag."""
    
    def get_child_tags(self, parent: str) -> List[str]:
        """Get all child tags of a parent tag."""
    
    def get_tag_path(self, tag: str) -> str:
        """Get the full hierarchical path for a tag."""
    
    def suggest_tags(self, content: str) -> List[TagSuggestion]:
        """
        Suggest tags based on content analysis.
        
        Args:
            content: Text content to analyze
            
        Returns:
            List of tag suggestions with confidence scores
        """
    
    def auto_categorize_card(self, card: Flashcard) -> List[str]:
        """
        Automatically categorize a card based on its content.
        
        Args:
            card: The flashcard to categorize
            
        Returns:
            List of suggested tags
        """
    
    def resolve_tag_alias(self, alias: str) -> Optional[str]:
        """Resolve a tag alias to its canonical name."""
    
    def get_tag_statistics(self) -> TagStatistics:
        """Get comprehensive tag usage statistics."""
```

### SmartCollectionManager

Dynamic collections that automatically group cards based on criteria.

```python
class SmartCollectionManager:
    """
    Manages smart collections that dynamically group flashcards.
    
    Smart collections automatically update based on card properties,
    performance metrics, and other criteria.
    """
    
    def __init__(self, tag_manager: TagManager) -> None:
        """
        Initialize the smart collection manager.
        
        Args:
            tag_manager: Tag manager instance for tag-based collections
        """
    
    def get_collection(self, name: str) -> Optional[SmartCollection]:
        """Get a smart collection by name."""
    
    def list_collections(self) -> List[SmartCollection]:
        """Get all available smart collections."""
    
    def create_custom_collection(
        self, 
        name: str, 
        criteria: CollectionCriteria
    ) -> SmartCollection:
        """
        Create a custom smart collection.
        
        Args:
            name: Collection name
            criteria: Collection criteria
            
        Returns:
            Created smart collection
        """
    
    def get_collection_cards(
        self, 
        collection: SmartCollection, 
        deck: Deck
    ) -> List[Flashcard]:
        """
        Get all cards that match a collection's criteria.
        
        Args:
            collection: The smart collection
            deck: The deck to filter
            
        Returns:
            List of matching flashcards
        """
    
    def get_collection_statistics(
        self, 
        collection: SmartCollection, 
        deck: Deck
    ) -> CollectionStatistics:
        """
        Get statistics for a collection.
        
        Args:
            collection: The smart collection
            deck: The deck to analyze
            
        Returns:
            Collection statistics
        """
    
    def refresh_collections(self) -> None:
        """Refresh all collection caches."""
```

## 💾 **Data Management**

### DataStorage

Abstract interface for data persistence.

```python
class DataStorage(ABC):
    """
    Abstract base class for data storage implementations.
    
    Defines the interface for persisting flashcards, decks, and metadata.
    """
    
    @abstractmethod
    def save_deck(self, deck: Deck) -> None:
        """Save a deck to storage."""
    
    @abstractmethod
    def load_deck(self, name: str) -> Optional[Deck]:
        """Load a deck from storage."""
    
    @abstractmethod
    def list_decks(self) -> List[str]:
        """List all available deck names."""
    
    @abstractmethod
    def delete_deck(self, name: str) -> bool:
        """Delete a deck from storage."""
    
    @abstractmethod
    def backup_data(self, backup_path: str) -> None:
        """Create a backup of all data."""
    
    @abstractmethod
    def restore_data(self, backup_path: str) -> None:
        """Restore data from a backup."""
```

### JSONStorage

JSON file-based storage implementation.

```python
class JSONStorage(DataStorage):
    """
    JSON file-based implementation of DataStorage.
    
    Stores decks and metadata as JSON files in the filesystem.
    """
    
    def __init__(self, data_directory: str = "data") -> None:
        """
        Initialize JSON storage.
        
        Args:
            data_directory: Directory for storing data files
        """
    
    def save_deck(self, deck: Deck) -> None:
        """Save a deck to a JSON file."""
    
    def load_deck(self, name: str) -> Optional[Deck]:
        """Load a deck from a JSON file."""
    
    def export_deck(
        self, 
        deck: Deck, 
        format: str = "json",
        include_metadata: bool = True
    ) -> str:
        """
        Export a deck to various formats.
        
        Args:
            deck: Deck to export
            format: Export format (json, csv, txt)
            include_metadata: Whether to include metadata
            
        Returns:
            Exported data as string
        """
    
    def import_deck(
        self, 
        file_path: str, 
        name: Optional[str] = None
    ) -> Deck:
        """
        Import a deck from a file.
        
        Args:
            file_path: Path to the file to import
            name: Optional deck name (auto-detected if None)
            
        Returns:
            Imported deck
        """
```

## 🎮 **Quiz Engine**

### QuizEngine

Core quiz session management and logic.

```python
class QuizEngine:
    """
    Manages quiz sessions and implements learning algorithms.
    
    Coordinates between spaced repetition, difficulty adjustment,
    and user interaction to create optimal learning experiences.
    """
    
    def __init__(
        self, 
        difficulty_analyzer: DifficultyAnalyzer,
        spaced_repetition: SpacedRepetition
    ) -> None:
        """
        Initialize the quiz engine.
        
        Args:
            difficulty_analyzer: Difficulty adjustment system
            spaced_repetition: Spaced repetition algorithm
        """
    
    def start_session(
        self, 
        deck: Deck, 
        mode: QuizMode = QuizMode.SPACED,
        config: Optional[QuizConfig] = None
    ) -> QuizSession:
        """
        Start a new quiz session.
        
        Args:
            deck: Deck to quiz from
            mode: Quiz mode (spaced, random, sequential, difficult)
            config: Optional session configuration
            
        Returns:
            Active quiz session
        """
    
    def get_next_card(self, session: QuizSession) -> Optional[Flashcard]:
        """Get the next card for the quiz session."""
    
    def submit_answer(
        self, 
        session: QuizSession, 
        card: Flashcard,
        answer: str, 
        confidence: int,
        response_time: float
    ) -> AnswerResult:
        """
        Submit an answer and get feedback.
        
        Args:
            session: Active quiz session
            card: The flashcard being answered
            answer: User's answer
            confidence: Confidence rating (1-5)
            response_time: Time taken to answer
            
        Returns:
            Answer result with feedback
        """
    
    def end_session(self, session: QuizSession) -> QuizResults:
        """
        End a quiz session and return results.
        
        Args:
            session: Session to end
            
        Returns:
            Comprehensive quiz results
        """
```

## 📊 **Data Models**

### Performance Analysis

```python
@dataclass
class PerformanceAnalysis:
    """Comprehensive performance analysis for a flashcard."""
    accuracy_rate: float
    average_response_time: float
    confidence_trend: float
    consistency_score: float
    learning_velocity: float
    difficulty_appropriateness: float
    
    def is_performing_well(self) -> bool:
        """Check if performance indicates good learning."""
    
    def needs_difficulty_adjustment(self) -> bool:
        """Check if difficulty should be adjusted."""
```

### Difficulty Adjustment

```python
@dataclass
class DifficultyAdjustment:
    """Represents a suggested difficulty adjustment."""
    current_difficulty: float
    suggested_difficulty: float
    adjustment_magnitude: float
    confidence: float
    reasoning: str
    factors: Dict[str, float]
    
    def get_change_description(self) -> str:
        """Get a human-readable description of the change."""
```

### Quiz Results

```python
@dataclass
class QuizResults:
    """Comprehensive results from a quiz session."""
    session_id: str
    deck_name: str
    start_time: datetime
    end_time: datetime
    cards_reviewed: int
    correct_answers: int
    accuracy_rate: float
    average_response_time: float
    difficulty_adjustments: List[DifficultyAdjustment]
    performance_summary: str
    
    def get_session_duration(self) -> timedelta:
        """Get the total session duration."""
    
    def get_cards_per_minute(self) -> float:
        """Calculate cards reviewed per minute."""
```

## 🔧 **Utilities**

### Configuration Management

```python
class ConfigManager:
    """Manages FlashGenie configuration settings."""
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
    
    def load_from_file(self, file_path: str) -> None:
        """Load configuration from a file."""
    
    def save_to_file(self, file_path: str) -> None:
        """Save configuration to a file."""
```

### Logging

```python
def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger
    """
```

## 🎯 **Usage Examples**

### Basic Usage

```python
from flashgenie import Flashcard, Deck, QuizEngine, DifficultyAnalyzer

# Create flashcards
card1 = Flashcard("What is Python?", "A programming language")
card2 = Flashcard("What is ML?", "Machine Learning")

# Create deck
deck = Deck("Programming Basics", flashcards=[card1, card2])

# Initialize quiz engine
analyzer = DifficultyAnalyzer()
quiz_engine = QuizEngine(analyzer)

# Start quiz session
session = quiz_engine.start_session(deck)

# Quiz loop
while card := quiz_engine.get_next_card(session):
    # Present question to user
    answer = input(f"Q: {card.question}\nA: ")
    confidence = int(input("Confidence (1-5): "))
    
    # Submit answer
    result = quiz_engine.submit_answer(
        session, card, answer, confidence, response_time=5.0
    )
    
    print(f"{'Correct!' if result.correct else 'Incorrect'}")
    if result.difficulty_adjustment:
        print(f"Difficulty adjusted: {result.difficulty_adjustment.reasoning}")

# End session
results = quiz_engine.end_session(session)
print(f"Session complete! Accuracy: {results.accuracy_rate:.1%}")
```

### Advanced Usage

```python
from flashgenie.core.tag_manager import TagManager
from flashgenie.core.smart_collections import SmartCollectionManager

# Initialize managers
tag_manager = TagManager()
collection_manager = SmartCollectionManager(tag_manager)

# Create hierarchical tags
tag_manager.create_tag("Programming", description="Programming concepts")
tag_manager.create_tag("Python", parent="Programming")
tag_manager.create_tag("Machine Learning", parent="Programming")

# Auto-tag cards
suggestions = tag_manager.suggest_tags("Python is a programming language")
print(f"Suggested tags: {[s.tag for s in suggestions]}")

# Use smart collections
struggling_cards = collection_manager.get_collection("Struggling Cards")
cards = collection_manager.get_collection_cards(struggling_cards, deck)
print(f"Found {len(cards)} struggling cards")
```

---

**Need more details?** Check out the [Plugin Development](plugin-development.md) guide for extending FlashGenie's functionality! 🧞‍♂️✨
