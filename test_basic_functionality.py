#!/usr/bin/env python3
"""
Basic functionality test for FlashGenie.

This script tests the core functionality to ensure everything is working correctly.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")
    
    try:
        from flashgenie.core.flashcard import Flashcard
        from flashgenie.core.deck import Deck
        from flashgenie.core.quiz_engine import QuizEngine
        from flashgenie.core.spaced_repetition import SpacedRepetitionAlgorithm
        from flashgenie.data.importers.csv_importer import CSVImporter
        from flashgenie.data.importers.txt_importer import TXTImporter
        from flashgenie.data.storage import DataStorage
        from flashgenie.interfaces.cli.terminal_ui import TerminalUI
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_flashcard_creation():
    """Test basic flashcard functionality."""
    print("Testing flashcard creation...")
    
    try:
        from flashgenie.core.flashcard import Flashcard
        
        # Create a flashcard
        card = Flashcard("What is 2 + 2?", "4", tags=["math"])
        
        # Test basic properties
        assert card.question == "What is 2 + 2?"
        assert card.answer == "4"
        assert card.tags == ["math"]
        assert card.difficulty == 0.5
        assert card.review_count == 0
        
        # Test serialization
        card_dict = card.to_dict()
        assert "question" in card_dict
        assert "answer" in card_dict
        
        # Test deserialization
        new_card = Flashcard.from_dict(card_dict)
        assert new_card.question == card.question
        assert new_card.answer == card.answer
        
        print("✓ Flashcard functionality working")
        return True
    except Exception as e:
        print(f"✗ Flashcard test failed: {e}")
        return False


def test_deck_creation():
    """Test basic deck functionality."""
    print("Testing deck creation...")
    
    try:
        from flashgenie.core.flashcard import Flashcard
        from flashgenie.core.deck import Deck
        
        # Create flashcards
        cards = [
            Flashcard("What is 2 + 2?", "4"),
            Flashcard("What is the capital of France?", "Paris"),
            Flashcard("What is H2O?", "Water")
        ]
        
        # Create deck
        deck = Deck("Test Deck", flashcards=cards)
        
        # Test basic properties
        assert deck.name == "Test Deck"
        assert len(deck.flashcards) == 3
        assert deck.size == 3
        
        # Test serialization
        deck_dict = deck.to_dict()
        assert "name" in deck_dict
        assert "flashcards" in deck_dict
        
        print("✓ Deck functionality working")
        return True
    except Exception as e:
        print(f"✗ Deck test failed: {e}")
        return False


def test_csv_import():
    """Test CSV import functionality."""
    print("Testing CSV import...")
    
    try:
        from flashgenie.data.importers.csv_importer import CSVImporter
        import tempfile
        
        # Create temporary CSV file
        csv_content = """question,answer
What is 2 + 2?,4
What is the capital of Spain?,Madrid
What is H2O?,Water"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_file = Path(f.name)
        
        try:
            # Import CSV
            importer = CSVImporter()
            deck = importer.import_file(csv_file)
            
            # Test results
            assert len(deck.flashcards) == 3
            assert deck.flashcards[0].question == "What is 2 + 2?"
            assert deck.flashcards[0].answer == "4"
            
            print("✓ CSV import working")
            return True
        finally:
            # Clean up
            csv_file.unlink()
            
    except Exception as e:
        print(f"✗ CSV import test failed: {e}")
        return False


def test_spaced_repetition():
    """Test spaced repetition algorithm."""
    print("Testing spaced repetition...")
    
    try:
        from flashgenie.core.flashcard import Flashcard
        from flashgenie.core.spaced_repetition import SpacedRepetitionAlgorithm, ReviewResult
        from datetime import datetime
        
        # Create algorithm and flashcard
        algorithm = SpacedRepetitionAlgorithm()
        card = Flashcard("Test question", "Test answer")
        
        # Create review result
        review = ReviewResult(quality=4, response_time=3.0, correct=True)
        
        # Update flashcard
        algorithm.update_flashcard(card, review)
        
        # Test that card was updated
        assert card.review_count == 1
        assert card.correct_count == 1
        assert card.last_reviewed is not None
        
        print("✓ Spaced repetition working")
        return True
    except Exception as e:
        print(f"✗ Spaced repetition test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧞‍♂️ FlashGenie Basic Functionality Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_flashcard_creation,
        test_deck_creation,
        test_csv_import,
        test_spaced_repetition
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FlashGenie is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
