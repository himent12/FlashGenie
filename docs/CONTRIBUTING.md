# Contributing to FlashGenie

Thank you for your interest in contributing to FlashGenie! This document provides guidelines and information for contributors.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contributing Guidelines](#contributing-guidelines)
5. [Plugin Development](#plugin-development)
6. [Testing](#testing)
7. [Documentation](#documentation)
8. [Pull Request Process](#pull-request-process)

## Code of Conduct

FlashGenie is committed to providing a welcoming and inclusive environment for all contributors. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Python and software development
- Familiarity with flashcard learning concepts (helpful but not required)

### Areas for Contribution

We welcome contributions in several areas:

- **🐛 Bug Fixes**: Fix issues and improve stability
- **✨ New Features**: Add new functionality and capabilities
- **🔌 Plugin Development**: Create plugins for the ecosystem
- **📚 Documentation**: Improve guides, tutorials, and API docs
- **🧪 Testing**: Add tests and improve test coverage
- **🎨 UI/UX**: Enhance user interface and experience
- **🔬 Research**: Integrate learning science research
- **🌐 Internationalization**: Add language support
- **♿ Accessibility**: Improve accessibility features

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/yourusername/FlashGenie.git
cd FlashGenie

# Add upstream remote
git remote add upstream https://github.com/himent12/FlashGenie.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt

# Install in development mode
pip install -e .
```

### 3. Verify Installation

```bash
# Run tests
python -m pytest tests/

# Check code style
flake8 flashgenie/
black --check flashgenie/

# Verify CLI works
python -m flashgenie --version
```

### 4. Set Up Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run hooks on all files (optional)
pre-commit run --all-files
```

## Contributing Guidelines

### Coding Standards

- **Python Style**: Follow PEP 8 and use Black for formatting
- **Type Hints**: Use type hints for all public functions
- **Docstrings**: Use Google-style docstrings
- **Imports**: Use absolute imports and organize with isort
- **Line Length**: Maximum 88 characters (Black default)

### Code Quality

```bash
# Format code
black flashgenie/

# Sort imports
isort flashgenie/

# Check style
flake8 flashgenie/

# Type checking
mypy flashgenie/

# Run all quality checks
make lint  # or python scripts/lint.py
```

### Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(plugins): add hot-swappable plugin loading
fix(spaced-repetition): correct interval calculation
docs(api): update plugin development guide
```

### Branch Naming

Use descriptive branch names:
- `feature/plugin-marketplace`
- `fix/memory-leak-in-quiz`
- `docs/update-installation-guide`
- `refactor/simplify-deck-management`

## Plugin Development

### Creating Plugins

Use the Plugin Development Kit (PDK):

```bash
# Create new plugin
python -m flashgenie pdk create \
    --name "my-plugin" \
    --type "importer" \
    --author "Your Name"

# Validate plugin
python -m flashgenie pdk validate --path ./my-plugin

# Test plugin
python -m flashgenie pdk test --path ./my-plugin --mode comprehensive

# Package plugin
python -m flashgenie pdk package --path ./my-plugin
```

### Plugin Guidelines

- Follow the [Plugin Development Guide](docs/plugins/README.md)
- Use appropriate plugin types and permissions
- Include comprehensive tests
- Provide clear documentation
- Follow security best practices

### Plugin Submission

1. Develop and test your plugin thoroughly
2. Submit to the community repository
3. Include detailed description and screenshots
4. Respond to review feedback promptly

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_deck.py

# Run with coverage
python -m pytest --cov=flashgenie

# Run integration tests
python -m pytest tests/integration/

# Run plugin tests
python -m pytest tests/plugins/
```

### Writing Tests

- Write tests for all new functionality
- Use pytest fixtures for common setup
- Mock external dependencies
- Test both success and failure cases
- Aim for >90% code coverage

Example test:

```python
import pytest
from flashgenie.core import Deck, Flashcard

class TestDeck:
    def test_add_flashcard(self):
        """Test adding flashcard to deck."""
        deck = Deck("Test Deck")
        card = Flashcard("Question", "Answer")
        
        deck.add_flashcard(card)
        
        assert len(deck.flashcards) == 1
        assert deck.flashcards[0] == card
    
    def test_add_duplicate_flashcard(self):
        """Test adding duplicate flashcard raises error."""
        deck = Deck("Test Deck")
        card = Flashcard("Question", "Answer")
        
        deck.add_flashcard(card)
        
        with pytest.raises(ValueError):
            deck.add_flashcard(card)
```

### Test Categories

- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **Plugin Tests**: Test plugin functionality
- **Performance Tests**: Test performance requirements
- **Security Tests**: Test security measures

## Documentation

### Documentation Types

- **User Documentation**: Guides for end users
- **Developer Documentation**: API reference and development guides
- **Plugin Documentation**: Plugin development and usage
- **Contributing Documentation**: This file and related guides

### Writing Documentation

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Keep documentation up-to-date with code changes
- Use Markdown format

### Building Documentation

```bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve

# Deploy documentation (maintainers only)
mkdocs gh-deploy
```

## Pull Request Process

### Before Submitting

1. **Update your fork**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes and commit**:
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

4. **Run tests and quality checks**:
   ```bash
   python -m pytest
   make lint
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Pull Request Template

When creating a pull request, include:

- **Description**: Clear description of changes
- **Type**: Feature, bug fix, documentation, etc.
- **Testing**: How you tested the changes
- **Screenshots**: For UI changes
- **Breaking Changes**: Any breaking changes
- **Related Issues**: Link to related issues

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and quality checks
2. **Code Review**: Maintainers review code for quality and design
3. **Testing**: Changes are tested in various environments
4. **Documentation**: Documentation is reviewed and updated
5. **Approval**: Changes are approved by maintainers
6. **Merge**: Changes are merged into main branch

### Review Criteria

- Code quality and style
- Test coverage and quality
- Documentation completeness
- Performance impact
- Security considerations
- Backward compatibility
- User experience impact

## Getting Help

### Communication Channels

- **GitHub Discussions**: General questions and discussions
- **GitHub Issues**: Bug reports and feature requests
- **Discord**: Real-time chat with community
- **Email**: Direct contact for sensitive issues

### Mentorship

New contributors can get help from:
- **Good First Issues**: Issues labeled for beginners
- **Mentorship Program**: Pairing with experienced contributors
- **Documentation**: Comprehensive guides and tutorials
- **Community Support**: Active community willing to help

## Recognition

Contributors are recognized through:
- **Contributors List**: Listed in README and documentation
- **Release Notes**: Mentioned in release announcements
- **Community Highlights**: Featured in community updates
- **Badges**: Special recognition for significant contributions

## License

By contributing to FlashGenie, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing, please:
1. Check existing documentation
2. Search GitHub discussions and issues
3. Ask in our Discord community
4. Create a new GitHub discussion

Thank you for contributing to FlashGenie! 🧞‍♂️
