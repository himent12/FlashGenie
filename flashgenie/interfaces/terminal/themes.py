"""
Theme system for FlashGenie's Rich Terminal UI.

This module provides customizable themes and color schemes for the terminal interface.
"""

from typing import Dict
from rich.theme import Theme


class FlashGenieTheme:
    """Manages themes and color schemes for the terminal interface."""

    def __init__(self):
        """Initialize the theme manager with predefined themes."""
        self.themes = self._load_predefined_themes()
        self.current_theme = "default"

    def _load_predefined_themes(self) -> Dict[str, Theme]:
        """Load predefined color themes."""
        themes = {}

        # Default FlashGenie theme
        themes["default"] = Theme({
            "primary": "bright_blue",
            "secondary": "bright_cyan",
            "success": "bright_green",
            "warning": "bright_yellow",
            "error": "bright_red",
            "info": "bright_blue",
            "title": "bold bright_white",
            "text": "white",
            "dim_text": "dim",
        })

        # Dark theme
        themes["dark"] = Theme({
            "primary": "blue",
            "secondary": "cyan",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "info": "blue",
            "title": "bold white",
            "text": "bright_black",
            "dim_text": "dim white",
        })

        # High contrast theme
        themes["high_contrast"] = Theme({
            "primary": "bright_white",
            "secondary": "bright_white",
            "success": "bright_green",
            "warning": "bright_yellow",
            "error": "bright_red",
            "info": "bright_white",
            "title": "bold bright_white",
            "text": "bright_white",
            "dim_text": "white",
        })

        return themes

    def get_theme(self, theme_name: str) -> Theme:
        """Get a theme by name."""
        if theme_name not in self.themes:
            available = ", ".join(self.themes.keys())
            raise ValueError(f"Theme '{theme_name}' not found. Available themes: {available}")

        return self.themes[theme_name]

    def list_themes(self) -> list:
        """Get list of available theme names."""
        return list(self.themes.keys())