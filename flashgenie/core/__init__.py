"""
Core FlashGenie modules.

This package contains the core functionality of FlashGenie including
flashcard management, study algorithms, and learning analytics.
"""

# Import from organized subdirectories for backward compatibility
from .content_system import (
    Flashcard, Deck, TagManager, SmartCollectionManager, DifficultyAnalyzer
)
from .study_system import (
    SpacedRepetitionAlgorithm, PerformanceTracker, QuizEngine, AdaptiveStudyPlanner
)
from .plugin_system import (
    BasePlugin, ImporterPlugin, ExporterPlugin, ThemePlugin,
    QuizModePlugin, AIEnhancementPlugin, AnalyticsPlugin,
    IntegrationPlugin, PluginType, Permission, PluginManager
)

# Import main interface classes (these remain in core)
from .plugin_dev_kit import PluginDevelopmentKit
from .knowledge_graph import KnowledgeGraph
from .contextual_learning_engine import ContextualLearningEngine
from .learning_velocity_tracker import LearningVelocityTracker
from .achievement_system import AchievementSystem

# Legacy imports for backward compatibility
SpacedRepetitionEngine = SpacedRepetitionAlgorithm
QuizSession = QuizEngine  # Placeholder for compatibility

__all__ = [
    # Content system
    'Flashcard',
    'Deck',
    'TagManager',
    'SmartCollectionManager',
    'DifficultyAnalyzer',

    # Study system
    'SpacedRepetitionEngine',
    'SpacedRepetitionAlgorithm',  # Legacy name
    'PerformanceTracker',
    'QuizEngine',
    'QuizSession',  # Legacy name
    'AdaptiveStudyPlanner',

    # Plugin system
    'BasePlugin',
    'ImporterPlugin',
    'ExporterPlugin',
    'ThemePlugin',
    'QuizModePlugin',
    'AIEnhancementPlugin',
    'AnalyticsPlugin',
    'IntegrationPlugin',
    'PluginType',
    'Permission',
    'PluginManager',

    # Main interfaces
    'PluginDevelopmentKit',
    'KnowledgeGraph',
    'ContextualLearningEngine',
    'LearningVelocityTracker',
    'AchievementSystem'
]
