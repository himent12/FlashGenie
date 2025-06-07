"""
Plugin packaging utilities for the Plugin Development Kit.

This module provides functions to package plugins for distribution.
"""

import zipfile
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

from flashgenie.utils.exceptions import FlashGenieError


class PluginPackager:
    """Packages plugins for distribution."""
    
    def __init__(self):
        """Initialize the packager."""
        self.default_exclude_patterns = {
            # Version control
            ".git", ".gitignore", ".gitattributes",
            ".svn", ".hg", ".bzr",
            
            # IDE files
            ".vscode", ".idea", "*.swp", "*.swo", "*~",
            ".DS_Store", "Thumbs.db",
            
            # Python cache
            "__pycache__", "*.pyc", "*.pyo", "*.pyd",
            ".pytest_cache", ".coverage", ".tox",
            
            # Build artifacts
            "build", "dist", "*.egg-info",
            
            # Temporary files
            "*.tmp", "*.temp", "*.log",
            
            # Development files
            ".env", ".env.local", "*.dev",
            "test_data", "examples"
        }
    
    def package_plugin(
        self, 
        plugin_path: Path, 
        output_dir: Optional[Path] = None,
        exclude_patterns: Optional[Set[str]] = None
    ) -> Path:
        """
        Package a plugin for distribution.
        
        Args:
            plugin_path: Path to the plugin directory
            output_dir: Directory to save the package (default: plugin_path parent)
            exclude_patterns: Additional patterns to exclude from packaging
            
        Returns:
            Path to the created package file
        """
        if not plugin_path.exists() or not plugin_path.is_dir():
            raise FlashGenieError(f"Plugin directory does not exist: {plugin_path}")
        
        # Load plugin manifest
        manifest_path = plugin_path / "plugin.json"
        if not manifest_path.exists():
            raise FlashGenieError("Plugin manifest (plugin.json) not found")
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            raise FlashGenieError(f"Invalid plugin manifest: {e}")
        
        # Get plugin info
        plugin_name = manifest.get("name", plugin_path.name)
        plugin_version = manifest.get("version", "1.0.0")
        
        # Determine output directory and filename
        if output_dir is None:
            output_dir = plugin_path.parent
        
        output_dir.mkdir(parents=True, exist_ok=True)
        package_filename = f"{plugin_name}-{plugin_version}.zip"
        package_path = output_dir / package_filename
        
        # Combine exclude patterns
        exclude_patterns = exclude_patterns or set()
        all_exclude_patterns = self.default_exclude_patterns | exclude_patterns
        
        # Create the package
        self._create_package(plugin_path, package_path, all_exclude_patterns)
        
        # Validate the package
        self._validate_package(package_path)
        
        return package_path
    
    def _create_package(
        self, 
        plugin_path: Path, 
        package_path: Path, 
        exclude_patterns: Set[str]
    ) -> None:
        """Create the plugin package ZIP file."""
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from plugin directory
            for file_path in plugin_path.rglob("*"):
                if file_path.is_file():
                    # Check if file should be excluded
                    relative_path = file_path.relative_to(plugin_path)
                    
                    if self._should_exclude_file(relative_path, exclude_patterns):
                        continue
                    
                    # Add file to ZIP
                    arcname = str(relative_path)
                    zipf.write(file_path, arcname)
    
    def _should_exclude_file(self, file_path: Path, exclude_patterns: Set[str]) -> bool:
        """Check if a file should be excluded from packaging."""
        file_str = str(file_path)
        file_name = file_path.name
        
        for pattern in exclude_patterns:
            # Exact match
            if file_name == pattern:
                return True
            
            # Directory match
            if pattern in file_path.parts:
                return True
            
            # Wildcard match (simple)
            if pattern.startswith("*."):
                extension = pattern[1:]  # Remove *
                if file_name.endswith(extension):
                    return True
            
            # Path contains pattern
            if pattern in file_str:
                return True
        
        return False
    
    def _validate_package(self, package_path: Path) -> None:
        """Validate the created package."""
        try:
            with zipfile.ZipFile(package_path, 'r') as zipf:
                # Check if required files are present
                file_list = zipf.namelist()
                
                required_files = ["plugin.json", "__init__.py"]
                for required_file in required_files:
                    if required_file not in file_list:
                        raise FlashGenieError(f"Required file missing from package: {required_file}")
                
                # Test ZIP integrity
                zipf.testzip()
                
        except zipfile.BadZipFile:
            raise FlashGenieError("Created package is not a valid ZIP file")
        except Exception as e:
            raise FlashGenieError(f"Package validation failed: {e}")
    
    def extract_package(self, package_path: Path, extract_dir: Path) -> Path:
        """
        Extract a plugin package.
        
        Args:
            package_path: Path to the plugin package
            extract_dir: Directory to extract to
            
        Returns:
            Path to the extracted plugin directory
        """
        if not package_path.exists():
            raise FlashGenieError(f"Package file does not exist: {package_path}")
        
        # Create extraction directory
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(package_path, 'r') as zipf:
                # Extract all files
                zipf.extractall(extract_dir)
                
                # Find the plugin directory
                # (it should be the root of the ZIP or a single subdirectory)
                extracted_items = list(extract_dir.iterdir())
                
                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    plugin_dir = extracted_items[0]
                else:
                    plugin_dir = extract_dir
                
                # Validate extracted plugin
                if not (plugin_dir / "plugin.json").exists():
                    raise FlashGenieError("Extracted package does not contain plugin.json")
                
                return plugin_dir
                
        except zipfile.BadZipFile:
            raise FlashGenieError("Package is not a valid ZIP file")
        except Exception as e:
            raise FlashGenieError(f"Package extraction failed: {e}")
    
    def get_package_info(self, package_path: Path) -> Dict[str, Any]:
        """
        Get information about a plugin package.
        
        Args:
            package_path: Path to the plugin package
            
        Returns:
            Dictionary with package information
        """
        if not package_path.exists():
            raise FlashGenieError(f"Package file does not exist: {package_path}")
        
        try:
            with zipfile.ZipFile(package_path, 'r') as zipf:
                # Get file list
                file_list = zipf.namelist()
                
                # Read manifest
                manifest_data = None
                if "plugin.json" in file_list:
                    with zipf.open("plugin.json") as manifest_file:
                        manifest_data = json.load(manifest_file)
                
                # Calculate package size
                package_size = package_path.stat().st_size
                
                # Count files
                file_count = len(file_list)
                
                return {
                    "package_path": str(package_path),
                    "package_size": package_size,
                    "file_count": file_count,
                    "files": file_list,
                    "manifest": manifest_data,
                    "valid": manifest_data is not None
                }
                
        except zipfile.BadZipFile:
            raise FlashGenieError("Package is not a valid ZIP file")
        except Exception as e:
            raise FlashGenieError(f"Failed to read package info: {e}")
    
    def create_plugin_template(self, template_dir: Path, plugin_info: Dict[str, Any]) -> None:
        """
        Create a plugin template directory structure.
        
        Args:
            template_dir: Directory to create template in
            plugin_info: Plugin information dictionary
        """
        template_dir.mkdir(parents=True, exist_ok=True)
        
        # Create basic structure
        (template_dir / "src").mkdir(exist_ok=True)
        (template_dir / "tests").mkdir(exist_ok=True)
        (template_dir / "docs").mkdir(exist_ok=True)
        
        # Create manifest template
        manifest_template = {
            "name": plugin_info.get("name", "my-plugin"),
            "version": plugin_info.get("version", "1.0.0"),
            "description": plugin_info.get("description", "A FlashGenie plugin"),
            "author": plugin_info.get("author", "Plugin Developer"),
            "license": plugin_info.get("license", "MIT"),
            "flashgenie_version": ">=1.8.0",
            "type": plugin_info.get("type", "integration"),
            "entry_point": "MyPlugin",
            "permissions": [],
            "dependencies": [],
            "settings_schema": {
                "enabled": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable this plugin"
                }
            }
        }
        
        with open(template_dir / "plugin.json", 'w') as f:
            json.dump(manifest_template, f, indent=2)
        
        # Create basic Python file
        python_template = '''"""
{description}

This plugin provides {type} functionality for FlashGenie.
"""

from ..plugin_system import BasePlugin


class MyPlugin(BasePlugin):
    """Main plugin class."""
    
    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
        self.name = "{name}"
        self.version = "{version}"
    
    def initialize(self) -> None:
        """Initialize the plugin."""
        self.logger.info(f"Initializing {{self.name}} plugin")
        # TODO: Add initialization logic
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        self.logger.info(f"Cleaning up {{self.name}} plugin")
        # TODO: Add cleanup logic
    
    def get_info(self) -> dict:
        """Get plugin information."""
        return {{
            "name": self.name,
            "version": self.version,
            "description": "{description}",
            "type": "{type}"
        }}
'''.format(**plugin_info)
        
        with open(template_dir / "__init__.py", 'w') as f:
            f.write(python_template)
        
        # Create README template
        readme_template = f'''# {plugin_info.get("name", "My Plugin")}

{plugin_info.get("description", "A FlashGenie plugin")}

## Installation

1. Download the plugin package
2. Install using FlashGenie CLI:
   ```bash
   python -m flashgenie plugins install {plugin_info.get("name", "my-plugin")}.zip
   ```

## Usage

TODO: Add usage instructions

## Configuration

TODO: Add configuration details

## License

{plugin_info.get("license", "MIT")} License
'''
        
        with open(template_dir / "README.md", 'w') as f:
            f.write(readme_template)
    
    def get_packaging_summary(self, package_path: Path) -> str:
        """Get a human-readable packaging summary."""
        try:
            info = self.get_package_info(package_path)
            
            summary = []
            summary.append(f"📦 **Plugin Package Created**")
            summary.append(f"   File: {package_path.name}")
            summary.append(f"   Size: {info['package_size'] / 1024:.1f} KB")
            summary.append(f"   Files: {info['file_count']}")
            
            if info['manifest']:
                manifest = info['manifest']
                summary.append(f"   Plugin: {manifest.get('name', 'Unknown')} v{manifest.get('version', '1.0.0')}")
                summary.append(f"   Type: {manifest.get('type', 'Unknown')}")
                summary.append(f"   Author: {manifest.get('author', 'Unknown')}")
            
            summary.append(f"\n✅ Package is ready for distribution!")
            
            return "\n".join(summary)
            
        except Exception as e:
            return f"❌ Failed to get package summary: {e}"
