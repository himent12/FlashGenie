# 🚀 FlashGenie Help System - Quick Reference

**Essential help commands for FlashGenie v1.8.4**

## 🔰 **Basic Help Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `help` | Show main help menu | `python -m flashgenie help` |
| `help COMMAND` | Get specific command help | `python -m flashgenie help import` |
| `help CATEGORY` | Show category commands | `python -m flashgenie help basic` |
| `search QUERY` | Search commands | `python -m flashgenie search quiz` |
| `version` | Show version info | `python -m flashgenie version` |

## 🎮 **Rich Interactive Shell (v1.8.4)**

| Command | Description | Example |
|---------|-------------|---------|
| `python -m flashgenie` | Start Rich interactive shell | All commands use Rich UI! |
| `FlashGenie > help` | Rich help in interactive mode | Beautiful Rich help system |
| `FlashGenie > list` | Rich deck tables | Rich tables with summaries |
| `FlashGenie > search quiz` | Rich search in shell | Rich search results |

## 📋 **Command Categories**

| Category | Icon | Commands | Description |
|----------|------|----------|-------------|
| `basic` | 🔰 | help, version | Basic commands |
| `deck_management` | 📚 | list, create, delete | Deck operations |
| `import_export` | 📁 | import, export | Data import/export |
| `study_session` | 🎯 | quiz, review | Learning sessions |
| `analytics` | 📊 | stats, progress | Statistics & progress |
| `accessibility` | ♿ | accessibility | Accessibility features |
| `developer` | 🔧 | debug, profile | Developer tools |
| `performance` | ⚡ | performance | Performance monitoring |

## 🔍 **Search Examples**

```bash
# Find import commands
python -m flashgenie search import

# Find accessibility features  
python -m flashgenie search accessibility

# Find study commands
python -m flashgenie search quiz

# Find statistics commands
python -m flashgenie search stats
```

## 🎯 **Quick Start Commands**

```bash
# Get help
python -m flashgenie help

# List decks
python -m flashgenie list

# Import deck
python -m flashgenie import deck.csv --name "My Deck"

# Start quiz
python -m flashgenie quiz "My Deck"

# View stats
python -m flashgenie stats
```

## ♿ **Accessibility Commands**

```bash
# Show accessibility status
python -m flashgenie accessibility --status

# Enable high contrast
python -m flashgenie accessibility --enable high_contrast

# Enable screen reader support
python -m flashgenie accessibility --enable screen_reader

# Enable audio feedback
python -m flashgenie accessibility --enable audio

# Test accessibility features
python -m flashgenie accessibility --test
```

## 🔧 **Developer Commands**

```bash
# Enable debug mode
python -m flashgenie debug --enable

# Show debug console
python -m flashgenie debug --console

# Show performance dashboard
python -m flashgenie performance --dashboard

# Optimize performance
python -m flashgenie performance --optimize

# Profile command
python -m flashgenie performance --profile "import deck.csv"
```

## 🏷️ **Command Aliases**

| Command | Aliases | Example |
|---------|---------|---------|
| `help` | `--help`, `-h` | `python -m flashgenie -h` |
| `version` | `--version`, `-v` | `python -m flashgenie -v` |
| `list` | `ls` | `python -m flashgenie ls` |
| `delete` | `remove`, `rm` | `python -m flashgenie rm "Deck"` |
| `quiz` | `study`, `practice` | `python -m flashgenie study "Deck"` |
| `stats` | `statistics`, `analytics` | `python -m flashgenie analytics` |
| `accessibility` | `a11y` | `python -m flashgenie a11y --status` |

## 💡 **Usage Tips**

- **Tab Completion**: Use Tab for command and file name completion
- **Rich UI**: All help uses beautiful Rich Terminal formatting
- **Accessibility**: Full screen reader and keyboard navigation support
- **Search**: Use fuzzy search to find commands even with typos
- **Categories**: Browse commands by functional categories
- **Examples**: All commands include real-world usage examples
- **Related Commands**: Each command shows related commands

## 🎨 **Rich Terminal UI Features**

- 🎨 **Colored Panels** - Information in beautiful colored panels
- 📊 **Tables** - Structured command information
- 🌳 **Tree Views** - Hierarchical command organization
- 🔍 **Search Highlighting** - Highlighted search results
- ⚡ **Icons** - Visual indicators for command types
- ♿ **Accessibility** - Screen reader and keyboard support

## 🆘 **Getting Help**

| Need | Command | Description |
|------|---------|-------------|
| **Overview** | `help` | Main help menu with categories |
| **Specific Command** | `help COMMAND` | Detailed command information |
| **Find Commands** | `search QUERY` | Search by name or description |
| **Browse Category** | `help CATEGORY` | Commands in specific category |
| **Accessibility** | `accessibility --status` | Accessibility options |
| **Developer Tools** | `debug --enable` | Enable developer features |

## 🔗 **Related Documentation**

- 📚 [Complete Command Reference](commands.md)
- 🆘 [Help System User Guide](help-system-guide.md)
- 🚀 [FlashGenie README](../README.md)
- ♿ [Accessibility Features](accessibility.md)

---

**💡 Pro Tip**: Start with `python -m flashgenie help` to see the beautiful Rich Terminal UI help system in action!
