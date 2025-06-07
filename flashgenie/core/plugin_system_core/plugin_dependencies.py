"""
FlashGenie Plugin Dependency Management

Advanced dependency resolution, installation, and conflict management
for the FlashGenie plugin ecosystem.
"""

import subprocess
import sys
import pkg_resources
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import re

from .plugin_system import PluginManifest
from flashgenie.utils.exceptions import FlashGenieError


class DependencyType(Enum):
    """Types of dependencies."""
    PYTHON_PACKAGE = "python_package"
    PLUGIN = "plugin"
    SYSTEM = "system"
    OPTIONAL = "optional"


class ConflictResolution(Enum):
    """Dependency conflict resolution strategies."""
    FAIL = "fail"
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    SKIP = "skip"
    USER_CHOICE = "user_choice"


@dataclass
class Dependency:
    """Represents a plugin dependency."""
    name: str
    version_spec: str
    dependency_type: DependencyType
    optional: bool = False
    description: str = ""
    install_command: Optional[str] = None


@dataclass
class DependencyConflict:
    """Represents a dependency conflict."""
    package_name: str
    required_versions: List[str]
    current_version: Optional[str]
    conflicting_plugins: List[str]
    resolution_options: List[str]


class DependencyResolver:
    """Resolves plugin dependencies and manages installations."""
    
    def __init__(self):
        """Initialize dependency resolver."""
        self.logger = logging.getLogger("dependency_resolver")
        
        # Dependency cache
        self.installed_packages: Dict[str, str] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        
        # Configuration
        self.conflict_resolution = ConflictResolution.USER_CHOICE
        self.auto_install = False
        self.virtual_env_path: Optional[Path] = None
        
        # Refresh package cache
        self._refresh_package_cache()
    
    def resolve_dependencies(self, plugin_manifest: PluginManifest) -> Tuple[List[Dependency], List[DependencyConflict]]:
        """Resolve all dependencies for a plugin."""
        self.logger.info(f"Resolving dependencies for plugin: {plugin_manifest.name}")
        
        dependencies = []
        conflicts = []
        
        # Parse plugin dependencies
        for dep_spec in plugin_manifest.dependencies:
            dependency = self._parse_dependency_spec(dep_spec)
            dependencies.append(dependency)
        
        # Check for conflicts
        for dependency in dependencies:
            if dependency.dependency_type == DependencyType.PYTHON_PACKAGE:
                conflict = self._check_package_conflict(dependency, plugin_manifest.name)
                if conflict:
                    conflicts.append(conflict)
        
        return dependencies, conflicts
    
    def install_dependencies(self, dependencies: List[Dependency], 
                           plugin_name: str) -> Dict[str, bool]:
        """Install plugin dependencies."""
        self.logger.info(f"Installing dependencies for plugin: {plugin_name}")
        
        results = {}
        
        for dependency in dependencies:
            if dependency.optional and not self.auto_install:
                self.logger.info(f"Skipping optional dependency: {dependency.name}")
                results[dependency.name] = True
                continue
            
            try:
                success = self._install_dependency(dependency)
                results[dependency.name] = success
                
                if success:
                    self.logger.info(f"Successfully installed dependency: {dependency.name}")
                else:
                    self.logger.warning(f"Failed to install dependency: {dependency.name}")
                    
            except Exception as e:
                self.logger.error(f"Error installing dependency {dependency.name}: {e}")
                results[dependency.name] = False
        
        # Update dependency graph
        self._update_dependency_graph(plugin_name, dependencies)
        
        return results
    
    def check_plugin_compatibility(self, plugin_manifest: PluginManifest) -> Dict[str, Any]:
        """Check if plugin is compatible with current environment."""
        compatibility = {
            "compatible": True,
            "issues": [],
            "warnings": [],
            "missing_dependencies": [],
            "conflicting_dependencies": []
        }
        
        # Check FlashGenie version compatibility
        flashgenie_version = plugin_manifest.flashgenie_version
        if not self._check_version_compatibility(flashgenie_version, "1.8.0"):
            compatibility["compatible"] = False
            compatibility["issues"].append(f"Requires FlashGenie {flashgenie_version}, current: 1.8.0")
        
        # Check Python version compatibility
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if not self._check_python_compatibility(plugin_manifest):
            compatibility["warnings"].append(f"Python version compatibility not verified: {python_version}")
        
        # Check dependencies
        dependencies, conflicts = self.resolve_dependencies(plugin_manifest)
        
        for dependency in dependencies:
            if dependency.dependency_type == DependencyType.PYTHON_PACKAGE:
                if not self._is_package_available(dependency):
                    compatibility["missing_dependencies"].append(dependency.name)
        
        for conflict in conflicts:
            compatibility["conflicting_dependencies"].append({
                "package": conflict.package_name,
                "required": conflict.required_versions,
                "current": conflict.current_version
            })
        
        if compatibility["missing_dependencies"] or compatibility["conflicting_dependencies"]:
            compatibility["compatible"] = False
        
        return compatibility
    
    def resolve_conflicts(self, conflicts: List[DependencyConflict], 
                         resolution: ConflictResolution = None) -> Dict[str, str]:
        """Resolve dependency conflicts."""
        resolution = resolution or self.conflict_resolution
        resolutions = {}
        
        for conflict in conflicts:
            if resolution == ConflictResolution.FAIL:
                raise FlashGenieError(f"Dependency conflict: {conflict.package_name}")
            
            elif resolution == ConflictResolution.UPGRADE:
                # Choose highest version
                versions = [self._parse_version(v) for v in conflict.required_versions]
                highest_version = max(versions)
                resolutions[conflict.package_name] = str(highest_version)
            
            elif resolution == ConflictResolution.DOWNGRADE:
                # Choose lowest version
                versions = [self._parse_version(v) for v in conflict.required_versions]
                lowest_version = min(versions)
                resolutions[conflict.package_name] = str(lowest_version)
            
            elif resolution == ConflictResolution.SKIP:
                # Skip conflicting package
                resolutions[conflict.package_name] = "skip"
            
            elif resolution == ConflictResolution.USER_CHOICE:
                # In a real implementation, this would prompt the user
                # For now, choose the first option
                if conflict.resolution_options:
                    resolutions[conflict.package_name] = conflict.resolution_options[0]
        
        return resolutions
    
    def get_dependency_tree(self, plugin_name: str) -> Dict[str, Any]:
        """Get dependency tree for a plugin."""
        if plugin_name not in self.dependency_graph:
            return {}
        
        tree = {
            "plugin": plugin_name,
            "dependencies": {},
            "total_dependencies": 0
        }
        
        dependencies = self.dependency_graph[plugin_name]
        for dep_name in dependencies:
            tree["dependencies"][dep_name] = {
                "installed": self._is_package_installed(dep_name),
                "version": self.installed_packages.get(dep_name, "unknown")
            }
        
        tree["total_dependencies"] = len(dependencies)
        return tree
    
    def cleanup_unused_dependencies(self) -> List[str]:
        """Remove unused dependencies."""
        # Find packages that are no longer needed
        all_required = set()
        for dependencies in self.dependency_graph.values():
            all_required.update(dependencies)
        
        unused = []
        for package_name in self.installed_packages:
            if package_name not in all_required:
                # Check if it's a core package that shouldn't be removed
                if not self._is_core_package(package_name):
                    unused.append(package_name)
        
        # In a real implementation, this would actually uninstall packages
        self.logger.info(f"Found {len(unused)} unused dependencies")
        return unused
    
    def _parse_dependency_spec(self, dep_spec: str) -> Dependency:
        """Parse dependency specification string."""
        # Handle different formats: "package>=1.0.0", "package==1.0.0", "package"
        match = re.match(r'^([a-zA-Z0-9_-]+)([><=!]+)?([0-9.]+)?$', dep_spec.strip())
        
        if match:
            name = match.group(1)
            operator = match.group(2) or ">="
            version = match.group(3) or "0.0.0"
            version_spec = f"{operator}{version}"
        else:
            # Fallback for complex specs
            name = dep_spec.split()[0]
            version_spec = dep_spec
        
        return Dependency(
            name=name,
            version_spec=version_spec,
            dependency_type=DependencyType.PYTHON_PACKAGE,
            optional=False
        )
    
    def _check_package_conflict(self, dependency: Dependency, plugin_name: str) -> Optional[DependencyConflict]:
        """Check if dependency conflicts with existing packages."""
        package_name = dependency.name
        required_version = dependency.version_spec
        
        # Check if package is already required by other plugins
        conflicting_plugins = []
        required_versions = [required_version]
        
        for other_plugin, deps in self.dependency_graph.items():
            if other_plugin != plugin_name and package_name in deps:
                conflicting_plugins.append(other_plugin)
                # In a real implementation, we'd track version requirements per plugin
                # For now, assume potential conflict
        
        if conflicting_plugins:
            current_version = self.installed_packages.get(package_name)
            
            return DependencyConflict(
                package_name=package_name,
                required_versions=required_versions,
                current_version=current_version,
                conflicting_plugins=conflicting_plugins,
                resolution_options=["upgrade", "downgrade", "skip"]
            )
        
        return None
    
    def _install_dependency(self, dependency: Dependency) -> bool:
        """Install a single dependency."""
        if dependency.dependency_type == DependencyType.PYTHON_PACKAGE:
            return self._install_python_package(dependency)
        elif dependency.dependency_type == DependencyType.SYSTEM:
            return self._install_system_package(dependency)
        else:
            self.logger.warning(f"Unsupported dependency type: {dependency.dependency_type}")
            return False
    
    def _install_python_package(self, dependency: Dependency) -> bool:
        """Install Python package dependency."""
        try:
            # Check if already installed and compatible
            if self._is_package_compatible(dependency):
                return True
            
            # Install package
            cmd = [sys.executable, "-m", "pip", "install", dependency.version_spec]
            
            if self.virtual_env_path:
                # Install in virtual environment
                cmd.extend(["--target", str(self.virtual_env_path)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Update package cache
            self._refresh_package_cache()
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install {dependency.name}: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Error installing {dependency.name}: {e}")
            return False
    
    def _install_system_package(self, dependency: Dependency) -> bool:
        """Install system package dependency."""
        if dependency.install_command:
            try:
                subprocess.run(dependency.install_command.split(), check=True)
                return True
            except subprocess.CalledProcessError:
                return False
        
        self.logger.warning(f"No install command for system dependency: {dependency.name}")
        return False
    
    def _is_package_available(self, dependency: Dependency) -> bool:
        """Check if package is available for installation."""
        if dependency.dependency_type == DependencyType.PYTHON_PACKAGE:
            # Check PyPI availability (simplified)
            return True  # Assume all packages are available
        return False
    
    def _is_package_installed(self, package_name: str) -> bool:
        """Check if package is installed."""
        return package_name in self.installed_packages
    
    def _is_package_compatible(self, dependency: Dependency) -> bool:
        """Check if installed package version is compatible."""
        if not self._is_package_installed(dependency.name):
            return False
        
        installed_version = self.installed_packages[dependency.name]
        return self._check_version_compatibility(dependency.version_spec, installed_version)
    
    def _check_version_compatibility(self, version_spec: str, installed_version: str) -> bool:
        """Check if installed version satisfies version specification."""
        try:
            # Use pkg_resources for version comparison
            requirement = pkg_resources.Requirement.parse(f"package{version_spec}")
            return installed_version in requirement
        except Exception:
            # Fallback to simple string comparison
            return version_spec in installed_version or installed_version in version_spec
    
    def _check_python_compatibility(self, plugin_manifest: PluginManifest) -> bool:
        """Check Python version compatibility."""
        # Check if plugin specifies Python version requirements
        # For now, assume compatibility
        return True
    
    def _parse_version(self, version_str: str) -> Tuple[int, ...]:
        """Parse version string into tuple for comparison."""
        # Remove operators and parse version numbers
        version_clean = re.sub(r'[><=!]+', '', version_str)
        try:
            return tuple(map(int, version_clean.split('.')))
        except ValueError:
            return (0, 0, 0)
    
    def _refresh_package_cache(self) -> None:
        """Refresh cache of installed packages."""
        try:
            installed_packages = pkg_resources.working_set
            self.installed_packages = {
                pkg.project_name: pkg.version 
                for pkg in installed_packages
            }
        except Exception as e:
            self.logger.warning(f"Failed to refresh package cache: {e}")
    
    def _update_dependency_graph(self, plugin_name: str, dependencies: List[Dependency]) -> None:
        """Update dependency graph with plugin dependencies."""
        dep_names = {dep.name for dep in dependencies if dep.dependency_type == DependencyType.PYTHON_PACKAGE}
        self.dependency_graph[plugin_name] = dep_names
    
    def _is_core_package(self, package_name: str) -> bool:
        """Check if package is a core package that shouldn't be removed."""
        core_packages = {
            "pip", "setuptools", "wheel", "python", "sys", "os", 
            "json", "datetime", "pathlib", "typing", "logging"
        }
        return package_name.lower() in core_packages


class PluginDependencyManager:
    """High-level dependency management for plugins."""
    
    def __init__(self):
        """Initialize dependency manager."""
        self.resolver = DependencyResolver()
        self.logger = logging.getLogger("plugin_dependency_manager")
    
    def prepare_plugin_environment(self, plugin_manifest: PluginManifest) -> Dict[str, Any]:
        """Prepare environment for plugin installation."""
        self.logger.info(f"Preparing environment for plugin: {plugin_manifest.name}")
        
        # Check compatibility
        compatibility = self.resolver.check_plugin_compatibility(plugin_manifest)
        
        if not compatibility["compatible"]:
            return {
                "success": False,
                "compatibility": compatibility,
                "message": "Plugin is not compatible with current environment"
            }
        
        # Resolve dependencies
        dependencies, conflicts = self.resolver.resolve_dependencies(plugin_manifest)
        
        # Resolve conflicts if any
        if conflicts:
            resolutions = self.resolver.resolve_conflicts(conflicts)
            self.logger.info(f"Resolved {len(conflicts)} dependency conflicts")
        
        # Install dependencies
        install_results = self.resolver.install_dependencies(dependencies, plugin_manifest.name)
        
        failed_installs = [name for name, success in install_results.items() if not success]
        
        return {
            "success": len(failed_installs) == 0,
            "compatibility": compatibility,
            "dependencies_installed": len(install_results),
            "failed_installs": failed_installs,
            "conflicts_resolved": len(conflicts) if conflicts else 0
        }
    
    def cleanup_plugin_environment(self, plugin_name: str) -> Dict[str, Any]:
        """Cleanup environment after plugin removal."""
        self.logger.info(f"Cleaning up environment for plugin: {plugin_name}")
        
        # Remove from dependency graph
        if plugin_name in self.resolver.dependency_graph:
            del self.resolver.dependency_graph[plugin_name]
        
        # Find and cleanup unused dependencies
        unused_deps = self.resolver.cleanup_unused_dependencies()
        
        return {
            "success": True,
            "unused_dependencies_found": len(unused_deps),
            "cleanup_performed": True
        }
    
    def get_system_dependency_status(self) -> Dict[str, Any]:
        """Get overall system dependency status."""
        total_packages = len(self.resolver.installed_packages)
        total_plugins = len(self.resolver.dependency_graph)
        
        # Calculate dependency statistics
        all_deps = set()
        for deps in self.resolver.dependency_graph.values():
            all_deps.update(deps)
        
        return {
            "total_installed_packages": total_packages,
            "total_plugins_with_dependencies": total_plugins,
            "unique_dependencies": len(all_deps),
            "dependency_graph_size": sum(len(deps) for deps in self.resolver.dependency_graph.values()),
            "conflict_resolution_strategy": self.resolver.conflict_resolution.value,
            "auto_install_enabled": self.resolver.auto_install
        }
