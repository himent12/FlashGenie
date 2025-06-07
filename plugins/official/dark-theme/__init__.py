"""
Dark Theme Plugin for FlashGenie

Provides a dark color scheme optimized for low-light environments
with customizable accent colors and contrast levels.
"""

from flashgenie.core.plugin_system import ThemePlugin
from typing import Dict, Any
import os


class DarkThemePlugin(ThemePlugin):
    """Dark theme plugin implementation."""
    
    def initialize(self) -> None:
        """Initialize the dark theme plugin."""
        self.logger.info("Dark theme plugin initialized")
        
        # Define color schemes for different contrast levels
        self.color_schemes = {
            "low": {
                "background": "#1e1e1e",
                "surface": "#252526",
                "text_primary": "#cccccc",
                "text_secondary": "#969696",
                "border": "#3e3e42",
                "success": "#4caf50",
                "warning": "#ff9800",
                "error": "#f44336",
                "info": "#2196f3"
            },
            "medium": {
                "background": "#0d1117",
                "surface": "#161b22",
                "text_primary": "#f0f6fc",
                "text_secondary": "#8b949e",
                "border": "#30363d",
                "success": "#238636",
                "warning": "#d29922",
                "error": "#da3633",
                "info": "#1f6feb"
            },
            "high": {
                "background": "#000000",
                "surface": "#0a0a0a",
                "text_primary": "#ffffff",
                "text_secondary": "#b3b3b3",
                "border": "#333333",
                "success": "#00ff00",
                "warning": "#ffff00",
                "error": "#ff0000",
                "info": "#00ffff"
            }
        }
    
    def cleanup(self) -> None:
        """Cleanup theme resources."""
        self.logger.info("Dark theme plugin cleaned up")
    
    def get_theme_name(self) -> str:
        """Get the name of this theme."""
        return "Dark Theme"
    
    def apply_theme(self) -> Dict[str, Any]:
        """Apply dark theme and return theme configuration."""
        contrast_level = self.get_setting("contrast_level", "medium")
        accent_color = self.get_setting("accent_color", "#007acc")
        
        # Get base color scheme
        colors = self.color_schemes[contrast_level].copy()
        colors["accent"] = accent_color
        
        # Create theme configuration
        theme_config = {
            "name": "dark-theme",
            "display_name": "Dark Theme",
            "colors": colors,
            "terminal": {
                "use_colors": True,
                "success_color": "green",
                "warning_color": "yellow",
                "error_color": "red",
                "info_color": "blue",
                "accent_color": "cyan"
            },
            "quiz": {
                "correct_color": colors["success"],
                "incorrect_color": colors["error"],
                "neutral_color": colors["text_secondary"],
                "highlight_color": accent_color
            },
            "progress": {
                "bar_color": accent_color,
                "background_color": colors["surface"],
                "text_color": colors["text_primary"]
            }
        }
        
        self.logger.info(f"Applied dark theme with {contrast_level} contrast")
        return theme_config
    
    def get_theme_info(self) -> Dict[str, Any]:
        """Get theme information and preview."""
        return {
            "name": self.get_theme_name(),
            "description": "Dark theme optimized for low-light environments",
            "preview": {
                "background": self.color_schemes["medium"]["background"],
                "text": self.color_schemes["medium"]["text_primary"],
                "accent": self.get_setting("accent_color", "#007acc")
            },
            "features": [
                "Reduced eye strain in dark environments",
                "Customizable accent colors",
                "Multiple contrast levels",
                "Accessibility optimized",
                "Terminal color support"
            ],
            "settings": {
                "accent_color": {
                    "name": "Accent Color",
                    "description": "Primary accent color for highlights",
                    "type": "color",
                    "default": "#007acc"
                },
                "contrast_level": {
                    "name": "Contrast Level", 
                    "description": "Adjust contrast for better readability",
                    "type": "select",
                    "options": ["low", "medium", "high"],
                    "default": "medium"
                }
            }
        }
    
    def get_css_styles(self) -> str:
        """Get CSS styles for web-based interfaces (future use)."""
        theme_config = self.apply_theme()
        colors = theme_config["colors"]
        
        css = f"""
        /* Dark Theme CSS */
        :root {{
            --bg-primary: {colors['background']};
            --bg-secondary: {colors['surface']};
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
            --border-color: {colors['border']};
            --accent-color: {colors['accent']};
            --success-color: {colors['success']};
            --warning-color: {colors['warning']};
            --error-color: {colors['error']};
            --info-color: {colors['info']};
        }}
        
        body {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        .card {{
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
        }}
        
        .button {{
            background-color: var(--accent-color);
            color: var(--text-primary);
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            cursor: pointer;
        }}
        
        .button:hover {{
            opacity: 0.8;
        }}
        
        .success {{ color: var(--success-color); }}
        .warning {{ color: var(--warning-color); }}
        .error {{ color: var(--error-color); }}
        .info {{ color: var(--info-color); }}
        """
        
        return css
    
    def get_terminal_colors(self) -> Dict[str, str]:
        """Get terminal color mappings."""
        contrast_level = self.get_setting("contrast_level", "medium")
        colors = self.color_schemes[contrast_level]
        
        return {
            "reset": "\033[0m",
            "bold": "\033[1m",
            "dim": "\033[2m",
            "underline": "\033[4m",
            "blink": "\033[5m",
            "reverse": "\033[7m",
            "strikethrough": "\033[9m",
            
            # Foreground colors
            "black": "\033[30m",
            "red": "\033[31m", 
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
            
            # Bright foreground colors
            "bright_black": "\033[90m",
            "bright_red": "\033[91m",
            "bright_green": "\033[92m", 
            "bright_yellow": "\033[93m",
            "bright_blue": "\033[94m",
            "bright_magenta": "\033[95m",
            "bright_cyan": "\033[96m",
            "bright_white": "\033[97m",
            
            # Background colors
            "bg_black": "\033[40m",
            "bg_red": "\033[41m",
            "bg_green": "\033[42m",
            "bg_yellow": "\033[43m",
            "bg_blue": "\033[44m",
            "bg_magenta": "\033[45m",
            "bg_cyan": "\033[46m",
            "bg_white": "\033[47m"
        }
