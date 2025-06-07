# FlashGenie Plugin Development Guide 🛠️

**Complete guide to developing plugins for FlashGenie v1.8.0**

This comprehensive guide covers everything you need to know about creating, testing, and distributing plugins for the FlashGenie ecosystem.

## 🚀 **Quick Start**

### **1. Install FlashGenie v1.8.0**
```bash
git clone https://github.com/himent12/FlashGenie.git
cd FlashGenie
pip install -r requirements.txt
```

### **2. Create Your First Plugin**
```bash
# Create a theme plugin
python -m flashgenie pdk create --name my-awesome-theme --type theme --author "Your Name"

# Create an AI enhancement plugin
python -m flashgenie pdk create --name smart-generator --type ai_enhancement --author "Your Name"
```

### **3. Test and Package**
```bash
# Validate your plugin
python -m flashgenie pdk validate --path my-awesome-theme

# Test functionality
python -m flashgenie pdk test --path my-awesome-theme --test-mode comprehensive

# Package for distribution
python -m flashgenie pdk package --path my-awesome-theme
```

## 🔌 **Plugin Types**

FlashGenie supports 7 different plugin types, each with specific capabilities:

### **📊 Importer Plugins**
Import data from various formats into FlashGenie.

**Base Class**: `ImporterPlugin`

**Required Methods**:
- `can_import(file_path: Path) -> bool`
- `import_data(file_path: Path, deck_name: str) -> Dict[str, Any]`
- `get_supported_formats() -> List[str]`

**Example**:
```python
from flashgenie.core.plugin_system import ImporterPlugin

class MyImporterPlugin(ImporterPlugin):
    def can_import(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == '.txt'
    
    def import_data(self, file_path: Path, deck_name: str) -> Dict[str, Any]:
        # Implementation here
        return {"success": True, "cards_imported": 10}
    
    def get_supported_formats(self) -> List[str]:
        return ['.txt']
```

### **📤 Exporter Plugins**
Export FlashGenie data to various formats.

**Base Class**: `ExporterPlugin`

**Required Methods**:
- `can_export(deck: Deck, format_type: str) -> bool`
- `export_data(deck: Deck, output_path: Path, format_type: str) -> Dict[str, Any]`
- `get_supported_formats() -> List[str]`

### **🎨 Theme Plugins**
Customize the visual appearance of FlashGenie.

**Base Class**: `ThemePlugin`

**Required Methods**:
- `get_theme_name() -> str`
- `apply_theme() -> Dict[str, Any]`
- `get_theme_info() -> Dict[str, Any]`

**Example**:
```python
from flashgenie.core.plugin_system import ThemePlugin

class DarkThemePlugin(ThemePlugin):
    def get_theme_name(self) -> str:
        return "Professional Dark"
    
    def apply_theme(self) -> Dict[str, Any]:
        return {
            "name": "dark-professional",
            "colors": {
                "background": "#1e1e1e",
                "text": "#ffffff",
                "accent": "#007acc",
                "success": "#4caf50",
                "warning": "#ff9800",
                "error": "#f44336"
            },
            "fonts": {
                "primary": "Segoe UI, sans-serif",
                "monospace": "Consolas, monospace"
            }
        }
    
    def get_theme_info(self) -> Dict[str, Any]:
        return {
            "name": self.get_theme_name(),
            "description": "Professional dark theme optimized for low-light environments",
            "features": ["dark_mode", "high_contrast", "accessibility"]
        }
```

### **🎮 Quiz Mode Plugins**
Create custom study modes and quiz experiences.

**Base Class**: `QuizModePlugin`

**Required Methods**:
- `get_mode_name() -> str`
- `create_session(deck: Deck, config: Dict[str, Any]) -> Any`
- `get_settings_schema() -> Dict[str, Any]`

### **🤖 AI Enhancement Plugins**
Add AI-powered features to FlashGenie.

**Base Class**: `AIEnhancementPlugin`

**Required Methods**:
- `get_ai_capabilities() -> List[str]`
- `process_content(content: str, task: str, **kwargs) -> Dict[str, Any]`
- `get_model_info() -> Dict[str, Any]`

**Example**:
```python
from flashgenie.core.plugin_system import AIEnhancementPlugin

class ContentGeneratorPlugin(AIEnhancementPlugin):
    def get_ai_capabilities(self) -> List[str]:
        return ["generate_flashcards", "expand_topics", "create_variations"]
    
    def process_content(self, content: str, task: str, **kwargs) -> Dict[str, Any]:
        if task == "generate_flashcards":
            # AI logic to generate flashcards from content
            return {
                "success": True,
                "generated_cards": [
                    {"question": "What is...?", "answer": "..."},
                    # More cards
                ]
            }
        return {"error": f"Unknown task: {task}"}
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_type": "local",
            "version": "1.0.0",
            "capabilities": self.get_ai_capabilities()
        }
```

### **📈 Analytics Plugins**
Provide advanced learning analytics and insights.

**Base Class**: `AnalyticsPlugin`

**Required Methods**:
- `generate_insights(deck: Deck, timeframe: str) -> Dict[str, Any]`
- `get_metrics() -> List[str]`
- `export_data(deck: Deck, format_type: str) -> bytes`

### **🔗 Integration Plugins**
Connect FlashGenie with external services.

**Base Class**: `IntegrationPlugin`

**Required Methods**:
- `get_service_name() -> str`
- `authenticate(credentials: Dict[str, str]) -> bool`
- `sync_data(operation: str, data: Any) -> Dict[str, Any]`

## 📋 **Plugin Manifest**

Every plugin requires a `plugin.json` manifest file:

```json
{
  "name": "my-awesome-plugin",
  "version": "1.0.0",
  "description": "An awesome plugin for FlashGenie",
  "author": "Your Name",
  "license": "MIT",
  "flashgenie_version": ">=1.8.0",
  "type": "theme",
  "entry_point": "MyAwesomePlugin",
  "permissions": ["deck_read"],
  "dependencies": ["requests>=2.28.0"],
  "settings_schema": {
    "enabled": {
      "type": "boolean",
      "default": true,
      "description": "Enable this plugin"
    },
    "theme_color": {
      "type": "string",
      "default": "#007acc",
      "description": "Primary theme color"
    }
  },
  "homepage": "https://github.com/yourusername/my-awesome-plugin",
  "repository": "https://github.com/yourusername/my-awesome-plugin",
  "tags": ["theme", "dark", "accessibility"]
}
```

### **Manifest Fields**

| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ | Unique plugin identifier (kebab-case) |
| `version` | ✅ | Semantic version (e.g., "1.0.0") |
| `description` | ✅ | Brief description of plugin functionality |
| `author` | ✅ | Plugin author name |
| `license` | ✅ | License type (e.g., "MIT", "GPL-3.0") |
| `flashgenie_version` | ✅ | Compatible FlashGenie versions |
| `type` | ✅ | Plugin type (see types above) |
| `entry_point` | ✅ | Main plugin class name |
| `permissions` | ❌ | Required permissions list |
| `dependencies` | ❌ | Python package dependencies |
| `settings_schema` | ❌ | Plugin configuration schema |
| `homepage` | ❌ | Plugin homepage URL |
| `repository` | ❌ | Source code repository URL |
| `tags` | ❌ | Searchable tags for marketplace |

## 🔒 **Permissions System**

FlashGenie uses a granular permission system to ensure security:

| Permission | Description |
|------------|-------------|
| `file_read` | Read files from the file system |
| `file_write` | Write files to the file system |
| `deck_read` | Read flashcard deck data |
| `deck_write` | Modify flashcard deck data |
| `user_data` | Access user statistics and progress |
| `network` | Make network requests |
| `system_integration` | Integrate with OS features |
| `config_read` | Read FlashGenie configuration |
| `config_write` | Modify FlashGenie configuration |

**Example Permission Usage**:
```python
def initialize(self) -> None:
    # Request required permissions
    self.require_permission(Permission.DECK_READ)
    self.require_permission(Permission.FILE_WRITE)
    
    # Plugin initialization code
    self.logger.info("Plugin initialized with required permissions")
```

## 🧪 **Testing Your Plugin**

### **Automated Testing**
```bash
# Basic functionality test
python -m flashgenie pdk test --path my-plugin --test-mode basic

# Comprehensive test with security checks
python -m flashgenie pdk test --path my-plugin --test-mode comprehensive
```

### **Manual Testing**
```bash
# Install plugin for testing
python -m flashgenie plugins install my-plugin/ --category development

# Enable and test
python -m flashgenie plugins enable my-plugin
python -m flashgenie plugins info my-plugin

# Test hot reload
python -m flashgenie plugins reload my-plugin
```

### **Writing Custom Tests**
Create a `test_plugin.py` file in your plugin directory:

```python
#!/usr/bin/env python3
import sys
import json
from pathlib import Path

# Test plugin functionality
def test_plugin_initialization():
    """Test plugin initialization."""
    # Load manifest
    with open("plugin.json", "r") as f:
        manifest_data = json.load(f)
    
    # Test plugin creation and initialization
    # Add your specific tests here
    
    return True

def main():
    """Run all tests."""
    tests = [test_plugin_initialization]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
            print(f"✅ {test.__name__}")
        else:
            print(f"❌ {test.__name__}")
    
    print(f"Tests: {passed}/{len(tests)} passed")
    return 0 if passed == len(tests) else 1

if __name__ == "__main__":
    sys.exit(main())
```

## 📦 **Distribution**

### **Packaging**
```bash
# Package your plugin
python -m flashgenie pdk package --path my-plugin --output packages/

# This creates: my-plugin-1.0.0.zip
```

### **Marketplace Submission**
```bash
# Submit to marketplace (future feature)
python -m flashgenie marketplace publish my-plugin-1.0.0.zip --category community
```

### **Manual Distribution**
```bash
# Users can install from ZIP
python -m flashgenie plugins install my-plugin-1.0.0.zip --category local

# Or from directory
python -m flashgenie plugins install /path/to/my-plugin/ --category local
```

## 🎯 **Best Practices**

### **Code Quality**
- ✅ Use type hints for all methods
- ✅ Add comprehensive docstrings
- ✅ Follow PEP 8 style guidelines
- ✅ Handle errors gracefully
- ✅ Use the plugin logger for debugging

### **Security**
- ✅ Request only necessary permissions
- ✅ Validate all user inputs
- ✅ Avoid dangerous operations
- ✅ Use secure coding practices
- ✅ Test with security validation

### **User Experience**
- ✅ Provide clear error messages
- ✅ Include helpful documentation
- ✅ Use intuitive settings names
- ✅ Respect user preferences
- ✅ Maintain backward compatibility

### **Documentation**
- ✅ Include README.md with usage examples
- ✅ Add LICENSE file
- ✅ Provide CHANGELOG.md for updates
- ✅ Document all settings and options
- ✅ Include screenshots if applicable

## 🔧 **Advanced Features**

### **Hot Reload Support**
Make your plugin hot-reload friendly:

```python
def cleanup(self) -> None:
    """Cleanup resources for hot reload."""
    # Close files, stop threads, cleanup resources
    if hasattr(self, 'background_thread'):
        self.background_thread.stop()
    
    self.logger.info("Plugin cleaned up for hot reload")
```

### **Settings Management**
Handle plugin settings properly:

```python
def initialize(self) -> None:
    # Get settings with defaults
    self.theme_color = self.get_setting("theme_color", "#007acc")
    self.enabled = self.get_setting("enabled", True)
    
    # Validate settings
    if not self.enabled:
        self.logger.info("Plugin disabled by user settings")
        return
```

### **Dependency Management**
Specify dependencies correctly:

```json
{
  "dependencies": [
    "requests>=2.28.0",
    "pandas>=1.5.0",
    "numpy>=1.21.0"
  ]
}
```

## 🆘 **Troubleshooting**

### **Common Issues**

**Plugin Not Loading**
- Check manifest syntax with `pdk validate`
- Verify all required fields are present
- Ensure entry_point class exists
- Check FlashGenie version compatibility

**Permission Errors**
- Add required permissions to manifest
- Use `require_permission()` in initialize()
- Check permission descriptions in docs

**Import Errors**
- Verify all dependencies are installed
- Check Python path and imports
- Use relative imports within plugin

**Hot Reload Issues**
- Implement proper cleanup() method
- Avoid global state and singletons
- Close resources in cleanup()

### **Getting Help**
- 📖 Check the documentation
- 💬 Ask in GitHub Discussions
- 🐛 Report bugs in GitHub Issues
- 📧 Contact plugin support team

## 🌟 **Plugin Examples**

Complete examples are available in the `examples/plugins/` directory:

- **Simple Theme**: Basic theme plugin
- **CSV Importer**: Advanced importer with validation
- **AI Content Generator**: AI-powered content creation
- **Study Reminders**: Integration with system notifications
- **Learning Analytics**: Advanced analytics and reporting

---

**Ready to build amazing plugins for FlashGenie? Start creating and join our thriving plugin ecosystem!** 🧞‍♂️✨
