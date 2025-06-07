#!/usr/bin/env python3
"""
FlashGenie v1.8.5 - Complete Release Demo

This script demonstrates all three phases of FlashGenie v1.8.5:
Phase 1: Rich Quiz Interface
Phase 2: Rich Statistics Dashboard  
Phase 3: AI Content Generation

A comprehensive showcase of the enhanced learning experience with Rich Terminal UI.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from flashgenie.interfaces.terminal import (
        RichTerminalUI, 
        RichQuizInterface, 
        RichStatisticsDashboard,
        RichAIInterface
    )
    from flashgenie.ai.content_generator import AIContentGenerator, ContentType
    from flashgenie.core.content_system.deck import Deck
    from flashgenie.core.content_system.flashcard import Flashcard
    from flashgenie.core.study_system.quiz_engine import QuizMode
    print("✅ FlashGenie v1.8.5 Complete - All components loaded successfully!")
except ImportError as e:
    print(f"❌ Could not load FlashGenie v1.8.5 components: {e}")
    print("Please install dependencies: pip install rich textual prompt-toolkit")
    sys.exit(1)


def create_comprehensive_demo_deck() -> Deck:
    """Create a comprehensive demo deck showcasing all v1.8.5 features."""
    deck = Deck(name="FlashGenie v1.8.5 Demo Deck", description="Comprehensive demo showcasing all v1.8.5 features")
    
    # Add diverse flashcards with realistic data
    demo_cards = [
        # Science cards
        ("What is the speed of light?", "299,792,458 m/s", ["physics", "constants"], 0.7, 0.4, 8),
        ("What is photosynthesis?", "Process by which plants convert sunlight into energy", ["biology", "plants"], 0.5, 0.6, 12),
        ("Chemical symbol for water?", "H2O", ["chemistry", "molecules"], 0.2, 0.9, 25),
        
        # Math cards
        ("Area of a circle formula?", "πr²", ["math", "geometry"], 0.4, 0.7, 15),
        ("What is the Pythagorean theorem?", "a² + b² = c²", ["math", "geometry"], 0.3, 0.8, 20),
        
        # Language cards
        ("Spanish for 'hello'?", "Hola", ["spanish", "greetings"], 0.1, 0.95, 30),
        ("French for 'thank you'?", "Merci", ["french", "politeness"], 0.2, 0.9, 22),
        
        # History cards
        ("When did World War II end?", "1945", ["history", "world-war"], 0.6, 0.5, 6),
        ("Who painted the Mona Lisa?", "Leonardo da Vinci", ["art", "renaissance"], 0.4, 0.7, 10),
        
        # Geography cards
        ("Capital of Japan?", "Tokyo", ["geography", "asia"], 0.3, 0.8, 18),
    ]
    
    for i, (question, answer, tags, difficulty, mastery, reviews) in enumerate(demo_cards):
        card = Flashcard(f"demo_{i+1}", question, answer, tags)
        card.difficulty = difficulty
        card.mastery_level = mastery
        card.review_count = reviews
        deck.add_flashcard(card)
    
    return deck


def demo_phase1_rich_quiz_interface():
    """Demo Phase 1: Rich Quiz Interface."""
    print("\n🎮 Phase 1 Demo: Rich Quiz Interface")
    print("=" * 50)
    
    ui = RichTerminalUI()
    quiz_interface = RichQuizInterface(ui.console)
    deck = create_comprehensive_demo_deck()
    
    ui.show_info("Demonstrating Rich Quiz Interface with beautiful Rich Terminal UI", "Phase 1")
    time.sleep(2)
    
    # Show quiz introduction
    quiz_interface._show_quiz_introduction(deck, QuizMode.SPACED_REPETITION, 3)
    time.sleep(3)
    
    ui.show_success("Rich Quiz Interface demo completed!", "Phase 1 Complete")
    
    return deck


def demo_phase2_rich_statistics_dashboard():
    """Demo Phase 2: Rich Statistics Dashboard."""
    print("\n📊 Phase 2 Demo: Rich Statistics Dashboard")
    print("=" * 50)
    
    ui = RichTerminalUI()
    stats_dashboard = RichStatisticsDashboard(ui.console)
    deck = create_comprehensive_demo_deck()
    
    ui.show_info("Demonstrating Rich Statistics Dashboard with comprehensive analytics", "Phase 2")
    time.sleep(2)
    
    # Show deck statistics
    stats_dashboard.show_deck_statistics(deck, detailed=True)
    time.sleep(4)
    
    # Show global statistics
    ui.show_info("Showing global statistics...", "Global Analytics")
    time.sleep(1)
    stats_dashboard.show_global_statistics([deck])
    time.sleep(3)
    
    ui.show_success("Rich Statistics Dashboard demo completed!", "Phase 2 Complete")
    
    return deck


def demo_phase3_ai_content_generation():
    """Demo Phase 3: AI Content Generation."""
    print("\n🤖 Phase 3 Demo: AI Content Generation")
    print("=" * 50)
    
    ui = RichTerminalUI()
    ai_interface = RichAIInterface(ui.console)
    ai_generator = AIContentGenerator()
    
    ui.show_info("Demonstrating AI Content Generation with intelligent flashcard creation", "Phase 3")
    time.sleep(2)
    
    # Demo AI content generation
    sample_text = """
    The Earth is the third planet from the Sun.
    Gravity is a force that attracts objects toward each other.
    The human heart has four chambers.
    Oxygen is essential for human life.
    """
    
    ui.show_info("Generating flashcards from sample text using AI...", "AI Generation")
    time.sleep(1)
    
    generated_content = ai_generator.generate_flashcards_from_text(sample_text, ContentType.FACTS, max_cards=3)
    
    if generated_content:
        # Display generated content
        for i, content in enumerate(generated_content, 1):
            ai_interface._display_content_for_review(content, i, len(generated_content))
            time.sleep(2)
    
    # Demo difficulty prediction
    test_card = Flashcard("ai_test", "What is quantum entanglement?", "A quantum mechanical phenomenon", ["physics", "quantum"])
    ui.show_info("Demonstrating AI difficulty prediction...", "AI Prediction")
    time.sleep(1)
    ai_interface.predict_card_difficulty(test_card)
    time.sleep(3)
    
    ui.show_success("AI Content Generation demo completed!", "Phase 3 Complete")


def demo_integrated_workflow():
    """Demo integrated workflow using all three phases."""
    print("\n🚀 Integrated Workflow Demo: All Phases Together")
    print("=" * 60)
    
    ui = RichTerminalUI()
    
    # Step 1: AI Content Generation
    ui.show_info("Step 1: Generate flashcards with AI", "Integrated Workflow")
    time.sleep(1)
    
    ai_generator = AIContentGenerator()
    sample_text = "Python is a programming language. Variables store data. Functions perform tasks."
    generated_content = ai_generator.generate_flashcards_from_text(sample_text, ContentType.DEFINITIONS, max_cards=2)
    
    # Create deck from AI content
    deck = Deck(name="AI Generated Programming Deck", description="Created with AI content generation")
    for i, content in enumerate(generated_content):
        card = Flashcard(f"ai_gen_{i+1}", content.question, content.answer, content.tags)
        card.difficulty = content.difficulty
        deck.add_flashcard(card)
    
    ui.show_success(f"Generated deck with {len(deck.flashcards)} AI-created cards", "AI Generation")
    time.sleep(2)
    
    # Step 2: View Statistics
    ui.show_info("Step 2: Analyze deck with Rich Statistics Dashboard", "Integrated Workflow")
    time.sleep(1)
    
    stats_dashboard = RichStatisticsDashboard(ui.console)
    stats_dashboard.show_deck_statistics(deck, detailed=False)
    time.sleep(3)
    
    # Step 3: Quiz Session
    ui.show_info("Step 3: Study with Rich Quiz Interface", "Integrated Workflow")
    time.sleep(1)
    
    quiz_interface = RichQuizInterface(ui.console)
    quiz_interface._show_quiz_introduction(deck, QuizMode.RANDOM, len(deck.flashcards))
    time.sleep(3)
    
    ui.show_success("Integrated workflow demo completed! All phases work together seamlessly.", "Workflow Complete")


def showcase_v1_8_5_features():
    """Showcase all v1.8.5 features in a comprehensive overview."""
    print("\n✨ FlashGenie v1.8.5 - Complete Feature Showcase")
    print("=" * 60)
    
    ui = RichTerminalUI()
    
    # Feature overview
    features_content = []
    features_content.append("🎉 [bold bright_blue]FlashGenie v1.8.5 - Complete Release[/bold bright_blue]")
    features_content.append("")
    features_content.append("🎮 [bold bright_green]Phase 1: Rich Quiz Interface[/bold bright_green]")
    features_content.append("  • Beautiful Rich Terminal UI quiz sessions")
    features_content.append("  • Interactive question display with progress tracking")
    features_content.append("  • Multiple quiz modes (spaced repetition, random, sequential)")
    features_content.append("  • Real-time feedback with Rich panels and formatting")
    features_content.append("  • Confidence tracking and difficulty adjustment")
    features_content.append("")
    features_content.append("📊 [bold bright_yellow]Phase 2: Rich Statistics Dashboard[/bold bright_yellow]")
    features_content.append("  • Comprehensive learning analytics with Rich formatting")
    features_content.append("  • Interactive charts and data visualization")
    features_content.append("  • Global statistics across all decks")
    features_content.append("  • Learning trends and progress tracking")
    features_content.append("  • Performance analysis with actionable insights")
    features_content.append("")
    features_content.append("🤖 [bold bright_cyan]Phase 3: AI Content Generation[/bold bright_cyan]")
    features_content.append("  • AI-powered flashcard generation from text")
    features_content.append("  • Intelligent difficulty prediction")
    features_content.append("  • Smart content suggestions and related topics")
    features_content.append("  • Automatic tag generation and categorization")
    features_content.append("  • Flashcard enhancement recommendations")
    features_content.append("")
    features_content.append("🌟 [bold bright_magenta]Enhanced User Experience[/bold bright_magenta]")
    features_content.append("  • Consistent Rich Terminal UI throughout the application")
    features_content.append("  • Seamless integration between all features")
    features_content.append("  • Beautiful error handling and user feedback")
    features_content.append("  • Professional appearance suitable for any environment")
    
    from rich.panel import Panel
    features_panel = Panel(
        "\n".join(features_content),
        title="✨ FlashGenie v1.8.5 Features",
        border_style="bright_blue",
        padding=(1, 2)
    )
    
    ui.console.print(features_panel)
    time.sleep(5)
    
    ui.show_success("FlashGenie v1.8.5 - The most advanced flashcard learning system!", "Complete Release")


def interactive_v1_8_5_demo():
    """Run an interactive demo of all FlashGenie v1.8.5 features."""
    print("\n🎮 Interactive FlashGenie v1.8.5 Demo")
    print("=" * 50)
    
    ui = RichTerminalUI()
    
    while True:
        try:
            options = [
                "Phase 1: Rich Quiz Interface Demo",
                "Phase 2: Rich Statistics Dashboard Demo",
                "Phase 3: AI Content Generation Demo",
                "Integrated Workflow Demo (All Phases)",
                "v1.8.5 Feature Showcase",
                "Complete System Test",
                "Exit Demo"
            ]
            
            print("\n📋 FlashGenie v1.8.5 Complete Demo Menu")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                demo_phase1_rich_quiz_interface()
            elif choice == "2":
                demo_phase2_rich_statistics_dashboard()
            elif choice == "3":
                demo_phase3_ai_content_generation()
            elif choice == "4":
                demo_integrated_workflow()
            elif choice == "5":
                showcase_v1_8_5_features()
            elif choice == "6":
                # Complete system test
                ui.show_info("Running complete FlashGenie v1.8.5 system test...", "System Test")
                demo_phase1_rich_quiz_interface()
                demo_phase2_rich_statistics_dashboard()
                demo_phase3_ai_content_generation()
                demo_integrated_workflow()
                showcase_v1_8_5_features()
                ui.show_success("Complete system test finished successfully!", "System Test Complete")
            elif choice == "7":
                ui.show_success("Thanks for exploring FlashGenie v1.8.5! 🎉", "Demo Complete")
                break
            else:
                ui.show_warning("Invalid choice. Please select 1-7.", "Invalid Input")
                
        except KeyboardInterrupt:
            ui.show_info("Demo interrupted. Goodbye! 👋", "Interrupted")
            break
        except Exception as e:
            ui.show_error(f"Demo error: {e}", "Error")


def main():
    """Main demo function."""
    print("🚀 FlashGenie v1.8.5 - Complete Release Demo")
    print("=" * 60)
    print("The Ultimate Rich Terminal UI Learning Experience")
    print("\nFlashGenie v1.8.5 represents a major milestone in flashcard learning:")
    print("\n🎮 Phase 1: Rich Quiz Interface")
    print("   Beautiful, interactive quiz sessions with Rich Terminal UI")
    print("\n📊 Phase 2: Rich Statistics Dashboard") 
    print("   Comprehensive analytics and progress tracking")
    print("\n🤖 Phase 3: AI Content Generation")
    print("   Intelligent flashcard creation and enhancement")
    print("\n✨ All phases work together seamlessly to provide the most")
    print("   advanced and beautiful flashcard learning experience available!")
    
    try:
        demo_choice = input("\n🎮 Would you like to run the interactive demo? (y/n): ").strip().lower()
        if demo_choice in ['y', 'yes']:
            interactive_v1_8_5_demo()
        else:
            print("\n🎬 Running automatic demo sequence...")
            showcase_v1_8_5_features()
            demo_phase1_rich_quiz_interface()
            demo_phase2_rich_statistics_dashboard()
            demo_phase3_ai_content_generation()
            demo_integrated_workflow()
            
            print("\n✅ FlashGenie v1.8.5 complete demo finished successfully!")
            print("🎉 All three phases working perfectly together!")
            print("\n💡 To use FlashGenie v1.8.5, run:")
            print("   python -m flashgenie")
            print("\n🎮 Try these new commands:")
            print("   FlashGenie > quiz      # Rich Quiz Interface")
            print("   FlashGenie > stats     # Rich Statistics Dashboard")
            print("   FlashGenie > ai        # AI Content Generation")
            print("   FlashGenie > generate  # AI Flashcard Generation")
            print("   FlashGenie > suggest   # AI Content Suggestions")
            print("   FlashGenie > enhance   # AI Card Enhancement")
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")


if __name__ == "__main__":
    main()
