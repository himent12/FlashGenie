"""
FlashGenie Plugin System - Core Architecture

This module provides the foundation for FlashGenie's extensible plugin system,
allowing third-party developers to extend functionality through well-defined APIs.
"""

import json
import importlib
import importlib.util
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, Set
from datetime import datetime
import logging

from flashgenie.utils.exceptions import FlashGenieError


class PluginType(Enum):
    """Types of plugins supported by FlashGenie."""
    IMPORTER = "importer"
    EXPORTER = "exporter"
    QUIZ_MODE = "quiz_mode"
    THEME = "theme"
    ANALYTICS = "analytics"
    INTEGRATION = "integration"
    AI_ENHANCEMENT = "ai_enhancement"


class PluginStatus(Enum):
    """Plugin status states."""
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    LOADING = "loading"


class Permission(Enum):
    """Plugin permissions for security control."""
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    NETWORK = "network"
    DECK_READ = "deck_read"
    DECK_WRITE = "deck_write"
    USER_DATA = "user_data"
    SYSTEM_INTEGRATION = "system_integration"
    CONFIG_READ = "config_read"
    CONFIG_WRITE = "config_write"


@dataclass
class PluginManifest:
    """Plugin manifest containing metadata and configuration."""
    name: str
    version: str
    description: str
    author: str
    license: str
    flashgenie_version: str
    plugin_type: PluginType
    entry_point: str
    permissions: List[Permission] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    settings_schema: Dict[str, Any] = field(default_factory=dict)
    homepage: Optional[str] = None
    repository: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginManifest':
        """Create manifest from dictionary."""
        # Convert string permissions to Permission enums
        permissions = []
        for perm in data.get('permissions', []):
            try:
                permissions.append(Permission(perm))
            except ValueError:
                logging.warning(f"Unknown permission: {perm}")
        
        # Convert string plugin type to enum
        plugin_type = PluginType(data['type'])
        
        return cls(
            name=data['name'],
            version=data['version'],
            description=data['description'],
            author=data['author'],
            license=data['license'],
            flashgenie_version=data['flashgenie_version'],
            plugin_type=plugin_type,
            entry_point=data['entry_point'],
            permissions=permissions,
            dependencies=data.get('dependencies', []),
            settings_schema=data.get('settings_schema', {}),
            homepage=data.get('homepage'),
            repository=data.get('repository'),
            tags=data.get('tags', [])
        )


@dataclass
class PluginInfo:
    """Runtime plugin information."""
    manifest: PluginManifest
    path: Path
    status: PluginStatus
    instance: Optional['BasePlugin'] = None
    error_message: Optional[str] = None
    loaded_at: Optional[datetime] = None
    settings: Dict[str, Any] = field(default_factory=dict)


class PluginError(FlashGenieError):
    """Plugin-specific errors."""
    pass


class BasePlugin(ABC):
    """Base class for all FlashGenie plugins."""
    
    def __init__(self, manifest: PluginManifest, settings: Dict[str, Any]):
        """Initialize plugin with manifest and settings."""
        self.manifest = manifest
        self.settings = settings
        self.logger = logging.getLogger(f"plugin.{manifest.name}")
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the plugin. Called when plugin is loaded."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources. Called when plugin is unloaded."""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information for display."""
        return {
            'name': self.manifest.name,
            'version': self.manifest.version,
            'description': self.manifest.description,
            'author': self.manifest.author,
            'type': self.manifest.plugin_type.value
        }
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get plugin setting value."""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set plugin setting value."""
        self.settings[key] = value
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if plugin has specific permission."""
        return permission in self.manifest.permissions
    
    def require_permission(self, permission: Permission) -> None:
        """Require specific permission, raise error if not granted."""
        if not self.has_permission(permission):
            raise PluginError(f"Plugin {self.manifest.name} requires permission: {permission.value}")


class ImporterPlugin(BasePlugin):
    """Base class for importer plugins."""
    
    @abstractmethod
    def can_import(self, file_path: Path) -> bool:
        """Check if this plugin can import the given file."""
        pass
    
    @abstractmethod
    def import_data(self, file_path: Path, deck_name: str) -> Dict[str, Any]:
        """Import data from file and return import results."""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        pass


class ExporterPlugin(BasePlugin):
    """Base class for exporter plugins."""
    
    @abstractmethod
    def can_export(self, format_type: str) -> bool:
        """Check if this plugin can export to the given format."""
        pass
    
    @abstractmethod
    def export_data(self, deck, output_path: Path, options: Dict[str, Any]) -> None:
        """Export deck data to file."""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats."""
        pass


class QuizModePlugin(BasePlugin):
    """Base class for quiz mode plugins."""
    
    @abstractmethod
    def get_mode_name(self) -> str:
        """Get the name of this quiz mode."""
        pass
    
    @abstractmethod
    def create_session(self, deck, config: Dict[str, Any]):
        """Create a quiz session with this mode."""
        pass
    
    @abstractmethod
    def get_settings_schema(self) -> Dict[str, Any]:
        """Get settings schema for this quiz mode."""
        pass


class ThemePlugin(BasePlugin):
    """Base class for theme plugins."""
    
    @abstractmethod
    def get_theme_name(self) -> str:
        """Get the name of this theme."""
        pass
    
    @abstractmethod
    def apply_theme(self) -> Dict[str, Any]:
        """Apply theme and return theme configuration."""
        pass
    
    @abstractmethod
    def get_theme_info(self) -> Dict[str, Any]:
        """Get theme information and preview."""
        pass


class PluginSecurityManager:
    """Manages plugin security and permissions."""
    
    def __init__(self):
        self.permission_descriptions = {
            Permission.FILE_READ: "Read files from disk",
            Permission.FILE_WRITE: "Write files to disk",
            Permission.NETWORK: "Access network resources",
            Permission.DECK_READ: "Read flashcard decks",
            Permission.DECK_WRITE: "Modify flashcard decks",
            Permission.USER_DATA: "Access user statistics and progress",
            Permission.SYSTEM_INTEGRATION: "Integrate with system features",
            Permission.CONFIG_READ: "Read FlashGenie configuration",
            Permission.CONFIG_WRITE: "Modify FlashGenie configuration"
        }
    
    def validate_permissions(self, manifest: PluginManifest) -> List[str]:
        """Validate plugin permissions and return warnings."""
        warnings = []
        
        # Check for dangerous permission combinations
        if Permission.FILE_WRITE in manifest.permissions and Permission.NETWORK in manifest.permissions:
            warnings.append("Plugin can write files AND access network - potential security risk")
        
        if Permission.CONFIG_WRITE in manifest.permissions:
            warnings.append("Plugin can modify FlashGenie configuration")
        
        return warnings
    
    def get_permission_description(self, permission: Permission) -> str:
        """Get human-readable permission description."""
        return self.permission_descriptions.get(permission, f"Unknown permission: {permission.value}")
    
    def check_plugin_safety(self, plugin_path: Path) -> List[str]:
        """Perform basic safety checks on plugin code."""
        warnings = []
        
        # Check for potentially dangerous imports
        dangerous_imports = ['os', 'subprocess', 'sys', 'shutil', 'socket']
        
        try:
            with open(plugin_path / "__init__.py", 'r') as f:
                content = f.read()
                for dangerous in dangerous_imports:
                    if f"import {dangerous}" in content or f"from {dangerous}" in content:
                        warnings.append(f"Plugin imports potentially dangerous module: {dangerous}")
        except FileNotFoundError:
            warnings.append("Plugin missing __init__.py file")
        
        return warnings
