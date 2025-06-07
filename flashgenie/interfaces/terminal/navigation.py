"""
Navigation system for FlashGenie's Rich Terminal UI.

This module provides breadcrumb navigation, context management, and keyboard shortcuts.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class NavigationContext:
    """Represents a navigation context/location."""
    name: str
    display_name: str
    data: Dict[str, Any]
    timestamp: datetime
    parent: Optional[str] = None


@dataclass
class KeyboardShortcut:
    """Represents a keyboard shortcut."""
    key: str
    description: str
    action: Callable
    context: Optional[str] = None


class NavigationManager:
    """Manages navigation context, breadcrumbs, and keyboard shortcuts."""

    def __init__(self):
        """Initialize the navigation manager."""
        self.contexts: Dict[str, NavigationContext] = {}
        self.breadcrumbs: List[str] = []
        self.current_context: Optional[str] = None
        self.shortcuts: Dict[str, KeyboardShortcut] = {}
        self.history: List[str] = []

    def push_context(self, name: str, display_name: str, data: Dict[str, Any] = None, parent: str = None) -> None:
        """Push a new navigation context."""
        if data is None:
            data = {}

        context = NavigationContext(
            name=name,
            display_name=display_name,
            data=data,
            timestamp=datetime.now(),
            parent=parent or self.current_context
        )

        self.contexts[name] = context

        if name not in self.breadcrumbs:
            self.breadcrumbs.append(name)

        self.current_context = name
        self.history.append(name)

        # Limit history size
        if len(self.history) > 100:
            self.history = self.history[-100:]

    def render_breadcrumbs(self, separator: str = " > ", max_length: int = 60) -> str:
        """Render breadcrumb navigation as a string."""
        if not self.breadcrumbs:
            return ""

        display_names = []
        for context_name in self.breadcrumbs:
            context = self.contexts.get(context_name)
            if context:
                display_names.append(context.display_name)
            else:
                display_names.append(context_name)

        breadcrumb_text = separator.join(display_names)

        if len(breadcrumb_text) > max_length:
            if len(display_names) > 2:
                breadcrumb_text = f"{display_names[0]}{separator}...{separator}{display_names[-1]}"
            else:
                breadcrumb_text = breadcrumb_text[:max_length-3] + "..."

        return breadcrumb_text

    def get_current_context(self) -> Optional[NavigationContext]:
        """Get the current navigation context."""
        if self.current_context:
            return self.contexts.get(self.current_context)
        return None

    def get_context_data(self, key: str = None) -> Any:
        """Get data from the current context."""
        context = self.get_current_context()
        if not context:
            return None

        if key:
            return context.data.get(key)
        return context.data

    def register_shortcut(self, key: str, description: str, action: Callable, context: str = None) -> None:
        """Register a keyboard shortcut."""
        shortcut = KeyboardShortcut(
            key=key,
            description=description,
            action=action,
            context=context
        )

        shortcut_id = f"{context or 'global'}:{key}"
        self.shortcuts[shortcut_id] = shortcut

    def handle_shortcut(self, key: str) -> bool:
        """Handle a keyboard shortcut."""
        # Simple implementation for now
        return False