"""
Plugin file creation utilities.

This module provides functions to create specific plugin files and configurations.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from ..plugin_system import PluginType


class PluginFileCreator:
    """Creates specific plugin files and configurations."""
    
    def __init__(self):
        """Initialize the file creator."""
        pass
    
    def create_manifest(
        self, 
        plugin_dir: Path, 
        plugin_name: str, 
        plugin_type: PluginType, 
        author: str
    ) -> None:
        """
        Create the plugin manifest file.
        
        Args:
            plugin_dir: Plugin directory path
            plugin_name: Name of the plugin
            plugin_type: Type of plugin to create
            author: Plugin author name
        """
        manifest = {
            "name": plugin_name,
            "version": "1.0.0",
            "description": f"A {plugin_type.value} plugin for FlashGenie",
            "author": author,
            "license": "MIT",
            "flashgenie_version": ">=1.8.2",
            "type": plugin_type.value,
            "entry_point": f"{self._to_class_name(plugin_name)}Plugin",
            "permissions": self._get_default_permissions(plugin_type),
            "dependencies": self._get_default_dependencies(plugin_type),
            "settings_schema": self._get_default_settings_schema(plugin_type),
            "homepage": f"https://github.com/{author.lower().replace(' ', '')}/{plugin_name}",
            "repository": f"https://github.com/{author.lower().replace(' ', '')}/{plugin_name}",
            "tags": self._get_default_tags(plugin_type)
        }
        
        with open(plugin_dir / "plugin.json", 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    def create_theme_files(self, plugin_dir: Path) -> None:
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
        
        with open(plugin_dir / "theme.json", 'w', encoding='utf-8') as f:
            json.dump(theme_config, f, indent=2, ensure_ascii=False)
    
    def create_importer_files(self, plugin_dir: Path) -> None:
        """Create importer-specific files."""
        # Create a sample data file
        sample_content = '''# Sample Import Data

This file shows the expected format for import data.

Question 1,Answer 1,tag1;tag2
Question 2,Answer 2,tag2;tag3
Question 3,Answer 3,tag1;tag3
'''
        
        with open(plugin_dir / "sample_data.csv", 'w', encoding='utf-8') as f:
            f.write(sample_content)
    
    def create_exporter_files(self, plugin_dir: Path) -> None:
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
        
        with open(plugin_dir / "export_template.html", 'w', encoding='utf-8') as f:
            f.write(template_content)
    
    def create_ai_files(self, plugin_dir: Path) -> None:
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
        
        with open(plugin_dir / "model_config.json", 'w', encoding='utf-8') as f:
            json.dump(model_config, f, indent=2, ensure_ascii=False)
    
    def create_license_file(self, plugin_dir: Path, author: str) -> None:
        """Create MIT license file."""
        license_content = f'''MIT License

Copyright (c) 2024 {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
        
        with open(plugin_dir / "LICENSE", 'w', encoding='utf-8') as f:
            f.write(license_content)
    
    def _to_class_name(self, plugin_name: str) -> str:
        """Convert plugin name to class name."""
        return ''.join(word.capitalize() for word in plugin_name.replace('-', '_').split('_'))
    
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
        tag_map = {
            PluginType.IMPORTER: ["import", "data", "file-processing"],
            PluginType.EXPORTER: ["export", "data", "file-generation"],
            PluginType.THEME: ["theme", "ui", "customization"],
            PluginType.QUIZ_MODE: ["quiz", "interaction", "learning"],
            PluginType.AI_ENHANCEMENT: ["ai", "enhancement", "automation"],
            PluginType.ANALYTICS: ["analytics", "reporting", "insights"],
            PluginType.INTEGRATION: ["integration", "api", "external-service"]
        }
        return tag_map.get(plugin_type, ["utility"])
