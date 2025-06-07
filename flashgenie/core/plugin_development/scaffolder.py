"""
Plugin scaffolding utilities for the Plugin Development Kit.

This module provides functions to create plugin scaffolds and templates.
Refactored for better maintainability and smaller file size.
"""

from pathlib import Path
from typing import Dict, Any, List
import logging

from ..plugin_system import PluginType
from .template_generator import PluginTemplateGenerator
from .file_creator import PluginFileCreator


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
        
        self.template_generator = PluginTemplateGenerator()
        self.file_creator = PluginFileCreator()
        self.logger = logging.getLogger(__name__)
    
    def create_plugin_scaffold(
        self, 
        plugin_name: str, 
        plugin_type: PluginType, 
        author: str,
        include_license: bool = True,
        include_examples: bool = True
    ) -> Path:
        """
        Create a complete plugin scaffold.
        
        Args:
            plugin_name: Name of the plugin
            plugin_type: Type of plugin to create
            author: Plugin author name
            include_license: Whether to include a LICENSE file
            include_examples: Whether to include example files
            
        Returns:
            Path to the created plugin directory
            
        Raises:
            ValueError: If plugin_name is invalid
            OSError: If directory creation fails
        """
        # Validate inputs
        if not plugin_name or not plugin_name.strip():
            raise ValueError("Plugin name cannot be empty")
        
        if not author or not author.strip():
            raise ValueError("Author name cannot be empty")
        
        try:
            # Create plugin directory
            plugin_dir = self.workspace_dir / plugin_name
            plugin_dir.mkdir(exist_ok=True)
            
            self.logger.info(f"Creating plugin scaffold for '{plugin_name}' in {plugin_dir}")
            
            # Create core files
            self._create_core_files(plugin_dir, plugin_name, plugin_type, author)
            
            # Create type-specific files
            self._create_type_specific_files(plugin_dir, plugin_type, include_examples)
            
            # Create optional files
            if include_license:
                self.file_creator.create_license_file(plugin_dir, author)
            
            self.logger.info(f"Plugin scaffold created successfully at {plugin_dir}")
            return plugin_dir
            
        except Exception as e:
            self.logger.error(f"Failed to create plugin scaffold: {e}")
            raise
    
    def _create_core_files(
        self, 
        plugin_dir: Path, 
        plugin_name: str, 
        plugin_type: PluginType, 
        author: str
    ) -> None:
        """Create core plugin files."""
        # Create manifest
        self.file_creator.create_manifest(plugin_dir, plugin_name, plugin_type, author)
        
        # Create main plugin file
        main_content = self.template_generator.generate_main_plugin_template(
            plugin_name, plugin_type
        )
        with open(plugin_dir / "__init__.py", 'w', encoding='utf-8') as f:
            f.write(main_content)
        
        # Create test file
        test_content = self.template_generator.generate_test_template(
            plugin_name, plugin_type
        )
        with open(plugin_dir / "test_plugin.py", 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Create README
        readme_content = self.template_generator.generate_readme_template(
            plugin_name, plugin_type, author
        )
        with open(plugin_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _create_type_specific_files(
        self, 
        plugin_dir: Path, 
        plugin_type: PluginType,
        include_examples: bool = True
    ) -> None:
        """Create additional files specific to the plugin type."""
        if not include_examples:
            return
            
        if plugin_type == PluginType.THEME:
            self.file_creator.create_theme_files(plugin_dir)
        elif plugin_type == PluginType.IMPORTER:
            self.file_creator.create_importer_files(plugin_dir)
        elif plugin_type == PluginType.EXPORTER:
            self.file_creator.create_exporter_files(plugin_dir)
        elif plugin_type == PluginType.AI_ENHANCEMENT:
            self.file_creator.create_ai_files(plugin_dir)
    
    def validate_plugin_structure(self, plugin_dir: Path) -> Dict[str, Any]:
        """
        Validate the structure of a plugin directory.
        
        Args:
            plugin_dir: Path to plugin directory
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "missing_files": [],
            "extra_files": []
        }
        
        # Required files
        required_files = ["plugin.json", "__init__.py"]
        recommended_files = ["README.md", "test_plugin.py", "LICENSE"]
        
        # Check required files
        for file_name in required_files:
            file_path = plugin_dir / file_name
            if not file_path.exists():
                validation_result["errors"].append(f"Missing required file: {file_name}")
                validation_result["missing_files"].append(file_name)
                validation_result["valid"] = False
        
        # Check recommended files
        for file_name in recommended_files:
            file_path = plugin_dir / file_name
            if not file_path.exists():
                validation_result["warnings"].append(f"Missing recommended file: {file_name}")
                validation_result["missing_files"].append(file_name)
        
        # Validate manifest if it exists
        manifest_path = plugin_dir / "plugin.json"
        if manifest_path.exists():
            try:
                import json
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                
                # Check required manifest fields
                required_fields = ["name", "version", "type", "entry_point"]
                for field in required_fields:
                    if field not in manifest:
                        validation_result["errors"].append(f"Missing required manifest field: {field}")
                        validation_result["valid"] = False
                        
            except json.JSONDecodeError as e:
                validation_result["errors"].append(f"Invalid JSON in plugin.json: {e}")
                validation_result["valid"] = False
            except Exception as e:
                validation_result["errors"].append(f"Error reading plugin.json: {e}")
                validation_result["valid"] = False
        
        return validation_result
    
    def list_available_templates(self) -> Dict[str, List[str]]:
        """
        List available plugin templates.
        
        Returns:
            Dictionary mapping plugin types to available templates
        """
        return {
            "importer": ["CSV Importer", "JSON Importer", "XML Importer"],
            "exporter": ["HTML Exporter", "PDF Exporter", "JSON Exporter"],
            "theme": ["Dark Theme", "Light Theme", "Custom Theme"],
            "quiz_mode": ["Timed Quiz", "Adaptive Quiz", "Spaced Repetition"],
            "ai_enhancement": ["Content Generator", "Smart Suggestions", "Auto-Tagger"],
            "analytics": ["Performance Tracker", "Progress Reporter", "Insight Generator"],
            "integration": ["Cloud Sync", "API Connector", "External Service"]
        }
    
    def get_plugin_info(self, plugin_dir: Path) -> Dict[str, Any]:
        """
        Get information about an existing plugin.
        
        Args:
            plugin_dir: Path to plugin directory
            
        Returns:
            Dictionary with plugin information
        """
        info = {
            "name": plugin_dir.name,
            "path": str(plugin_dir),
            "valid": False,
            "manifest": None,
            "files": []
        }
        
        # List files
        if plugin_dir.exists() and plugin_dir.is_dir():
            info["files"] = [f.name for f in plugin_dir.iterdir() if f.is_file()]
        
        # Read manifest
        manifest_path = plugin_dir / "plugin.json"
        if manifest_path.exists():
            try:
                import json
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    info["manifest"] = json.load(f)
                info["valid"] = True
            except Exception as e:
                info["error"] = str(e)
        
        return info
