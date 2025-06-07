"""
Rich Terminal UI Framework for FlashGenie v1.8.4.

This module provides an enhanced terminal interface using the Rich library
for beautiful formatting, layouts, and interactive elements.
"""

from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime

from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.prompt import Prompt, Confirm

from .themes import FlashGenieTheme
from .navigation import NavigationManager
from .widgets import WidgetManager
from .debug_console import DebugConsole
from .search_system import FuzzySearchEngine, InteractiveSearchInterface
from .accessibility import AccessibilityManager
from .performance_optimizer import PerformanceOptimizer


class RichTerminalUI:
    """
    Enhanced terminal UI framework using Rich library.

    Provides beautiful formatting, interactive widgets, and responsive layouts
    for an improved user experience in the terminal.
    """

    def __init__(self, theme_name: str = "default"):
        """
        Initialize the Rich Terminal UI.

        Args:
            theme_name: Name of the theme to use
        """
        self.theme_manager = FlashGenieTheme()
        self.theme = self.theme_manager.get_theme(theme_name)

        self.console = Console(
            theme=self.theme,
            force_terminal=True,
            width=None,  # Auto-detect terminal width
            legacy_windows=False
        )

        self.navigation = NavigationManager()
        self.widgets = WidgetManager(self.console)

        # Phase 2 enhancements
        self.debug_console = DebugConsole(self.console)
        self.search_interface = InteractiveSearchInterface(self.console)

        # Phase 3 enhancements
        self.accessibility = AccessibilityManager(self.console)
        self.performance = PerformanceOptimizer(self.console)

        # State management
        self.debug_mode = False
        self.status_bar_enabled = True

    def show_welcome_screen(self) -> None:
        """Display the FlashGenie welcome screen."""
        welcome_text = Text()
        welcome_text.append("🧞‍♂️ ", style="bright_blue")
        welcome_text.append("FlashGenie v1.8.4", style="bold bright_blue")
        welcome_text.append("\n\nIntelligent Flashcard Learning Platform", style="bright_white")
        welcome_text.append("\nEnhanced Terminal Interface", style="dim")

        features = [
            "🎯 Adaptive Spaced Repetition",
            "🧠 AI-Powered Content Generation",
            "📊 Learning Analytics",
            "🔌 Plugin Ecosystem",
            "⚡ Enhanced Terminal UI"
        ]

        feature_text = Text("\n\nKey Features:\n", style="bright_yellow")
        for feature in features:
            feature_text.append(f"  {feature}\n", style="bright_white")

        welcome_panel = Panel(
            Align.center(
                Group(
                    welcome_text,
                    feature_text,
                    Text("\nPress any key to continue...", style="dim italic")
                )
            ),
            title="Welcome to FlashGenie",
            border_style="bright_blue",
            padding=(2, 4)
        )

        self.console.print(welcome_panel)

        # Wait for user input
        try:
            input()
        except KeyboardInterrupt:
            self.console.print("\n👋 Goodbye!", style="bright_yellow")
            exit(0)

    def show_error(self, error: Union[str, Exception], title: str = "Error") -> None:
        """Display an error message with proper formatting."""
        if isinstance(error, Exception):
            error_text = str(error)
        else:
            error_text = error

        error_panel = Panel(
            Text(error_text, style="bright_red"),
            title=f"❌ {title}",
            border_style="bright_red",
            padding=(1, 2)
        )

        self.console.print(error_panel)

    def show_success(self, message: str, title: str = "Success") -> None:
        """Display a success message with proper formatting."""
        success_panel = Panel(
            Text(message, style="bright_green"),
            title=f"✅ {title}",
            border_style="bright_green",
            padding=(1, 2)
        )

        self.console.print(success_panel)

    def show_info(self, message: str, title: str = "Information") -> None:
        """Display an information message with proper formatting."""
        info_panel = Panel(
            Text(message, style="bright_blue"),
            title=f"ℹ️  {title}",
            border_style="bright_blue",
            padding=(1, 2)
        )

        self.console.print(info_panel)

    def show_warning(self, message: str, title: str = "Warning") -> None:
        """Display a warning message with proper formatting."""
        warning_panel = Panel(
            Text(message, style="bright_yellow"),
            title=f"⚠️  {title}",
            border_style="bright_yellow",
            padding=(1, 2)
        )

        self.console.print(warning_panel)

    def set_theme(self, theme_name: str) -> None:
        """Change the current theme."""
        try:
            self.theme = self.theme_manager.get_theme(theme_name)
            self.console = Console(
                theme=self.theme,
                force_terminal=True,
                width=self.console.size.width,
                legacy_windows=False
            )
            self.show_success(f"Theme changed to '{theme_name}'")
        except Exception as e:
            self.show_error(f"Failed to change theme: {e}")

    def get_terminal_size(self) -> tuple:
        """Get current terminal size."""
        size = self.console.size
        return (size.width, size.height)

    def is_terminal_too_small(self, min_width: int = 80, min_height: int = 24) -> bool:
        """Check if terminal is too small for optimal display."""
        width, height = self.get_terminal_size()
        return width < min_width or height < min_height

    # Phase 2 Enhanced Features

    def toggle_debug_mode(self) -> None:
        """Toggle debug mode on/off."""
        self.debug_mode = not self.debug_mode

        if self.debug_mode:
            self.debug_console.enable()
            self.show_success("Debug mode enabled - Developer tools are now active", "Debug Mode")
        else:
            self.debug_console.disable()
            self.show_info("Debug mode disabled", "Debug Mode")

    def show_debug_panel(self) -> None:
        """Show the developer debug panel."""
        if not self.debug_mode:
            self.show_warning("Debug mode is not enabled. Use toggle_debug_mode() first.", "Debug Panel")
            return

        self.debug_console.show_debug_panel()

    def profile_function(self, func):
        """Decorator to profile function execution time."""
        return self.debug_console.profile_function(func)

    def watch_object(self, name: str, obj) -> None:
        """Add an object to the debug watch list."""
        self.debug_console.watch_object(name, obj)
        if self.debug_mode:
            self.show_info(f"Now watching object: {name}", "Debug Watch")

    def inspect_object(self, obj, name: str = "object") -> None:
        """Inspect an object and display its properties."""
        self.debug_console.inspect_object(obj, name)

    def interactive_search(self, items: List[Dict], fields: List[str], title: str = "Search") -> Optional[Dict]:
        """Launch interactive search interface."""
        return self.search_interface.interactive_search(items, fields, title)

    def create_multi_select_menu(self, title: str, options: List[str], description: str = None) -> List[int]:
        """Create an interactive multi-select menu."""
        return self.widgets.create_multi_select_menu(title, options, description)

    def create_form(self, fields: Dict[str, Dict], title: str = "Form") -> Dict[str, Any]:
        """Create an interactive form."""
        return self.widgets.create_form_builder(fields, title)

    def memory_profile(self) -> Dict[str, Any]:
        """Get detailed memory profiling information."""
        return self.debug_console.memory_profile()

    def enable_profiling(self) -> None:
        """Enable function profiling."""
        self.debug_console.enable_profiling()
        self.show_success("Function profiling enabled", "Profiling")

    def disable_profiling(self) -> None:
        """Disable function profiling."""
        self.debug_console.disable_profiling()
        self.show_info("Function profiling disabled", "Profiling")

    # Phase 3 Enhanced Features - Accessibility & Performance

    def enable_accessibility_mode(self, mode: str = "auto") -> None:
        """
        Enable accessibility features.

        Args:
            mode: Accessibility mode (auto, screen_reader, high_contrast, large_text, audio)
        """
        if mode == "auto":
            # Auto-detect and enable appropriate features
            if self.accessibility.screen_reader.is_screen_reader_active():
                self.accessibility.enable_screen_reader_mode()
            else:
                self.accessibility.enable_high_contrast_mode()
        elif mode == "screen_reader":
            self.accessibility.enable_screen_reader_mode()
        elif mode == "high_contrast":
            self.accessibility.enable_high_contrast_mode()
        elif mode == "large_text":
            self.accessibility.enable_large_text_mode()
        elif mode == "audio":
            self.accessibility.enable_audio_feedback()

        self.show_success(f"Accessibility mode '{mode}' enabled", "Accessibility")

    def disable_accessibility_mode(self, mode: str = "all") -> None:
        """
        Disable accessibility features.

        Args:
            mode: Accessibility mode to disable (all, screen_reader, high_contrast, etc.)
        """
        if mode == "all" or mode == "screen_reader":
            self.accessibility.disable_screen_reader_mode()
        if mode == "all" or mode == "high_contrast":
            self.accessibility.disable_high_contrast_mode()
        if mode == "all" or mode == "large_text":
            self.accessibility.disable_large_text_mode()
        if mode == "all" or mode == "audio":
            self.accessibility.disable_audio_feedback()

        self.show_info(f"Accessibility mode '{mode}' disabled", "Accessibility")

    def show_accessibility_menu(self) -> None:
        """Show accessibility options menu."""
        self.accessibility.show_accessibility_menu()

    def get_accessibility_status(self) -> Dict[str, Any]:
        """Get current accessibility status."""
        return self.accessibility.get_accessibility_status()

    def optimize_performance(self) -> Dict[str, Any]:
        """Optimize system performance."""
        result = self.performance.optimize_memory()
        self.show_success(
            f"Performance optimized: {result['memory_freed_mb']:.1f}MB freed, "
            f"{result['objects_collected']} objects collected",
            "Performance Optimization"
        )
        return result

    def show_performance_dashboard(self) -> None:
        """Show performance monitoring dashboard."""
        dashboard = self.performance.get_performance_dashboard()
        self.console.print(dashboard)

    def cached_operation(self, cache_key: str, ttl: int = 3600):
        """Decorator for caching operation results."""
        return self.performance.cached_operation(cache_key, ttl)

    async def run_async_task(self, task_func: Callable, task_name: str, *args, **kwargs) -> Any:
        """Run async task with progress feedback."""
        return await self.performance.run_async_with_progress(task_func, task_name, *args, **kwargs)

    def create_accessible_panel(self, content: Any, title: str, panel_type: str = "info") -> Panel:
        """Create an accessible panel with proper markup."""
        return self.accessibility.create_accessible_panel(content, title, panel_type)

    def announce(self, message: str) -> None:
        """Announce message for screen readers."""
        self.accessibility._announce(message)

    def cleanup(self) -> None:
        """Clean up all UI components."""
        try:
            self.performance.cleanup()
            self.debug_console.stop_performance_monitoring()
            self.widgets.cleanup()
        except Exception:
            # Ignore cleanup errors
            pass