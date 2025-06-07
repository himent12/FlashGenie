"""
Plugin Development Kit for FlashGenie.

This module provides the main PluginDevelopmentKit class that serves as the
public interface for plugin development functionality.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Set

from .plugin_system import PluginType
from .plugin_development.scaffolder import PluginScaffolder
from .plugin_development.validator import PluginValidator
from .plugin_development.tester import PluginTester
from .plugin_development.packager import PluginPackager
from flashgenie.utils.exceptions import FlashGenieError


class PluginDevelopmentKit:
    """
    Main interface for plugin development functionality.
    
    This class provides a simplified interface to the plugin development
    system while maintaining backward compatibility.
    """
    
    def __init__(self, workspace_dir: Optional[str] = None):
        """
        Initialize the Plugin Development Kit.
        
        Args:
            workspace_dir: Optional workspace directory for plugin development
        """
        self.workspace_dir = Path(workspace_dir or "plugins/development")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.scaffolder = PluginScaffolder(self.workspace_dir)
        self.validator = PluginValidator()
        self.tester = PluginTester()
        self.packager = PluginPackager()
    
    def create_plugin_scaffold(
        self, 
        plugin_name: str, 
        plugin_type: PluginType, 
        author: str = "Plugin Developer"
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
        try:
            return self.scaffolder.create_plugin_scaffold(plugin_name, plugin_type, author)
        except Exception as e:
            raise FlashGenieError(f"Failed to create plugin scaffold: {e}")
    
    def validate_plugin(self, plugin_path: Path) -> Dict[str, Any]:
        """
        Validate a plugin directory.
        
        Args:
            plugin_path: Path to the plugin directory
            
        Returns:
            Dictionary with validation results
        """
        try:
            return self.validator.validate_plugin(plugin_path)
        except Exception as e:
            raise FlashGenieError(f"Failed to validate plugin: {e}")
    
    def test_plugin(self, plugin_path: Path, test_mode: str = "basic") -> Dict[str, Any]:
        """
        Test a plugin with the specified test mode.
        
        Args:
            plugin_path: Path to the plugin directory
            test_mode: Test mode (basic, detailed, comprehensive)
            
        Returns:
            Dictionary with test results
        """
        try:
            return self.tester.test_plugin(plugin_path, test_mode)
        except Exception as e:
            raise FlashGenieError(f"Failed to test plugin: {e}")
    
    def package_plugin(
        self, 
        plugin_path: Path, 
        output_dir: Optional[Path] = None
    ) -> Path:
        """
        Package a plugin for distribution.
        
        Args:
            plugin_path: Path to the plugin directory
            output_dir: Directory to save the package
            
        Returns:
            Path to the created package file
        """
        try:
            return self.packager.package_plugin(plugin_path, output_dir)
        except Exception as e:
            raise FlashGenieError(f"Failed to package plugin: {e}")
    
    def install_plugin_for_testing(self, plugin_path: Path) -> bool:
        """
        Install a plugin for testing purposes.
        
        Args:
            plugin_path: Path to the plugin directory
            
        Returns:
            True if installation successful
        """
        try:
            # For testing, we can create a symlink or copy to the plugins directory
            # This is a simplified implementation
            test_plugins_dir = Path("plugins/testing")
            test_plugins_dir.mkdir(parents=True, exist_ok=True)
            
            plugin_name = plugin_path.name
            test_plugin_path = test_plugins_dir / plugin_name
            
            # Remove existing test installation
            if test_plugin_path.exists():
                import shutil
                shutil.rmtree(test_plugin_path)
            
            # Copy plugin to test directory
            import shutil
            shutil.copytree(plugin_path, test_plugin_path)
            
            return True
            
        except Exception as e:
            raise FlashGenieError(f"Failed to install plugin for testing: {e}")
    
    def get_plugin_template(self, plugin_type: PluginType) -> Dict[str, Any]:
        """
        Get a template for creating a specific type of plugin.
        
        Args:
            plugin_type: Type of plugin
            
        Returns:
            Dictionary with template information
        """
        templates = {
            PluginType.IMPORTER: {
                "description": "Import flashcard data from various file formats",
                "required_methods": ["can_import", "import_data", "get_supported_formats"],
                "permissions": ["file_read", "deck_write"],
                "dependencies": ["pandas>=1.5.0"],
                "example_usage": "Import CSV files with custom column mapping"
            },
            PluginType.EXPORTER: {
                "description": "Export flashcard data to different formats",
                "required_methods": ["can_export", "export_data", "get_supported_formats"],
                "permissions": ["deck_read", "file_write"],
                "dependencies": ["jinja2>=3.0.0"],
                "example_usage": "Export decks to PDF with custom templates"
            },
            PluginType.THEME: {
                "description": "Customize the visual appearance of FlashGenie",
                "required_methods": ["get_theme_name", "apply_theme", "get_theme_info"],
                "permissions": ["config_read"],
                "dependencies": [],
                "example_usage": "Apply dark theme with custom colors"
            },
            PluginType.QUIZ_MODE: {
                "description": "Create custom study modes and quiz experiences",
                "required_methods": ["get_mode_name", "create_session", "get_settings_schema"],
                "permissions": ["deck_read", "user_data"],
                "dependencies": [],
                "example_usage": "Timed quiz mode with leaderboards"
            },
            PluginType.AI_ENHANCEMENT: {
                "description": "Add AI-powered features and content generation",
                "required_methods": ["get_ai_capabilities", "process_content", "get_model_info"],
                "permissions": ["deck_read", "deck_write", "network"],
                "dependencies": ["requests>=2.28.0"],
                "example_usage": "Generate flashcards from text using AI"
            },
            PluginType.ANALYTICS: {
                "description": "Provide advanced learning analytics and insights",
                "required_methods": ["generate_insights", "get_metrics", "export_data"],
                "permissions": ["deck_read", "user_data"],
                "dependencies": ["matplotlib>=3.5.0", "numpy>=1.21.0"],
                "example_usage": "Learning progress visualization and predictions"
            },
            PluginType.INTEGRATION: {
                "description": "Integrate with external services and platforms",
                "required_methods": ["get_service_name", "authenticate", "sync_data"],
                "permissions": ["network", "system_integration"],
                "dependencies": ["requests>=2.28.0"],
                "example_usage": "Sync with Google Drive or Notion"
            }
        }
        
        return templates.get(plugin_type, {
            "description": "Custom FlashGenie plugin",
            "required_methods": [],
            "permissions": [],
            "dependencies": [],
            "example_usage": "Extend FlashGenie functionality"
        })
    
    def get_development_guidelines(self) -> Dict[str, Any]:
        """
        Get plugin development guidelines and best practices.
        
        Returns:
            Dictionary with development guidelines
        """
        return {
            "file_structure": {
                "required": ["plugin.json", "__init__.py"],
                "recommended": ["README.md", "test_plugin.py", "LICENSE"],
                "optional": ["CHANGELOG.md", "docs/", "examples/"]
            },
            "coding_standards": {
                "style": "Follow PEP 8 style guidelines",
                "documentation": "Add docstrings to all public methods",
                "type_hints": "Use type hints for better code clarity",
                "error_handling": "Handle errors gracefully with proper exceptions"
            },
            "security": {
                "permissions": "Request only necessary permissions",
                "validation": "Validate all user inputs",
                "secrets": "Never hardcode API keys or passwords",
                "safe_operations": "Avoid dangerous operations like eval() or exec()"
            },
            "testing": {
                "unit_tests": "Write unit tests for all functionality",
                "integration_tests": "Test integration with FlashGenie",
                "performance_tests": "Ensure reasonable performance",
                "security_tests": "Test for security vulnerabilities"
            },
            "distribution": {
                "versioning": "Use semantic versioning (e.g., 1.0.0)",
                "documentation": "Provide clear installation and usage instructions",
                "licensing": "Include appropriate license file",
                "packaging": "Use the PDK packaging tools"
            }
        }
    
    def get_plugin_examples(self) -> Dict[str, str]:
        """
        Get examples of different plugin types.
        
        Returns:
            Dictionary mapping plugin types to example descriptions
        """
        return {
            "importer": "CSV Importer - Import flashcards from CSV files with custom column mapping",
            "exporter": "PDF Exporter - Export decks to beautifully formatted PDF files",
            "theme": "Dark Theme - Professional dark mode theme with accessibility features",
            "quiz_mode": "Speed Quiz - Timed quiz mode with performance tracking",
            "ai_enhancement": "Content Generator - AI-powered flashcard generation from text",
            "analytics": "Learning Insights - Advanced analytics with progress predictions",
            "integration": "Google Drive Sync - Synchronize decks with Google Drive"
        }
    
    def get_workspace_info(self) -> Dict[str, Any]:
        """
        Get information about the development workspace.
        
        Returns:
            Dictionary with workspace information
        """
        # Count plugins in workspace
        plugin_dirs = [d for d in self.workspace_dir.iterdir() 
                      if d.is_dir() and (d / "plugin.json").exists()]
        
        # Categorize by status
        valid_plugins = []
        invalid_plugins = []
        
        for plugin_dir in plugin_dirs:
            try:
                validation = self.validate_plugin(plugin_dir)
                if validation["valid"]:
                    valid_plugins.append(plugin_dir.name)
                else:
                    invalid_plugins.append(plugin_dir.name)
            except Exception:
                invalid_plugins.append(plugin_dir.name)
        
        return {
            "workspace_path": str(self.workspace_dir),
            "total_plugins": len(plugin_dirs),
            "valid_plugins": valid_plugins,
            "invalid_plugins": invalid_plugins,
            "plugin_count_by_status": {
                "valid": len(valid_plugins),
                "invalid": len(invalid_plugins)
            }
        }
    
    def cleanup_workspace(self) -> Dict[str, Any]:
        """
        Clean up the development workspace.
        
        Returns:
            Dictionary with cleanup results
        """
        cleanup_results = {
            "files_removed": 0,
            "directories_removed": 0,
            "space_freed": 0,
            "errors": []
        }
        
        try:
            import shutil
            
            # Remove temporary files
            temp_patterns = ["*.tmp", "*.temp", "*.log", "__pycache__"]
            
            for pattern in temp_patterns:
                for temp_file in self.workspace_dir.rglob(pattern):
                    try:
                        if temp_file.is_file():
                            size = temp_file.stat().st_size
                            temp_file.unlink()
                            cleanup_results["files_removed"] += 1
                            cleanup_results["space_freed"] += size
                        elif temp_file.is_dir():
                            shutil.rmtree(temp_file)
                            cleanup_results["directories_removed"] += 1
                    except Exception as e:
                        cleanup_results["errors"].append(f"Failed to remove {temp_file}: {e}")
            
        except Exception as e:
            cleanup_results["errors"].append(f"Cleanup failed: {e}")
        
        return cleanup_results
