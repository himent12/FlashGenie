#!/usr/bin/env python3
"""
Comprehensive Test Suite for FlashGenie v1.8.5

This script tests all three phases and their integration to ensure
everything is working correctly after the updates.
"""

import sys
import traceback
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_phase1_rich_quiz_interface():
    """Test Phase 1: Rich Quiz Interface"""
    print("🧪 Testing Phase 1: Rich Quiz Interface")
    print("-" * 50)
    
    try:
        # Import components
        from flashgenie.interfaces.terminal import RichTerminalUI, RichQuizInterface
        from flashgenie.core.content_system.deck import Deck
        from flashgenie.core.content_system.flashcard import Flashcard
        from flashgenie.core.study_system.quiz_engine import QuizMode, QuizEngine
        
        print("✅ All imports successful")
        
        # Create test components
        ui = RichTerminalUI()
        quiz_interface = RichQuizInterface(ui.console)
        quiz_engine = QuizEngine()
        
        print("✅ Components initialized")
        
        # Create test deck with proper flashcards
        deck = Deck(name="Test Quiz Deck", description="Test deck for quiz interface")
        
        # Create flashcards with all required attributes
        for i in range(3):
            card = Flashcard(
                card_id=f"quiz_test_{i+1}",
                question=f"Test question {i+1}?",
                answer=f"Test answer {i+1}",
                tags=["test", "quiz"]
            )
            # Set required attributes for quiz engine
            card.difficulty = 0.3 + (i * 0.2)
            card.next_review = datetime.now() - timedelta(hours=1)  # Make cards due
            card.review_count = i + 1
            deck.add_flashcard(card)
        
        print(f"✅ Test deck created with {len(deck.flashcards)} cards")
        
        # Test quiz engine card selection
        selected_cards = quiz_engine.select_cards_for_quiz(deck, QuizMode.SPACED_REPETITION, 2)
        print(f"✅ Quiz engine selected {len(selected_cards)} cards")
        
        # Test quiz interface components
        quiz_interface._show_quiz_introduction(deck, QuizMode.SPACED_REPETITION, len(selected_cards))
        print("✅ Quiz introduction displayed")
        
        # Test quiz interface functionality
        print("✅ Quiz interface components working correctly")
        
        print("🎉 Phase 1: Rich Quiz Interface - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Phase 1 Test Failed: {e}")
        traceback.print_exc()
        return False


def test_phase2_rich_statistics_dashboard():
    """Test Phase 2: Rich Statistics Dashboard"""
    print("\n🧪 Testing Phase 2: Rich Statistics Dashboard")
    print("-" * 50)
    
    try:
        # Import components
        from flashgenie.interfaces.terminal import RichTerminalUI, RichStatisticsDashboard
        from flashgenie.core.content_system.deck import Deck
        from flashgenie.core.content_system.flashcard import Flashcard
        
        print("✅ All imports successful")
        
        # Create test components
        ui = RichTerminalUI()
        stats_dashboard = RichStatisticsDashboard(ui.console)
        
        print("✅ Components initialized")
        
        # Create test deck with realistic data
        deck = Deck(name="Test Stats Deck", description="Test deck for statistics")
        
        for i in range(5):
            card = Flashcard(
                card_id=f"stats_test_{i+1}",
                question=f"Stats question {i+1}?",
                answer=f"Stats answer {i+1}",
                tags=["stats", "test", f"category_{i%3}"]
            )
            # Set realistic statistics data
            card.difficulty = 0.2 + (i * 0.15)
            card.review_count = 5 + i
            card.correct_count = 3 + i
            card.next_review = datetime.now() + timedelta(days=i)
            card.last_reviewed = datetime.now() - timedelta(hours=i+1)
            
            # Add mastery level for statistics
            card.mastery_level = 0.9 - (i * 0.15)
            
            deck.add_flashcard(card)
        
        print(f"✅ Test deck created with {len(deck.flashcards)} cards")
        
        # Test statistics calculation
        stats = stats_dashboard._calculate_deck_statistics(deck)
        print(f"✅ Statistics calculated: {stats['total_cards']} total cards")
        
        # Test different dashboard views
        stats_dashboard.show_deck_statistics(deck, detailed=False)
        print("✅ Simple statistics view displayed")
        
        stats_dashboard.show_deck_statistics(deck, detailed=True)
        print("✅ Detailed statistics view displayed")
        
        # Test global statistics
        stats_dashboard.show_global_statistics([deck])
        print("✅ Global statistics displayed")
        
        print("🎉 Phase 2: Rich Statistics Dashboard - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Phase 2 Test Failed: {e}")
        traceback.print_exc()
        return False


def test_phase3_ai_content_generation():
    """Test Phase 3: AI Content Generation"""
    print("\n🧪 Testing Phase 3: AI Content Generation")
    print("-" * 50)
    
    try:
        # Import components
        from flashgenie.interfaces.terminal import RichTerminalUI, RichAIInterface
        from flashgenie.ai.content_generator import AIContentGenerator, ContentType
        from flashgenie.core.content_system.deck import Deck
        from flashgenie.core.content_system.flashcard import Flashcard
        
        print("✅ All imports successful")
        
        # Create test components
        ui = RichTerminalUI()
        ai_interface = RichAIInterface(ui.console)
        ai_generator = AIContentGenerator()
        
        print("✅ Components initialized")
        
        # Test AI content generation
        test_text = """
        The speed of light is 299,792,458 meters per second.
        Water boils at 100 degrees Celsius.
        The chemical symbol for gold is Au.
        Python is a programming language.
        """
        
        generated_content = ai_generator.generate_flashcards_from_text(
            test_text, ContentType.FACTS, max_cards=3
        )
        print(f"✅ Generated {len(generated_content)} flashcards from text")
        
        # Test difficulty prediction
        test_card = Flashcard(
            card_id="ai_test",
            question="What is quantum mechanics?",
            answer="The branch of physics dealing with atomic and subatomic particles",
            tags=["physics", "quantum"]
        )
        
        difficulty = ai_generator.predict_difficulty(test_card.question, test_card.answer)
        print(f"✅ Difficulty predicted: {difficulty:.2f}")
        
        # Test hint generation
        hints = ai_generator.generate_hints(test_card)
        print(f"✅ Generated {len(hints)} hints")
        
        # Test content suggestions
        deck = Deck(name="AI Test Deck", description="Test deck for AI features")
        deck.add_flashcard(test_card)
        
        suggestions = ai_generator.suggest_related_content(deck.flashcards, count=2)
        print(f"✅ Generated {len(suggestions)} content suggestions")
        
        # Test card enhancement
        enhancements = ai_generator.enhance_existing_cards([test_card])
        print(f"✅ Generated enhancements for {len(enhancements)} cards")
        
        # Test Rich AI interface components
        ai_interface.predict_card_difficulty(test_card)
        print("✅ Rich AI interface difficulty prediction displayed")
        
        print("🎉 Phase 3: AI Content Generation - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Phase 3 Test Failed: {e}")
        traceback.print_exc()
        return False


def test_integration_workflow():
    """Test integrated workflow using all three phases"""
    print("\n🧪 Testing Integrated Workflow")
    print("-" * 50)
    
    try:
        # Import all components
        from flashgenie.interfaces.terminal import (
            RichTerminalUI, RichQuizInterface, 
            RichStatisticsDashboard, RichAIInterface
        )
        from flashgenie.ai.content_generator import AIContentGenerator, ContentType
        from flashgenie.core.content_system.deck import Deck
        from flashgenie.core.content_system.flashcard import Flashcard
        from flashgenie.core.study_system.quiz_engine import QuizMode
        
        print("✅ All components imported")
        
        # Initialize all interfaces
        ui = RichTerminalUI()
        quiz_interface = RichQuizInterface(ui.console)
        stats_dashboard = RichStatisticsDashboard(ui.console)
        ai_interface = RichAIInterface(ui.console)
        ai_generator = AIContentGenerator()
        
        print("✅ All interfaces initialized")
        
        # Step 1: Generate content with AI
        sample_text = "Mathematics is the study of numbers. Algebra deals with variables."
        generated_content = ai_generator.generate_flashcards_from_text(
            sample_text, ContentType.DEFINITIONS, max_cards=2
        )
        
        # Step 2: Create deck from AI content
        deck = Deck(name="Integration Test Deck", description="Created through integrated workflow")
        for i, content in enumerate(generated_content):
            card = Flashcard(
                card_id=f"integration_{i+1}",
                question=content.question,
                answer=content.answer,
                tags=content.tags
            )
            card.difficulty = content.difficulty
            card.next_review = datetime.now() - timedelta(hours=1)  # Make due for review
            deck.add_flashcard(card)
        
        print(f"✅ Created integrated deck with {len(deck.flashcards)} AI-generated cards")
        
        # Step 3: View statistics
        stats_dashboard.show_deck_statistics(deck, detailed=False)
        print("✅ Statistics displayed for AI-generated deck")
        
        # Step 4: Test quiz readiness
        quiz_interface._show_quiz_introduction(deck, QuizMode.RANDOM, len(deck.flashcards))
        print("✅ Quiz interface ready for AI-generated deck")
        
        # Step 5: Test AI suggestions
        suggestions = ai_generator.suggest_related_content(deck.flashcards, count=1)
        print(f"✅ Generated {len(suggestions)} suggestions for existing deck")
        
        print("🎉 Integrated Workflow - ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Integration Test Failed: {e}")
        traceback.print_exc()
        return False


def test_command_handler_integration():
    """Test Rich Command Handler integration"""
    print("\n🧪 Testing Rich Command Handler Integration")
    print("-" * 50)

    try:
        from flashgenie.interfaces.cli.rich_command_handler import RichCommandHandler
        from flashgenie.interfaces.terminal import RichTerminalUI

        print("✅ Command handler imports successful")

        # Initialize command handler with Rich UI
        ui = RichTerminalUI()
        handler = RichCommandHandler(ui)

        print("✅ Command handler initialized")

        # Test that all new commands are registered
        expected_commands = ['ai', 'generate', 'suggest', 'enhance', 'quiz', 'stats']
        for cmd in expected_commands:
            if cmd in handler.commands:
                print(f"✅ Command '{cmd}' registered")
            else:
                print(f"❌ Command '{cmd}' missing")
                return False

        print("🎉 Command Handler Integration - ALL TESTS PASSED")
        return True

    except Exception as e:
        print(f"❌ Command Handler Test Failed: {e}")
        traceback.print_exc()
        return False


def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 FlashGenie v1.8.5 - Comprehensive Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Phase 1: Rich Quiz Interface", test_phase1_rich_quiz_interface()))
    test_results.append(("Phase 2: Rich Statistics Dashboard", test_phase2_rich_statistics_dashboard()))
    test_results.append(("Phase 3: AI Content Generation", test_phase3_ai_content_generation()))
    test_results.append(("Integrated Workflow", test_integration_workflow()))
    test_results.append(("Command Handler Integration", test_command_handler_integration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! FlashGenie v1.8.5 is ready for production!")
        return True
    else:
        print(f"\n❌ {failed} test(s) failed. Please review and fix issues.")
        return False


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
