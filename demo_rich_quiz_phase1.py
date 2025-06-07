#!/usr/bin/env python3
"""
FlashGenie v1.8.5 Phase 1 - Rich Quiz Interface Demo

This script demonstrates the new Rich Quiz Interface with beautiful
Rich Terminal UI formatting, interactive question display, and real-time progress tracking.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from flashgenie.interfaces.terminal import RichTerminalUI, RichQuizInterface
    from flashgenie.core.content_system.deck import Deck
    from flashgenie.core.content_system.flashcard import Flashcard
    from flashgenie.core.study_system.quiz_engine import QuizMode
    print("✅ FlashGenie Rich Quiz Interface components loaded successfully!")
except ImportError as e:
    print(f"❌ Could not load FlashGenie Rich Quiz Interface: {e}")
    print("Please install dependencies: pip install rich textual prompt-toolkit")
    sys.exit(1)


def create_sample_deck() -> Deck:
    """Create a sample deck for testing the Rich Quiz Interface."""
    deck = Deck(name="Rich Quiz Demo Deck", description="Sample deck for testing Rich Quiz Interface")
    
    # Add sample flashcards
    sample_cards = [
        ("What is the capital of France?", "Paris", ["geography", "europe"], 0.3),
        ("What is 2 + 2?", "4", ["math", "basic"], 0.1),
        ("Who wrote Romeo and Juliet?", "William Shakespeare", ["literature", "shakespeare"], 0.5),
        ("What is the largest planet in our solar system?", "Jupiter", ["astronomy", "planets"], 0.4),
        ("What is the chemical symbol for water?", "H2O", ["chemistry", "molecules"], 0.3),
        ("In which year did World War II end?", "1945", ["history", "world-war"], 0.6),
        ("What is the speed of light?", "299,792,458 m/s", ["physics", "constants"], 0.8),
        ("Who painted the Mona Lisa?", "Leonardo da Vinci", ["art", "renaissance"], 0.4),
        ("What is the smallest unit of matter?", "Atom", ["chemistry", "physics"], 0.5),
        ("Which programming language is known for 'Hello, World!'?", "C", ["programming", "languages"], 0.7)
    ]
    
    for i, (question, answer, tags, difficulty) in enumerate(sample_cards):
        card = Flashcard(
            card_id=f"demo_card_{i+1}",
            question=question,
            answer=answer,
            tags=tags
        )
        card.difficulty = difficulty
        deck.add_flashcard(card)
    
    return deck


def demo_rich_quiz_interface():
    """Demo the Rich Quiz Interface functionality."""
    print("\n🎮 Demo: Rich Quiz Interface")
    print("=" * 40)
    
    # Initialize Rich UI and quiz interface
    ui = RichTerminalUI()
    quiz_interface = RichQuizInterface(ui.console)
    
    # Create sample deck
    deck = create_sample_deck()
    
    ui.show_info("Created sample deck with 10 flashcards", "Setup")
    time.sleep(1)
    
    # Demo different quiz modes
    quiz_modes = [
        (QuizMode.SPACED_REPETITION, "Spaced Repetition"),
        (QuizMode.RANDOM, "Random Order"),
        (QuizMode.SEQUENTIAL, "Sequential Order"),
        (QuizMode.DIFFICULT_FIRST, "Difficult First")
    ]
    
    for mode, mode_name in quiz_modes:
        ui.show_info(f"Testing {mode_name} quiz mode...", "Quiz Mode Test")
        time.sleep(1)
        
        try:
            # Start a short quiz session (3 cards)
            results = quiz_interface.start_quiz_session(
                deck=deck,
                mode=mode,
                card_count=3,
                timed=False
            )
            
            ui.show_success(f"{mode_name} quiz completed!", "Quiz Complete")
            time.sleep(2)
            
        except KeyboardInterrupt:
            ui.show_warning("Quiz interrupted by user", "Interrupted")
            break
        except Exception as e:
            ui.show_error(f"Quiz error: {e}", "Error")


def demo_quiz_features():
    """Demo specific quiz features."""
    print("\n🎯 Demo: Quiz Features")
    print("=" * 40)
    
    ui = RichTerminalUI()
    quiz_interface = RichQuizInterface(ui.console)
    deck = create_sample_deck()
    
    # Demo timed mode
    ui.show_info("Testing timed quiz mode...", "Timed Quiz Test")
    time.sleep(1)
    
    try:
        results = quiz_interface.start_quiz_session(
            deck=deck,
            mode=QuizMode.RANDOM,
            card_count=2,
            timed=True,
            time_limit=15
        )
        
        ui.show_success("Timed quiz completed!", "Timed Quiz Complete")
        
    except KeyboardInterrupt:
        ui.show_warning("Timed quiz interrupted", "Interrupted")
    except Exception as e:
        ui.show_error(f"Timed quiz error: {e}", "Error")


def demo_quiz_customization():
    """Demo quiz customization options."""
    print("\n🎨 Demo: Quiz Customization")
    print("=" * 40)
    
    ui = RichTerminalUI()
    quiz_interface = RichQuizInterface(ui.console)
    deck = create_sample_deck()
    
    # Demo customized quiz
    ui.show_info("Testing customized quiz settings...", "Customization Test")
    time.sleep(1)
    
    try:
        results = quiz_interface.start_quiz_session(
            deck=deck,
            mode=QuizMode.DIFFICULT_FIRST,
            card_count=3,
            show_hints=True,
            show_tags=True,
            show_difficulty=True
        )
        
        ui.show_success("Customized quiz completed!", "Customization Complete")
        
    except KeyboardInterrupt:
        ui.show_warning("Customized quiz interrupted", "Interrupted")
    except Exception as e:
        ui.show_error(f"Customized quiz error: {e}", "Error")


def demo_quiz_statistics():
    """Demo quiz statistics and feedback."""
    print("\n📊 Demo: Quiz Statistics")
    print("=" * 40)
    
    ui = RichTerminalUI()
    
    # Show sample statistics
    sample_stats = {
        'total_cards': 10,
        'correct_answers': 7,
        'incorrect_answers': 2,
        'skipped_cards': 1,
        'accuracy': 77.8,
        'average_confidence': 3.4,
        'difficulty_adjustments': 3,
        'session_duration': '5m 23s'
    }
    
    # Create statistics panel
    stats_content = []
    stats_content.append("🎉 [bold bright_green]Quiz Session Complete![/bold bright_green]")
    stats_content.append("")
    stats_content.append("📊 [bold]Results Summary:[/bold]")
    stats_content.append(f"  ✅ Correct: {sample_stats['correct_answers']}")
    stats_content.append(f"  ❌ Incorrect: {sample_stats['incorrect_answers']}")
    stats_content.append(f"  ⏭️  Skipped: {sample_stats['skipped_cards']}")
    stats_content.append(f"  🎯 Accuracy: {sample_stats['accuracy']:.1f}%")
    stats_content.append("")
    stats_content.append("⏱️  [bold]Performance:[/bold]")
    stats_content.append(f"  📅 Duration: {sample_stats['session_duration']}")
    stats_content.append(f"  ⭐ Avg Confidence: {sample_stats['average_confidence']:.1f}/5")
    stats_content.append(f"  🔧 Difficulty Adjustments: {sample_stats['difficulty_adjustments']}")
    
    from rich.panel import Panel
    stats_panel = Panel(
        "\n".join(stats_content),
        title="🏆 Quiz Statistics Demo",
        border_style="bright_green",
        padding=(1, 2)
    )
    
    ui.console.print(stats_panel)
    ui.show_success("Statistics demo completed!", "Demo Complete")


def interactive_quiz_demo():
    """Run an interactive demo of the Rich Quiz Interface."""
    print("\n🎮 Interactive Rich Quiz Demo")
    print("=" * 50)
    
    ui = RichTerminalUI()
    
    while True:
        try:
            options = [
                "Rich Quiz Interface Demo",
                "Quiz Features Demo",
                "Quiz Customization Demo", 
                "Quiz Statistics Demo",
                "Full Interactive Quiz",
                "Exit Demo"
            ]
            
            print("\n📋 Rich Quiz Interface Demo Menu")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                demo_rich_quiz_interface()
            elif choice == "2":
                demo_quiz_features()
            elif choice == "3":
                demo_quiz_customization()
            elif choice == "4":
                demo_quiz_statistics()
            elif choice == "5":
                # Full interactive quiz
                deck = create_sample_deck()
                quiz_interface = RichQuizInterface(ui.console)
                ui.show_info("Starting full interactive quiz...", "Interactive Quiz")
                
                try:
                    results = quiz_interface.start_quiz_session(
                        deck=deck,
                        mode=QuizMode.SPACED_REPETITION,
                        card_count=5
                    )
                    ui.show_success("Interactive quiz completed!", "Quiz Complete")
                except KeyboardInterrupt:
                    ui.show_warning("Quiz interrupted", "Interrupted")
                    
            elif choice == "6":
                ui.show_success("Thanks for exploring the FlashGenie Rich Quiz Interface! 🎉", "Demo Complete")
                break
            else:
                ui.show_warning("Invalid choice. Please select 1-6.", "Invalid Input")
                
        except KeyboardInterrupt:
            ui.show_info("Demo interrupted. Goodbye! 👋", "Interrupted")
            break
        except Exception as e:
            ui.show_error(f"Demo error: {e}", "Error")


def main():
    """Main demo function."""
    print("🚀 FlashGenie v1.8.5 Phase 1 - Rich Quiz Interface Demo")
    print("=" * 60)
    print("Enhanced Quiz Experience with Rich Terminal UI")
    print("\nThis demo showcases the new Rich Quiz Interface features:")
    print("• Beautiful Rich Terminal UI quiz sessions")
    print("• Interactive question display with progress tracking")
    print("• Real-time feedback with Rich panels and formatting")
    print("• Multiple quiz modes (spaced repetition, random, sequential, difficult)")
    print("• Timed quiz mode with countdown")
    print("• Confidence tracking and difficulty adjustment")
    print("• Rich statistics and completion summaries")
    
    try:
        demo_choice = input("\n🎮 Would you like to run the interactive demo? (y/n): ").strip().lower()
        if demo_choice in ['y', 'yes']:
            interactive_quiz_demo()
        else:
            print("\n🎬 Running automatic demo sequence...")
            demo_rich_quiz_interface()
            demo_quiz_features()
            demo_quiz_customization()
            demo_quiz_statistics()
            
            print("\n✅ Rich Quiz Interface demo completed successfully!")
            print("🎉 FlashGenie v1.8.5 Phase 1 is ready!")
            print("\n💡 To test the actual Rich Quiz Interface, run:")
            print("   python -m flashgenie")
            print("   FlashGenie > load 'Your Deck'")
            print("   FlashGenie > quiz")
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")


if __name__ == "__main__":
    main()
