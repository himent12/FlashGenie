"""
Plugin system core components for FlashGenie.

This package contains the core plugin system modules including
plugin management, loading, and base plugin classes.
"""

from .plugin_manager import PluginManager
from .plugin_system import (
    BasePlugin, ImporterPlugin, ExporterPlugin, ThemePlugin,
    QuizModePlugin, AIEnhancementPlugin, AnalyticsPlugin,
    IntegrationPlugin, PluginType, Permission
)

__all__ = [
    'PluginManager',
    'BasePlugin',
    'ImporterPlugin', 
    'ExporterPlugin',
    'ThemePlugin',
    'QuizModePlugin',
    'AIEnhancementPlugin',
    'AnalyticsPlugin',
    'IntegrationPlugin',
    'PluginType',
    'Permission'
]
