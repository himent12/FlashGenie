#!/usr/bin/env python3
"""
FlashGenie v1.8.3 Phase 2 Demo - Interactive Widgets & Developer Tools

This script demonstrates the Phase 2 enhancements including interactive widgets,
developer tools, debugging features, and advanced search capabilities.
"""

import sys
import time
import random
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from flashgenie.interfaces.terminal import RichTerminalUI, DebugConsole, FuzzySearchEngine
    print("✅ FlashGenie Phase 2 components loaded successfully!")
except ImportError as e:
    print(f"❌ Could not load FlashGenie Phase 2 components: {e}")
    print("Please install dependencies: pip install rich textual prompt-toolkit psutil")
    sys.exit(1)


def demo_interactive_widgets():
    """Demo interactive widgets and controls."""
    print("\n🎮 Demo: Interactive Widgets")
    print("=" * 40)
    
    ui = RichTerminalUI()
    
    # Demo multi-select menu
    ui.show_info("Demonstrating multi-select menu...", "Interactive Widgets")
    
    options = [
        "Spanish Vocabulary",
        "Math Formulas", 
        "History Facts",
        "Programming Terms",
        "Science Concepts"
    ]
    
    print("\n📋 Multi-Select Menu Demo")
    print("(Simulated - in real use, this would be fully interactive)")
    
    # Simulate selection
    selected = [0, 2, 4]  # Simulate user selecting items 1, 3, 5
    
    selected_names = [options[i] for i in selected]
    ui.show_success(f"Selected decks: {', '.join(selected_names)}", "Selection Complete")
    
    # Demo form builder
    ui.show_info("Demonstrating form builder...", "Interactive Widgets")
    
    form_fields = {
        "deck_name": {
            "type": "text",
            "prompt": "Enter deck name",
            "required": True,
            "default": "My New Deck"
        },
        "difficulty": {
            "type": "choice",
            "prompt": "Select difficulty level",
            "choices": ["Easy", "Medium", "Hard"],
            "default": "Medium"
        },
        "max_cards": {
            "type": "int",
            "prompt": "Maximum cards per session",
            "default": 20,
            "validation": {"min": 1, "max": 100}
        },
        "enable_hints": {
            "type": "bool",
            "prompt": "Enable hints during quiz",
            "default": True
        }
    }
    
    print("\n📝 Form Builder Demo")
    print("(Simulated form data)")
    
    # Simulate form results
    form_results = {
        "deck_name": "Advanced Spanish",
        "difficulty": "Medium",
        "max_cards": 25,
        "enable_hints": True
    }
    
    ui.show_success(f"Form completed: {form_results}", "Form Results")


def demo_developer_tools():
    """Demo developer tools and debugging features."""
    print("\n🔧 Demo: Developer Tools")
    print("=" * 40)
    
    ui = RichTerminalUI()
    
    # Enable debug mode
    ui.toggle_debug_mode()
    
    # Demo object watching
    sample_data = {
        "decks": ["Spanish", "Math", "History"],
        "current_session": {"cards_studied": 15, "accuracy": 0.87},
        "user_stats": {"total_time": 3600, "streak": 7}
    }
    
    ui.watch_object("sample_data", sample_data)
    ui.watch_object("demo_list", [1, 2, 3, 4, 5])
    
    # Demo object inspection
    ui.inspect_object(sample_data, "sample_data")
    
    # Demo memory profiling
    memory_info = ui.memory_profile()
    ui.show_info(f"Memory usage: {memory_info['rss_mb']:.1f} MB", "Memory Profile")
    
    # Demo function profiling
    ui.enable_profiling()
    
    @ui.profile_function
    def sample_function():
        """Sample function for profiling demo."""
        time.sleep(0.1)  # Simulate work
        return "completed"
    
    # Run profiled function
    result = sample_function()
    ui.show_success(f"Profiled function result: {result}", "Function Profiling")
    
    # Show debug panel
    ui.show_debug_panel()


def demo_advanced_search():
    """Demo advanced search and filtering."""
    print("\n🔍 Demo: Advanced Search")
    print("=" * 40)
    
    ui = RichTerminalUI()
    
    # Sample data for searching
    sample_decks = [
        {"name": "Spanish Vocabulary", "cards": 245, "category": "Language", "difficulty": "Medium", "tags": ["spanish", "vocabulary", "language"]},
        {"name": "Math Formulas", "cards": 89, "category": "Mathematics", "difficulty": "Hard", "tags": ["math", "formulas", "algebra"]},
        {"name": "History Facts", "cards": 156, "category": "History", "difficulty": "Easy", "tags": ["history", "facts", "world"]},
        {"name": "Programming Terms", "cards": 203, "category": "Technology", "difficulty": "Medium", "tags": ["programming", "coding", "tech"]},
        {"name": "Science Concepts", "cards": 134, "category": "Science", "difficulty": "Hard", "tags": ["science", "physics", "chemistry"]},
        {"name": "French Phrases", "cards": 178, "category": "Language", "difficulty": "Medium", "tags": ["french", "phrases", "language"]},
        {"name": "Geography Quiz", "cards": 92, "category": "Geography", "difficulty": "Easy", "tags": ["geography", "countries", "capitals"]}
    ]
    
    # Demo fuzzy search
    search_engine = FuzzySearchEngine()
    
    # Set field weights (name is more important than tags)
    search_engine.set_field_weights({
        "name": 2.0,
        "category": 1.5,
        "tags": 1.0
    })
    
    # Demo searches
    search_queries = ["spanish", "math", "prog", "lang"]
    
    for query in search_queries:
        results = search_engine.search(
            sample_decks, 
            query, 
            ["name", "category", "tags"],
            max_results=3
        )
        
        ui.show_info(f"Search '{query}' found {len(results)} results", "Search Results")
        
        if results:
            # Show top result
            top_result = results[0]
            result_text = f"Top match: {top_result.item['name']} (score: {top_result.score:.2f})"
            ui.show_success(result_text, "Best Match")
    
    # Demo filtering
    ui.show_info("Demonstrating filtering capabilities...", "Advanced Search")
    
    # Filter by difficulty
    hard_decks = [deck for deck in sample_decks if deck["difficulty"] == "Hard"]
    ui.show_success(f"Hard difficulty decks: {len(hard_decks)}", "Filter Results")
    
    # Filter by category
    language_decks = [deck for deck in sample_decks if deck["category"] == "Language"]
    ui.show_success(f"Language decks: {len(language_decks)}", "Filter Results")


def demo_progress_dashboard():
    """Demo progress dashboard and monitoring."""
    print("\n📊 Demo: Progress Dashboard")
    print("=" * 40)
    
    ui = RichTerminalUI()
    
    # Sample progress data
    tasks = {
        "Importing Spanish Deck": {"current": 245, "total": 245, "status": "complete"},
        "Processing Math Cards": {"current": 67, "total": 89, "status": "running"},
        "Analyzing History Data": {"current": 23, "total": 156, "status": "running"},
        "Generating Quiz Questions": {"current": 0, "total": 50, "status": "error"},
        "Updating Statistics": {"current": 8, "total": 10, "status": "running"}
    }
    
    # Create and display dashboard
    dashboard = ui.widgets.create_progress_dashboard(tasks, "FlashGenie Processing Dashboard")
    
    dashboard_panel = Panel(
        dashboard,
        title="📊 Live Progress Dashboard",
        border_style="bright_blue",
        padding=(1, 2)
    )
    
    ui.console.print(dashboard_panel)
    
    ui.show_success("Progress dashboard displayed successfully!", "Dashboard Demo")


def interactive_phase2_demo():
    """Run an interactive demo of Phase 2 features."""
    print("\n🎮 Interactive Phase 2 Demo")
    print("=" * 50)
    
    ui = RichTerminalUI()
    
    while True:
        try:
            options = [
                "Interactive Widgets Demo",
                "Developer Tools Demo",
                "Advanced Search Demo",
                "Progress Dashboard Demo",
                "Exit Demo"
            ]
            
            print("\n📋 Phase 2 Feature Demo Menu")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                demo_interactive_widgets()
            elif choice == "2":
                demo_developer_tools()
            elif choice == "3":
                demo_advanced_search()
            elif choice == "4":
                demo_progress_dashboard()
            elif choice == "5":
                ui.show_success("Thanks for exploring FlashGenie v1.8.3 Phase 2! 🚀", "Demo Complete")
                break
            else:
                ui.show_warning("Invalid choice. Please select 1-5.", "Invalid Input")
                
        except KeyboardInterrupt:
            ui.show_info("Demo interrupted. Goodbye! 👋", "Interrupted")
            break
        except Exception as e:
            ui.show_error(f"Demo error: {e}", "Error")


def main():
    """Main demo function."""
    print("🚀 FlashGenie v1.8.3 Phase 2 Demo")
    print("=" * 50)
    print("Phase 2: Interactive Widgets & Developer Tools")
    print("\nThis demo showcases the advanced features added in Phase 2:")
    print("• Interactive widgets and controls")
    print("• Developer tools and debugging")
    print("• Advanced search and filtering")
    print("• Progress monitoring and dashboards")
    
    try:
        demo_choice = input("\n🎮 Would you like to run the interactive demo? (y/n): ").strip().lower()
        if demo_choice in ['y', 'yes']:
            interactive_phase2_demo()
        else:
            print("\n🎬 Running automatic demo sequence...")
            demo_interactive_widgets()
            demo_developer_tools()
            demo_advanced_search()
            demo_progress_dashboard()
            
            print("\n✅ Phase 2 demo completed successfully!")
            print("🎉 FlashGenie v1.8.3 Phase 2 is ready to enhance your development experience!")
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")


if __name__ == "__main__":
    main()
