"""
FlashGenie Plugin Development Kit (PDK)

Provides tools and utilities for plugin developers to create, test, and package
FlashGenie plugins with ease.
"""

import json
import shutil
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import tempfile
import subprocess
import sys

from flashgenie.core.plugin_system import PluginType, Permission
from flashgenie.core.plugin_manager import PluginManager
from flashgenie.utils.exceptions import FlashGenieError


class PluginDevelopmentKit:
    """Plugin Development Kit for creating and testing plugins."""
    
    def __init__(self, workspace_dir: Optional[Path] = None):
        """Initialize the PDK."""
        self.workspace_dir = workspace_dir or Path("plugin_workspace")
        self.templates_dir = Path(__file__).parent / "plugin_templates"
        self.plugin_manager = PluginManager()
        
        # Ensure workspace exists
        self.workspace_dir.mkdir(exist_ok=True)
    
    def create_plugin_scaffold(self, plugin_name: str, plugin_type: PluginType, 
                             author: str = "Plugin Developer") -> Path:
        """Create a new plugin scaffold with template files."""
        print(f"🏗️ Creating plugin scaffold: {plugin_name}")
        
        # Validate plugin name
        if not plugin_name.replace("-", "").replace("_", "").isalnum():
            raise FlashGenieError("Plugin name must contain only letters, numbers, hyphens, and underscores")
        
        # Create plugin directory
        plugin_dir = self.workspace_dir / plugin_name
        if plugin_dir.exists():
            raise FlashGenieError(f"Plugin directory already exists: {plugin_dir}")
        
        plugin_dir.mkdir(parents=True)
        
        # Generate plugin manifest
        manifest = self._generate_manifest_template(plugin_name, plugin_type, author)
        manifest_file = plugin_dir / "plugin.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Generate plugin code template
        code_template = self._generate_code_template(plugin_name, plugin_type)
        code_file = plugin_dir / "__init__.py"
        with open(code_file, 'w') as f:
            f.write(code_template)
        
        # Generate README
        readme_content = self._generate_readme_template(plugin_name, plugin_type, author)
        readme_file = plugin_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        # Generate test file
        test_content = self._generate_test_template(plugin_name, plugin_type)
        test_file = plugin_dir / "test_plugin.py"
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        print(f"✅ Plugin scaffold created at: {plugin_dir}")
        print(f"📝 Edit {manifest_file} to configure your plugin")
        print(f"💻 Edit {code_file} to implement your plugin")
        print(f"🧪 Run tests with: python {test_file}")
        
        return plugin_dir
    
    def validate_plugin(self, plugin_dir: Path) -> Dict[str, Any]:
        """Validate a plugin for compliance and best practices."""
        print(f"🔍 Validating plugin: {plugin_dir}")
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check required files
        required_files = ["plugin.json", "__init__.py"]
        for file_name in required_files:
            file_path = plugin_dir / file_name
            if not file_path.exists():
                validation_results["errors"].append(f"Missing required file: {file_name}")
                validation_results["valid"] = False
        
        if not validation_results["valid"]:
            return validation_results
        
        # Validate manifest
        try:
            with open(plugin_dir / "plugin.json", 'r') as f:
                manifest = json.load(f)
            
            manifest_validation = self._validate_manifest(manifest)
            validation_results["errors"].extend(manifest_validation["errors"])
            validation_results["warnings"].extend(manifest_validation["warnings"])
            
            if manifest_validation["errors"]:
                validation_results["valid"] = False
        
        except Exception as e:
            validation_results["errors"].append(f"Invalid plugin.json: {e}")
            validation_results["valid"] = False
        
        # Validate Python code
        try:
            code_validation = self._validate_python_code(plugin_dir / "__init__.py")
            validation_results["warnings"].extend(code_validation["warnings"])
            validation_results["suggestions"].extend(code_validation["suggestions"])
        
        except Exception as e:
            validation_results["errors"].append(f"Python code validation failed: {e}")
            validation_results["valid"] = False
        
        # Security checks
        security_check = self._perform_security_check(plugin_dir)
        validation_results["warnings"].extend(security_check["warnings"])
        
        # Best practices check
        best_practices = self._check_best_practices(plugin_dir)
        validation_results["suggestions"].extend(best_practices["suggestions"])
        
        return validation_results
    
    def test_plugin(self, plugin_dir: Path, test_mode: str = "basic") -> Dict[str, Any]:
        """Test a plugin in isolated environment."""
        print(f"🧪 Testing plugin: {plugin_dir}")
        
        test_results = {
            "success": True,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
            "output": []
        }
        
        try:
            # Load plugin in test environment
            temp_plugins_dir = Path(tempfile.mkdtemp())
            test_plugin_dir = temp_plugins_dir / "test" / plugin_dir.name
            test_plugin_dir.parent.mkdir(parents=True)
            shutil.copytree(plugin_dir, test_plugin_dir)
            
            # Initialize plugin manager with test directory
            test_plugin_manager = PluginManager(temp_plugins_dir)
            
            # Discover and load plugin
            discovered = test_plugin_manager.discover_plugins()
            if plugin_dir.name not in discovered:
                test_results["success"] = False
                test_results["errors"].append("Plugin not discovered")
                return test_results
            
            # Test plugin loading
            test_results["tests_run"] += 1
            if test_plugin_manager.load_plugin(plugin_dir.name):
                test_results["tests_passed"] += 1
                test_results["output"].append("✅ Plugin loaded successfully")
            else:
                test_results["tests_failed"] += 1
                test_results["errors"].append("Failed to load plugin")
                test_results["success"] = False
            
            # Test plugin functionality
            if test_mode in ["detailed", "comprehensive"]:
                plugin_instance = test_plugin_manager.get_plugin(plugin_dir.name)
                if plugin_instance:
                    func_test_results = self._test_plugin_functionality(plugin_instance)
                    test_results["tests_run"] += func_test_results["tests_run"]
                    test_results["tests_passed"] += func_test_results["tests_passed"]
                    test_results["tests_failed"] += func_test_results["tests_failed"]
                    test_results["output"].extend(func_test_results["output"])
                    
                    if func_test_results["tests_failed"] > 0:
                        test_results["success"] = False
            
            # Test plugin unloading
            test_results["tests_run"] += 1
            if test_plugin_manager.unload_plugin(plugin_dir.name):
                test_results["tests_passed"] += 1
                test_results["output"].append("✅ Plugin unloaded successfully")
            else:
                test_results["tests_failed"] += 1
                test_results["errors"].append("Failed to unload plugin")
                test_results["success"] = False
            
            # Cleanup
            shutil.rmtree(temp_plugins_dir, ignore_errors=True)
        
        except Exception as e:
            test_results["success"] = False
            test_results["errors"].append(f"Test execution failed: {e}")
        
        return test_results
    
    def package_plugin(self, plugin_dir: Path, output_dir: Optional[Path] = None) -> Path:
        """Package a plugin for distribution."""
        print(f"📦 Packaging plugin: {plugin_dir}")
        
        # Validate plugin first
        validation = self.validate_plugin(plugin_dir)
        if not validation["valid"]:
            raise FlashGenieError(f"Plugin validation failed: {validation['errors']}")
        
        # Determine output location
        output_dir = output_dir or self.workspace_dir / "packages"
        output_dir.mkdir(exist_ok=True)
        
        # Create package filename
        with open(plugin_dir / "plugin.json", 'r') as f:
            manifest = json.load(f)
        
        package_name = f"{manifest['name']}-{manifest['version']}.zip"
        package_path = output_dir / package_name
        
        # Create ZIP package
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in plugin_dir.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    arcname = file_path.relative_to(plugin_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Plugin packaged: {package_path}")
        return package_path
    
    def install_plugin_for_testing(self, plugin_dir: Path) -> bool:
        """Install plugin in development category for testing."""
        try:
            return self.plugin_manager.install_plugin(plugin_dir, "development")
        except Exception as e:
            print(f"❌ Failed to install plugin for testing: {e}")
            return False
    
    def _generate_manifest_template(self, plugin_name: str, plugin_type: PluginType, 
                                  author: str) -> Dict[str, Any]:
        """Generate plugin manifest template."""
        # Determine default permissions based on plugin type
        default_permissions = {
            PluginType.IMPORTER: ["file_read", "deck_write"],
            PluginType.EXPORTER: ["deck_read", "file_write"],
            PluginType.THEME: [],
            PluginType.QUIZ_MODE: ["deck_read", "user_data"],
            PluginType.AI_ENHANCEMENT: ["deck_read", "deck_write", "user_data"],
            PluginType.ANALYTICS: ["deck_read", "user_data"],
            PluginType.INTEGRATION: ["user_data", "system_integration"]
        }.get(plugin_type, [])
        
        return {
            "name": plugin_name,
            "version": "1.0.0",
            "description": f"A {plugin_type.value} plugin for FlashGenie",
            "author": author,
            "license": "MIT",
            "flashgenie_version": ">=1.7.0",
            "type": plugin_type.value,
            "entry_point": f"{self._to_class_name(plugin_name)}Plugin",
            "permissions": default_permissions,
            "dependencies": [],
            "settings_schema": {
                "enabled": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable this plugin"
                }
            },
            "homepage": "https://github.com/your-username/your-plugin",
            "repository": "https://github.com/your-username/your-plugin",
            "tags": [plugin_type.value, "community"]
        }
    
    def _to_class_name(self, plugin_name: str) -> str:
        """Convert plugin name to class name."""
        # Convert kebab-case or snake_case to PascalCase
        parts = plugin_name.replace("-", "_").split("_")
        return "".join(word.capitalize() for word in parts)
    
    def _generate_code_template(self, plugin_name: str, plugin_type: PluginType) -> str:
        """Generate plugin code template."""
        class_name = f"{self._to_class_name(plugin_name)}Plugin"
        
        # Base class mapping
        base_classes = {
            PluginType.IMPORTER: "ImporterPlugin",
            PluginType.EXPORTER: "ExporterPlugin",
            PluginType.THEME: "ThemePlugin",
            PluginType.QUIZ_MODE: "QuizModePlugin",
            PluginType.AI_ENHANCEMENT: "AIEnhancementPlugin",
            PluginType.ANALYTICS: "AnalyticsPlugin",
            PluginType.INTEGRATION: "IntegrationPlugin"
        }
        
        base_class = base_classes.get(plugin_type, "BasePlugin")
        
        template = f'''"""
{plugin_name.replace("-", " ").replace("_", " ").title()} Plugin for FlashGenie

TODO: Add plugin description here.
"""

from typing import Dict, Any, List, Optional
from flashgenie.core.plugin_system import {base_class}


class {class_name}({base_class}):
    """{plugin_name.replace("-", " ").replace("_", " ").title()} plugin implementation."""
    
    def initialize(self) -> None:
        """Initialize the plugin."""
        # TODO: Add any required permission checks
        # self.require_permission(Permission.DECK_READ)
        
        self.logger.info("{plugin_name} plugin initialized")
        
        # TODO: Initialize plugin resources here
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        self.logger.info("{plugin_name} plugin cleaned up")
        
        # TODO: Cleanup plugin resources here
'''

        # Add plugin-type specific methods
        if plugin_type == PluginType.IMPORTER:
            template += '''
    def can_import(self, file_path) -> bool:
        """Check if this plugin can import the given file."""
        # TODO: Implement file format detection
        return False
    
    def import_data(self, file_path, deck_name: str) -> Dict[str, Any]:
        """Import data from file and return import results."""
        # TODO: Implement data import logic
        return {"success": False, "error": "Not implemented"}
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        # TODO: Return list of supported file extensions
        return []
'''
        elif plugin_type == PluginType.THEME:
            template += '''
    def get_theme_name(self) -> str:
        """Get the name of this theme."""
        return "{plugin_name.replace("-", " ").replace("_", " ").title()}"
    
    def apply_theme(self) -> Dict[str, Any]:
        """Apply theme and return theme configuration."""
        # TODO: Implement theme application logic
        return {{
            "name": "{plugin_name}",
            "colors": {{
                "background": "#ffffff",
                "text": "#000000"
            }}
        }}
    
    def get_theme_info(self) -> Dict[str, Any]:
        """Get theme information and preview."""
        return {{
            "name": self.get_theme_name(),
            "description": "TODO: Add theme description",
            "features": ["TODO: List theme features"]
        }}
'''
        elif plugin_type == PluginType.AI_ENHANCEMENT:
            template += '''
    def get_ai_capabilities(self) -> List[str]:
        """Get list of AI capabilities this plugin provides."""
        # TODO: Return list of AI capabilities
        return []
    
    def process_content(self, content: str, task: str, **kwargs) -> Dict[str, Any]:
        """Process content using AI capabilities."""
        # TODO: Implement AI content processing
        return {"error": "Not implemented"}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the AI model used."""
        return {{
            "model_type": "custom",
            "version": "1.0.0",
            "capabilities": self.get_ai_capabilities()
        }}
'''

        return template
    
    def _generate_readme_template(self, plugin_name: str, plugin_type: PluginType, 
                                author: str) -> str:
        """Generate README template."""
        return f'''# {plugin_name.replace("-", " ").replace("_", " ").title()}

A {plugin_type.value} plugin for FlashGenie.

## Description

TODO: Add detailed description of what this plugin does.

## Features

- TODO: List plugin features
- TODO: Add more features

## Installation

1. Package the plugin:
   ```bash
   python -m flashgenie.core.plugin_dev_kit package {plugin_name}
   ```

2. Install the plugin:
   ```bash
   python -m flashgenie plugins install {plugin_name}-1.0.0.zip
   ```

3. Enable the plugin:
   ```bash
   python -m flashgenie plugins enable {plugin_name}
   ```

## Configuration

TODO: Document plugin settings and configuration options.

## Usage

TODO: Provide usage examples and instructions.

## Development

### Testing

Run the plugin tests:
```bash
python test_plugin.py
```

### Contributing

TODO: Add contribution guidelines.

## License

MIT License - see LICENSE file for details.

## Author

{author}
'''
    
    def _generate_test_template(self, plugin_name: str, plugin_type: PluginType) -> str:
        """Generate test template."""
        class_name = f"{self._to_class_name(plugin_name)}Plugin"
        
        return f'''#!/usr/bin/env python3
"""
Test script for {plugin_name} plugin.
"""

import sys
import json
from pathlib import Path

# Add FlashGenie to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flashgenie.core.plugin_system import PluginManifest
from {plugin_name.replace("-", "_")} import {class_name}


def test_plugin_initialization():
    """Test plugin initialization."""
    print("Testing plugin initialization...")
    
    # Load manifest
    with open("plugin.json", "r") as f:
        manifest_data = json.load(f)
    
    manifest = PluginManifest.from_dict(manifest_data)
    
    # Create plugin instance
    plugin = {class_name}(manifest, {{}})
    
    try:
        plugin.initialize()
        print("✅ Plugin initialized successfully")
        
        # Test plugin info
        info = plugin.get_info()
        print(f"Plugin info: {{info}}")
        
        plugin.cleanup()
        print("✅ Plugin cleaned up successfully")
        
        return True
    except Exception as e:
        print(f"❌ Plugin test failed: {{e}}")
        return False


def test_plugin_functionality():
    """Test plugin-specific functionality."""
    print("Testing plugin functionality...")
    
    # TODO: Add plugin-specific tests here
    
    return True


def main():
    """Run all tests."""
    print(f"🧪 Testing {plugin_name} plugin")
    print("=" * 50)
    
    tests = [
        test_plugin_initialization,
        test_plugin_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {{passed}}/{{total}} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''
    
    def _validate_manifest(self, manifest: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate plugin manifest."""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ["name", "version", "description", "author", "license", 
                          "flashgenie_version", "type", "entry_point"]
        
        for field in required_fields:
            if field not in manifest:
                errors.append(f"Missing required field: {field}")
        
        # Validate plugin type
        if "type" in manifest:
            try:
                PluginType(manifest["type"])
            except ValueError:
                errors.append(f"Invalid plugin type: {manifest['type']}")
        
        # Validate permissions
        if "permissions" in manifest:
            for perm in manifest["permissions"]:
                try:
                    Permission(perm)
                except ValueError:
                    warnings.append(f"Unknown permission: {perm}")
        
        return {"errors": errors, "warnings": warnings}
    
    def _validate_python_code(self, code_file: Path) -> Dict[str, List[str]]:
        """Validate Python code."""
        warnings = []
        suggestions = []
        
        try:
            with open(code_file, 'r') as f:
                code = f.read()
            
            # Basic syntax check
            compile(code, str(code_file), 'exec')
            
            # Check for common issues
            if "TODO" in code:
                suggestions.append("Remove TODO comments before release")
            
            if "print(" in code and "self.logger" in code:
                suggestions.append("Consider using logger instead of print statements")
        
        except SyntaxError as e:
            warnings.append(f"Syntax error: {e}")
        
        return {"warnings": warnings, "suggestions": suggestions}
    
    def _perform_security_check(self, plugin_dir: Path) -> Dict[str, List[str]]:
        """Perform basic security checks."""
        warnings = []
        
        # Check for potentially dangerous imports
        dangerous_imports = ["os", "subprocess", "sys", "shutil", "socket"]
        
        for py_file in plugin_dir.glob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                for dangerous in dangerous_imports:
                    if f"import {dangerous}" in content or f"from {dangerous}" in content:
                        warnings.append(f"Potentially dangerous import in {py_file.name}: {dangerous}")
            
            except Exception:
                pass
        
        return {"warnings": warnings}
    
    def _check_best_practices(self, plugin_dir: Path) -> Dict[str, List[str]]:
        """Check for best practices compliance."""
        suggestions = []
        
        # Check for README
        if not (plugin_dir / "README.md").exists():
            suggestions.append("Add a README.md file with plugin documentation")
        
        # Check for tests
        test_files = list(plugin_dir.glob("test*.py"))
        if not test_files:
            suggestions.append("Add test files to verify plugin functionality")
        
        # Check for license
        if not (plugin_dir / "LICENSE").exists():
            suggestions.append("Add a LICENSE file")
        
        return {"suggestions": suggestions}
    
    def _test_plugin_functionality(self, plugin_instance) -> Dict[str, Any]:
        """Test plugin-specific functionality."""
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "output": []
        }
        
        # Test get_info method
        results["tests_run"] += 1
        try:
            info = plugin_instance.get_info()
            if isinstance(info, dict) and "name" in info:
                results["tests_passed"] += 1
                results["output"].append("✅ get_info() method works correctly")
            else:
                results["tests_failed"] += 1
                results["output"].append("❌ get_info() returned invalid data")
        except Exception as e:
            results["tests_failed"] += 1
            results["output"].append(f"❌ get_info() failed: {e}")
        
        # TODO: Add more plugin-type specific tests
        
        return results
