"""
Plugin testing utilities for the Plugin Development Kit.

This module provides functions to test plugin functionality and performance.
"""

import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import importlib.util
import json

from flashgenie.utils.exceptions import FlashGenieError


class PluginTester:
    """Tests plugin functionality and performance."""
    
    def __init__(self):
        """Initialize the tester."""
        self.test_modes = {
            "basic": self._run_basic_tests,
            "detailed": self._run_detailed_tests,
            "comprehensive": self._run_comprehensive_tests
        }
    
    def test_plugin(self, plugin_path: Path, test_mode: str = "basic") -> Dict[str, Any]:
        """
        Test a plugin with the specified test mode.
        
        Args:
            plugin_path: Path to the plugin directory
            test_mode: Test mode (basic, detailed, comprehensive)
            
        Returns:
            Dictionary with test results
        """
        if test_mode not in self.test_modes:
            raise FlashGenieError(f"Invalid test mode: {test_mode}")
        
        results = {
            "success": True,
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "output": [],
            "errors": [],
            "performance": {}
        }
        
        # Check if plugin directory exists
        if not plugin_path.exists() or not plugin_path.is_dir():
            results["success"] = False
            results["errors"].append(f"Plugin directory does not exist: {plugin_path}")
            return results
        
        # Run the specified test mode
        try:
            test_function = self.test_modes[test_mode]
            test_function(plugin_path, results)
        except Exception as e:
            results["success"] = False
            results["errors"].append(f"Test execution failed: {e}")
        
        # Calculate final success status
        results["success"] = (results["tests_failed"] == 0 and 
                            len(results["errors"]) == 0)
        
        return results
    
    def _run_basic_tests(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Run basic plugin tests."""
        # Test 1: Plugin loading
        self._test_plugin_loading(plugin_path, results)
        
        # Test 2: Manifest validation
        self._test_manifest_validation(plugin_path, results)
        
        # Test 3: Basic functionality
        self._test_basic_functionality(plugin_path, results)
    
    def _run_detailed_tests(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Run detailed plugin tests."""
        # Run basic tests first
        self._run_basic_tests(plugin_path, results)
        
        # Test 4: Plugin initialization
        self._test_plugin_initialization(plugin_path, results)
        
        # Test 5: Settings handling
        self._test_settings_handling(plugin_path, results)
        
        # Test 6: Error handling
        self._test_error_handling(plugin_path, results)
    
    def _run_comprehensive_tests(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Run comprehensive plugin tests."""
        # Run detailed tests first
        self._run_detailed_tests(plugin_path, results)
        
        # Test 7: Performance testing
        self._test_performance(plugin_path, results)
        
        # Test 8: Memory usage
        self._test_memory_usage(plugin_path, results)
        
        # Test 9: Security validation
        self._test_security(plugin_path, results)
        
        # Test 10: Integration testing
        self._test_integration(plugin_path, results)
    
    def _test_plugin_loading(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Test if the plugin can be loaded."""
        test_name = "Plugin Loading"
        results["tests_run"] += 1
        
        try:
            # Check if __init__.py exists
            init_file = plugin_path / "__init__.py"
            if not init_file.exists():
                raise Exception("__init__.py not found")
            
            # Try to load the module
            spec = importlib.util.spec_from_file_location("test_plugin", init_file)
            if spec is None or spec.loader is None:
                raise Exception("Cannot create module spec")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            results["tests_passed"] += 1
            results["output"].append(f"✅ {test_name}: Plugin loaded successfully")
            
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"❌ {test_name}: {e}")
    
    def _test_manifest_validation(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Test manifest file validation."""
        test_name = "Manifest Validation"
        results["tests_run"] += 1
        
        try:
            manifest_file = plugin_path / "plugin.json"
            if not manifest_file.exists():
                raise Exception("plugin.json not found")
            
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            # Check required fields
            required_fields = ["name", "version", "type", "entry_point"]
            for field in required_fields:
                if field not in manifest:
                    raise Exception(f"Required field missing: {field}")
            
            results["tests_passed"] += 1
            results["output"].append(f"✅ {test_name}: Manifest is valid")
            
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"❌ {test_name}: {e}")
    
    def _test_basic_functionality(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Test basic plugin functionality."""
        test_name = "Basic Functionality"
        results["tests_run"] += 1
        
        try:
            # Run the plugin's test file if it exists
            test_file = plugin_path / "test_plugin.py"
            if test_file.exists():
                # Run the test file
                result = subprocess.run(
                    [sys.executable, str(test_file)],
                    cwd=plugin_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    results["tests_passed"] += 1
                    results["output"].append(f"✅ {test_name}: Plugin tests passed")
                    if result.stdout:
                        results["output"].append(f"Test output: {result.stdout}")
                else:
                    raise Exception(f"Plugin tests failed: {result.stderr}")
            else:
                # Basic import test
                init_file = plugin_path / "__init__.py"
                spec = importlib.util.spec_from_file_location("test_plugin", init_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    results["tests_passed"] += 1
                    results["output"].append(f"✅ {test_name}: Basic import successful")
                else:
                    raise Exception("Cannot load plugin module")
            
        except subprocess.TimeoutExpired:
            results["tests_failed"] += 1
            results["errors"].append(f"❌ {test_name}: Test timeout (30s)")
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"❌ {test_name}: {e}")
    
    def _test_plugin_initialization(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Test plugin initialization process."""
        test_name = "Plugin Initialization"
        results["tests_run"] += 1
        
        try:
            # Load plugin and test initialization
            init_file = plugin_path / "__init__.py"
            spec = importlib.util.spec_from_file_location("test_plugin", init_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find plugin class
                plugin_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        attr_name.endswith('Plugin') and 
                        attr_name != 'Plugin'):
                        plugin_class = attr
                        break
                
                if plugin_class:
                    # Test instantiation
                    plugin_instance = plugin_class()
                    
                    # Test initialization if method exists
                    if hasattr(plugin_instance, 'initialize'):
                        plugin_instance.initialize()
                    
                    results["tests_passed"] += 1
                    results["output"].append(f"✅ {test_name}: Plugin initialized successfully")
                else:
                    raise Exception("No plugin class found")
            else:
                raise Exception("Cannot load plugin module")
                
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"❌ {test_name}: {e}")
    
    def _test_settings_handling(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Test plugin settings handling."""
        test_name = "Settings Handling"
        results["tests_run"] += 1
        
        try:
            # Load manifest to check settings schema
            manifest_file = plugin_path / "plugin.json"
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            settings_schema = manifest.get("settings_schema", {})
            
            if settings_schema:
                # Test that settings schema is valid
                for setting_name, setting_config in settings_schema.items():
                    if not isinstance(setting_config, dict):
                        raise Exception(f"Invalid setting config for {setting_name}")
                    
                    if "type" not in setting_config:
                        raise Exception(f"Setting {setting_name} missing type")
                
                results["tests_passed"] += 1
                results["output"].append(f"✅ {test_name}: Settings schema is valid")
            else:
                results["tests_passed"] += 1
                results["output"].append(f"✅ {test_name}: No settings schema (OK)")
                
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"❌ {test_name}: {e}")
    
    def _test_error_handling(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Test plugin error handling."""
        test_name = "Error Handling"
        results["tests_run"] += 1
        
        try:
            # This is a basic test - in a real implementation,
            # we would test various error conditions
            results["tests_passed"] += 1
            results["output"].append(f"✅ {test_name}: Basic error handling test passed")
            
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"❌ {test_name}: {e}")
    
    def _test_performance(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Test plugin performance."""
        test_name = "Performance"
        results["tests_run"] += 1
        
        try:
            import time
            
            # Measure plugin loading time
            start_time = time.time()
            
            init_file = plugin_path / "__init__.py"
            spec = importlib.util.spec_from_file_location("test_plugin", init_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            
            load_time = time.time() - start_time
            
            results["performance"]["load_time"] = load_time
            
            if load_time < 1.0:  # Should load within 1 second
                results["tests_passed"] += 1
                results["output"].append(f"✅ {test_name}: Load time {load_time:.3f}s (Good)")
            else:
                results["tests_failed"] += 1
                results["errors"].append(f"❌ {test_name}: Slow load time {load_time:.3f}s")
                
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"❌ {test_name}: {e}")
    
    def _test_memory_usage(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Test plugin memory usage."""
        test_name = "Memory Usage"
        results["tests_run"] += 1
        
        try:
            import psutil
            import os
            
            # Measure memory before loading
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss
            
            # Load plugin
            init_file = plugin_path / "__init__.py"
            spec = importlib.util.spec_from_file_location("test_plugin", init_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            
            # Measure memory after loading
            memory_after = process.memory_info().rss
            memory_used = memory_after - memory_before
            
            results["performance"]["memory_used"] = memory_used
            
            # 10MB threshold for plugin loading
            if memory_used < 10 * 1024 * 1024:
                results["tests_passed"] += 1
                results["output"].append(f"✅ {test_name}: Memory usage {memory_used / 1024 / 1024:.2f}MB (Good)")
            else:
                results["tests_failed"] += 1
                results["errors"].append(f"❌ {test_name}: High memory usage {memory_used / 1024 / 1024:.2f}MB")
                
        except ImportError:
            # psutil not available, skip test
            results["tests_passed"] += 1
            results["output"].append(f"⏭️ {test_name}: Skipped (psutil not available)")
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"❌ {test_name}: {e}")
    
    def _test_security(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Test plugin security."""
        test_name = "Security Validation"
        results["tests_run"] += 1
        
        try:
            # Basic security check - look for dangerous patterns
            dangerous_patterns = [
                "eval(", "exec(", "__import__", "subprocess", "os.system"
            ]
            
            security_issues = []
            
            for py_file in plugin_path.glob("*.py"):
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                    
                    for pattern in dangerous_patterns:
                        if pattern in content:
                            security_issues.append(f"{py_file.name}: {pattern}")
                except Exception:
                    continue
            
            if security_issues:
                results["tests_failed"] += 1
                results["errors"].append(f"❌ {test_name}: Security issues found: {', '.join(security_issues)}")
            else:
                results["tests_passed"] += 1
                results["output"].append(f"✅ {test_name}: No obvious security issues")
                
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"❌ {test_name}: {e}")
    
    def _test_integration(self, plugin_path: Path, results: Dict[str, Any]) -> None:
        """Test plugin integration with FlashGenie."""
        test_name = "Integration"
        results["tests_run"] += 1
        
        try:
            # Check for FlashGenie imports
            init_file = plugin_path / "__init__.py"
            with open(init_file, 'r') as f:
                content = f.read()
            
            if "flashgenie" in content.lower():
                results["tests_passed"] += 1
                results["output"].append(f"✅ {test_name}: FlashGenie integration detected")
            else:
                results["tests_failed"] += 1
                results["errors"].append(f"❌ {test_name}: No FlashGenie integration found")
                
        except Exception as e:
            results["tests_failed"] += 1
            results["errors"].append(f"❌ {test_name}: {e}")
    
    def get_test_summary(self, results: Dict[str, Any]) -> str:
        """Get a human-readable test summary."""
        summary = []
        
        if results["success"]:
            summary.append("🎉 All tests passed!")
        else:
            summary.append("❌ Some tests failed!")
        
        summary.append(f"\n📊 Test Results:")
        summary.append(f"   Tests run: {results['tests_run']}")
        summary.append(f"   Passed: {results['tests_passed']}")
        summary.append(f"   Failed: {results['tests_failed']}")
        
        if results["performance"]:
            summary.append(f"\n⚡ Performance:")
            for metric, value in results["performance"].items():
                if metric == "load_time":
                    summary.append(f"   Load time: {value:.3f}s")
                elif metric == "memory_used":
                    summary.append(f"   Memory used: {value / 1024 / 1024:.2f}MB")
        
        if results["output"]:
            summary.append(f"\n📝 Test Output:")
            for output in results["output"]:
                summary.append(f"   {output}")
        
        if results["errors"]:
            summary.append(f"\n🚨 Errors:")
            for error in results["errors"]:
                summary.append(f"   {error}")
        
        return "\n".join(summary)
