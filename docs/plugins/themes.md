# Theme Plugin Development Guide

Theme plugins allow customization of FlashGenie's visual appearance, including colors, fonts, layouts, and UI components. This guide covers creating beautiful and accessible theme plugins.

## Overview

Theme plugins modify FlashGenie's visual presentation without changing functionality. They can provide dark modes, accessibility enhancements, brand customizations, and seasonal themes.

## Base Class: ThemePlugin

All theme plugins must inherit from `ThemePlugin`:

```python
from flashgenie.core.plugin_system import ThemePlugin
from typing import Dict, Any

class MyThemePlugin(ThemePlugin):
    def __init__(self):
        super().__init__()
        self.name = "my-theme"
        self.version = "1.0.0"
        self.description = "A custom theme for FlashGenie"
    
    def get_theme_name(self) -> str:
        """Get the theme name."""
        return "My Custom Theme"
    
    def apply_theme(self) -> Dict[str, Any]:
        """Apply the theme and return theme data."""
        return self.get_theme_data()
    
    def get_theme_data(self) -> Dict[str, Any]:
        """Get complete theme configuration."""
        # Implementation here
        pass
```

## Required Methods

### `get_theme_name() -> str`

Returns the display name of the theme:

```python
def get_theme_name(self) -> str:
    """Get the theme name."""
    return "Dark Professional"
```

### `apply_theme() -> Dict[str, Any]`

Applies the theme and returns theme configuration:

```python
def apply_theme(self) -> Dict[str, Any]:
    """Apply the theme and return theme data."""
    theme_data = self.get_theme_data()
    
    # Apply any dynamic modifications
    if self.get_setting("high_contrast", False):
        theme_data = self._apply_high_contrast(theme_data)
    
    return theme_data
```

### `get_theme_data() -> Dict[str, Any]`

Returns the complete theme configuration:

```python
def get_theme_data(self) -> Dict[str, Any]:
    """Get complete theme configuration."""
    return {
        "colors": self._get_color_scheme(),
        "typography": self._get_typography(),
        "spacing": self._get_spacing(),
        "components": self._get_component_styles(),
        "animations": self._get_animations(),
        "accessibility": self._get_accessibility_settings()
    }
```

## Complete Example: Dark Theme

Here's a complete dark theme plugin:

```python
from typing import Dict, Any
from flashgenie.core.plugin_system import ThemePlugin

class DarkThemePlugin(ThemePlugin):
    def __init__(self):
        super().__init__()
        self.name = "dark-theme"
        self.version = "1.0.0"
        self.description = "Professional dark theme with blue accents"
    
    def initialize(self):
        """Initialize the theme plugin."""
        self.logger.info("Dark theme plugin initialized")
        self.require_permission(Permission.CONFIG_READ)
    
    def get_theme_name(self) -> str:
        """Get the theme name."""
        return "Dark Professional"
    
    def apply_theme(self) -> Dict[str, Any]:
        """Apply the theme and return theme data."""
        theme_data = self.get_theme_data()
        
        # Apply user customizations
        accent_color = self.get_setting("accent_color", "#2196F3")
        theme_data["colors"]["primary"] = accent_color
        
        # Apply accessibility settings
        if self.get_setting("high_contrast", False):
            theme_data = self._apply_high_contrast(theme_data)
        
        if self.get_setting("large_text", False):
            theme_data = self._apply_large_text(theme_data)
        
        return theme_data
    
    def get_theme_data(self) -> Dict[str, Any]:
        """Get complete theme configuration."""
        return {
            "name": self.get_theme_name(),
            "type": "dark",
            "colors": self._get_color_scheme(),
            "typography": self._get_typography(),
            "spacing": self._get_spacing(),
            "components": self._get_component_styles(),
            "animations": self._get_animations(),
            "accessibility": self._get_accessibility_settings()
        }
    
    def _get_color_scheme(self) -> Dict[str, str]:
        """Get the color scheme."""
        return {
            # Base colors
            "background": "#121212",
            "surface": "#1E1E1E",
            "surface_variant": "#2D2D2D",
            
            # Text colors
            "text_primary": "#FFFFFF",
            "text_secondary": "#B3B3B3",
            "text_disabled": "#666666",
            
            # Brand colors
            "primary": "#2196F3",
            "primary_variant": "#1976D2",
            "secondary": "#03DAC6",
            "secondary_variant": "#018786",
            
            # Status colors
            "success": "#4CAF50",
            "warning": "#FF9800",
            "error": "#F44336",
            "info": "#2196F3",
            
            # Interactive colors
            "hover": "#333333",
            "focus": "#404040",
            "active": "#4A4A4A",
            "selected": "#2196F3",
            
            # Border colors
            "border": "#404040",
            "border_light": "#2D2D2D",
            "border_focus": "#2196F3",
            
            # Shadow colors
            "shadow": "rgba(0, 0, 0, 0.5)",
            "shadow_light": "rgba(0, 0, 0, 0.2)"
        }
    
    def _get_typography(self) -> Dict[str, Any]:
        """Get typography settings."""
        return {
            "font_families": {
                "primary": "'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif",
                "monospace": "'Fira Code', 'Consolas', 'Monaco', monospace",
                "heading": "'Inter', 'Segoe UI', sans-serif"
            },
            "font_sizes": {
                "xs": "0.75rem",    # 12px
                "sm": "0.875rem",   # 14px
                "base": "1rem",     # 16px
                "lg": "1.125rem",   # 18px
                "xl": "1.25rem",    # 20px
                "2xl": "1.5rem",    # 24px
                "3xl": "1.875rem",  # 30px
                "4xl": "2.25rem"    # 36px
            },
            "font_weights": {
                "light": 300,
                "normal": 400,
                "medium": 500,
                "semibold": 600,
                "bold": 700
            },
            "line_heights": {
                "tight": 1.25,
                "normal": 1.5,
                "relaxed": 1.75
            }
        }
    
    def _get_spacing(self) -> Dict[str, str]:
        """Get spacing values."""
        return {
            "xs": "0.25rem",    # 4px
            "sm": "0.5rem",     # 8px
            "md": "1rem",       # 16px
            "lg": "1.5rem",     # 24px
            "xl": "2rem",       # 32px
            "2xl": "3rem",      # 48px
            "3xl": "4rem"       # 64px
        }
    
    def _get_component_styles(self) -> Dict[str, Any]:
        """Get component-specific styles."""
        return {
            "button": {
                "primary": {
                    "background": "#2196F3",
                    "color": "#FFFFFF",
                    "border": "none",
                    "border_radius": "0.375rem",
                    "padding": "0.5rem 1rem",
                    "font_weight": 500,
                    "hover": {
                        "background": "#1976D2"
                    },
                    "focus": {
                        "outline": "2px solid #2196F3",
                        "outline_offset": "2px"
                    }
                },
                "secondary": {
                    "background": "transparent",
                    "color": "#2196F3",
                    "border": "1px solid #2196F3",
                    "border_radius": "0.375rem",
                    "padding": "0.5rem 1rem",
                    "font_weight": 500,
                    "hover": {
                        "background": "#2196F3",
                        "color": "#FFFFFF"
                    }
                }
            },
            "card": {
                "background": "#1E1E1E",
                "border": "1px solid #404040",
                "border_radius": "0.5rem",
                "padding": "1.5rem",
                "shadow": "0 4px 6px rgba(0, 0, 0, 0.3)",
                "hover": {
                    "shadow": "0 8px 15px rgba(0, 0, 0, 0.4)",
                    "transform": "translateY(-2px)"
                }
            },
            "input": {
                "background": "#2D2D2D",
                "color": "#FFFFFF",
                "border": "1px solid #404040",
                "border_radius": "0.375rem",
                "padding": "0.75rem",
                "focus": {
                    "border_color": "#2196F3",
                    "outline": "none",
                    "box_shadow": "0 0 0 3px rgba(33, 150, 243, 0.1)"
                }
            },
            "navigation": {
                "background": "#1E1E1E",
                "border_bottom": "1px solid #404040",
                "item": {
                    "color": "#B3B3B3",
                    "hover": {
                        "color": "#FFFFFF",
                        "background": "#333333"
                    },
                    "active": {
                        "color": "#2196F3",
                        "background": "#2D2D2D"
                    }
                }
            },
            "flashcard": {
                "background": "#1E1E1E",
                "border": "1px solid #404040",
                "border_radius": "0.75rem",
                "padding": "2rem",
                "shadow": "0 4px 12px rgba(0, 0, 0, 0.3)",
                "flip": {
                    "animation": "flip 0.6s ease-in-out"
                }
            }
        }
    
    def _get_animations(self) -> Dict[str, Any]:
        """Get animation settings."""
        return {
            "duration": {
                "fast": "150ms",
                "normal": "300ms",
                "slow": "500ms"
            },
            "easing": {
                "ease_in": "cubic-bezier(0.4, 0, 1, 1)",
                "ease_out": "cubic-bezier(0, 0, 0.2, 1)",
                "ease_in_out": "cubic-bezier(0.4, 0, 0.2, 1)"
            },
            "keyframes": {
                "flip": {
                    "0%": {"transform": "rotateY(0deg)"},
                    "50%": {"transform": "rotateY(90deg)"},
                    "100%": {"transform": "rotateY(0deg)"}
                },
                "fade_in": {
                    "0%": {"opacity": 0},
                    "100%": {"opacity": 1}
                },
                "slide_up": {
                    "0%": {"transform": "translateY(20px)", "opacity": 0},
                    "100%": {"transform": "translateY(0)", "opacity": 1}
                }
            }
        }
    
    def _get_accessibility_settings(self) -> Dict[str, Any]:
        """Get accessibility settings."""
        return {
            "focus_visible": True,
            "reduced_motion": False,
            "high_contrast": False,
            "large_text": False,
            "keyboard_navigation": True,
            "screen_reader_support": True
        }
    
    def _apply_high_contrast(self, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply high contrast modifications."""
        # Increase contrast ratios
        theme_data["colors"]["background"] = "#000000"
        theme_data["colors"]["text_primary"] = "#FFFFFF"
        theme_data["colors"]["border"] = "#FFFFFF"
        
        # Enhance component contrast
        theme_data["components"]["card"]["border"] = "2px solid #FFFFFF"
        theme_data["components"]["input"]["border"] = "2px solid #FFFFFF"
        
        return theme_data
    
    def _apply_large_text(self, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply large text modifications."""
        # Increase font sizes
        font_sizes = theme_data["typography"]["font_sizes"]
        for size_key in font_sizes:
            current_size = float(font_sizes[size_key].replace("rem", ""))
            font_sizes[size_key] = f"{current_size * 1.25}rem"
        
        # Increase spacing
        spacing = theme_data["spacing"]
        for space_key in spacing:
            current_space = float(spacing[space_key].replace("rem", ""))
            spacing[space_key] = f"{current_space * 1.2}rem"
        
        return theme_data
    
    def get_theme_info(self) -> Dict[str, Any]:
        """Get theme information."""
        return {
            "name": self.get_theme_name(),
            "description": self.description,
            "version": self.version,
            "type": "dark",
            "features": [
                "Dark color scheme",
                "Blue accent colors",
                "High contrast support",
                "Large text support",
                "Smooth animations",
                "Accessibility features"
            ],
            "customizable_settings": [
                "accent_color",
                "high_contrast",
                "large_text",
                "reduced_motion"
            ]
        }
```

## Plugin Manifest

Your `plugin.json` should specify theme-specific settings:

```json
{
  "name": "dark-theme",
  "version": "1.0.0",
  "description": "Professional dark theme with customizable accents",
  "author": "Your Name",
  "license": "MIT",
  "type": "theme",
  "entry_point": "DarkThemePlugin",
  "permissions": ["config_read"],
  "dependencies": [],
  "settings_schema": {
    "accent_color": {
      "type": "string",
      "default": "#2196F3",
      "description": "Primary accent color",
      "format": "color"
    },
    "high_contrast": {
      "type": "boolean",
      "default": false,
      "description": "Enable high contrast mode"
    },
    "large_text": {
      "type": "boolean",
      "default": false,
      "description": "Enable large text mode"
    },
    "reduced_motion": {
      "type": "boolean",
      "default": false,
      "description": "Reduce animations and motion"
    }
  },
  "theme_info": {
    "type": "dark",
    "supports_customization": true,
    "accessibility_features": ["high_contrast", "large_text", "reduced_motion"],
    "preview_image": "preview.png"
  },
  "flashgenie_version": ">=1.8.0"
}
```

## Theme Assets

Include additional assets in your theme:

```
dark-theme/
├── plugin.json
├── __init__.py
├── assets/
│   ├── preview.png          # Theme preview image
│   ├── icons/               # Custom icons
│   │   ├── logo-dark.svg
│   │   └── favicon-dark.ico
│   ├── fonts/               # Custom fonts (optional)
│   │   └── custom-font.woff2
│   └── images/              # Background images
│       └── pattern.svg
├── styles/                  # Additional CSS/SCSS
│   ├── components.css
│   └── animations.css
└── README.md
```

## Testing Your Theme

Create comprehensive tests in `test_plugin.py`:

```python
import unittest
from your_plugin import DarkThemePlugin

class TestDarkTheme(unittest.TestCase):
    def setUp(self):
        self.plugin = DarkThemePlugin()
        self.plugin.initialize()
    
    def test_theme_name(self):
        """Test theme name retrieval."""
        self.assertEqual(self.plugin.get_theme_name(), "Dark Professional")
    
    def test_theme_data_structure(self):
        """Test theme data structure."""
        theme_data = self.plugin.get_theme_data()
        
        required_keys = ["colors", "typography", "spacing", "components"]
        for key in required_keys:
            self.assertIn(key, theme_data)
    
    def test_color_scheme(self):
        """Test color scheme completeness."""
        theme_data = self.plugin.get_theme_data()
        colors = theme_data["colors"]
        
        required_colors = ["background", "text_primary", "primary", "error"]
        for color in required_colors:
            self.assertIn(color, colors)
            self.assertTrue(colors[color].startswith("#"))
    
    def test_high_contrast_mode(self):
        """Test high contrast modifications."""
        # Enable high contrast
        self.plugin.settings["high_contrast"] = True
        
        theme_data = self.plugin.apply_theme()
        self.assertEqual(theme_data["colors"]["background"], "#000000")
    
    def test_accessibility_settings(self):
        """Test accessibility features."""
        theme_data = self.plugin.get_theme_data()
        accessibility = theme_data["accessibility"]
        
        self.assertIn("focus_visible", accessibility)
        self.assertIn("keyboard_navigation", accessibility)

if __name__ == '__main__':
    unittest.main()
```

## Best Practices

### Design Principles
- Follow accessibility guidelines (WCAG 2.1)
- Maintain sufficient color contrast ratios
- Support both light and dark preferences
- Provide consistent visual hierarchy

### Performance
- Minimize CSS bundle size
- Use efficient selectors
- Optimize custom fonts
- Implement smooth transitions

### Customization
- Allow accent color customization
- Support accessibility preferences
- Provide multiple variants
- Enable user overrides

### Compatibility
- Test across different screen sizes
- Ensure component compatibility
- Support system preferences
- Handle fallback scenarios

## Advanced Features

### Dynamic Theming
Support system theme changes:

```python
def supports_auto_switching(self) -> bool:
    """Check if theme supports automatic light/dark switching."""
    return True

def get_light_variant(self) -> Dict[str, Any]:
    """Get light variant of the theme."""
    pass
```

### Custom Components
Provide custom component styles:

```python
def get_custom_components(self) -> Dict[str, Any]:
    """Get custom component definitions."""
    return {
        "progress_ring": {
            "styles": "...",
            "template": "..."
        }
    }
```

### Theme Inheritance
Support theme inheritance:

```python
def get_base_theme(self) -> str:
    """Get base theme to inherit from."""
    return "default"
```

## Integration Examples

- **Accessibility Theme**: High contrast, large text, reduced motion
- **Brand Theme**: Corporate colors and fonts
- **Seasonal Theme**: Holiday-specific decorations
- **Gaming Theme**: Vibrant colors and animations
- **Minimalist Theme**: Clean, simple design

## Next Steps

- [Quiz Mode Plugin Guide](./quiz-modes.md)
- [Accessibility Guidelines](../developer-guides/accessibility.md)
- [Design System Guide](../developer-guides/design-system.md)
