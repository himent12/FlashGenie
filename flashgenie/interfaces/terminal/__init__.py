"""
Enhanced Terminal Interface for FlashGenie v1.8.4.

This module provides a rich, interactive terminal interface using the Rich library
for beautiful formatting, responsive layouts, and enhanced user experience.

Key Features:
- Rich text formatting and themes
- Interactive widgets and menus
- Breadcrumb navigation and context management
- Keyboard shortcuts and accessibility
- Responsive layouts and progress indicators
"""

from .rich_ui import RichTerminalUI
from .themes import FlashGenieTheme
from .navigation import NavigationManager, NavigationContext, KeyboardShortcut
from .widgets import WidgetManager
from .debug_console import DebugConsole
from .search_system import FuzzySearchEngine, InteractiveSearchInterface
from .accessibility import AccessibilityManager
from .performance_optimizer import PerformanceOptimizer
from .help_system import HelpSystem
from .rich_quiz_interface import RichQuizInterface
from .rich_statistics_dashboard import RichStatisticsDashboard

__all__ = [
    "RichTerminalUI",
    "FlashGenieTheme",
    "NavigationManager",
    "NavigationContext",
    "KeyboardShortcut",
    "WidgetManager",
    "DebugConsole",
    "FuzzySearchEngine",
    "InteractiveSearchInterface",
    "AccessibilityManager",
    "PerformanceOptimizer",
    "HelpSystem",
    "RichQuizInterface",
    "RichStatisticsDashboard"
]

# Version info
__version__ = "1.8.4"
__author__ = "FlashGenie Development Team"
__description__ = "Enhanced Terminal Interface for FlashGenie"