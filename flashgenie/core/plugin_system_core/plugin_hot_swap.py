"""
FlashGenie Hot-Swappable Plugin System

Enables dynamic plugin loading, unloading, and updating without
requiring application restart.
"""

import threading
import time
import importlib
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import logging
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    Observer = None
    FileSystemEventHandler = None
    WATCHDOG_AVAILABLE = False

from .plugin_system import BasePlugin, PluginManifest, PluginInfo, PluginStatus
from flashgenie.utils.exceptions import FlashGenieError

# Forward reference to avoid circular import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .plugin_manager import PluginManager


class PluginWatcher(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):
    """File system watcher for plugin changes."""
    
    def __init__(self, hot_swap_manager: 'HotSwapManager'):
        """Initialize plugin watcher."""
        self.hot_swap_manager = hot_swap_manager
        self.logger = logging.getLogger("plugin_watcher")
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Check if it's a plugin file
        if file_path.name in ["plugin.json", "__init__.py"]:
            plugin_dir = file_path.parent
            self.logger.info(f"Plugin file modified: {file_path}")
            
            # Schedule hot reload
            self.hot_swap_manager.schedule_reload(plugin_dir)
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            plugin_dir = Path(event.src_path)
            manifest_file = plugin_dir / "plugin.json"
            
            # Check if new plugin directory with manifest
            if manifest_file.exists():
                self.logger.info(f"New plugin detected: {plugin_dir}")
                self.hot_swap_manager.schedule_install(plugin_dir)
    
    def on_deleted(self, event):
        """Handle file deletion events."""
        if event.is_directory:
            plugin_dir = Path(event.src_path)
            self.logger.info(f"Plugin directory deleted: {plugin_dir}")
            self.hot_swap_manager.schedule_uninstall(plugin_dir.name)


class HotSwapManager:
    """Manages hot-swappable plugin operations."""
    
    def __init__(self, plugin_manager: 'PluginManager'):
        """Initialize hot swap manager."""
        self.plugin_manager = plugin_manager
        self.logger = logging.getLogger("hot_swap_manager")
        
        # Hot swap configuration
        self.enabled = True
        self.watch_directories = [plugin_manager.plugins_dir]
        self.reload_delay = 2.0  # Seconds to wait before reloading
        
        # State management
        self.pending_operations: Dict[str, Dict[str, Any]] = {}
        self.operation_lock = threading.Lock()
        self.reload_timer: Optional[threading.Timer] = None
        
        # File system watcher
        self.observer: Optional[Observer] = None
        self.watcher = PluginWatcher(self)
        
        # Plugin state backup for rollback
        self.plugin_backups: Dict[str, Dict[str, Any]] = {}
        
        # Event callbacks
        self.callbacks: Dict[str, List[Callable]] = {
            "before_reload": [],
            "after_reload": [],
            "reload_failed": [],
            "plugin_updated": [],
            "plugin_installed": [],
            "plugin_uninstalled": []
        }
    
    def start_watching(self) -> None:
        """Start watching plugin directories for changes."""
        if not self.enabled or self.observer or not WATCHDOG_AVAILABLE:
            if not WATCHDOG_AVAILABLE:
                self.logger.warning("Watchdog not available, hot swap monitoring disabled")
            return

        self.observer = Observer()

        for watch_dir in self.watch_directories:
            if watch_dir.exists():
                self.observer.schedule(self.watcher, str(watch_dir), recursive=True)
                self.logger.info(f"Watching plugin directory: {watch_dir}")

        self.observer.start()
        self.logger.info("Hot swap monitoring started")
    
    def stop_watching(self) -> None:
        """Stop watching plugin directories."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.logger.info("Hot swap monitoring stopped")
    
    def schedule_reload(self, plugin_dir: Path) -> None:
        """Schedule a plugin reload after a delay."""
        plugin_name = plugin_dir.name
        
        with self.operation_lock:
            # Cancel existing timer
            if self.reload_timer:
                self.reload_timer.cancel()
            
            # Schedule new reload
            self.pending_operations[plugin_name] = {
                "operation": "reload",
                "plugin_dir": plugin_dir,
                "scheduled_at": datetime.now()
            }
            
            # Start timer
            self.reload_timer = threading.Timer(self.reload_delay, self._execute_pending_operations)
            self.reload_timer.start()
            
            self.logger.info(f"Scheduled reload for plugin: {plugin_name}")
    
    def schedule_install(self, plugin_dir: Path) -> None:
        """Schedule a plugin installation."""
        plugin_name = plugin_dir.name
        
        with self.operation_lock:
            self.pending_operations[plugin_name] = {
                "operation": "install",
                "plugin_dir": plugin_dir,
                "scheduled_at": datetime.now()
            }
            
            # Execute immediately for installs
            threading.Thread(target=self._execute_pending_operations, daemon=True).start()
    
    def schedule_uninstall(self, plugin_name: str) -> None:
        """Schedule a plugin uninstallation."""
        with self.operation_lock:
            self.pending_operations[plugin_name] = {
                "operation": "uninstall",
                "plugin_name": plugin_name,
                "scheduled_at": datetime.now()
            }
            
            # Execute immediately for uninstalls
            threading.Thread(target=self._execute_pending_operations, daemon=True).start()
    
    def hot_reload_plugin(self, plugin_name: str) -> bool:
        """Perform hot reload of a specific plugin."""
        self.logger.info(f"Hot reloading plugin: {plugin_name}")
        
        try:
            # Backup current state
            self._backup_plugin_state(plugin_name)
            
            # Notify callbacks
            self._trigger_callbacks("before_reload", plugin_name)
            
            # Get plugin info
            plugin_info = self.plugin_manager.plugins.get(plugin_name)
            if not plugin_info:
                raise FlashGenieError(f"Plugin not found: {plugin_name}")
            
            was_enabled = plugin_info.status == PluginStatus.ENABLED
            
            # Unload plugin if loaded
            if was_enabled:
                if not self.plugin_manager.unload_plugin(plugin_name):
                    raise FlashGenieError(f"Failed to unload plugin: {plugin_name}")
            
            # Clear module cache
            self._clear_plugin_module_cache(plugin_name)
            
            # Reload manifest
            manifest_file = plugin_info.path / "plugin.json"
            if manifest_file.exists():
                new_manifest = self.plugin_manager._load_manifest(manifest_file)
                plugin_info.manifest = new_manifest
            
            # Reload plugin if it was enabled
            if was_enabled:
                if not self.plugin_manager.load_plugin(plugin_name):
                    # Rollback on failure
                    self._rollback_plugin_state(plugin_name)
                    raise FlashGenieError(f"Failed to reload plugin: {plugin_name}")
            
            # Clear backup on success
            self._clear_plugin_backup(plugin_name)
            
            # Notify callbacks
            self._trigger_callbacks("after_reload", plugin_name)
            self._trigger_callbacks("plugin_updated", plugin_name)
            
            self.logger.info(f"Successfully hot reloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Hot reload failed for {plugin_name}: {e}")
            
            # Attempt rollback
            try:
                self._rollback_plugin_state(plugin_name)
            except Exception as rollback_error:
                self.logger.error(f"Rollback failed for {plugin_name}: {rollback_error}")
            
            # Notify callbacks
            self._trigger_callbacks("reload_failed", plugin_name, error=str(e))
            
            return False
    
    def hot_install_plugin(self, plugin_dir: Path) -> bool:
        """Perform hot installation of a new plugin."""
        plugin_name = plugin_dir.name
        self.logger.info(f"Hot installing plugin: {plugin_name}")
        
        try:
            # Install plugin
            if self.plugin_manager.install_plugin(plugin_dir, "local"):
                # Discover and load
                self.plugin_manager.discover_plugins()
                
                # Notify callbacks
                self._trigger_callbacks("plugin_installed", plugin_name)
                
                self.logger.info(f"Successfully hot installed plugin: {plugin_name}")
                return True
            else:
                raise FlashGenieError("Installation failed")
                
        except Exception as e:
            self.logger.error(f"Hot install failed for {plugin_name}: {e}")
            return False
    
    def hot_uninstall_plugin(self, plugin_name: str) -> bool:
        """Perform hot uninstallation of a plugin."""
        self.logger.info(f"Hot uninstalling plugin: {plugin_name}")
        
        try:
            # Uninstall plugin
            if self.plugin_manager.uninstall_plugin(plugin_name):
                # Clear module cache
                self._clear_plugin_module_cache(plugin_name)
                
                # Notify callbacks
                self._trigger_callbacks("plugin_uninstalled", plugin_name)
                
                self.logger.info(f"Successfully hot uninstalled plugin: {plugin_name}")
                return True
            else:
                raise FlashGenieError("Uninstallation failed")
                
        except Exception as e:
            self.logger.error(f"Hot uninstall failed for {plugin_name}: {e}")
            return False
    
    def add_callback(self, event: str, callback: Callable) -> None:
        """Add callback for hot swap events."""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def remove_callback(self, event: str, callback: Callable) -> None:
        """Remove callback for hot swap events."""
        if event in self.callbacks and callback in self.callbacks[event]:
            self.callbacks[event].remove(callback)
    
    def get_hot_swap_status(self) -> Dict[str, Any]:
        """Get current hot swap system status."""
        return {
            "enabled": self.enabled,
            "watching": self.observer is not None,
            "watch_directories": [str(d) for d in self.watch_directories],
            "pending_operations": len(self.pending_operations),
            "reload_delay": self.reload_delay,
            "active_backups": len(self.plugin_backups)
        }
    
    def _execute_pending_operations(self) -> None:
        """Execute all pending hot swap operations."""
        with self.operation_lock:
            operations = list(self.pending_operations.items())
            self.pending_operations.clear()
        
        for plugin_name, operation_data in operations:
            operation = operation_data["operation"]
            
            try:
                if operation == "reload":
                    self.hot_reload_plugin(plugin_name)
                elif operation == "install":
                    self.hot_install_plugin(operation_data["plugin_dir"])
                elif operation == "uninstall":
                    self.hot_uninstall_plugin(plugin_name)
                
            except Exception as e:
                self.logger.error(f"Failed to execute {operation} for {plugin_name}: {e}")
    
    def _backup_plugin_state(self, plugin_name: str) -> None:
        """Backup plugin state for rollback."""
        plugin_info = self.plugin_manager.plugins.get(plugin_name)
        if plugin_info:
            self.plugin_backups[plugin_name] = {
                "status": plugin_info.status,
                "instance": plugin_info.instance,
                "settings": plugin_info.settings.copy(),
                "error_message": plugin_info.error_message,
                "loaded_at": plugin_info.loaded_at
            }
    
    def _rollback_plugin_state(self, plugin_name: str) -> None:
        """Rollback plugin to previous state."""
        if plugin_name not in self.plugin_backups:
            return
        
        backup = self.plugin_backups[plugin_name]
        plugin_info = self.plugin_manager.plugins.get(plugin_name)
        
        if plugin_info:
            plugin_info.status = backup["status"]
            plugin_info.instance = backup["instance"]
            plugin_info.settings = backup["settings"]
            plugin_info.error_message = backup["error_message"]
            plugin_info.loaded_at = backup["loaded_at"]
            
            self.logger.info(f"Rolled back plugin state: {plugin_name}")
    
    def _clear_plugin_backup(self, plugin_name: str) -> None:
        """Clear plugin backup after successful operation."""
        if plugin_name in self.plugin_backups:
            del self.plugin_backups[plugin_name]
    
    def _clear_plugin_module_cache(self, plugin_name: str) -> None:
        """Clear Python module cache for plugin."""
        # Find and remove plugin modules from sys.modules
        modules_to_remove = []
        
        for module_name in sys.modules:
            if module_name.startswith(f"plugin_{plugin_name}") or module_name == plugin_name:
                modules_to_remove.append(module_name)
        
        for module_name in modules_to_remove:
            del sys.modules[module_name]
            self.logger.debug(f"Cleared module cache: {module_name}")
    
    def _trigger_callbacks(self, event: str, plugin_name: str, **kwargs) -> None:
        """Trigger callbacks for hot swap events."""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(plugin_name, **kwargs)
                except Exception as e:
                    self.logger.error(f"Callback error for {event}: {e}")


class PluginUpdateManager:
    """Manages plugin updates and version compatibility."""
    
    def __init__(self, plugin_manager: 'PluginManager', hot_swap_manager: HotSwapManager):
        """Initialize update manager."""
        self.plugin_manager = plugin_manager
        self.hot_swap_manager = hot_swap_manager
        self.logger = logging.getLogger("plugin_update_manager")
    
    def check_for_updates(self) -> Dict[str, Dict[str, Any]]:
        """Check for available plugin updates."""
        updates = {}
        
        for plugin_name, plugin_info in self.plugin_manager.plugins.items():
            # In a real implementation, this would check against marketplace
            # For now, simulate update availability
            current_version = plugin_info.manifest.version
            
            # Simulate available update
            if plugin_name in ["dark-theme", "ai-content-generator"]:
                updates[plugin_name] = {
                    "current_version": current_version,
                    "available_version": "1.1.0",
                    "update_size": "2.5 MB",
                    "changelog": "Bug fixes and performance improvements",
                    "compatibility": "compatible",
                    "security_update": False
                }
        
        return updates
    
    def update_plugin(self, plugin_name: str, version: str = "latest") -> bool:
        """Update a plugin to specified version."""
        self.logger.info(f"Updating plugin {plugin_name} to {version}")
        
        try:
            # In a real implementation, this would download and install the update
            # For now, simulate the update process
            
            # Backup current plugin
            self.hot_swap_manager._backup_plugin_state(plugin_name)
            
            # Simulate update
            time.sleep(1)  # Simulate download time
            
            # Hot reload with new version
            if self.hot_swap_manager.hot_reload_plugin(plugin_name):
                self.logger.info(f"Successfully updated plugin: {plugin_name}")
                return True
            else:
                raise FlashGenieError("Hot reload failed after update")
                
        except Exception as e:
            self.logger.error(f"Plugin update failed for {plugin_name}: {e}")
            
            # Attempt rollback
            try:
                self.hot_swap_manager._rollback_plugin_state(plugin_name)
            except Exception:
                pass
            
            return False
    
    def batch_update_plugins(self, plugin_names: List[str]) -> Dict[str, bool]:
        """Update multiple plugins in batch."""
        results = {}
        
        for plugin_name in plugin_names:
            results[plugin_name] = self.update_plugin(plugin_name)
        
        return results
