"""
FlashGenie Plugin Manager

Handles plugin discovery, loading, lifecycle management, and security.
"""

import json
import importlib
import importlib.util
import sys
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
from datetime import datetime
import logging

from .plugin_system import (
    BasePlugin, PluginManifest, PluginInfo, PluginType, PluginStatus,
    Permission, PluginError, PluginSecurityManager,
    ImporterPlugin, ExporterPlugin, QuizModePlugin, ThemePlugin,
    AIEnhancementPlugin, AnalyticsPlugin, IntegrationPlugin
)
from .plugin_marketplace import PluginMarketplace
from .plugin_hot_swap import HotSwapManager, PluginUpdateManager
from .plugin_dependencies import PluginDependencyManager
from flashgenie.config import APP_VERSION
from flashgenie.utils.exceptions import FlashGenieError


class PluginManager:
    """Central manager for all plugin operations."""
    
    def __init__(self, plugins_dir: Optional[Path] = None):
        """Initialize plugin manager."""
        self.plugins_dir = plugins_dir or Path("plugins")
        self.plugins: Dict[str, PluginInfo] = {}
        self.security_manager = PluginSecurityManager()
        self.logger = logging.getLogger("plugin_manager")

        # Plugin type mappings
        self.plugin_base_classes = {
            PluginType.IMPORTER: ImporterPlugin,
            PluginType.EXPORTER: ExporterPlugin,
            PluginType.QUIZ_MODE: QuizModePlugin,
            PluginType.THEME: ThemePlugin,
            PluginType.AI_ENHANCEMENT: AIEnhancementPlugin,
            PluginType.ANALYTICS: AnalyticsPlugin,
            PluginType.INTEGRATION: IntegrationPlugin,
        }

        # Phase 3 components
        self.marketplace = PluginMarketplace()
        self.dependency_manager = PluginDependencyManager()
        self.hot_swap_manager = HotSwapManager(self)
        self.update_manager = PluginUpdateManager(self, self.hot_swap_manager)

        # Ensure plugin directories exist
        self._create_plugin_directories()

        # Load plugin settings
        self.settings_file = self.plugins_dir / "settings.json"
        self.plugin_settings = self._load_plugin_settings()

        # Start hot swap monitoring
        self.hot_swap_manager.start_watching()
    
    def _create_plugin_directories(self) -> None:
        """Create plugin directory structure."""
        directories = [
            self.plugins_dir,
            self.plugins_dir / "official",
            self.plugins_dir / "community", 
            self.plugins_dir / "local",
            self.plugins_dir / "development"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_plugin_settings(self) -> Dict[str, Dict[str, Any]]:
        """Load plugin settings from file."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load plugin settings: {e}")
        return {}
    
    def _save_plugin_settings(self) -> None:
        """Save plugin settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.plugin_settings, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save plugin settings: {e}")
    
    def discover_plugins(self) -> List[str]:
        """Discover all available plugins."""
        discovered = []
        
        # Search in all plugin directories
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith('.'):
                for potential_plugin in plugin_dir.iterdir():
                    if potential_plugin.is_dir():
                        manifest_file = potential_plugin / "plugin.json"
                        if manifest_file.exists():
                            try:
                                manifest = self._load_manifest(manifest_file)
                                plugin_info = PluginInfo(
                                    manifest=manifest,
                                    path=potential_plugin,
                                    status=PluginStatus.INSTALLED
                                )
                                self.plugins[manifest.name] = plugin_info
                                discovered.append(manifest.name)
                                self.logger.info(f"Discovered plugin: {manifest.name}")
                            except Exception as e:
                                self.logger.error(f"Failed to load plugin manifest {manifest_file}: {e}")
        
        return discovered
    
    def _load_manifest(self, manifest_file: Path) -> PluginManifest:
        """Load plugin manifest from file."""
        with open(manifest_file, 'r') as f:
            data = json.load(f)
        
        # Validate required fields
        required_fields = ['name', 'version', 'description', 'author', 'license', 
                          'flashgenie_version', 'type', 'entry_point']
        for field in required_fields:
            if field not in data:
                raise PluginError(f"Missing required field in manifest: {field}")
        
        return PluginManifest.from_dict(data)
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load and initialize a plugin."""
        if plugin_name not in self.plugins:
            raise PluginError(f"Plugin not found: {plugin_name}")
        
        plugin_info = self.plugins[plugin_name]
        
        if plugin_info.status == PluginStatus.ENABLED:
            self.logger.info(f"Plugin {plugin_name} already loaded")
            return True
        
        try:
            plugin_info.status = PluginStatus.LOADING
            
            # Security checks
            warnings = self.security_manager.check_plugin_safety(plugin_info.path)
            if warnings:
                self.logger.warning(f"Security warnings for {plugin_name}: {warnings}")
            
            # Load plugin module
            spec = importlib.util.spec_from_file_location(
                plugin_name, 
                plugin_info.path / "__init__.py"
            )
            if spec is None or spec.loader is None:
                raise PluginError(f"Cannot load plugin module: {plugin_name}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"plugin_{plugin_name}"] = module
            spec.loader.exec_module(module)
            
            # Get plugin class
            entry_parts = plugin_info.manifest.entry_point.split('.')
            plugin_class = module
            for part in entry_parts:
                plugin_class = getattr(plugin_class, part)
            
            # Validate plugin class
            expected_base = self.plugin_base_classes.get(plugin_info.manifest.plugin_type, BasePlugin)
            if not issubclass(plugin_class, expected_base):
                raise PluginError(f"Plugin {plugin_name} does not inherit from {expected_base.__name__}")
            
            # Get plugin settings
            settings = self.plugin_settings.get(plugin_name, {})
            
            # Create plugin instance
            plugin_instance = plugin_class(plugin_info.manifest, settings)
            
            # Initialize plugin
            plugin_instance.initialize()
            
            # Update plugin info
            plugin_info.instance = plugin_instance
            plugin_info.status = PluginStatus.ENABLED
            plugin_info.loaded_at = datetime.now()
            plugin_info.settings = settings
            plugin_info.error_message = None
            
            self.logger.info(f"Successfully loaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name not in self.plugins:
            raise PluginError(f"Plugin not found: {plugin_name}")
        
        plugin_info = self.plugins[plugin_name]
        
        if plugin_info.status != PluginStatus.ENABLED:
            self.logger.info(f"Plugin {plugin_name} not loaded")
            return True
        
        try:
            # Cleanup plugin
            if plugin_info.instance:
                plugin_info.instance.cleanup()
            
            # Remove from sys.modules
            module_name = f"plugin_{plugin_name}"
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Update plugin info
            plugin_info.instance = None
            plugin_info.status = PluginStatus.INSTALLED
            plugin_info.loaded_at = None
            plugin_info.error_message = None
            
            self.logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin (load if not already loaded)."""
        return self.load_plugin(plugin_name)
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin (unload if loaded)."""
        return self.unload_plugin(plugin_name)
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get loaded plugin instance."""
        if plugin_name in self.plugins:
            plugin_info = self.plugins[plugin_name]
            if plugin_info.status == PluginStatus.ENABLED:
                return plugin_info.instance
        return None
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[BasePlugin]:
        """Get all loaded plugins of specific type."""
        plugins = []
        for plugin_info in self.plugins.values():
            if (plugin_info.manifest.plugin_type == plugin_type and 
                plugin_info.status == PluginStatus.ENABLED and 
                plugin_info.instance):
                plugins.append(plugin_info.instance)
        return plugins
    
    def list_plugins(self, status_filter: Optional[PluginStatus] = None) -> List[PluginInfo]:
        """List all plugins, optionally filtered by status."""
        plugins = list(self.plugins.values())
        if status_filter:
            plugins = [p for p in plugins if p.status == status_filter]
        return plugins
    
    def install_plugin(self, plugin_path: Path, category: str = "local") -> bool:
        """Install a plugin from a file or directory."""
        try:
            if plugin_path.suffix == '.zip':
                return self._install_from_zip(plugin_path, category)
            elif plugin_path.is_dir():
                return self._install_from_directory(plugin_path, category)
            else:
                raise PluginError(f"Unsupported plugin format: {plugin_path}")
        except Exception as e:
            self.logger.error(f"Failed to install plugin from {plugin_path}: {e}")
            return False
    
    def _install_from_zip(self, zip_path: Path, category: str) -> bool:
        """Install plugin from ZIP file."""
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            # Extract to temporary directory first
            temp_dir = self.plugins_dir / "temp" / zip_path.stem
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                zip_file.extractall(temp_dir)
                
                # Find plugin.json
                manifest_file = None
                for root, dirs, files in temp_dir.rglob("*"):
                    if "plugin.json" in files:
                        manifest_file = Path(root) / "plugin.json"
                        break
                
                if not manifest_file:
                    raise PluginError("No plugin.json found in ZIP file")
                
                # Load and validate manifest
                manifest = self._load_manifest(manifest_file)
                
                # Copy to final location
                final_dir = self.plugins_dir / category / manifest.name
                if final_dir.exists():
                    shutil.rmtree(final_dir)
                
                shutil.copytree(manifest_file.parent, final_dir)
                
                # Add to plugins
                plugin_info = PluginInfo(
                    manifest=manifest,
                    path=final_dir,
                    status=PluginStatus.INSTALLED
                )
                self.plugins[manifest.name] = plugin_info
                
                self.logger.info(f"Installed plugin: {manifest.name}")
                return True
                
            finally:
                # Cleanup temp directory
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _install_from_directory(self, source_dir: Path, category: str) -> bool:
        """Install plugin from directory."""
        manifest_file = source_dir / "plugin.json"
        if not manifest_file.exists():
            raise PluginError("No plugin.json found in directory")
        
        # Load and validate manifest
        manifest = self._load_manifest(manifest_file)
        
        # Copy to final location
        final_dir = self.plugins_dir / category / manifest.name
        if final_dir.exists():
            shutil.rmtree(final_dir)
        
        shutil.copytree(source_dir, final_dir)
        
        # Add to plugins
        plugin_info = PluginInfo(
            manifest=manifest,
            path=final_dir,
            status=PluginStatus.INSTALLED
        )
        self.plugins[manifest.name] = plugin_info
        
        self.logger.info(f"Installed plugin: {manifest.name}")
        return True
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """Uninstall a plugin."""
        if plugin_name not in self.plugins:
            raise PluginError(f"Plugin not found: {plugin_name}")
        
        plugin_info = self.plugins[plugin_name]
        
        try:
            # Unload if loaded
            if plugin_info.status == PluginStatus.ENABLED:
                self.unload_plugin(plugin_name)
            
            # Remove plugin directory
            shutil.rmtree(plugin_info.path)
            
            # Remove from plugins dict
            del self.plugins[plugin_name]
            
            # Remove settings
            if plugin_name in self.plugin_settings:
                del self.plugin_settings[plugin_name]
                self._save_plugin_settings()
            
            self.logger.info(f"Uninstalled plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall plugin {plugin_name}: {e}")
            return False
    
    def update_plugin_settings(self, plugin_name: str, settings: Dict[str, Any]) -> None:
        """Update plugin settings."""
        self.plugin_settings[plugin_name] = settings
        self._save_plugin_settings()

        # Update loaded plugin settings
        if plugin_name in self.plugins:
            plugin_info = self.plugins[plugin_name]
            if plugin_info.instance:
                plugin_info.instance.settings.update(settings)
                plugin_info.settings = settings

    # Phase 3: Marketplace Integration
    def search_marketplace(self, query: str = "", **filters) -> List[Any]:
        """Search plugins in the marketplace."""
        return self.marketplace.search_plugins(query, **filters)

    def get_featured_plugins(self) -> List[Any]:
        """Get featured plugins from marketplace."""
        return self.marketplace.get_featured_plugins()

    def install_from_marketplace(self, plugin_name: str) -> bool:
        """Install plugin from marketplace."""
        try:
            # Download plugin
            download_path = self.marketplace.download_plugin(plugin_name, self.plugins_dir / "downloads")

            # Install plugin
            return self.install_plugin(download_path, "community")

        except Exception as e:
            self.logger.error(f"Failed to install from marketplace: {e}")
            return False

    def rate_plugin(self, plugin_name: str, rating: float, review: str, user_id: str) -> bool:
        """Rate and review a plugin."""
        return self.marketplace.submit_rating(plugin_name, rating, review, user_id)

    def get_plugin_recommendations(self) -> List[Any]:
        """Get plugin recommendations based on installed plugins."""
        installed_plugins = list(self.plugins.keys())
        return self.marketplace.get_plugin_recommendations(installed_plugins)

    # Phase 3: Hot Swap Functionality
    def enable_hot_swap(self) -> None:
        """Enable hot swap monitoring."""
        self.hot_swap_manager.start_watching()

    def disable_hot_swap(self) -> None:
        """Disable hot swap monitoring."""
        self.hot_swap_manager.stop_watching()

    def hot_reload_plugin(self, plugin_name: str) -> bool:
        """Hot reload a plugin without restart."""
        return self.hot_swap_manager.hot_reload_plugin(plugin_name)

    def check_for_updates(self) -> Dict[str, Dict[str, Any]]:
        """Check for plugin updates."""
        return self.update_manager.check_for_updates()

    def update_plugin(self, plugin_name: str, version: str = "latest") -> bool:
        """Update plugin to specified version."""
        return self.update_manager.update_plugin(plugin_name, version)

    # Phase 3: Advanced Dependency Management
    def install_plugin_with_dependencies(self, plugin_path: Path, category: str = "local") -> Dict[str, Any]:
        """Install plugin with automatic dependency resolution."""
        try:
            # Load plugin manifest
            manifest_file = plugin_path / "plugin.json"
            if not manifest_file.exists():
                raise FlashGenieError("Plugin manifest not found")

            manifest = self._load_manifest(manifest_file)

            # Prepare environment and install dependencies
            env_result = self.dependency_manager.prepare_plugin_environment(manifest)

            if not env_result["success"]:
                return env_result

            # Install plugin
            success = self.install_plugin(plugin_path, category)

            return {
                "success": success,
                "plugin_installed": success,
                "environment_prepared": env_result["success"],
                "dependencies_installed": env_result["dependencies_installed"],
                "conflicts_resolved": env_result.get("conflicts_resolved", 0)
            }

        except Exception as e:
            self.logger.error(f"Failed to install plugin with dependencies: {e}")
            return {"success": False, "error": str(e)}

    def uninstall_plugin_with_cleanup(self, plugin_name: str) -> Dict[str, Any]:
        """Uninstall plugin and cleanup unused dependencies."""
        try:
            # Uninstall plugin
            success = self.uninstall_plugin(plugin_name)

            if success:
                # Cleanup environment
                cleanup_result = self.dependency_manager.cleanup_plugin_environment(plugin_name)
                return {
                    "success": True,
                    "plugin_uninstalled": True,
                    "environment_cleaned": cleanup_result["success"],
                    "unused_dependencies_removed": cleanup_result["unused_dependencies_found"]
                }
            else:
                return {"success": False, "error": "Plugin uninstallation failed"}

        except Exception as e:
            self.logger.error(f"Failed to uninstall plugin with cleanup: {e}")
            return {"success": False, "error": str(e)}

    def get_dependency_info(self, plugin_name: str) -> Dict[str, Any]:
        """Get dependency information for a plugin."""
        return self.dependency_manager.resolver.get_dependency_tree(plugin_name)

    # Phase 3: Enhanced Plugin Information
    def get_comprehensive_plugin_info(self, plugin_name: str) -> Dict[str, Any]:
        """Get comprehensive plugin information including marketplace data."""
        # Get basic plugin info
        basic_info = {}
        if plugin_name in self.plugins:
            plugin_info = self.plugins[plugin_name]
            basic_info = {
                "name": plugin_info.manifest.name,
                "version": plugin_info.manifest.version,
                "description": plugin_info.manifest.description,
                "author": plugin_info.manifest.author,
                "type": plugin_info.manifest.plugin_type.value,
                "status": plugin_info.status.value,
                "permissions": [p.value for p in plugin_info.manifest.permissions],
                "dependencies": plugin_info.manifest.dependencies,
                "settings": plugin_info.settings
            }

        # Get marketplace info
        marketplace_info = self.marketplace.get_plugin_details(plugin_name)
        if marketplace_info:
            basic_info.update({
                "marketplace_rating": marketplace_info.stats.average_rating,
                "downloads": marketplace_info.stats.downloads,
                "categories": [c.value for c in marketplace_info.categories],
                "price": marketplace_info.price,
                "verified": marketplace_info.verified,
                "featured": marketplace_info.featured
            })

        # Get dependency info
        dependency_info = self.get_dependency_info(plugin_name)
        basic_info["dependency_tree"] = dependency_info

        return basic_info

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "plugin_manager": {
                "total_plugins": len(self.plugins),
                "enabled_plugins": len([p for p in self.plugins.values() if p.status == PluginStatus.ENABLED]),
                "plugin_directories": [str(d) for d in [self.plugins_dir / cat for cat in ["official", "community", "local", "development"]]]
            },
            "marketplace": self.marketplace.get_marketplace_stats(),
            "hot_swap": self.hot_swap_manager.get_hot_swap_status(),
            "dependencies": self.dependency_manager.get_system_dependency_status()
        }
