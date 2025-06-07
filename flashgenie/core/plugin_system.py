"""
FlashGenie Plugin System - Main Interface

This module provides the main interface to FlashGenie's plugin system,
importing and exposing all plugin-related functionality.
"""

# Import core plugin system components
from .plugin_system_core.plugin_system import (
    PluginType,
    PluginStatus,
    Permission,
    PluginManifest,
    PluginInfo,
    PluginError,
    BasePlugin,
    ImporterPlugin,
    ExporterPlugin,
    QuizModePlugin,
    ThemePlugin,
    AIEnhancementPlugin,
    AnalyticsPlugin,
    IntegrationPlugin,
    PluginSecurityManager
)

from .plugin_system_core.plugin_manager import PluginManager
from .plugin_system_core.plugin_marketplace import PluginMarketplace
from .plugin_system_core.plugin_hot_swap import HotSwapManager, PluginUpdateManager
from .plugin_system_core.plugin_dependencies import PluginDependencyManager

__all__ = [
    # Core plugin types and enums
    'PluginType',
    'PluginStatus', 
    'Permission',
    
    # Plugin data structures
    'PluginManifest',
    'PluginInfo',
    'PluginError',
    
    # Base plugin classes
    'BasePlugin',
    'ImporterPlugin',
    'ExporterPlugin',
    'QuizModePlugin',
    'ThemePlugin',
    'AIEnhancementPlugin',
    'AnalyticsPlugin',
    'IntegrationPlugin',
    
    # Plugin management
    'PluginManager',
    'PluginMarketplace',
    'HotSwapManager',
    'PluginUpdateManager',
    'PluginDependencyManager',
    'PluginSecurityManager'
]
