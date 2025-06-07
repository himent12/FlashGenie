#!/usr/bin/env python3
"""
Test script for FlashGenie v1.5 Phase 2 Advanced Learning Features

This script tests all the new advanced features to ensure they work correctly.
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the flashgenie package to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_adaptive_study_planner():
    """Test the adaptive study planner."""
    print("🧠 Testing Adaptive Study Planner...")
    
    try:
        from flashgenie.core.adaptive_study_planner import (
            AdaptiveStudyPlanner, StudyContext, EnergyLevel, Environment
        )
        from flashgenie.core.difficulty_analyzer import DifficultyAnalyzer
        from flashgenie.core.smart_collections import SmartCollectionManager
        from flashgenie.core.tag_manager import TagManager
        from flashgenie.core.deck import Deck
        from flashgenie.core.flashcard import Flashcard
        
        # Create test deck
        cards = [
            Flashcard("What is Python?", "A programming language", {"programming", "python"}),
            Flashcard("What is ML?", "Machine Learning", {"ai", "ml"}),
            Flashcard("What is AI?", "Artificial Intelligence", {"ai"})
        ]
        deck = Deck("Test Deck", flashcards=cards)
        
        # Initialize components
        tag_manager = TagManager()
        difficulty_analyzer = DifficultyAnalyzer()
        collection_manager = SmartCollectionManager(tag_manager)
        planner = AdaptiveStudyPlanner(difficulty_analyzer, collection_manager)
        
        # Create study context
        context = StudyContext(
            available_time=30,
            energy_level=EnergyLevel.HIGH,
            time_of_day=datetime.now(),
            environment=Environment.QUIET_HOME
        )
        
        # Generate study plan
        study_plan = planner.plan_session(deck, context)
        
        print(f"   ✅ Study plan created: {study_plan.session_id}")
        print(f"   ✅ Duration: {study_plan.total_duration} minutes")
        print(f"   ✅ Segments: {len(study_plan.segments)}")
        print(f"   ✅ Confidence: {study_plan.confidence_score:.2f}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return True


def test_learning_velocity_tracker():
    """Test the learning velocity tracker."""
    print("📈 Testing Learning Velocity Tracker...")
    
    try:
        from flashgenie.core.learning_velocity_tracker import LearningVelocityTracker
        from flashgenie.core.deck import Deck
        from flashgenie.core.flashcard import Flashcard
        
        # Create test deck with some review history
        cards = []
        for i in range(10):
            card = Flashcard(f"Question {i}", f"Answer {i}", {"test"})
            card.review_count = i + 1
            card.correct_count = i
            card.last_reviewed = datetime.now() - timedelta(days=i)
            cards.append(card)
        
        deck = Deck("Test Deck", flashcards=cards)
        
        # Initialize tracker
        tracker = LearningVelocityTracker()
        
        # Calculate velocity
        velocity = tracker.calculate_current_velocity(deck)
        print(f"   ✅ Current velocity calculated")
        print(f"   ✅ Cards per day: {velocity.cards_per_day:.1f}")
        print(f"   ✅ Learning phase: {velocity.phase.value}")
        
        # Predict mastery
        prediction = tracker.predict_mastery_timeline(deck)
        print(f"   ✅ Mastery prediction: {prediction.estimated_days_to_mastery} days")
        print(f"   ✅ Confidence: {prediction.confidence_score:.2f}")
        
        # Analyze trends
        trends = tracker.analyze_learning_trends(deck)
        print(f"   ✅ Trends analyzed: {trends['velocity_trend'].value}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return True


def test_contextual_learning_engine():
    """Test the contextual learning engine."""
    print("🌍 Testing Contextual Learning Engine...")
    
    try:
        from flashgenie.core.contextual_learning_engine import (
            ContextualLearningEngine, LearningContext, Environment, DeviceType, AttentionLevel
        )
        from flashgenie.core.quiz_engine import QuizEngine
        from flashgenie.core.deck import Deck
        from flashgenie.core.flashcard import Flashcard
        
        # Create test components
        quiz_engine = QuizEngine()
        engine = ContextualLearningEngine(quiz_engine)
        
        # Test context detection
        context = engine.detect_context()
        print(f"   ✅ Context detected: {context.environment.value}")
        print(f"   ✅ Available time: {context.available_time} minutes")
        print(f"   ✅ Attention level: {context.attention_level.value}")
        
        # Create test deck
        cards = [Flashcard(f"Q{i}", f"A{i}", {"test"}) for i in range(5)]
        deck = Deck("Test Deck", flashcards=cards)
        
        # Test quiz configuration adaptation
        config = engine.adapt_quiz_configuration(context, deck)
        print(f"   ✅ Quiz config adapted")
        print(f"   ✅ Input method: {config.input_method}")
        print(f"   ✅ Auto advance: {config.auto_advance}")
        
        # Test card selection
        selected_cards = engine.select_optimal_cards(deck, context, target_count=3)
        print(f"   ✅ Cards selected: {len(selected_cards)}")
        
        # Test recommendations
        recommendations = engine.get_context_recommendations(context)
        print(f"   ✅ Recommendations: {len(recommendations)}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return True


def test_knowledge_graph():
    """Test the knowledge graph builder."""
    print("🕸️ Testing Knowledge Graph Builder...")
    
    try:
        from flashgenie.core.knowledge_graph import KnowledgeGraphBuilder
        from flashgenie.core.tag_manager import TagManager
        from flashgenie.core.deck import Deck
        from flashgenie.core.flashcard import Flashcard
        
        # Create test deck with hierarchical tags
        cards = [
            Flashcard("What is Python?", "Programming language", {"programming", "python", "languages"}),
            Flashcard("What is Java?", "Programming language", {"programming", "java", "languages"}),
            Flashcard("What is ML?", "Machine Learning", {"ai", "ml", "advanced"}),
            Flashcard("What is AI?", "Artificial Intelligence", {"ai", "advanced"}),
            Flashcard("What is a variable?", "Storage location", {"programming", "basics"})
        ]
        deck = Deck("Test Deck", flashcards=cards)
        
        # Initialize components
        tag_manager = TagManager()
        graph_builder = KnowledgeGraphBuilder(tag_manager)
        
        # Build graph
        knowledge_graph = graph_builder.build_graph(deck)
        
        print(f"   ✅ Knowledge graph built")
        print(f"   ✅ Nodes: {len(knowledge_graph.nodes)}")
        print(f"   ✅ Relationships: {len(knowledge_graph.relationships)}")
        print(f"   ✅ Learning paths: {len(knowledge_graph.learning_paths)}")
        print(f"   ✅ Knowledge gaps: {len(knowledge_graph.knowledge_gaps)}")
        
        # Test export
        export_data = knowledge_graph.export_for_visualization()
        print(f"   ✅ Export data generated: {len(export_data['nodes'])} nodes")
        
        # Test mastery summary
        summary = knowledge_graph.get_mastery_summary()
        print(f"   ✅ Mastery summary: {summary.get('total_concepts', 0)} concepts")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return True


def test_achievement_system():
    """Test the achievement system."""
    print("🏆 Testing Achievement System...")
    
    try:
        from flashgenie.core.achievement_system import AchievementEngine
        
        # Initialize achievement engine
        engine = AchievementEngine()
        
        print(f"   ✅ Achievement engine initialized")
        print(f"   ✅ Total achievements: {len(engine.achievements)}")
        
        # Test user stats
        user_stats = {
            'sessions_completed': 1,
            'total_cards_reviewed': 50,
            'accuracy_rate': 0.85,
            'avg_response_time': 3.5
        }
        
        # Check achievements
        newly_earned = engine.check_achievements(user_stats)
        print(f"   ✅ Achievements checked: {len(newly_earned)} newly earned")
        
        # Test streak updates
        session_stats = {
            'accuracy_rate': 0.9,
            'cards_reviewed': 10
        }
        streak_updates = engine.update_streaks(session_stats)
        print(f"   ✅ Streaks updated: {len(streak_updates)} streaks")
        
        # Test progress
        progress = engine.get_achievement_progress(user_stats)
        print(f"   ✅ Progress calculated for {len(progress)} achievements")
        
        # Test level calculation
        level, points, points_to_next = engine.get_user_level_and_points()
        print(f"   ✅ User level: {level}, Points: {points}")
        
        # Test leaderboard stats
        leaderboard_stats = engine.get_leaderboard_stats()
        print(f"   ✅ Leaderboard stats generated")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return True


def test_content_recommender():
    """Test the content recommendation engine."""
    print("💡 Testing Content Recommendation Engine...")
    
    try:
        from flashgenie.core.content_recommender import ContentRecommendationEngine
        from flashgenie.core.tag_manager import TagManager
        from flashgenie.core.deck import Deck
        from flashgenie.core.flashcard import Flashcard
        
        # Create test deck
        cards = [
            Flashcard("What is Python?", "Programming language", {"programming", "python"}),
            Flashcard("Advanced Python concepts", "Complex topic", {"programming", "python", "advanced"}),
            Flashcard("What is Java?", "Programming language", {"programming", "java"}),
        ]
        
        # Set different difficulties to create gaps
        cards[0].difficulty = 0.2
        cards[1].difficulty = 0.8  # Big jump
        cards[2].difficulty = 0.3
        
        deck = Deck("Test Deck", flashcards=cards)
        
        # Initialize components
        tag_manager = TagManager()
        recommender = ContentRecommendationEngine(tag_manager)
        
        # Test card suggestions
        card_suggestions = recommender.suggest_new_cards(deck, count=3)
        print(f"   ✅ Card suggestions: {len(card_suggestions)}")
        for suggestion in card_suggestions[:2]:
            print(f"      • {suggestion.suggested_question[:50]}...")
        
        # Test topic suggestions
        topic_suggestions = recommender.suggest_related_topics(deck)
        print(f"   ✅ Topic suggestions: {len(topic_suggestions)}")
        
        # Test prerequisite gaps
        prerequisites = recommender.identify_prerequisite_gaps(deck)
        print(f"   ✅ Prerequisite gaps: {len(prerequisites)}")
        
        # Test study sequence
        sequence = recommender.recommend_study_sequence(deck)
        print(f"   ✅ Study sequence: {len(sequence)} phases")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    return True


def main():
    """Run all Phase 2 feature tests."""
    print("🚀 FlashGenie v1.5 Phase 2 Feature Tests")
    print("=" * 50)
    
    tests = [
        test_adaptive_study_planner,
        test_learning_velocity_tracker,
        test_contextual_learning_engine,
        test_knowledge_graph,
        test_achievement_system,
        test_content_recommender
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 2 features are working correctly!")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
