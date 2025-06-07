"""
Terminal-based user interface for FlashGenie v1.8.3.

This module provides the main terminal interface for interacting
with FlashGenie through the command line. Enhanced with Rich UI framework.
"""

import sys
from typing import List, Optional
from pathlib import Path

from flashgenie.interfaces.cli.commands import CommandHandler
from flashgenie.interfaces.cli.rich_command_handler import RichCommandHandler
from flashgenie.interfaces.cli.formatters import OutputFormatter
from flashgenie.config import APP_NAME, APP_VERSION

# Enhanced Rich UI components
try:
    from ..terminal import RichTerminalUI
    RICH_UI_AVAILABLE = True
except ImportError:
    RICH_UI_AVAILABLE = False


class TerminalUI:
    """
    Main terminal user interface for FlashGenie v1.8.3.

    Provides an interactive command-line interface for managing
    flashcards, importing data, and running quiz sessions.
    Enhanced with Rich UI framework for better user experience.
    """

    def __init__(self, use_rich_ui: bool = True):
        """
        Initialize the terminal UI.

        Args:
            use_rich_ui: Whether to use Rich UI framework (falls back to basic if unavailable)
        """
        self.formatter = OutputFormatter()
        self.running = False

        # Initialize Rich UI if available and requested
        self.use_rich_ui = use_rich_ui and RICH_UI_AVAILABLE
        if self.use_rich_ui:
            self.rich_ui = RichTerminalUI()
            self.rich_ui.navigation.push_context("home", "FlashGenie Home")
            # Use Rich command handler for enhanced experience
            self.command_handler = RichCommandHandler(self.rich_ui)
        else:
            self.rich_ui = None
            # Fallback to basic command handler
            self.command_handler = CommandHandler()
    
    def start(self) -> None:
        """Start the terminal interface with enhanced UI."""
        # Check terminal size for optimal experience
        if self.use_rich_ui and self.rich_ui.is_terminal_too_small():
            self.rich_ui.show_warning(
                "Terminal window is quite small. For the best experience, please resize to at least 80x24 characters.",
                "Small Terminal"
            )

        self.show_welcome()
        self.running = True

        # Register navigation shortcuts
        if self.use_rich_ui:
            self._register_shortcuts()

        while self.running:
            try:
                command_line = self.get_command_input()
                if not command_line:
                    continue

                # Check for keyboard shortcuts first
                if self.use_rich_ui and self.rich_ui.navigation.handle_shortcut(command_line):
                    continue

                # Parse command and arguments
                parts = command_line.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []

                # Handle command
                self.running = self.command_handler.handle_command(command, args)

            except KeyboardInterrupt:
                if self.use_rich_ui:
                    self.rich_ui.show_info("Use 'exit' or 'quit' to leave FlashGenie", "Interrupted")
                else:
                    print("\n" + self.formatter.info("Use 'exit' or 'quit' to leave FlashGenie"))
            except EOFError:
                if self.use_rich_ui:
                    self.rich_ui.show_success("Goodbye! 👋", "FlashGenie")
                else:
                    print("\n" + self.formatter.success("Goodbye!"))
                break
    
    def show_welcome(self) -> None:
        """Display welcome message and basic information with enhanced UI."""
        if self.use_rich_ui:
            # Rich welcome screen with enhanced features
            self.rich_ui.show_welcome_screen()

            # Show quick start tips
            self.rich_ui.show_info(
                "💡 Quick Start: Type 'help' for commands, 'list' to see decks, or 'import FILE' to get started",
                "Getting Started"
            )

            # Show Rich UI features
            self.rich_ui.show_success(
                "🎨 Rich Terminal UI enabled! Enjoy beautiful formatting and enhanced accessibility",
                "Rich UI Active"
            )
        else:
            # Fallback to basic welcome
            welcome_text = f"""
{self.formatter.header(f"🧞‍♂️ {APP_NAME} v{APP_VERSION}")}

Welcome to FlashGenie - Your intelligent flashcard companion!

{self.formatter.info("Type 'help' for available commands")}
{self.formatter.info("Type 'import <file>' to get started with your flashcards")}
{self.formatter.info("Note: Rich Terminal UI not available - using basic interface")}
            """
            print(welcome_text)
    
    def get_command_input(self) -> str:
        """Get command input from user with Rich Terminal UI."""
        if self.use_rich_ui:
            # Rich prompt with enhanced styling
            from rich.prompt import Prompt
            return Prompt.ask(
                "[bold bright_cyan]FlashGenie[/bold bright_cyan] [bright_white]>[/bright_white]",
                console=self.rich_ui.console
            ).strip()
        else:
            # Fallback prompt
            prompt = f"{self.formatter.highlight('FlashGenie')} > "
            return input(prompt).strip()
    
    def run_interactive_import(self) -> None:
        """Run interactive import wizard."""
        print(self.formatter.header("Import Flashcards"))
        
        # Get file path
        file_path_str = input("Enter file path: ").strip()
        if not file_path_str:
            print(self.formatter.error("No file path provided"))
            return
        
        file_path = Path(file_path_str)
        
        # Handle import
        self.command_handler.handle_command('import', [str(file_path)])
    
    def run_interactive_quiz(self) -> None:
        """Run interactive quiz setup."""
        if self.command_handler.current_deck is None:
            print(self.formatter.error("No deck loaded. Load a deck first."))
            return
        
        print(self.formatter.header("Quiz Setup"))
        
        # Show quiz mode options
        modes = [
            "Spaced Repetition (recommended)",
            "Random Order",
            "Sequential Order", 
            "Difficult Cards First"
        ]
        
        print(self.formatter.menu_options(modes, "Select Quiz Mode"))
        
        try:
            choice = input("Enter choice (1-4, or press Enter for default): ").strip()
            
            mode_map = {
                '1': 'spaced',
                '2': 'random',
                '3': 'sequential',
                '4': 'difficult',
                '': 'spaced'  # default
            }
            
            mode = mode_map.get(choice, 'spaced')
            self.command_handler.handle_command('quiz', [mode])
            
        except (ValueError, KeyboardInterrupt):
            print(self.formatter.info("Quiz cancelled"))
    
    def show_deck_selection(self) -> None:
        """Show deck selection interface."""
        print(self.formatter.header("Select a Deck"))
        
        decks = self.command_handler.storage.list_decks()
        
        if not decks:
            print(self.formatter.info("No decks available. Import some flashcards first!"))
            return
        
        # Display decks with numbers
        for i, deck in enumerate(decks, 1):
            print(f"{i}. {deck['name']} ({deck['card_count']} cards)")
        
        try:
            choice = input("\nEnter deck number: ").strip()
            
            if choice.isdigit():
                deck_index = int(choice) - 1
                if 0 <= deck_index < len(decks):
                    deck_name = decks[deck_index]['name']
                    self.command_handler.handle_command('load', [deck_name])
                else:
                    print(self.formatter.error("Invalid deck number"))
            else:
                print(self.formatter.error("Please enter a valid number"))
                
        except (ValueError, KeyboardInterrupt):
            print(self.formatter.info("Selection cancelled"))
    
    def show_main_menu(self) -> None:
        """Show main menu options."""
        options = [
            "Import flashcards from file",
            "Load existing deck",
            "Start quiz session",
            "View deck statistics",
            "List all decks",
            "Help",
            "Exit"
        ]
        
        print(self.formatter.menu_options(options, "Main Menu"))
        
        try:
            choice = input("Enter choice (1-7): ").strip()
            
            if choice == '1':
                self.run_interactive_import()
            elif choice == '2':
                self.show_deck_selection()
            elif choice == '3':
                self.run_interactive_quiz()
            elif choice == '4':
                self.command_handler.handle_command('stats')
            elif choice == '5':
                self.command_handler.handle_command('list')
            elif choice == '6':
                self.command_handler.handle_command('help')
            elif choice == '7':
                self.running = False
            else:
                print(self.formatter.error("Invalid choice"))
                
        except (ValueError, KeyboardInterrupt):
            print(self.formatter.info("Selection cancelled"))
    
    def run_guided_setup(self) -> None:
        """Run guided setup for new users."""
        print(self.formatter.header("Welcome to FlashGenie!"))
        print("Let's get you started with your first deck of flashcards.\n")
        
        # Check if any decks exist
        decks = self.command_handler.storage.list_decks()
        
        if decks:
            print(f"You have {len(decks)} existing deck(s).")
            choice = input("Would you like to (1) load existing deck or (2) import new flashcards? ").strip()
            
            if choice == '1':
                self.show_deck_selection()
            else:
                self.run_interactive_import()
        else:
            print("No existing decks found. Let's import your first set of flashcards!")
            self.run_interactive_import()
    
    @staticmethod
    def run_single_command(command: str, args: List[str] = None) -> None:
        """
        Run a single command without starting interactive mode.
        
        Args:
            command: Command to run
            args: Command arguments
        """
        ui = TerminalUI()
        ui.command_handler.handle_command(command, args or [])
    
    @staticmethod
    def run_file_import(file_path: str) -> None:
        """
        Import a file directly without interactive mode.
        
        Args:
            file_path: Path to file to import
        """
        TerminalUI.run_single_command('import', [file_path])
    
    @staticmethod
    def run_quick_quiz(deck_name: str = None) -> None:
        """
        Start a quick quiz session.
        
        Args:
            deck_name: Name of deck to quiz (prompts if None)
        """
        ui = TerminalUI()
        
        if deck_name:
            ui.command_handler.handle_command('load', [deck_name])
        else:
            ui.show_deck_selection()
        
        if ui.command_handler.current_deck:
            ui.command_handler.handle_command('quiz', ['spaced'])

    def _register_shortcuts(self) -> None:
        """Register keyboard shortcuts for enhanced navigation."""
        if not self.use_rich_ui:
            return

        # Navigation shortcuts
        self.rich_ui.navigation.register_shortcut(
            "m", "Main Menu", lambda: self.show_main_menu(), "home"
        )
        self.rich_ui.navigation.register_shortcut(
            "i", "Import", lambda: self.run_interactive_import(), "home"
        )
        self.rich_ui.navigation.register_shortcut(
            "l", "List Decks", lambda: self.command_handler.handle_command('list'), "home"
        )
        self.rich_ui.navigation.register_shortcut(
            "s", "Stats", lambda: self.command_handler.handle_command('stats'), "home"
        )
        self.rich_ui.navigation.register_shortcut(
            "t", "Toggle Theme", self._cycle_theme, "home"
        )

    def _cycle_theme(self) -> None:
        """Cycle through available themes."""
        if not self.use_rich_ui:
            return

        themes = self.rich_ui.theme_manager.list_themes()
        current_theme = getattr(self.rich_ui, '_current_theme_name', 'default')

        try:
            current_index = themes.index(current_theme)
            next_index = (current_index + 1) % len(themes)
            next_theme = themes[next_index]

            self.rich_ui.set_theme(next_theme)
            self.rich_ui._current_theme_name = next_theme
        except (ValueError, IndexError):
            self.rich_ui.set_theme('default')
            self.rich_ui._current_theme_name = 'default'


def main():
    """Main entry point for the terminal interface."""
    if len(sys.argv) > 1:
        # Handle command line arguments
        command = sys.argv[1]
        args = sys.argv[2:] if len(sys.argv) > 2 else []
        
        if command == 'import' and args:
            TerminalUI.run_file_import(args[0])
        elif command == 'quiz':
            deck_name = args[0] if args else None
            TerminalUI.run_quick_quiz(deck_name)
        else:
            TerminalUI.run_single_command(command, args)
    else:
        # Start interactive mode
        ui = TerminalUI()
        ui.start()


if __name__ == "__main__":
    main()
