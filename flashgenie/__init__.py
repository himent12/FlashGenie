"""
FlashGenie v1.8.3 - Revolutionary Rich Terminal Interface

An advanced flashcard application with adaptive spaced repetition algorithms,
smart difficulty adjustment, and world-class Rich Terminal UI.

Features:
- Revolutionary Rich Terminal Interface with professional design
- Comprehensive accessibility support (screen readers, high contrast, audio)
- Interactive widgets and advanced developer tools
- Real-time performance monitoring and optimization
- Smart difficulty auto-adjustment based on performance
- Hierarchical tagging with auto-categorization
- Smart collections for dynamic card grouping
- Enhanced spaced repetition with confidence tracking
- Comprehensive analytics and progress tracking
- Advanced plugin system with marketplace
- Contextual learning engine
- Learning velocity tracking
- Achievement system
"""

__version__ = "1.8.3"
__author__ = "FlashGenie Team"
__email__ = "huckflower@gmail.com"

# Core imports for easy access
try:
    from flashgenie.core.content_system.flashcard import Flashcard
    from flashgenie.core.content_system.deck import Deck
    from flashgenie.core.study_system.quiz_engine import QuizEngine
    from flashgenie.core.content_system.difficulty_analyzer import DifficultyAnalyzer
    from flashgenie.core.content_system.tag_manager import TagManager
    from flashgenie.core.content_system.smart_collections import SmartCollectionManager
    from flashgenie.data.storage import DataStorage

    __all__ = [
        "Flashcard",
        "Deck",
        "QuizEngine",
        "DifficultyAnalyzer",
        "TagManager",
        "SmartCollectionManager",
        "DataStorage",
    ]
except ImportError as e:
    # Graceful degradation if some modules are not available
    import warnings
    warnings.warn(f"Some FlashGenie modules could not be imported: {e}", ImportWarning)
    __all__ = []
