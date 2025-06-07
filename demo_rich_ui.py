#!/usr/bin/env python3
"""
FlashGenie v1.8.3 Rich Terminal UI Demo

This script demonstrates the new Rich Terminal UI features in a simple,
interactive way without requiring the full FlashGenie setup.
"""

import sys
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from flashgenie.interfaces.terminal import RichTerminalUI
    print("✅ FlashGenie Rich UI loaded successfully!")
except ImportError as e:
    print(f"❌ Could not load FlashGenie Rich UI: {e}")
    print("Please install dependencies: pip install rich textual prompt-toolkit")
    sys.exit(1)


def demo_welcome():
    """Demo the welcome screen."""
    print("\n🎬 Demo: Welcome Screen")
    print("=" * 40)
    
    ui = RichTerminalUI()
    ui.show_welcome_screen()


def demo_messages():
    """Demo different message types."""
    print("\n🎬 Demo: Message Types")
    print("=" * 40)
    
    ui = RichTerminalUI()
    
    ui.show_success("Import completed successfully! 245 cards added to your deck.", "Import Success")
    time.sleep(1)
    
    ui.show_info("Your next review session is scheduled for tomorrow at 9:00 AM.", "Study Reminder")
    time.sleep(1)
    
    ui.show_warning("You have 23 cards due for review. Consider starting a study session.", "Due Cards")
    time.sleep(1)
    
    ui.show_error("Could not connect to the plugin marketplace. Please check your internet connection.", "Connection Error")


def demo_themes():
    """Demo the theme system."""
    print("\n🎬 Demo: Theme System")
    print("=" * 40)
    
    ui = RichTerminalUI()
    themes = ui.theme_manager.list_themes()
    
    for theme in themes:
        print(f"\n🎨 Switching to '{theme}' theme...")
        ui.set_theme(theme)
        ui.show_info(f"This is how the interface looks in the '{theme}' theme.", f"Theme: {theme}")
        time.sleep(1.5)


def demo_widgets():
    """Demo the widget system."""
    print("\n🎬 Demo: Widgets & Tables")
    print("=" * 40)
    
    ui = RichTerminalUI()
    
    # Demo table
    headers = ["Deck Name", "Cards", "Due", "Accuracy", "Last Study"]
    rows = [
        ["Spanish Vocabulary", "245", "23", "87%", "2 hours ago"],
        ["Math Formulas", "89", "5", "92%", "1 day ago"],
        ["History Facts", "156", "12", "79%", "3 hours ago"],
        ["Programming Terms", "203", "8", "94%", "30 minutes ago"],
        ["Science Concepts", "134", "0", "88%", "1 week ago"]
    ]
    
    table = ui.widgets.create_table("📚 Your Flashcard Decks", headers, rows)
    ui.console.print(table)
    
    time.sleep(2)
    
    # Demo stats panel
    stats = {
        "Total Decks": 5,
        "Total Cards": 827,
        "Cards Due": 48,
        "Overall Accuracy": 0.88,
        "Study Streak": "7 days",
        "Time Studied Today": "45 minutes"
    }
    
    stats_panel = ui.widgets.create_stats_panel(stats, "Learning Statistics")
    ui.console.print(stats_panel)
    
    time.sleep(2)
    
    # Demo flashcard display
    card_panel = ui.widgets.create_card_display(
        question="What is the capital of France?",
        answer="Paris",
        hint="It's known as the City of Light and is famous for the Eiffel Tower",
        tags=["Geography", "Europe", "Capitals", "France"],
        difficulty=0.3
    )
    ui.console.print(card_panel)


def demo_navigation():
    """Demo the navigation system."""
    print("\n🎬 Demo: Navigation System")
    print("=" * 40)
    
    ui = RichTerminalUI()
    nav = ui.navigation
    
    # Simulate navigation through the app
    contexts = [
        ("home", "FlashGenie Home", {}),
        ("decks", "Deck Library", {"total_decks": 5}),
        ("spanish_deck", "Spanish Vocabulary", {"cards": 245, "due": 23}),
        ("quiz", "Quiz Session", {"question": 12, "total": 20, "accuracy": 0.85})
    ]
    
    for name, display_name, data in contexts:
        nav.push_context(name, display_name, data)
        breadcrumbs = nav.render_breadcrumbs()
        current = nav.get_current_context()
        
        ui.show_info(
            f"Current location: {current.display_name}\n"
            f"Breadcrumbs: {breadcrumbs}\n"
            f"Context data: {current.data}",
            "Navigation Update"
        )
        time.sleep(1.5)


def interactive_demo():
    """Run an interactive demo."""
    print("\n🎮 Interactive Demo")
    print("=" * 40)
    
    ui = RichTerminalUI()
    
    while True:
        try:
            print("\n📋 Choose a demo:")
            print("  1. Welcome Screen")
            print("  2. Message Types")
            print("  3. Theme System")
            print("  4. Widgets & Tables")
            print("  5. Navigation System")
            print("  6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                demo_welcome()
            elif choice == "2":
                demo_messages()
            elif choice == "3":
                demo_themes()
            elif choice == "4":
                demo_widgets()
            elif choice == "5":
                demo_navigation()
            elif choice == "6":
                ui.show_success("Thanks for exploring FlashGenie v1.8.3 Rich UI! 🎉", "Demo Complete")
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
    print("🚀 FlashGenie v1.8.3 Rich Terminal UI Demo")
    print("=" * 50)
    print("This demo showcases the new Rich Terminal UI features")
    print("that make FlashGenie's command-line interface beautiful and interactive.")
    
    try:
        demo_choice = input("\n🎮 Would you like to run the interactive demo? (y/n): ").strip().lower()
        if demo_choice in ['y', 'yes']:
            interactive_demo()
        else:
            print("\n🎬 Running automatic demo sequence...")
            demo_welcome()
            demo_messages()
            demo_themes()
            demo_widgets()
            demo_navigation()
            
            print("\n✅ Demo completed successfully!")
            print("🎉 FlashGenie v1.8.3 Rich Terminal UI is ready to transform your learning experience!")
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")


if __name__ == "__main__":
    main()
