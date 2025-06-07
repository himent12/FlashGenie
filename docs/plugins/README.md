# FlashGenie Plugin System Documentation

Welcome to the FlashGenie Plugin System! This comprehensive guide will help you understand, develop, and use plugins to extend FlashGenie's functionality.

## Table of Contents

1. [Plugin System Overview](#plugin-system-overview)
2. [Plugin Types](#plugin-types)
3. [Getting Started](#getting-started)
4. [Plugin Development Kit (PDK)](#plugin-development-kit-pdk)
5. [Plugin Marketplace](#plugin-marketplace)
6. [Best Practices](#best-practices)

## Plugin System Overview

FlashGenie's plugin system allows you to extend the application's functionality through modular components. Plugins can add new features, integrate with external services, customize the user interface, and enhance the learning experience.

### Key Features

- **Hot-swappable**: Install, enable, disable, and uninstall plugins without restarting
- **Secure**: Sandboxed execution with permission-based access control
- **Type-safe**: Strong typing and validation for plugin interfaces
- **Marketplace**: Discover and install plugins from the community
- **Development Kit**: Comprehensive tools for plugin development

## Plugin Types

FlashGenie supports seven main plugin types:

| Type | Description | Use Cases |
|------|-------------|-----------|
| **Importers** | Import flashcard data from external sources | CSV files, Anki decks, Quizlet sets |
| **Exporters** | Export flashcard data to various formats | PDF, HTML, mobile apps |
| **Themes** | Customize the visual appearance | Dark mode, accessibility themes |
| **Quiz Modes** | Create custom study experiences | Timed quizzes, multiplayer modes |
| **AI Enhancements** | Add AI-powered features | Content generation, smart suggestions |
| **Analytics** | Provide learning insights and metrics | Progress tracking, performance analysis |
| **Integrations** | Connect with external services | Google Drive, Notion, Slack |

## Getting Started

### Installing Plugins

```bash
# Install from marketplace
python -m flashgenie plugins install plugin-name

# Install from local file
python -m flashgenie plugins install /path/to/plugin.zip

# List available plugins
python -m flashgenie plugins list

# Enable/disable plugins
python -m flashgenie plugins enable plugin-name
python -m flashgenie plugins disable plugin-name
```

### Basic Plugin Structure

Every plugin must have this basic structure:

```
my-plugin/
├── plugin.json          # Plugin manifest
├── __init__.py          # Main plugin code
├── README.md            # Documentation
├── test_plugin.py       # Tests
└── requirements.txt     # Dependencies (optional)
```

### Minimal Plugin Example

**plugin.json:**
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "A simple example plugin",
  "author": "Your Name",
  "type": "integration",
  "entry_point": "MyPlugin",
  "permissions": ["network"],
  "flashgenie_version": ">=1.8.0"
}
```

**__init__.py:**
```python
from flashgenie.core.plugin_system import IntegrationPlugin

class MyPlugin(IntegrationPlugin):
    def __init__(self):
        super().__init__()
        self.name = "my-plugin"
        self.version = "1.0.0"
    
    def initialize(self):
        self.logger.info("Plugin initialized!")
    
    def cleanup(self):
        self.logger.info("Plugin cleaned up!")
```

## Plugin Development Kit (PDK)

The PDK provides comprehensive tools for plugin development:

### Creating a New Plugin

```python
from flashgenie.core import PluginDevelopmentKit
from flashgenie.core.plugin_system import PluginType

# Initialize PDK
pdk = PluginDevelopmentKit("./my-plugins")

# Create plugin scaffold
plugin_path = pdk.create_plugin_scaffold(
    plugin_name="my-awesome-plugin",
    plugin_type=PluginType.IMPORTER,
    author="Your Name"
)
```

### Validating Plugins

```python
# Validate plugin structure and code
validation_results = pdk.validate_plugin(plugin_path)

if validation_results["valid"]:
    print("✅ Plugin is valid!")
else:
    print("❌ Validation errors:")
    for error in validation_results["errors"]:
        print(f"  - {error}")
```

### Testing Plugins

```python
# Run comprehensive tests
test_results = pdk.test_plugin(plugin_path, test_mode="comprehensive")

print(f"Tests run: {test_results['tests_run']}")
print(f"Passed: {test_results['tests_passed']}")
print(f"Failed: {test_results['tests_failed']}")
```

### Packaging Plugins

```python
# Package for distribution
package_path = pdk.package_plugin(plugin_path)
print(f"Plugin packaged: {package_path}")
```

## Plugin Marketplace

### Publishing Plugins

1. **Prepare your plugin:**
   ```bash
   python -m flashgenie pdk validate --path ./my-plugin
   python -m flashgenie pdk test --path ./my-plugin --mode comprehensive
   python -m flashgenie pdk package --path ./my-plugin
   ```

2. **Submit to marketplace:**
   ```bash
   python -m flashgenie marketplace submit ./my-plugin-1.0.0.zip
   ```

### Discovering Plugins

```bash
# Browse marketplace
python -m flashgenie marketplace browse

# Search for plugins
python -m flashgenie marketplace search "csv importer"

# Get plugin details
python -m flashgenie marketplace info plugin-name
```

## Best Practices

### Security
- Request only necessary permissions
- Validate all user inputs
- Never hardcode API keys or secrets
- Use secure communication protocols

### Performance
- Minimize startup time
- Use lazy loading for heavy resources
- Implement proper error handling
- Cache expensive operations

### User Experience
- Provide clear error messages
- Include comprehensive documentation
- Follow FlashGenie's UI guidelines
- Support internationalization

### Development
- Write comprehensive tests
- Use semantic versioning
- Document your API
- Follow Python PEP 8 style guidelines

## Next Steps

- [Importer Plugin Guide](./importers.md)
- [Exporter Plugin Guide](./exporters.md)
- [Theme Plugin Guide](./themes.md)
- [Quiz Mode Plugin Guide](./quiz-modes.md)
- [AI Enhancement Plugin Guide](./ai-enhancements.md)
- [Analytics Plugin Guide](./analytics.md)
- [Integration Plugin Guide](./integrations.md)
- [PDK API Reference](../api-reference/pdk.md)

## Support

- **Documentation**: [docs.flashgenie.com](https://docs.flashgenie.com)
- **Community**: [community.flashgenie.com](https://community.flashgenie.com)
- **Issues**: [GitHub Issues](https://github.com/flashgenie/flashgenie/issues)
- **Discord**: [FlashGenie Discord](https://discord.gg/flashgenie)
