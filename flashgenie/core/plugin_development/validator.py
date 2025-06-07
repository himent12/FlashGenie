"""
Plugin validation utilities for the Plugin Development Kit.

This module provides functions to validate plugin structure, security, and best practices.
"""

import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Set

from ..plugin_system import PluginType


class PluginValidator:
    """Validates plugin structure, security, and best practices."""
    
    def __init__(self):
        """Initialize the validator."""
        self.required_files = ["plugin.json", "__init__.py"]
        self.recommended_files = ["README.md", "test_plugin.py"]
        self.security_patterns = [
            r"eval\s*\(",
            r"exec\s*\(",
            r"__import__\s*\(",
            r"open\s*\([^)]*['\"]w['\"]",  # Write mode file operations
            r"subprocess\.",
            r"os\.system",
            r"os\.popen"
        ]
    
    def validate_plugin(self, plugin_path: Path) -> Dict[str, Any]:
        """
        Validate a plugin directory.
        
        Args:
            plugin_path: Path to the plugin directory
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check if directory exists
        if not plugin_path.exists() or not plugin_path.is_dir():
            results["valid"] = False
            results["errors"].append(f"Plugin directory does not exist: {plugin_path}")
            return results
        
        # Validate file structure
        self._validate_file_structure(plugin_path, results)
        
        # Validate manifest
        if (plugin_path / "plugin.json").exists():
            self._validate_manifest(plugin_path / "plugin.json", results)
        
        # Validate Python code
        if (plugin_path / "__init__.py").exists():
            self._validate_python_code(plugin_path / "__init__.py", results)
        
        # Security validation
        self._validate_security(plugin_path, results)
        
        # Best practices validation
        self._validate_best_practices(plugin_path, results)
        
        return results
    
    def _validate_file_structure(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Validate the plugin file structure."""
        # Check required files
        for required_file in self.required_files:
            file_path = plugin_path / required_file
            if not file_path.exists():
                results["valid"] = False
                results["errors"].append(f"Required file missing: {required_file}")
        
        # Check recommended files
        for recommended_file in self.recommended_files:
            file_path = plugin_path / recommended_file
            if not file_path.exists():
                results["suggestions"].append(f"Consider adding {recommended_file} for better documentation")
        
        # Check for common issues
        init_file = plugin_path / "__init__.py"
        if init_file.exists() and init_file.stat().st_size == 0:
            results["warnings"].append("__init__.py is empty - plugin may not function correctly")
    
    def _validate_manifest(self, manifest_path: Path, results: Dict[str, Any]) -> None:
        """Validate the plugin manifest."""
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            results["valid"] = False
            results["errors"].append(f"Invalid JSON in plugin.json: {e}")
            return
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Cannot read plugin.json: {e}")
            return
        
        # Check required fields
        required_fields = [
            "name", "version", "description", "author", "license",
            "flashgenie_version", "type", "entry_point"
        ]
        
        for field in required_fields:
            if field not in manifest:
                results["valid"] = False
                results["errors"].append(f"Required field missing in manifest: {field}")
        
        # Validate plugin type
        if "type" in manifest:
            try:
                PluginType(manifest["type"])
            except ValueError:
                results["valid"] = False
                results["errors"].append(f"Invalid plugin type: {manifest['type']}")
        
        # Validate version format
        if "version" in manifest:
            if not re.match(r'^\d+\.\d+\.\d+', manifest["version"]):
                results["warnings"].append("Version should follow semantic versioning (e.g., 1.0.0)")
        
        # Validate FlashGenie version requirement
        if "flashgenie_version" in manifest:
            if not re.match(r'^>=?\d+\.\d+\.\d+', manifest["flashgenie_version"]):
                results["warnings"].append("FlashGenie version should specify minimum version (e.g., >=1.8.0)")
        
        # Check permissions
        if "permissions" in manifest:
            valid_permissions = [
                "file_read", "file_write", "deck_read", "deck_write",
                "user_data", "network", "system_integration", "config_read", "config_write"
            ]
            
            for permission in manifest["permissions"]:
                if permission not in valid_permissions:
                    results["warnings"].append(f"Unknown permission: {permission}")
        
        # Check dependencies format
        if "dependencies" in manifest:
            for dep in manifest["dependencies"]:
                if not re.match(r'^[a-zA-Z0-9_-]+([><=!]+[\d.]+)?$', dep):
                    results["warnings"].append(f"Dependency format may be invalid: {dep}")
        
        # Validate settings schema
        if "settings_schema" in manifest:
            self._validate_settings_schema(manifest["settings_schema"], results)
    
    def _validate_settings_schema(self, schema: Dict[str, Any], results: Dict[str, Any]) -> None:
        """Validate the settings schema."""
        for setting_name, setting_config in schema.items():
            if not isinstance(setting_config, dict):
                results["warnings"].append(f"Setting '{setting_name}' should be an object")
                continue
            
            # Check required fields
            if "type" not in setting_config:
                results["warnings"].append(f"Setting '{setting_name}' missing type specification")
            
            # Validate type
            valid_types = ["string", "number", "integer", "boolean", "array", "object"]
            if "type" in setting_config and setting_config["type"] not in valid_types:
                results["warnings"].append(f"Setting '{setting_name}' has invalid type: {setting_config['type']}")
            
            # Check for description
            if "description" not in setting_config:
                results["suggestions"].append(f"Consider adding description for setting '{setting_name}'")
    
    def _validate_python_code(self, code_path: Path, results: Dict[str, Any]) -> None:
        """Validate Python code syntax and structure."""
        try:
            with open(code_path, 'r') as f:
                code_content = f.read()
        except Exception as e:
            results["errors"].append(f"Cannot read Python file: {e}")
            return
        
        # Check syntax
        try:
            ast.parse(code_content)
        except SyntaxError as e:
            results["valid"] = False
            results["errors"].append(f"Python syntax error: {e}")
            return
        
        # Check for required class
        try:
            tree = ast.parse(code_content)
            class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            if not class_names:
                results["warnings"].append("No plugin class found in __init__.py")
            elif len(class_names) > 1:
                results["suggestions"].append("Consider organizing multiple classes into separate modules")
        except Exception:
            pass  # AST parsing issues are not critical
        
        # Check imports
        self._validate_imports(code_content, results)
        
        # Check for docstrings
        if '"""' not in code_content and "'''" not in code_content:
            results["suggestions"].append("Consider adding docstrings for better documentation")
    
    def _validate_imports(self, code_content: str, results: Dict[str, Any]) -> None:
        """Validate import statements."""
        lines = code_content.split('\n')
        
        # Check for relative imports from FlashGenie
        flashgenie_imports = []
        for line in lines:
            if 'from flashgenie' in line or 'import flashgenie' in line:
                flashgenie_imports.append(line.strip())
        
        if not flashgenie_imports:
            results["warnings"].append("No FlashGenie imports found - plugin may not integrate properly")
        
        # Check for dangerous imports
        dangerous_imports = ['os', 'subprocess', 'sys', 'importlib']
        for line in lines:
            for dangerous in dangerous_imports:
                if f'import {dangerous}' in line or f'from {dangerous}' in line:
                    results["warnings"].append(f"Potentially dangerous import detected: {dangerous}")
    
    def _validate_security(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Validate plugin security."""
        # Check all Python files
        for py_file in plugin_path.glob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Check for security patterns
                for pattern in self.security_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        results["warnings"].append(f"Potentially unsafe code pattern in {py_file.name}: {pattern}")
                
                # Check for hardcoded secrets
                secret_patterns = [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'api_key\s*=\s*["\'][^"\']+["\']',
                    r'secret\s*=\s*["\'][^"\']+["\']',
                    r'token\s*=\s*["\'][^"\']+["\']'
                ]
                
                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        results["warnings"].append(f"Possible hardcoded secret in {py_file.name}")
                
            except Exception:
                continue  # Skip files that can't be read
    
    def _validate_best_practices(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Validate best practices compliance."""
        # Check for LICENSE file
        license_files = ["LICENSE", "LICENSE.txt", "LICENSE.md"]
        has_license = any((plugin_path / license_file).exists() for license_file in license_files)
        
        if not has_license:
            results["suggestions"].append("Consider adding a LICENSE file")
        
        # Check for CHANGELOG
        changelog_files = ["CHANGELOG.md", "CHANGELOG.txt", "CHANGES.md"]
        has_changelog = any((plugin_path / changelog_file).exists() for changelog_file in changelog_files)
        
        if not has_changelog:
            results["suggestions"].append("Consider adding a CHANGELOG file")
        
        # Check README content
        readme_path = plugin_path / "README.md"
        if readme_path.exists():
            try:
                with open(readme_path, 'r') as f:
                    readme_content = f.read()
                
                # Check for essential sections
                essential_sections = ["installation", "usage", "configuration"]
                for section in essential_sections:
                    if section.lower() not in readme_content.lower():
                        results["suggestions"].append(f"Consider adding {section} section to README")
                
                # Check length
                if len(readme_content) < 200:
                    results["suggestions"].append("README is quite short - consider adding more details")
                    
            except Exception:
                pass
        
        # Check test coverage
        test_files = list(plugin_path.glob("test_*.py")) + list(plugin_path.glob("*_test.py"))
        if not test_files:
            results["suggestions"].append("Consider adding test files for better quality assurance")
        
        # Check for configuration files
        config_files = ["config.json", "settings.json", ".env"]
        for config_file in config_files:
            if (plugin_path / config_file).exists():
                results["suggestions"].append(f"Consider documenting {config_file} in README")
    
    def get_validation_summary(self, results: Dict[str, Any]) -> str:
        """Get a human-readable validation summary."""
        summary = []
        
        if results["valid"]:
            summary.append("✅ Plugin validation passed!")
        else:
            summary.append("❌ Plugin validation failed!")
        
        if results["errors"]:
            summary.append(f"\n🚨 Errors ({len(results['errors'])}):")
            for error in results["errors"]:
                summary.append(f"   • {error}")
        
        if results["warnings"]:
            summary.append(f"\n⚠️ Warnings ({len(results['warnings'])}):")
            for warning in results["warnings"]:
                summary.append(f"   • {warning}")
        
        if results["suggestions"]:
            summary.append(f"\n💡 Suggestions ({len(results['suggestions'])}):")
            for suggestion in results["suggestions"]:
                summary.append(f"   • {suggestion}")
        
        return "\n".join(summary)
