# FlashGenie Tests

This directory contains test files for FlashGenie development and validation.

## Test Files

### Core Component Tests
- `test_deck.py` - Tests for Deck class functionality
- `test_flashcard.py` - Tests for Flashcard class functionality  
- `test_quiz_engine.py` - Tests for quiz engine functionality
- `test_spaced_repetition.py` - Tests for spaced repetition algorithm
- `test_context_analyzer.py` - Tests for context analysis features
- `test_plugin_scaffolder.py` - Tests for plugin scaffolding system

### Comprehensive System Tests
- `test_v1.8.5_comprehensive.py` - **Complete v1.8.5 system test suite**

## v1.8.5 Comprehensive Test Suite

The `test_v1.8.5_comprehensive.py` file contains a complete test suite for all three phases of FlashGenie v1.8.5:

### What It Tests

#### Phase 1: Rich Quiz Interface
- Rich Terminal UI quiz components
- Quiz engine card selection
- Quiz interface initialization and display
- Multiple quiz modes functionality

#### Phase 2: Rich Statistics Dashboard  
- Statistics calculation and display
- Rich UI dashboard components
- Global and detailed statistics views
- Data visualization and formatting

#### Phase 3: AI Content Generation
- AI content generator functionality
- Difficulty prediction algorithms
- Content suggestions and enhancements
- Rich AI interface components

#### Integration Testing
- All phases working together
- AI-generated content → Statistics → Quiz workflow
- Command handler integration
- Rich UI consistency across all features

### Running the Tests

```bash
# Run the comprehensive v1.8.5 test suite
cd FlashGenie
python tests/test_v1.8.5_comprehensive.py
```

### Expected Output

When all tests pass, you should see:
```
🎉 ALL TESTS PASSED! FlashGenie v1.8.5 is ready for production!
```

### Test Results Summary

The comprehensive test validates:
- ✅ Phase 1: Rich Quiz Interface
- ✅ Phase 2: Rich Statistics Dashboard  
- ✅ Phase 3: AI Content Generation
- ✅ Integrated Workflow
- ✅ Command Handler Integration

## Development Guidelines

### When to Run Tests

- **Before committing changes** - Run comprehensive tests to ensure nothing is broken
- **After adding new features** - Verify integration with existing components
- **Before releases** - Complete validation of all functionality

### Adding New Tests

When adding new features to FlashGenie:

1. Add unit tests for individual components
2. Update the comprehensive test suite if needed
3. Ensure all tests pass before committing

### Test Dependencies

The comprehensive test requires:
- Rich Terminal UI components
- All three v1.8.5 phases (Quiz, Statistics, AI)
- Core FlashGenie components (Deck, Flashcard, etc.)

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Troubleshooting

### Common Issues

**Import Errors**: Make sure you're running from the FlashGenie root directory and all dependencies are installed.

**Rich UI Not Available**: The comprehensive test requires Rich Terminal UI. Install with `pip install rich`.

**Test Failures**: Check the error output for specific component failures and verify the related code.

### Getting Help

If tests fail or you need help with testing:
1. Check the error output for specific failure details
2. Verify all dependencies are installed correctly
3. Ensure you're running from the correct directory
4. Review the test code to understand what's being validated

The comprehensive test suite is designed to catch integration issues and ensure all v1.8.5 features work together correctly.
