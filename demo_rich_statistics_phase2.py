#!/usr/bin/env python3
"""
FlashGenie v1.8.5 Phase 2 - Rich Statistics Dashboard Demo

This script demonstrates the new Rich Statistics Dashboard with comprehensive
analytics, interactive charts, progress tracking, and detailed performance insights.
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from flashgenie.interfaces.terminal import RichTerminalUI, RichStatisticsDashboard
    from flashgenie.core.content_system.deck import Deck
    from flashgenie.core.content_system.flashcard import Flashcard
    print("✅ FlashGenie Rich Statistics Dashboard components loaded successfully!")
except ImportError as e:
    print(f"❌ Could not load FlashGenie Rich Statistics Dashboard: {e}")
    print("Please install dependencies: pip install rich textual prompt-toolkit")
    sys.exit(1)


def create_sample_decks() -> list[Deck]:
    """Create sample decks with realistic data for testing the Rich Statistics Dashboard."""
    decks = []
    
    # Deck 1: Spanish Vocabulary
    spanish_deck = Deck(name="Spanish Vocabulary", description="Common Spanish words and phrases")
    spanish_cards = [
        ("Hola", "Hello", ["greetings", "basic"], 0.2, 0.9, 15),
        ("Gracias", "Thank you", ["greetings", "basic"], 0.1, 0.95, 20),
        ("Por favor", "Please", ["greetings", "basic"], 0.3, 0.8, 12),
        ("¿Cómo estás?", "How are you?", ["questions", "greetings"], 0.4, 0.7, 8),
        ("Me llamo", "My name is", ["introductions"], 0.5, 0.6, 6),
        ("¿Dónde está?", "Where is?", ["questions", "directions"], 0.6, 0.5, 4),
        ("No entiendo", "I don't understand", ["communication"], 0.7, 0.4, 3),
        ("Disculpe", "Excuse me", ["politeness"], 0.8, 0.3, 2),
    ]
    
    for i, (question, answer, tags, difficulty, mastery, reviews) in enumerate(spanish_cards):
        card = Flashcard(f"spanish_{i+1}", question, answer, tags)
        card.difficulty = difficulty
        card.mastery_level = mastery
        card.review_count = reviews
        spanish_deck.add_flashcard(card)
    
    decks.append(spanish_deck)
    
    # Deck 2: Math Formulas
    math_deck = Deck(name="Math Formulas", description="Essential mathematical formulas")
    math_cards = [
        ("Area of circle", "πr²", ["geometry", "area"], 0.3, 0.85, 18),
        ("Quadratic formula", "x = (-b ± √(b²-4ac)) / 2a", ["algebra", "equations"], 0.8, 0.4, 5),
        ("Pythagorean theorem", "a² + b² = c²", ["geometry", "triangles"], 0.2, 0.9, 22),
        ("Slope formula", "(y₂-y₁)/(x₂-x₁)", ["algebra", "lines"], 0.4, 0.7, 10),
        ("Distance formula", "√[(x₂-x₁)² + (y₂-y₁)²]", ["geometry", "coordinates"], 0.6, 0.5, 7),
        ("Volume of sphere", "(4/3)πr³", ["geometry", "volume"], 0.5, 0.6, 9),
    ]
    
    for i, (question, answer, tags, difficulty, mastery, reviews) in enumerate(math_cards):
        card = Flashcard(f"math_{i+1}", question, answer, tags)
        card.difficulty = difficulty
        card.mastery_level = mastery
        card.review_count = reviews
        math_deck.add_flashcard(card)
    
    decks.append(math_deck)
    
    # Deck 3: Science Facts
    science_deck = Deck(name="Science Facts", description="Interesting scientific facts")
    science_cards = [
        ("Speed of light", "299,792,458 m/s", ["physics", "constants"], 0.7, 0.3, 3),
        ("Chemical symbol for gold", "Au", ["chemistry", "elements"], 0.2, 0.9, 25),
        ("Largest planet", "Jupiter", ["astronomy", "planets"], 0.1, 0.95, 30),
        ("DNA stands for", "Deoxyribonucleic acid", ["biology", "genetics"], 0.6, 0.5, 8),
        ("Boiling point of water", "100°C or 212°F", ["chemistry", "temperature"], 0.3, 0.8, 16),
    ]
    
    for i, (question, answer, tags, difficulty, mastery, reviews) in enumerate(science_cards):
        card = Flashcard(f"science_{i+1}", question, answer, tags)
        card.difficulty = difficulty
        card.mastery_level = mastery
        card.review_count = reviews
        science_deck.add_flashcard(card)
    
    decks.append(science_deck)
    
    return decks


def demo_deck_statistics():
    """Demo deck-specific statistics dashboard."""
    print("\n📊 Demo: Deck Statistics Dashboard")
    print("=" * 40)
    
    ui = RichTerminalUI()
    stats_dashboard = RichStatisticsDashboard(ui.console)
    decks = create_sample_decks()
    
    for deck in decks:
        ui.show_info(f"Showing statistics for '{deck.name}'...", "Deck Statistics")
        time.sleep(1)
        
        # Show detailed statistics
        stats_dashboard.show_deck_statistics(deck, detailed=True)
        time.sleep(3)
        
        ui.show_success(f"Statistics for '{deck.name}' displayed!", "Stats Complete")
        time.sleep(1)


def demo_global_statistics():
    """Demo global statistics across all decks."""
    print("\n🌍 Demo: Global Statistics Dashboard")
    print("=" * 40)
    
    ui = RichTerminalUI()
    stats_dashboard = RichStatisticsDashboard(ui.console)
    decks = create_sample_decks()
    
    ui.show_info("Showing global statistics across all decks...", "Global Statistics")
    time.sleep(1)
    
    stats_dashboard.show_global_statistics(decks)
    time.sleep(3)
    
    ui.show_success("Global statistics displayed!", "Global Stats Complete")


def demo_learning_trends():
    """Demo learning trends and progress tracking."""
    print("\n📈 Demo: Learning Trends Dashboard")
    print("=" * 40)
    
    ui = RichTerminalUI()
    stats_dashboard = RichStatisticsDashboard(ui.console)
    decks = create_sample_decks()
    
    for deck in decks[:2]:  # Show trends for first 2 decks
        ui.show_info(f"Showing learning trends for '{deck.name}'...", "Learning Trends")
        time.sleep(1)
        
        stats_dashboard.show_learning_trends(deck, days=30)
        time.sleep(3)
        
        ui.show_success(f"Trends for '{deck.name}' displayed!", "Trends Complete")
        time.sleep(1)


def demo_performance_analysis():
    """Demo detailed performance analysis."""
    print("\n🎯 Demo: Performance Analysis Dashboard")
    print("=" * 40)
    
    ui = RichTerminalUI()
    stats_dashboard = RichStatisticsDashboard(ui.console)
    decks = create_sample_decks()
    
    for deck in decks[:2]:  # Show performance for first 2 decks
        ui.show_info(f"Showing performance analysis for '{deck.name}'...", "Performance Analysis")
        time.sleep(1)
        
        stats_dashboard.show_performance_analysis(deck)
        time.sleep(3)
        
        ui.show_success(f"Performance analysis for '{deck.name}' displayed!", "Analysis Complete")
        time.sleep(1)


def demo_statistics_features():
    """Demo various statistics features."""
    print("\n🔍 Demo: Statistics Features")
    print("=" * 40)
    
    ui = RichTerminalUI()
    stats_dashboard = RichStatisticsDashboard(ui.console)
    decks = create_sample_decks()
    
    # Demo simple overview
    ui.show_info("Testing simple overview mode...", "Simple Overview")
    time.sleep(1)
    
    stats_dashboard.show_deck_statistics(decks[0], detailed=False)
    time.sleep(3)
    
    # Demo detailed view
    ui.show_info("Testing detailed statistics mode...", "Detailed View")
    time.sleep(1)
    
    stats_dashboard.show_deck_statistics(decks[0], detailed=True)
    time.sleep(3)
    
    ui.show_success("Statistics features demo completed!", "Features Complete")


def demo_interactive_statistics():
    """Demo interactive statistics with user choices."""
    print("\n🎮 Demo: Interactive Statistics")
    print("=" * 40)
    
    ui = RichTerminalUI()
    stats_dashboard = RichStatisticsDashboard(ui.console)
    decks = create_sample_decks()
    
    # Simulate interactive choices
    choices = [
        ("Deck Overview", lambda: stats_dashboard.show_deck_statistics(decks[0], detailed=False)),
        ("Detailed Analysis", lambda: stats_dashboard.show_deck_statistics(decks[0], detailed=True)),
        ("Global Statistics", lambda: stats_dashboard.show_global_statistics(decks)),
        ("Learning Trends", lambda: stats_dashboard.show_learning_trends(decks[0])),
        ("Performance Analysis", lambda: stats_dashboard.show_performance_analysis(decks[0]))
    ]
    
    for choice_name, choice_func in choices:
        ui.show_info(f"Demonstrating: {choice_name}", "Interactive Demo")
        time.sleep(1)
        
        try:
            choice_func()
            time.sleep(2)
            ui.show_success(f"{choice_name} completed!", "Demo Success")
        except Exception as e:
            ui.show_error(f"Demo error: {e}", "Demo Error")
        
        time.sleep(1)


def interactive_statistics_demo():
    """Run an interactive demo of the Rich Statistics Dashboard."""
    print("\n🎮 Interactive Rich Statistics Demo")
    print("=" * 50)
    
    ui = RichTerminalUI()
    
    while True:
        try:
            options = [
                "Deck Statistics Dashboard",
                "Global Statistics Dashboard",
                "Learning Trends Dashboard",
                "Performance Analysis Dashboard",
                "Statistics Features Demo",
                "Interactive Statistics Demo",
                "Exit Demo"
            ]
            
            print("\n📋 Rich Statistics Dashboard Demo Menu")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                demo_deck_statistics()
            elif choice == "2":
                demo_global_statistics()
            elif choice == "3":
                demo_learning_trends()
            elif choice == "4":
                demo_performance_analysis()
            elif choice == "5":
                demo_statistics_features()
            elif choice == "6":
                demo_interactive_statistics()
            elif choice == "7":
                ui.show_success("Thanks for exploring the FlashGenie Rich Statistics Dashboard! 🎉", "Demo Complete")
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
    print("🚀 FlashGenie v1.8.5 Phase 2 - Rich Statistics Dashboard Demo")
    print("=" * 70)
    print("Comprehensive Analytics with Rich Terminal UI")
    print("\nThis demo showcases the new Rich Statistics Dashboard features:")
    print("• Beautiful Rich Terminal UI statistics displays")
    print("• Comprehensive deck analytics with progress tracking")
    print("• Global statistics across all decks")
    print("• Learning trends and progress visualization")
    print("• Detailed performance analysis and insights")
    print("• Interactive charts and data visualization")
    print("• Rich formatting with panels, tables, and progress bars")
    
    try:
        demo_choice = input("\n🎮 Would you like to run the interactive demo? (y/n): ").strip().lower()
        if demo_choice in ['y', 'yes']:
            interactive_statistics_demo()
        else:
            print("\n🎬 Running automatic demo sequence...")
            demo_deck_statistics()
            demo_global_statistics()
            demo_learning_trends()
            demo_performance_analysis()
            demo_statistics_features()
            demo_interactive_statistics()
            
            print("\n✅ Rich Statistics Dashboard demo completed successfully!")
            print("🎉 FlashGenie v1.8.5 Phase 2 is ready!")
            print("\n💡 To test the actual Rich Statistics Dashboard, run:")
            print("   python -m flashgenie")
            print("   FlashGenie > load 'Your Deck'")
            print("   FlashGenie > stats --detailed")
            print("   FlashGenie > stats --global")
            print("   FlashGenie > stats --trends")
            print("   FlashGenie > stats --performance")
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")


if __name__ == "__main__":
    main()
