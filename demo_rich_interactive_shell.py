#!/usr/bin/env python3
"""
FlashGenie v1.8.4 Rich Interactive Shell Demo

This script demonstrates the enhanced interactive shell with Rich Terminal UI,
showing how the beautiful formatting now works inside the FlashGenie shell.
"""

import sys
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from flashgenie.interfaces.cli.rich_command_handler import RichCommandHandler
    from flashgenie.interfaces.terminal import RichTerminalUI
    print("✅ FlashGenie Rich Interactive Shell components loaded successfully!")
except ImportError as e:
    print(f"❌ Could not load FlashGenie Rich Interactive Shell: {e}")
    print("Please install dependencies: pip install rich textual prompt-toolkit")
    sys.exit(1)


def demo_rich_command_handler():
    """Demo the Rich command handler functionality."""
    print("\n🎨 Demo: Rich Command Handler")
    print("=" * 40)
    
    # Initialize Rich UI and command handler
    ui = RichTerminalUI()
    handler = RichCommandHandler(ui)
    
    # Demo commands
    commands_to_test = [
        ("help", []),
        ("help", ["import"]),
        ("search", ["import"]),
        ("list", []),
        ("accessibility", ["--status"]),
        ("debug", ["--enable"]),
        ("performance", ["--dashboard"]),
    ]
    
    for command, args in commands_to_test:
        ui.show_info(f"Testing command: {command} {' '.join(args)}", "Command Test")
        time.sleep(1)
        
        try:
            handler.handle_command(command, args)
            time.sleep(2)
        except Exception as e:
            ui.show_error(f"Command failed: {e}", "Error")
        
        print()  # Add spacing


def demo_interactive_features():
    """Demo interactive features of the Rich shell."""
    print("\n🎮 Demo: Interactive Features")
    print("=" * 40)
    
    ui = RichTerminalUI()
    handler = RichCommandHandler(ui)
    
    # Demo error handling
    ui.show_info("Testing error handling with invalid command...", "Error Handling Test")
    handler.handle_command("invalid_command", [])
    time.sleep(2)
    
    # Demo help system integration
    ui.show_info("Testing integrated help system...", "Help System Test")
    handler.handle_command("help", [])
    time.sleep(2)
    
    # Demo search functionality
    ui.show_info("Testing command search...", "Search Test")
    handler.handle_command("search", ["accessibility"])
    time.sleep(2)


def demo_accessibility_integration():
    """Demo accessibility features in the interactive shell."""
    print("\n♿ Demo: Accessibility Integration")
    print("=" * 40)
    
    ui = RichTerminalUI()
    handler = RichCommandHandler(ui)
    
    # Demo accessibility status
    ui.show_info("Testing accessibility status...", "Accessibility Test")
    handler.handle_command("accessibility", ["--status"])
    time.sleep(2)
    
    # Demo accessibility help
    ui.show_info("Testing accessibility help...", "Accessibility Help Test")
    handler.handle_command("help", ["accessibility"])
    time.sleep(2)


def demo_developer_features():
    """Demo developer features in the interactive shell."""
    print("\n🔧 Demo: Developer Features")
    print("=" * 40)
    
    ui = RichTerminalUI()
    handler = RichCommandHandler(ui)
    
    # Demo debug mode
    ui.show_info("Testing debug mode...", "Debug Test")
    handler.handle_command("debug", ["--enable"])
    time.sleep(2)
    
    # Demo performance dashboard
    ui.show_info("Testing performance dashboard...", "Performance Test")
    handler.handle_command("performance", ["--dashboard"])
    time.sleep(2)


def demo_deck_operations():
    """Demo deck operations with Rich UI."""
    print("\n📚 Demo: Deck Operations")
    print("=" * 40)
    
    ui = RichTerminalUI()
    handler = RichCommandHandler(ui)
    
    # Demo list decks
    ui.show_info("Testing deck listing...", "Deck List Test")
    handler.handle_command("list", [])
    time.sleep(2)
    
    # Demo import (if sample file exists)
    sample_file = Path("assets/sample_data/example_deck.csv")
    if sample_file.exists():
        ui.show_info("Testing deck import...", "Import Test")
        handler.handle_command("import", [str(sample_file)])
        time.sleep(2)
        
        # Demo load deck
        ui.show_info("Testing deck loading...", "Load Test")
        handler.handle_command("load", ["example_deck"])
        time.sleep(2)
    else:
        ui.show_warning("Sample deck file not found, skipping import test", "Import Test")


def simulate_interactive_session():
    """Simulate an interactive session with Rich UI."""
    print("\n🎭 Demo: Simulated Interactive Session")
    print("=" * 40)
    
    ui = RichTerminalUI()
    handler = RichCommandHandler(ui)
    
    # Simulate welcome
    ui.show_welcome_screen()
    ui.show_info(
        "💡 Quick Start: Type 'help' for commands, 'list' to see decks, or 'import FILE' to get started",
        "Getting Started"
    )
    ui.show_success(
        "🎨 Rich Terminal UI enabled! Enjoy beautiful formatting and enhanced accessibility",
        "Rich UI Active"
    )
    
    time.sleep(2)
    
    # Simulate user commands
    simulated_commands = [
        ("help", "Getting help"),
        ("list", "Listing decks"),
        ("search quiz", "Searching for quiz commands"),
        ("accessibility --status", "Checking accessibility"),
        ("help import", "Getting import help"),
    ]
    
    for command, description in simulated_commands:
        ui.show_info(f"User types: {command}", "Simulated Input")
        time.sleep(1)
        
        parts = command.split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        handler.handle_command(cmd, args)
        time.sleep(2)
        print()


def interactive_demo():
    """Run an interactive demo of the Rich shell."""
    print("\n🎮 Interactive Rich Shell Demo")
    print("=" * 50)
    
    ui = RichTerminalUI()
    
    while True:
        try:
            options = [
                "Rich Command Handler",
                "Interactive Features",
                "Accessibility Integration", 
                "Developer Features",
                "Deck Operations",
                "Simulated Interactive Session",
                "Exit Demo"
            ]
            
            print("\n📋 Rich Interactive Shell Demo Menu")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                demo_rich_command_handler()
            elif choice == "2":
                demo_interactive_features()
            elif choice == "3":
                demo_accessibility_integration()
            elif choice == "4":
                demo_developer_features()
            elif choice == "5":
                demo_deck_operations()
            elif choice == "6":
                simulate_interactive_session()
            elif choice == "7":
                ui.show_success("Thanks for exploring the FlashGenie Rich Interactive Shell! 🎉", "Demo Complete")
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
    print("🚀 FlashGenie v1.8.4 Rich Interactive Shell Demo")
    print("=" * 60)
    print("Enhanced Interactive Shell with Rich Terminal UI")
    print("\nThis demo showcases the Rich UI integration in the interactive shell:")
    print("• Beautiful Rich Terminal UI formatting inside FlashGenie shell")
    print("• Enhanced command handling with Rich panels and tables")
    print("• Integrated help system with searchable commands")
    print("• Accessibility features available in interactive mode")
    print("• Developer tools accessible from the shell")
    print("• Error handling with helpful Rich UI messages")
    
    try:
        demo_choice = input("\n🎮 Would you like to run the interactive demo? (y/n): ").strip().lower()
        if demo_choice in ['y', 'yes']:
            interactive_demo()
        else:
            print("\n🎬 Running automatic demo sequence...")
            demo_rich_command_handler()
            demo_interactive_features()
            demo_accessibility_integration()
            demo_developer_features()
            demo_deck_operations()
            simulate_interactive_session()
            
            print("\n✅ Rich Interactive Shell demo completed successfully!")
            print("🎉 FlashGenie v1.8.4 Rich Interactive Shell is ready!")
            print("\n💡 To test the actual interactive shell, run:")
            print("   python -m flashgenie")
            print("   Then try commands like: help, list, search import, accessibility --status")
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")


if __name__ == "__main__":
    main()
