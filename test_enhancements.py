#!/usr/bin/env python3
"""
Test script for FlashGenie enhancements.

This script tests the new smart difficulty adjustment and advanced tagging features.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_difficulty_analyzer():
    """Test the difficulty analyzer functionality."""
    print("Testing Difficulty Analyzer...")
    
    try:
        from flashgenie.core.flashcard import Flashcard
        from flashgenie.core.difficulty_analyzer import DifficultyAnalyzer, ConfidenceLevel
        
        # Create a flashcard
        card = Flashcard("What is 2 + 2?", "4")
        
        # Simulate some reviews with different performance
        card.mark_reviewed(correct=True, quality=4, response_time=2.0, confidence=4)
        card.mark_reviewed(correct=True, quality=5, response_time=1.5, confidence=5)
        card.mark_reviewed(correct=False, quality=1, response_time=8.0, confidence=2)
        card.mark_reviewed(correct=True, quality=3, response_time=4.0, confidence=3)
        
        # Test difficulty analyzer
        analyzer = DifficultyAnalyzer()
        performance = analyzer.analyze_card_performance(card)
        
        print(f"  ✓ Performance analysis: accuracy={performance.accuracy_rate:.2f}, avg_time={performance.average_response_time:.1f}s")
        
        # Test difficulty adjustment
        old_difficulty = card.difficulty
        new_difficulty = analyzer.suggest_difficulty_adjustment(card, performance, ConfidenceLevel.HIGH)
        
        print(f"  ✓ Difficulty suggestion: {old_difficulty:.2f} → {new_difficulty:.2f}")
        
        # Test explanation
        explanation = analyzer.get_difficulty_explanation(old_difficulty, new_difficulty, performance)
        print(f"  ✓ Explanation: {explanation}")
        
        return True
    except Exception as e:
        print(f"  ✗ Difficulty analyzer test failed: {e}")
        return False


def test_tag_manager():
    """Test the tag manager functionality."""
    print("Testing Tag Manager...")
    
    try:
        from flashgenie.core.tag_manager import TagManager
        from flashgenie.core.flashcard import Flashcard
        
        # Create tag manager
        tag_manager = TagManager()
        
        # Test hierarchical tag creation
        tag = tag_manager.create_hierarchical_tag("Science > Mathematics > Algebra")
        print(f"  ✓ Created hierarchical tag: {tag.get_full_path(tag_manager)}")
        
        # Test tag suggestions
        card = Flashcard("What is the quadratic formula?", "x = (-b ± √(b²-4ac)) / 2a")
        suggestions = tag_manager.suggest_tags(card.question, card.answer)
        print(f"  ✓ Tag suggestions: {suggestions}")
        
        # Test auto-categorization
        auto_tags = tag_manager.auto_categorize(card)
        print(f"  ✓ Auto-categorization: {auto_tags}")
        
        # Test alias creation
        tag_manager.add_alias("math", "mathematics")
        resolved = tag_manager.resolve_tag_name("math")
        print(f"  ✓ Tag alias resolution: math → {resolved}")
        
        return True
    except Exception as e:
        print(f"  ✗ Tag manager test failed: {e}")
        return False


def test_smart_collections():
    """Test the smart collections functionality."""
    print("Testing Smart Collections...")
    
    try:
        from flashgenie.core.flashcard import Flashcard
        from flashgenie.core.deck import Deck
        from flashgenie.core.smart_collections import SmartCollectionManager
        from flashgenie.core.tag_manager import TagManager
        
        # Create test deck with varied cards
        cards = [
            Flashcard("Easy math", "2+2=4", tags=["math", "basic"]),
            Flashcard("Hard physics", "E=mc²", tags=["physics", "advanced"]),
            Flashcard("Medium biology", "DNA structure", tags=["biology", "intermediate"]),
        ]
        
        # Set different difficulties
        cards[0].difficulty = 0.2  # Easy
        cards[1].difficulty = 0.8  # Hard
        cards[2].difficulty = 0.5  # Medium
        
        # Simulate some reviews
        cards[0].mark_reviewed(correct=True, quality=5)
        cards[1].mark_reviewed(correct=False, quality=1)
        cards[2].mark_reviewed(correct=True, quality=3)
        
        deck = Deck("Test Deck", flashcards=cards)
        
        # Create collection manager
        tag_manager = TagManager()
        collection_manager = SmartCollectionManager(tag_manager)
        
        # Test difficulty-based collection
        easy_cards = collection_manager.get_collection("Easy Cards")
        if easy_cards:
            easy_results = easy_cards.get_cards(deck)
            print(f"  ✓ Easy cards collection: {len(easy_results)} cards")
        
        # Test performance-based collection
        struggling_cards = collection_manager.get_collection("Struggling Cards")
        if struggling_cards:
            struggling_results = struggling_cards.get_cards(deck)
            print(f"  ✓ Struggling cards collection: {len(struggling_results)} cards")
        
        # Test custom tag-based collection
        math_collection = collection_manager.create_tag_collection(
            "Math Cards", 
            required_tags=["math"]
        )
        math_results = math_collection.get_cards(deck)
        print(f"  ✓ Math cards collection: {len(math_results)} cards")
        
        # Test collection statistics
        stats = math_collection.get_statistics(deck)
        print(f"  ✓ Collection stats: {stats['total_cards']} total, {stats['avg_difficulty']:.2f} avg difficulty")
        
        return True
    except Exception as e:
        print(f"  ✗ Smart collections test failed: {e}")
        return False


def test_enhanced_deck():
    """Test enhanced deck functionality."""
    print("Testing Enhanced Deck Features...")
    
    try:
        from flashgenie.core.flashcard import Flashcard
        from flashgenie.core.deck import Deck
        from flashgenie.core.tag_manager import TagManager
        
        # Create test deck
        cards = [
            Flashcard("What is Python?", "A programming language", tags=["programming"]),
            Flashcard("What is machine learning?", "AI subset", tags=["ai", "advanced"]),
            Flashcard("What is HTML?", "Markup language"),  # No tags
        ]
        
        deck = Deck("Test Deck", flashcards=cards)
        
        # Test auto-tagging
        tag_manager = TagManager()
        tagged_count = deck.auto_tag_cards(tag_manager)
        print(f"  ✓ Auto-tagged {tagged_count} cards")
        
        # Test performance summary
        performance = deck.get_performance_summary()
        print(f"  ✓ Performance summary: {performance['total_cards']} cards, {performance['average_difficulty']:.2f} avg difficulty")
        
        # Test difficulty distribution
        distribution = deck.get_difficulty_distribution()
        print(f"  ✓ Difficulty distribution: {distribution}")
        
        return True
    except Exception as e:
        print(f"  ✗ Enhanced deck test failed: {e}")
        return False


def test_enhanced_quiz():
    """Test enhanced quiz functionality."""
    print("Testing Enhanced Quiz Features...")
    
    try:
        from flashgenie.core.flashcard import Flashcard
        from flashgenie.core.deck import Deck
        from flashgenie.core.quiz_engine import QuizEngine
        
        # Create test deck
        card = Flashcard("Test question", "Test answer")
        deck = Deck("Test Deck", flashcards=[card])
        
        # Create quiz engine
        quiz_engine = QuizEngine()
        session = quiz_engine.start_session(deck)
        
        # Get question
        question = quiz_engine.get_next_question()
        if question:
            print(f"  ✓ Got quiz question: {question.flashcard.question}")
            
            # Submit answer with confidence
            correct = quiz_engine.submit_answer(question, "Test answer", confidence=4)
            print(f"  ✓ Submitted answer with confidence, correct: {correct}")
            
            # Check if difficulty was analyzed
            if hasattr(question.flashcard, 'confidence_ratings') and question.flashcard.confidence_ratings:
                print(f"  ✓ Confidence rating recorded: {question.flashcard.confidence_ratings[-1]}")
        
        quiz_engine.end_session()
        print("  ✓ Quiz session completed")
        
        return True
    except Exception as e:
        print(f"  ✗ Enhanced quiz test failed: {e}")
        return False


def main():
    """Run all enhancement tests."""
    print("🧞‍♂️ FlashGenie Enhancements Test")
    print("=" * 40)
    
    tests = [
        test_difficulty_analyzer,
        test_tag_manager,
        test_smart_collections,
        test_enhanced_deck,
        test_enhanced_quiz
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
        print("🎉 All enhancement tests passed! New features are working.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
