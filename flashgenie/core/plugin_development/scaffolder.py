"""
Plugin scaffolding utilities for the Plugin Development Kit.

This module provides functions to create plugin scaffolds and templates.
"""

from pathlib import Path
from typing import Dict, Any, List
import json

from ..plugin_system import PluginType


class PluginScaffolder:
    """Creates plugin scaffolds and templates."""
    
    def __init__(self, workspace_dir: Path):
        """
        Initialize the scaffolder.
        
        Args:
            workspace_dir: Directory for plugin development workspace
        """
        self.workspace_dir = workspace_dir
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
    
    def create_plugin_scaffold(
        self, 
        plugin_name: str, 
        plugin_type: PluginType, 
        author: str
    ) -> Path:
        """
        Create a complete plugin scaffold.
        
        Args:
            plugin_name: Name of the plugin
            plugin_type: Type of plugin to create
            author: Plugin author name
            
        Returns:
            Path to the created plugin directory
        """
        # Create plugin directory
        plugin_dir = self.workspace_dir / plugin_name
        plugin_dir.mkdir(exist_ok=True)
        
        # Create manifest
        self._create_manifest(plugin_dir, plugin_name, plugin_type, author)
        
        # Create main plugin file
        self._create_main_plugin_file(plugin_dir, plugin_name, plugin_type)
        
        # Create test file
        self._create_test_file(plugin_dir, plugin_name, plugin_type)
        
        # Create README
        self._create_readme(plugin_dir, plugin_name, plugin_type, author)
        
        # Create additional files based on plugin type
        self._create_type_specific_files(plugin_dir, plugin_type)
        
        return plugin_dir
    
    def _create_manifest(
        self, 
        plugin_dir: Path, 
        plugin_name: str, 
        plugin_type: PluginType, 
        author: str
    ) -> None:
        """Create the plugin manifest file."""
        manifest = {
            "name": plugin_name,
            "version": "1.0.0",
            "description": f"A {plugin_type.value} plugin for FlashGenie",
            "author": author,
            "license": "MIT",
            "flashgenie_version": ">=1.8.0",
            "type": plugin_type.value,
            "entry_point": f"{self._to_class_name(plugin_name)}Plugin",
            "permissions": self._get_default_permissions(plugin_type),
            "dependencies": self._get_default_dependencies(plugin_type),
            "settings_schema": self._get_default_settings_schema(plugin_type),
            "homepage": f"https://github.com/{author.lower().replace(' ', '')}/{plugin_name}",
            "repository": f"https://github.com/{author.lower().replace(' ', '')}/{plugin_name}",
            "tags": self._get_default_tags(plugin_type)
        }
        
        with open(plugin_dir / "plugin.json", 'w') as f:
            json.dump(manifest, f, indent=2)
    
    def _create_main_plugin_file(
        self, 
        plugin_dir: Path, 
        plugin_name: str, 
        plugin_type: PluginType
    ) -> None:
        """Create the main plugin implementation file."""
        class_name = self._to_class_name(plugin_name)
        base_class = self._get_base_class(plugin_type)
        
        content = f'''"""
{plugin_name} - A {plugin_type.value} plugin for FlashGenie.

This plugin provides {plugin_type.value} functionality for FlashGenie.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from ..plugin_system import {base_class}
from flashgenie.utils.exceptions import FlashGenieError


class {class_name}Plugin({base_class}):
    """
    {plugin_name} plugin implementation.
    
    This plugin provides {plugin_type.value} functionality.
    """
    
    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
        self.name = "{plugin_name}"
        self.version = "1.0.0"
        self.description = "A {plugin_type.value} plugin for FlashGenie"
    
    def initialize(self) -> None:
        """Initialize the plugin."""
        self.logger.info(f"Initializing {{self.name}} plugin")
        
        # Request required permissions
        {self._get_permission_requests(plugin_type)}
        
        # Initialize plugin-specific components
        self._setup_plugin()
        
        self.logger.info(f"{{self.name}} plugin initialized successfully")
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        self.logger.info(f"Cleaning up {{self.name}} plugin")
        
        # Cleanup plugin-specific resources
        self._cleanup_plugin()
        
        self.logger.info(f"{{self.name}} plugin cleaned up")
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {{
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "type": "{plugin_type.value}",
            "status": "active" if self.is_initialized else "inactive",
            "settings": dict(self.settings)
        }}
    
    {self._get_type_specific_methods(plugin_type)}
    
    def _setup_plugin(self) -> None:
        """Setup plugin-specific components."""
        # TODO: Implement plugin-specific setup
        pass
    
    def _cleanup_plugin(self) -> None:
        """Cleanup plugin-specific resources."""
        # TODO: Implement plugin-specific cleanup
        pass
'''
        
        with open(plugin_dir / "__init__.py", 'w') as f:
            f.write(content)
    
    def _create_test_file(
        self, 
        plugin_dir: Path, 
        plugin_name: str, 
        plugin_type: PluginType
    ) -> None:
        """Create a test file for the plugin."""
        class_name = self._to_class_name(plugin_name)
        
        content = f'''#!/usr/bin/env python3
"""
Test suite for {plugin_name} plugin.

This module contains tests for the {plugin_name} plugin functionality.
"""

import sys
import unittest
from pathlib import Path

# Add plugin to path for testing
sys.path.insert(0, str(Path(__file__).parent))

from __init__ import {class_name}Plugin


class Test{class_name}Plugin(unittest.TestCase):
    """Test cases for {class_name}Plugin."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = {class_name}Plugin()
    
    def tearDown(self):
        """Clean up after tests."""
        if self.plugin.is_initialized:
            self.plugin.cleanup()
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        self.assertFalse(self.plugin.is_initialized)
        
        # Initialize plugin
        self.plugin.initialize()
        self.assertTrue(self.plugin.is_initialized)
        
        # Check plugin info
        info = self.plugin.get_info()
        self.assertEqual(info["name"], "{plugin_name}")
        self.assertEqual(info["type"], "{plugin_type.value}")
        self.assertEqual(info["status"], "active")
    
    def test_plugin_cleanup(self):
        """Test plugin cleanup."""
        self.plugin.initialize()
        self.assertTrue(self.plugin.is_initialized)
        
        # Cleanup plugin
        self.plugin.cleanup()
        # Note: is_initialized might still be True after cleanup
        # depending on implementation
    
    def test_plugin_info(self):
        """Test plugin information retrieval."""
        info = self.plugin.get_info()
        
        self.assertIn("name", info)
        self.assertIn("version", info)
        self.assertIn("description", info)
        self.assertIn("type", info)
        self.assertIn("status", info)
        self.assertIn("settings", info)
        
        self.assertEqual(info["type"], "{plugin_type.value}")
    
    {self._get_type_specific_tests(plugin_type)}


def main():
    """Run all tests."""
    unittest.main()


if __name__ == "__main__":
    main()
'''
        
        with open(plugin_dir / "test_plugin.py", 'w') as f:
            f.write(content)
    
    def _create_readme(
        self, 
        plugin_dir: Path, 
        plugin_name: str, 
        plugin_type: PluginType, 
        author: str
    ) -> None:
        """Create a README file for the plugin."""
        content = f'''# {plugin_name}

A {plugin_type.value} plugin for FlashGenie.

## Description

This plugin provides {plugin_type.value} functionality for FlashGenie, allowing users to {self._get_plugin_purpose(plugin_type)}.

## Features

{self._get_feature_list(plugin_type)}

## Installation

1. Download the plugin package
2. Install using FlashGenie CLI:
   ```bash
   python -m flashgenie plugins install {plugin_name}.zip
   ```
3. Enable the plugin:
   ```bash
   python -m flashgenie plugins enable {plugin_name}
   ```

## Usage

{self._get_usage_instructions(plugin_type)}

## Configuration

The plugin supports the following settings:

{self._get_settings_documentation(plugin_type)}

## Development

### Testing

Run the plugin tests:
```bash
python test_plugin.py
```

### Building

Package the plugin for distribution:
```bash
python -m flashgenie pdk package --path .
```

## License

MIT License - see LICENSE file for details.

## Author

{author}

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For issues and questions, please visit the [GitHub repository](https://github.com/{author.lower().replace(' ', '')}/{plugin_name}).
'''
        
        with open(plugin_dir / "README.md", 'w') as f:
            f.write(content)
    
    def _create_type_specific_files(self, plugin_dir: Path, plugin_type: PluginType) -> None:
        """Create additional files specific to the plugin type."""
        if plugin_type == PluginType.THEME:
            self._create_theme_files(plugin_dir)
        elif plugin_type == PluginType.IMPORTER:
            self._create_importer_files(plugin_dir)
        elif plugin_type == PluginType.EXPORTER:
            self._create_exporter_files(plugin_dir)
        elif plugin_type == PluginType.AI_ENHANCEMENT:
            self._create_ai_files(plugin_dir)
    
    def _create_theme_files(self, plugin_dir: Path) -> None:
        """Create theme-specific files."""
        # Create a sample theme configuration
        theme_config = {
            "name": "Custom Theme",
            "colors": {
                "background": "#ffffff",
                "text": "#333333",
                "accent": "#007bff",
                "success": "#28a745",
                "warning": "#ffc107",
                "error": "#dc3545"
            },
            "fonts": {
                "primary": "Arial, sans-serif",
                "monospace": "Courier New, monospace"
            },
            "spacing": {
                "small": "8px",
                "medium": "16px",
                "large": "24px"
            }
        }
        
        with open(plugin_dir / "theme.json", 'w') as f:
            json.dump(theme_config, f, indent=2)
    
    def _create_importer_files(self, plugin_dir: Path) -> None:
        """Create importer-specific files."""
        # Create a sample data file
        sample_content = '''# Sample Import Data

This file shows the expected format for import data.

Question 1,Answer 1,tag1;tag2
Question 2,Answer 2,tag2;tag3
Question 3,Answer 3,tag1;tag3
'''
        
        with open(plugin_dir / "sample_data.csv", 'w') as f:
            f.write(sample_content)
    
    def _create_exporter_files(self, plugin_dir: Path) -> None:
        """Create exporter-specific files."""
        # Create a sample template
        template_content = '''<!DOCTYPE html>
<html>
<head>
    <title>FlashGenie Export</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .card { border: 1px solid #ccc; margin: 10px; padding: 10px; }
        .question { font-weight: bold; }
        .answer { margin-top: 5px; }
    </style>
</head>
<body>
    <h1>Flashcard Export</h1>
    <!-- Template content will be generated here -->
</body>
</html>
'''
        
        with open(plugin_dir / "export_template.html", 'w') as f:
            f.write(template_content)
    
    def _create_ai_files(self, plugin_dir: Path) -> None:
        """Create AI enhancement specific files."""
        # Create a sample model configuration
        model_config = {
            "model_type": "local",
            "model_name": "custom_model",
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 150,
                "top_p": 0.9
            },
            "capabilities": [
                "generate_flashcards",
                "expand_topics",
                "create_variations"
            ]
        }
        
        with open(plugin_dir / "model_config.json", 'w') as f:
            json.dump(model_config, f, indent=2)
    
    def _to_class_name(self, plugin_name: str) -> str:
        """Convert plugin name to class name."""
        return ''.join(word.capitalize() for word in plugin_name.replace('-', '_').split('_'))
    
    def _get_base_class(self, plugin_type: PluginType) -> str:
        """Get the base class for a plugin type."""
        base_classes = {
            PluginType.IMPORTER: "ImporterPlugin",
            PluginType.EXPORTER: "ExporterPlugin",
            PluginType.THEME: "ThemePlugin",
            PluginType.QUIZ_MODE: "QuizModePlugin",
            PluginType.AI_ENHANCEMENT: "AIEnhancementPlugin",
            PluginType.ANALYTICS: "AnalyticsPlugin",
            PluginType.INTEGRATION: "IntegrationPlugin"
        }
        return base_classes.get(plugin_type, "BasePlugin")
    
    def _get_default_permissions(self, plugin_type: PluginType) -> List[str]:
        """Get default permissions for a plugin type."""
        permission_map = {
            PluginType.IMPORTER: ["file_read", "deck_write"],
            PluginType.EXPORTER: ["deck_read", "file_write"],
            PluginType.THEME: ["config_read"],
            PluginType.QUIZ_MODE: ["deck_read", "user_data"],
            PluginType.AI_ENHANCEMENT: ["deck_read", "deck_write", "network"],
            PluginType.ANALYTICS: ["deck_read", "user_data"],
            PluginType.INTEGRATION: ["network", "system_integration"]
        }
        return permission_map.get(plugin_type, [])
    
    def _get_default_dependencies(self, plugin_type: PluginType) -> List[str]:
        """Get default dependencies for a plugin type."""
        dependency_map = {
            PluginType.IMPORTER: ["pandas>=1.5.0"],
            PluginType.EXPORTER: ["jinja2>=3.0.0"],
            PluginType.THEME: [],
            PluginType.QUIZ_MODE: [],
            PluginType.AI_ENHANCEMENT: ["requests>=2.28.0"],
            PluginType.ANALYTICS: ["matplotlib>=3.5.0", "numpy>=1.21.0"],
            PluginType.INTEGRATION: ["requests>=2.28.0"]
        }
        return dependency_map.get(plugin_type, [])
    
    def _get_default_settings_schema(self, plugin_type: PluginType) -> Dict[str, Any]:
        """Get default settings schema for a plugin type."""
        base_schema = {
            "enabled": {
                "type": "boolean",
                "default": True,
                "description": "Enable this plugin"
            }
        }
        
        type_specific = {
            PluginType.THEME: {
                "theme_name": {
                    "type": "string",
                    "default": "default",
                    "description": "Theme name to apply"
                }
            },
            PluginType.AI_ENHANCEMENT: {
                "api_key": {
                    "type": "string",
                    "default": "",
                    "description": "API key for AI service"
                },
                "model": {
                    "type": "string",
                    "default": "gpt-3.5-turbo",
                    "description": "AI model to use"
                }
            }
        }
        
        base_schema.update(type_specific.get(plugin_type, {}))
        return base_schema
    
    def _get_default_tags(self, plugin_type: PluginType) -> List[str]:
        """Get default tags for a plugin type."""
        return [plugin_type.value, "flashgenie", "plugin"]

    def _get_permission_requests(self, plugin_type: PluginType) -> str:
        """Get permission request code for a plugin type."""
        permissions = self._get_default_permissions(plugin_type)
        if not permissions:
            return "# No special permissions required"

        lines = []
        for perm in permissions:
            lines.append(f"        self.require_permission(Permission.{perm.upper()})")

        return "\n".join(lines)

    def _get_type_specific_methods(self, plugin_type: PluginType) -> str:
        """Get type-specific method implementations."""
        if plugin_type == PluginType.IMPORTER:
            return '''
    def can_import(self, file_path: Path) -> bool:
        """Check if this plugin can import the given file."""
        # TODO: Implement file format detection
        return file_path.suffix.lower() in ['.csv', '.txt']

    def import_data(self, file_path: Path, deck_name: str) -> Dict[str, Any]:
        """Import data from file."""
        # TODO: Implement data import logic
        return {"success": True, "cards_imported": 0}

    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return ['.csv', '.txt']'''

        elif plugin_type == PluginType.EXPORTER:
            return '''
    def can_export(self, deck, format_type: str) -> bool:
        """Check if this plugin can export in the given format."""
        # TODO: Implement format support check
        return format_type in ['html', 'pdf']

    def export_data(self, deck, output_path: Path, format_type: str) -> Dict[str, Any]:
        """Export deck data."""
        # TODO: Implement data export logic
        return {"success": True, "cards_exported": len(deck.flashcards)}

    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats."""
        return ['html', 'pdf']'''

        elif plugin_type == PluginType.THEME:
            return '''
    def get_theme_name(self) -> str:
        """Get the theme name."""
        return self.get_setting("theme_name", "default")

    def apply_theme(self) -> Dict[str, Any]:
        """Apply the theme and return theme data."""
        # TODO: Implement theme application logic
        return {"name": self.get_theme_name(), "applied": True}

    def get_theme_info(self) -> Dict[str, Any]:
        """Get theme information."""
        return {
            "name": self.get_theme_name(),
            "description": self.description,
            "version": self.version
        }'''

        else:
            return '''
    # TODO: Implement plugin-specific methods
    pass'''

    def _get_type_specific_tests(self, plugin_type: PluginType) -> str:
        """Get type-specific test methods."""
        if plugin_type == PluginType.IMPORTER:
            return '''
    def test_can_import(self):
        """Test file import capability check."""
        self.plugin.initialize()

        # Test with supported file
        test_file = Path("test.csv")
        self.assertTrue(self.plugin.can_import(test_file))

        # Test with unsupported file
        unsupported_file = Path("test.xyz")
        self.assertFalse(self.plugin.can_import(unsupported_file))

    def test_supported_formats(self):
        """Test supported formats list."""
        formats = self.plugin.get_supported_formats()
        self.assertIsInstance(formats, list)
        self.assertGreater(len(formats), 0)'''

        elif plugin_type == PluginType.THEME:
            return '''
    def test_theme_application(self):
        """Test theme application."""
        self.plugin.initialize()

        theme_data = self.plugin.apply_theme()
        self.assertIsInstance(theme_data, dict)
        self.assertIn("name", theme_data)
        self.assertIn("applied", theme_data)

    def test_theme_info(self):
        """Test theme information retrieval."""
        info = self.plugin.get_theme_info()
        self.assertIsInstance(info, dict)
        self.assertIn("name", info)
        self.assertIn("description", info)'''

        else:
            return '''
    # TODO: Add plugin-specific tests
    pass'''

    def _get_plugin_purpose(self, plugin_type: PluginType) -> str:
        """Get a description of the plugin's purpose."""
        purposes = {
            PluginType.IMPORTER: "import flashcard data from various file formats",
            PluginType.EXPORTER: "export flashcard data to different formats",
            PluginType.THEME: "customize the visual appearance of FlashGenie",
            PluginType.QUIZ_MODE: "create custom study modes and quiz experiences",
            PluginType.AI_ENHANCEMENT: "add AI-powered features and content generation",
            PluginType.ANALYTICS: "provide advanced learning analytics and insights",
            PluginType.INTEGRATION: "integrate with external services and platforms"
        }
        return purposes.get(plugin_type, "extend FlashGenie functionality")

    def _get_feature_list(self, plugin_type: PluginType) -> str:
        """Get a feature list for the plugin type."""
        features = {
            PluginType.IMPORTER: """- Support for multiple file formats
- Intelligent data parsing and validation
- Automatic tag detection and assignment
- Error handling and reporting""",
            PluginType.EXPORTER: """- Multiple export formats
- Customizable templates
- Batch export capabilities
- Format-specific optimizations""",
            PluginType.THEME: """- Custom color schemes
- Font customization
- Layout modifications
- Accessibility features""",
            PluginType.AI_ENHANCEMENT: """- AI-powered content generation
- Intelligent suggestions
- Natural language processing
- Machine learning integration"""
        }
        return features.get(plugin_type, "- Extensible functionality\n- Easy configuration\n- Robust error handling")

    def _get_usage_instructions(self, plugin_type: PluginType) -> str:
        """Get usage instructions for the plugin type."""
        instructions = {
            PluginType.IMPORTER: """After enabling the plugin, you can import files using:
```bash
python -m flashgenie import your_file.csv --format csv
```""",
            PluginType.THEME: """After enabling the plugin, the theme will be automatically applied. You can configure theme settings in the plugin configuration.""",
            PluginType.AI_ENHANCEMENT: """Configure your AI API settings in the plugin configuration, then use AI features through the FlashGenie interface."""
        }
        return instructions.get(plugin_type, "Refer to the plugin documentation for specific usage instructions.")

    def _get_settings_documentation(self, plugin_type: PluginType) -> str:
        """Get settings documentation for the plugin type."""
        settings_docs = {
            PluginType.THEME: """- `enabled`: Enable/disable the plugin (boolean)
- `theme_name`: Name of the theme to apply (string)""",
            PluginType.AI_ENHANCEMENT: """- `enabled`: Enable/disable the plugin (boolean)
- `api_key`: API key for AI service (string)
- `model`: AI model to use (string)"""
        }
        return settings_docs.get(plugin_type, "- `enabled`: Enable/disable the plugin (boolean)")
