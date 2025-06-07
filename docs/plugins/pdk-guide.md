# Plugin Development Kit (PDK) Guide

The FlashGenie Plugin Development Kit (PDK) provides comprehensive tools for creating, testing, validating, and packaging plugins. This guide covers all PDK features and workflows.

## Overview

The PDK streamlines plugin development with:
- **Scaffolding**: Generate plugin templates
- **Validation**: Check plugin structure and code quality
- **Testing**: Run comprehensive plugin tests
- **Packaging**: Create distribution-ready packages
- **Development Tools**: Debug and optimize plugins

## Getting Started

### Installation

The PDK is included with FlashGenie:

```bash
# Verify PDK installation
python -m flashgenie pdk --version

# Get help
python -m flashgenie pdk --help
```

### Initialize Development Environment

```python
from flashgenie.core import PluginDevelopmentKit
from flashgenie.core.plugin_system import PluginType

# Create PDK instance
pdk = PluginDevelopmentKit("./my-plugins")

# Check workspace info
workspace_info = pdk.get_workspace_info()
print(f"Workspace: {workspace_info['workspace_path']}")
print(f"Plugins: {workspace_info['total_plugins']}")
```

## Plugin Scaffolding

### Creating New Plugins

Generate a complete plugin structure:

```python
# Create importer plugin
plugin_path = pdk.create_plugin_scaffold(
    plugin_name="csv-importer",
    plugin_type=PluginType.IMPORTER,
    author="Your Name"
)

# Create theme plugin
plugin_path = pdk.create_plugin_scaffold(
    plugin_name="dark-theme",
    plugin_type=PluginType.THEME,
    author="Your Name"
)
```

### CLI Usage

```bash
# Create plugin via CLI
python -m flashgenie pdk create \
    --name "my-plugin" \
    --type "importer" \
    --author "Your Name" \
    --output "./plugins"

# List available plugin types
python -m flashgenie pdk types
```

### Generated Structure

The scaffolder creates this structure:

```
my-plugin/
├── plugin.json              # Plugin manifest
├── __init__.py              # Main plugin code
├── README.md                # Documentation
├── test_plugin.py           # Unit tests
├── CHANGELOG.md             # Version history
├── LICENSE                  # License file
├── requirements.txt         # Dependencies
├── assets/                  # Plugin assets
│   └── icon.png
└── docs/                    # Additional docs
    └── usage.md
```

## Plugin Validation

### Comprehensive Validation

```python
# Validate plugin structure and code
validation_results = pdk.validate_plugin(plugin_path)

if validation_results["valid"]:
    print("✅ Plugin is valid!")
else:
    print("❌ Validation errors:")
    for error in validation_results["errors"]:
        print(f"  - {error}")
    
    print("⚠️ Warnings:")
    for warning in validation_results["warnings"]:
        print(f"  - {warning}")
    
    print("💡 Suggestions:")
    for suggestion in validation_results["suggestions"]:
        print(f"  - {suggestion}")
```

### CLI Validation

```bash
# Validate plugin
python -m flashgenie pdk validate --path ./my-plugin

# Validate with detailed output
python -m flashgenie pdk validate --path ./my-plugin --verbose

# Validate multiple plugins
python -m flashgenie pdk validate --path ./plugins --recursive
```

### Validation Checks

The validator checks:

**Structure Validation:**
- Required files (plugin.json, __init__.py)
- Recommended files (README.md, tests)
- File organization

**Manifest Validation:**
- Required fields
- Version format
- Plugin type validity
- Permission requests
- Dependency format

**Code Validation:**
- Python syntax
- Import statements
- Security patterns
- Coding standards

**Security Validation:**
- Dangerous operations
- Hardcoded secrets
- Permission usage
- Safe practices

## Plugin Testing

### Test Modes

The PDK provides three test modes:

```python
# Basic tests (structure, loading, manifest)
basic_results = pdk.test_plugin(plugin_path, test_mode="basic")

# Detailed tests (initialization, settings, errors)
detailed_results = pdk.test_plugin(plugin_path, test_mode="detailed")

# Comprehensive tests (performance, security, integration)
comprehensive_results = pdk.test_plugin(plugin_path, test_mode="comprehensive")
```

### CLI Testing

```bash
# Run basic tests
python -m flashgenie pdk test --path ./my-plugin

# Run comprehensive tests
python -m flashgenie pdk test --path ./my-plugin --mode comprehensive

# Run tests with coverage
python -m flashgenie pdk test --path ./my-plugin --coverage

# Run specific test categories
python -m flashgenie pdk test --path ./my-plugin --categories security,performance
```

### Test Results

```python
# Analyze test results
print(f"Tests run: {results['tests_run']}")
print(f"Passed: {results['tests_passed']}")
print(f"Failed: {results['tests_failed']}")

if results['performance']:
    print(f"Load time: {results['performance']['load_time']:.3f}s")
    print(f"Memory used: {results['performance']['memory_used'] / 1024 / 1024:.2f}MB")

# Get detailed summary
summary = pdk.tester.get_test_summary(results)
print(summary)
```

### Custom Tests

Add custom tests to your plugin:

```python
# test_plugin.py
import unittest
from your_plugin import YourPlugin

class TestYourPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = YourPlugin()
        self.plugin.initialize()
    
    def test_plugin_functionality(self):
        """Test core plugin functionality."""
        result = self.plugin.some_method()
        self.assertTrue(result)
    
    def test_error_handling(self):
        """Test error handling."""
        with self.assertRaises(ValueError):
            self.plugin.invalid_operation()
    
    def test_performance(self):
        """Test performance requirements."""
        import time
        start = time.time()
        self.plugin.heavy_operation()
        duration = time.time() - start
        self.assertLess(duration, 1.0)  # Should complete in < 1s

if __name__ == '__main__':
    unittest.main()
```

## Plugin Packaging

### Creating Packages

```python
# Package plugin for distribution
package_path = pdk.package_plugin(plugin_path)
print(f"Package created: {package_path}")

# Package with custom output directory
package_path = pdk.package_plugin(
    plugin_path, 
    output_dir=Path("./dist")
)

# Get packaging summary
summary = pdk.packager.get_packaging_summary(package_path)
print(summary)
```

### CLI Packaging

```bash
# Package plugin
python -m flashgenie pdk package --path ./my-plugin

# Package to specific directory
python -m flashgenie pdk package --path ./my-plugin --output ./dist

# Package with exclusions
python -m flashgenie pdk package --path ./my-plugin --exclude "*.pyc,__pycache__"
```

### Package Contents

Packages include:
- All plugin files
- Manifest and metadata
- Documentation
- Assets and resources
- Dependency information

Excluded by default:
- Version control files (.git, .svn)
- IDE files (.vscode, .idea)
- Python cache (__pycache__, *.pyc)
- Temporary files (*.tmp, *.log)
- Development files (.env, test_data)

## Development Workflow

### Complete Development Cycle

```python
# 1. Create plugin
plugin_path = pdk.create_plugin_scaffold(
    "awesome-plugin", PluginType.INTEGRATION, "Developer"
)

# 2. Develop plugin code
# ... edit files ...

# 3. Validate during development
validation = pdk.validate_plugin(plugin_path)
if not validation["valid"]:
    print("Fix validation errors before continuing")

# 4. Test plugin
test_results = pdk.test_plugin(plugin_path, "detailed")
if not test_results["success"]:
    print("Fix test failures before packaging")

# 5. Package for distribution
package_path = pdk.package_plugin(plugin_path)

# 6. Install for testing
pdk.install_plugin_for_testing(plugin_path)
```

### CLI Workflow

```bash
# Complete workflow via CLI
python -m flashgenie pdk create --name "my-plugin" --type "importer"
cd my-plugin

# Edit plugin files...

python -m flashgenie pdk validate --path .
python -m flashgenie pdk test --path . --mode comprehensive
python -m flashgenie pdk package --path .

# Install for testing
python -m flashgenie plugins install ./my-plugin-1.0.0.zip
```

## Advanced Features

### Plugin Templates

Get plugin templates for different types:

```python
# Get template information
template = pdk.get_plugin_template(PluginType.IMPORTER)
print(f"Description: {template['description']}")
print(f"Required methods: {template['required_methods']}")
print(f"Permissions: {template['permissions']}")
```

### Development Guidelines

```python
# Get development guidelines
guidelines = pdk.get_development_guidelines()
print("File structure:", guidelines["file_structure"])
print("Coding standards:", guidelines["coding_standards"])
print("Security:", guidelines["security"])
```

### Workspace Management

```python
# Get workspace information
workspace_info = pdk.get_workspace_info()
print(f"Valid plugins: {workspace_info['valid_plugins']}")
print(f"Invalid plugins: {workspace_info['invalid_plugins']}")

# Clean up workspace
cleanup_results = pdk.cleanup_workspace()
print(f"Files removed: {cleanup_results['files_removed']}")
print(f"Space freed: {cleanup_results['space_freed']} bytes")
```

## Configuration

### PDK Settings

Configure PDK behavior:

```python
# Configure PDK
pdk_config = {
    "validation": {
        "strict_mode": True,
        "check_security": True,
        "require_tests": True
    },
    "testing": {
        "default_mode": "detailed",
        "timeout": 30,
        "coverage_threshold": 80
    },
    "packaging": {
        "compression_level": 6,
        "include_source": True,
        "sign_packages": False
    }
}
```

### Environment Variables

```bash
# Set PDK environment variables
export FLASHGENIE_PDK_WORKSPACE="./plugins"
export FLASHGENIE_PDK_STRICT_VALIDATION="true"
export FLASHGENIE_PDK_TEST_TIMEOUT="60"
```

## Integration with IDEs

### VS Code Integration

Create `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Validate Plugin",
            "type": "shell",
            "command": "python",
            "args": ["-m", "flashgenie", "pdk", "validate", "--path", "."],
            "group": "build"
        },
        {
            "label": "Test Plugin",
            "type": "shell",
            "command": "python",
            "args": ["-m", "flashgenie", "pdk", "test", "--path", ".", "--mode", "comprehensive"],
            "group": "test"
        },
        {
            "label": "Package Plugin",
            "type": "shell",
            "command": "python",
            "args": ["-m", "flashgenie", "pdk", "package", "--path", "."],
            "group": "build"
        }
    ]
}
```

### PyCharm Integration

Create external tools for PDK commands in PyCharm settings.

## Troubleshooting

### Common Issues

**Validation Failures:**
```bash
# Check specific validation issues
python -m flashgenie pdk validate --path . --verbose --check security
```

**Test Failures:**
```bash
# Run tests with debug output
python -m flashgenie pdk test --path . --debug --verbose
```

**Packaging Issues:**
```bash
# Check package contents
python -m flashgenie pdk package --path . --dry-run --verbose
```

### Debug Mode

Enable debug mode for detailed output:

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run PDK operations with debug info
pdk = PluginDevelopmentKit("./plugins", debug=True)
```

## Best Practices

### Development
- Use version control from the start
- Write tests before implementing features
- Validate frequently during development
- Follow the plugin development guidelines

### Testing
- Test all plugin functionality
- Include edge cases and error conditions
- Test with different FlashGenie versions
- Verify performance requirements

### Documentation
- Write clear README files
- Document all public methods
- Include usage examples
- Provide troubleshooting guides

### Distribution
- Use semantic versioning
- Include comprehensive changelogs
- Test packages before distribution
- Provide installation instructions

## Next Steps

- [Plugin Security Guide](../developer-guides/security.md)
- [Plugin Performance Guide](../developer-guides/performance.md)
- [Plugin Marketplace Guide](../user-guides/marketplace.md)
- [Contributing to FlashGenie](../CONTRIBUTING.md)
