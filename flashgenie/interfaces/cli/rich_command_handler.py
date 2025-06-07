"""
Rich Terminal UI Command Handler for FlashGenie v1.8.4.

This module provides Rich Terminal UI integration for the interactive shell,
bringing beautiful formatting and enhanced user experience to all commands.
"""

from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
import sys

from flashgenie.core.content_system.deck import Deck
from flashgenie.core.study_system.quiz_engine import QuizEngine, QuizMode
from flashgenie.core.content_system.tag_manager import TagManager
from flashgenie.core.content_system.smart_collections import SmartCollectionManager
from flashgenie.data.storage import DataStorage
from flashgenie.data.importers.csv_importer import CSVImporter
from flashgenie.data.importers.txt_importer import TXTImporter
from flashgenie.utils.exceptions import FlashGenieError

# Rich Terminal UI components
try:
    from ..terminal import RichTerminalUI, HelpSystem
    from ..terminal.rich_quiz_interface import RichQuizInterface
    from ..terminal.rich_statistics_dashboard import RichStatisticsDashboard
    from ..terminal.rich_ai_interface import RichAIInterface
    RICH_UI_AVAILABLE = True
except ImportError:
    RICH_UI_AVAILABLE = False


class RichCommandHandler:
    """
    Rich Terminal UI-enabled command handler for interactive shell.
    
    Provides all FlashGenie commands with beautiful Rich Terminal UI formatting,
    enhanced user experience, and comprehensive help system integration.
    """
    
    def __init__(self, rich_ui: Optional['RichTerminalUI'] = None):
        """
        Initialize the Rich command handler.
        
        Args:
            rich_ui: Rich Terminal UI instance (creates new if None)
        """
        # Core components
        self.storage = DataStorage()
        self.quiz_engine = QuizEngine()
        self.tag_manager = TagManager()
        self.collection_manager = SmartCollectionManager(self.tag_manager)
        self.current_deck: Optional[Deck] = None
        
        # Rich UI components
        if RICH_UI_AVAILABLE:
            self.rich_ui = rich_ui or RichTerminalUI()
            self.help_system = HelpSystem(self.rich_ui.console)
        else:
            self.rich_ui = None
            self.help_system = None
        
        # Command registry with Rich UI integration
        self.commands: Dict[str, Callable] = {
            'help': self.show_help,
            'list': self.list_decks,
            'load': self.load_deck,
            'import': self.import_file,
            'quiz': self.start_quiz,
            'stats': self.show_stats,
            'collections': self.show_collections,
            'autotag': self.auto_tag_deck,
            'tags': self.manage_tags,
            'search': self.search_commands,
            'accessibility': self.configure_accessibility,
            'debug': self.toggle_debug,
            'performance': self.show_performance,
            'ai': self.ai_features,
            'generate': self.ai_generate_content,
            'suggest': self.ai_suggest_content,
            'enhance': self.ai_enhance_cards,
            'exit': self.exit_app,
            'quit': self.exit_app,
        }
    
    def handle_command(self, command: str, args: List[str] = None) -> bool:
        """
        Handle a user command with Rich Terminal UI.
        
        Args:
            command: Command name
            args: Command arguments
            
        Returns:
            True to continue, False to exit
        """
        args = args or []
        
        if command in self.commands:
            try:
                return self.commands[command](args)
            except FlashGenieError as e:
                if self.rich_ui:
                    self.rich_ui.show_error(str(e), "FlashGenie Error")
                else:
                    print(f"Error: {e}")
                return True
            except Exception as e:
                if self.rich_ui:
                    self.rich_ui.show_error(f"Unexpected error: {e}", "System Error")
                else:
                    print(f"Unexpected error: {e}")
                return True
        else:
            if self.rich_ui:
                self.rich_ui.show_error(f"Unknown command: {command}", "Invalid Command")
                self.rich_ui.show_info("Type 'help' for available commands or 'search TERM' to find commands", "Tip")
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands.")
            return True
    
    def show_help(self, args: List[str] = None) -> bool:
        """Show comprehensive help with Rich Terminal UI."""
        if self.help_system and self.rich_ui:
            if args:
                # Show help for specific command or category
                self.help_system.show_command_help(args[0])
            else:
                # Show main help menu
                self.help_system.show_main_help()
        else:
            # Fallback to basic help
            self._show_basic_help()
        return True
    
    def search_commands(self, args: List[str] = None) -> bool:
        """Search commands with Rich Terminal UI."""
        if not args:
            if self.rich_ui:
                self.rich_ui.show_warning("Please provide a search term", "Search")
                self.rich_ui.show_info("Usage: search TERM", "Help")
            else:
                print("Usage: search TERM")
            return True
        
        query = " ".join(args)
        if self.help_system:
            self.help_system.search_commands(query)
        else:
            print(f"Search functionality requires Rich Terminal UI")
        return True
    
    def configure_accessibility(self, args: List[str] = None) -> bool:
        """Configure accessibility features."""
        if not self.rich_ui:
            print("Accessibility features require Rich Terminal UI")
            return True
        
        if not args:
            self.rich_ui.show_accessibility_menu()
        elif args[0] == "--enable" and len(args) > 1:
            self.rich_ui.enable_accessibility_mode(args[1])
        elif args[0] == "--disable" and len(args) > 1:
            self.rich_ui.disable_accessibility_mode(args[1])
        elif args[0] == "--status":
            self.rich_ui.show_accessibility_menu()
        else:
            self.rich_ui.show_info("Usage: accessibility [--enable MODE] [--disable MODE] [--status]", "Help")
        
        return True
    
    def toggle_debug(self, args: List[str] = None) -> bool:
        """Toggle debug mode."""
        if not self.rich_ui:
            print("Debug features require Rich Terminal UI")
            return True
        
        if not args or args[0] == "--enable":
            self.rich_ui.toggle_debug_mode()
            self.rich_ui.show_success("Debug mode enabled", "Debug")
        elif args[0] == "--disable":
            self.rich_ui.debug_mode = False
            self.rich_ui.show_info("Debug mode disabled", "Debug")
        elif args[0] == "--console":
            self.rich_ui.show_debug_panel()
        else:
            self.rich_ui.show_info("Usage: debug [--enable] [--disable] [--console]", "Help")
        
        return True
    
    def show_performance(self, args: List[str] = None) -> bool:
        """Show performance dashboard."""
        if not self.rich_ui:
            print("Performance features require Rich Terminal UI")
            return True
        
        if not args or args[0] == "--dashboard":
            self.rich_ui.show_performance_dashboard()
        elif args[0] == "--optimize":
            result = self.rich_ui.optimize_performance()
            self.rich_ui.show_success(f"Performance optimized: {result.get('memory_freed_mb', 0):.1f}MB freed", "Optimization")
        else:
            self.rich_ui.show_info("Usage: performance [--dashboard] [--optimize]", "Help")
        
        return True
    
    def list_decks(self, args: List[str] = None) -> bool:
        """List all available decks with Rich Terminal UI."""
        decks = self.storage.list_decks()
        
        if not decks:
            if self.rich_ui:
                self.rich_ui.show_info("No decks found. Import some flashcards to get started!", "No Decks")
            else:
                print("No decks found. Import some flashcards to get started!")
            return True
        
        if self.rich_ui:
            # Create Rich table
            from rich.table import Table
            
            table = Table(title="📚 Your Flashcard Decks")
            table.add_column("Name", style="bright_cyan", no_wrap=True)
            table.add_column("Cards", justify="right", style="bright_white")
            table.add_column("Due", justify="right", style="bright_yellow")
            table.add_column("Modified", style="bright_green")
            
            for deck in decks:
                table.add_row(
                    deck["name"],
                    str(deck["card_count"]),
                    str(deck["due_count"]),
                    deck["modified_at"][:10]  # Just the date part
                )
            
            self.rich_ui.console.print(table)
            
            # Summary panel
            total_cards = sum(deck["card_count"] for deck in decks)
            total_due = sum(deck["due_count"] for deck in decks)
            
            summary_content = []
            summary_content.append(f"Total Decks: {len(decks)}")
            summary_content.append(f"Total Cards: {total_cards}")
            summary_content.append(f"Cards Due: {total_due}")
            if decks:
                most_recent = max(decks, key=lambda d: d['modified_at'])
                summary_content.append(f"Most Recent: {most_recent['name']}")
            
            from rich.panel import Panel
            summary_panel = Panel(
                "\n".join(summary_content),
                title="📊 Library Summary",
                border_style="bright_blue"
            )
            self.rich_ui.console.print(summary_panel)
        else:
            # Fallback to basic table
            print("Available Decks")
            print("=" * 50)
            print(f"{'Name':<20} | {'Cards':<5} | {'Due':<3} | {'Modified'}")
            print("-" * 50)
            for deck in decks:
                print(f"{deck['name']:<20} | {deck['card_count']:<5} | {deck['due_count']:<3} | {deck['modified_at'][:10]}")
        
        return True
    
    def load_deck(self, args: List[str]) -> bool:
        """Load a deck by name or ID with Rich Terminal UI."""
        if not args:
            if self.rich_ui:
                self.rich_ui.show_warning("Please specify a deck name or ID", "Missing Argument")
                self.rich_ui.show_info("Usage: load DECK_NAME", "Help")
            else:
                print("Please specify a deck name or ID")
            return True
        
        deck_identifier = " ".join(args)
        
        # Try to load by name first
        deck = self.storage.load_deck_by_name(deck_identifier)
        
        if deck is None:
            # Try to load by ID
            try:
                deck = self.storage.load_deck(deck_identifier)
            except FlashGenieError:
                if self.rich_ui:
                    self.rich_ui.show_error(f"Deck '{deck_identifier}' not found", "Deck Not Found")
                else:
                    print(f"Deck '{deck_identifier}' not found")
                return True
        
        self.current_deck = deck
        
        if self.rich_ui:
            self.rich_ui.show_success(f"Loaded deck: {deck.name}", "Deck Loaded")
            
            # Create deck summary panel
            summary_content = []
            summary_content.append(f"Name: {deck.name}")
            summary_content.append(f"Cards: {len(deck.flashcards)}")
            summary_content.append(f"Due for review: {'⚠️ ' if deck.due_count > 0 else ''}{deck.due_count}")
            if deck.description:
                summary_content.append(f"Description: {deck.description}")
            if deck.tags:
                summary_content.append(f"Tags: {', '.join(deck.tags)}")
            
            from rich.panel import Panel
            summary_panel = Panel(
                "\n".join(summary_content),
                title=f"📚 {deck.name}",
                border_style="bright_green"
            )
            self.rich_ui.console.print(summary_panel)
        else:
            # Fallback display
            print(f"✓ Loaded deck: {deck.name}")
            print(f"Name: {deck.name}")
            print(f"Cards: {len(deck.flashcards)}")
            print(f"Due for review: {deck.due_count}")
            if deck.description:
                print(f"Description: {deck.description}")
            if deck.tags:
                print(f"Tags: {', '.join(deck.tags)}")
        
        return True
    
    def import_file(self, args: List[str]) -> bool:
        """Import flashcards from a file with Rich Terminal UI."""
        if not args:
            if self.rich_ui:
                self.rich_ui.show_warning("Please specify a file path", "Missing Argument")
                self.rich_ui.show_info("Usage: import FILE_PATH", "Help")
            else:
                print("Please specify a file path")
            return True
        
        file_path = Path(" ".join(args))
        
        if not file_path.exists():
            if self.rich_ui:
                self.rich_ui.show_error(f"File not found: {file_path}", "File Not Found")
            else:
                print(f"File not found: {file_path}")
            return True
        
        try:
            # Determine importer based on file extension
            if file_path.suffix.lower() == '.csv':
                importer = CSVImporter()
            elif file_path.suffix.lower() in ['.txt', '.text']:
                importer = TXTImporter()
            else:
                if self.rich_ui:
                    self.rich_ui.show_error(f"Unsupported file format: {file_path.suffix}", "Unsupported Format")
                else:
                    print(f"Unsupported file format: {file_path.suffix}")
                return True
            
            if self.rich_ui:
                # Rich UI import with progress
                with self.rich_ui.widgets.create_status_indicator(f"Importing from {file_path.name}..."):
                    deck = importer.import_file(file_path, deck_name=file_path.stem)
                    self.storage.save_deck(deck)
                    self.current_deck = deck
                
                self.rich_ui.show_success(f"Successfully imported {len(deck.flashcards)} cards into deck '{deck.name}'", "Import Complete")
                
                # Create import summary panel
                summary_content = []
                summary_content.append(f"Name: {deck.name}")
                summary_content.append(f"Cards: {len(deck.flashcards)}")
                summary_content.append(f"File: {file_path.name}")
                summary_content.append(f"Format: {file_path.suffix.upper()}")
                
                from rich.panel import Panel
                summary_panel = Panel(
                    "\n".join(summary_content),
                    title="📊 Import Summary",
                    border_style="bright_green"
                )
                self.rich_ui.console.print(summary_panel)
            else:
                # Fallback import
                print(f"Importing from {file_path}...")
                deck = importer.import_file(file_path, deck_name=file_path.stem)
                self.storage.save_deck(deck)
                self.current_deck = deck
                print(f"✓ Successfully imported {len(deck.flashcards)} flashcards")
                print(f"Name: {deck.name}")
                print(f"Cards: {len(deck.flashcards)}")
                print(f"Due for review: ⚠ {deck.due_count}")
                if deck.description:
                    print(f"Description: {deck.description}")
                if deck.tags:
                    print(f"Tags: {', '.join(deck.tags)}")
            
        except FlashGenieError as e:
            if self.rich_ui:
                self.rich_ui.show_error(f"Import failed: {e}", "Import Error")
            else:
                print(f"Import failed: {e}")
        
        return True
    
    def _show_basic_help(self) -> None:
        """Show basic help when Rich UI is not available."""
        help_text = """
Available Commands:
  help                 - Show this help message
  list                 - List all available decks
  load <deck_name>     - Load a deck by name or ID
  import <file_path>   - Import flashcards from a file
  quiz [mode]          - Start a quiz session
  stats                - Show statistics for current deck
  collections          - Show smart collections and their statistics
  autotag              - Automatically tag cards in current deck
  tags [command]       - Manage tags and hierarchies
  search <term>        - Search for commands (Rich UI only)
  accessibility        - Configure accessibility features (Rich UI only)
  debug                - Toggle debug mode (Rich UI only)
  performance          - Show performance dashboard (Rich UI only)
  exit/quit            - Exit the application

Quiz Modes:
  spaced    - Spaced repetition (default)
  random    - Random order
  sequential - Sequential order
  difficult - Difficult cards first

Examples:
  load "My Spanish Deck"
  import flashcards.csv
  quiz spaced
  search import
  accessibility --enable high_contrast
        """
        print(help_text)
    
    def start_quiz(self, args: List[str] = None) -> bool:
        """Start a Rich quiz session with beautiful UI."""
        if self.current_deck is None:
            if self.rich_ui:
                self.rich_ui.show_error("No deck loaded. Use 'load' command first.", "No Deck Loaded")
                self.rich_ui.show_info("Use 'list' to see available decks, then 'load DECK_NAME'", "Tip")
            else:
                print("No deck loaded. Use 'load' command first.")
            return True

        if not self.current_deck.flashcards:
            if self.rich_ui:
                self.rich_ui.show_error("The current deck is empty.", "Empty Deck")
                self.rich_ui.show_info("Import some flashcards first with 'import FILE_PATH'", "Tip")
            else:
                print("The current deck is empty.")
            return True

        # Parse quiz arguments
        quiz_mode = QuizMode.SPACED_REPETITION
        card_count = None
        timed_mode = False

        if args:
            for arg in args:
                if arg.lower() in ['spaced', 'spaced_repetition']:
                    quiz_mode = QuizMode.SPACED_REPETITION
                elif arg.lower() == 'random':
                    quiz_mode = QuizMode.RANDOM
                elif arg.lower() == 'sequential':
                    quiz_mode = QuizMode.SEQUENTIAL
                elif arg.lower() in ['difficult', 'difficult_first']:
                    quiz_mode = QuizMode.DIFFICULT_FIRST
                elif arg.lower() == 'timed':
                    timed_mode = True
                elif arg.isdigit():
                    card_count = int(arg)

        # Start Rich quiz session
        if self.rich_ui and RICH_UI_AVAILABLE:
            try:
                quiz_interface = RichQuizInterface(self.rich_ui.console)
                results = quiz_interface.start_quiz_session(
                    deck=self.current_deck,
                    mode=quiz_mode,
                    card_count=card_count,
                    timed=timed_mode
                )

                # Show completion message
                if results.get('end_time'):
                    self.rich_ui.show_success(
                        f"Quiz completed! Accuracy: {results.get('correct_answers', 0)}/{results.get('total_cards', 0)}",
                        "Quiz Complete"
                    )

            except Exception as e:
                self.rich_ui.show_error(f"Quiz error: {e}", "Quiz Error")
        else:
            # Fallback to basic quiz
            print(f"Starting basic quiz for '{self.current_deck.name}'...")
            print("Rich Quiz Interface not available - using basic mode")

        return True
    
    def show_stats(self, args: List[str] = None) -> bool:
        """Show Rich statistics dashboard with comprehensive analytics."""
        # Parse arguments
        show_detailed = False
        show_global = False
        show_trends = False
        show_performance = False

        if args:
            for arg in args:
                if arg.lower() in ['--detailed', '-d']:
                    show_detailed = True
                elif arg.lower() in ['--global', '-g']:
                    show_global = True
                elif arg.lower() in ['--trends', '-t']:
                    show_trends = True
                elif arg.lower() in ['--performance', '-p']:
                    show_performance = True

        if self.rich_ui and RICH_UI_AVAILABLE:
            try:
                stats_dashboard = RichStatisticsDashboard(self.rich_ui.console)

                if show_global:
                    # Show global statistics across all decks
                    all_decks = self.storage.list_decks()
                    deck_objects = []
                    for deck_info in all_decks:
                        try:
                            deck = self.storage.load_deck_by_name(deck_info['name'])
                            if deck:
                                deck_objects.append(deck)
                        except Exception:
                            continue

                    stats_dashboard.show_global_statistics(deck_objects)

                elif show_trends and self.current_deck:
                    # Show learning trends for current deck
                    stats_dashboard.show_learning_trends(self.current_deck, days=30)

                elif show_performance and self.current_deck:
                    # Show performance analysis for current deck
                    stats_dashboard.show_performance_analysis(self.current_deck)

                elif self.current_deck:
                    # Show deck-specific statistics
                    stats_dashboard.show_deck_statistics(self.current_deck, detailed=show_detailed)

                else:
                    # No deck loaded, show global stats
                    self.rich_ui.show_warning("No deck loaded. Showing global statistics...", "No Deck")
                    all_decks = self.storage.list_decks()
                    deck_objects = []
                    for deck_info in all_decks:
                        try:
                            deck = self.storage.load_deck_by_name(deck_info['name'])
                            if deck:
                                deck_objects.append(deck)
                        except Exception:
                            continue

                    if deck_objects:
                        stats_dashboard.show_global_statistics(deck_objects)
                    else:
                        self.rich_ui.show_info("No decks found. Import some flashcards to see statistics!", "No Data")

            except Exception as e:
                self.rich_ui.show_error(f"Statistics error: {e}", "Stats Error")
        else:
            # Fallback to basic stats
            if self.current_deck:
                print(f"Basic statistics for '{self.current_deck.name}':")
                print(f"  Total cards: {len(self.current_deck.flashcards)}")
                print(f"  Due for review: {self.current_deck.due_count}")
            else:
                print("No deck loaded. Use 'load' command first.")

        return True
    
    def show_collections(self, args: List[str] = None) -> bool:
        """Show collections (placeholder)."""
        if self.rich_ui:
            self.rich_ui.show_info("Smart collections will be implemented in the full version", "Collections Placeholder")
        else:
            print("Smart collections will be implemented in the full version")
        return True
    
    def auto_tag_deck(self, args: List[str] = None) -> bool:
        """Auto-tag deck (placeholder)."""
        if self.rich_ui:
            self.rich_ui.show_info("Auto-tagging will be implemented in the full version", "Auto-tag Placeholder")
        else:
            print("Auto-tagging will be implemented in the full version")
        return True
    
    def manage_tags(self, args: List[str] = None) -> bool:
        """Manage tags (placeholder)."""
        if self.rich_ui:
            self.rich_ui.show_info("Tag management will be implemented in the full version", "Tags Placeholder")
        else:
            print("Tag management will be implemented in the full version")
        return True
    
    def ai_features(self, args: List[str] = None) -> bool:
        """Show AI features menu and capabilities."""
        if not self.rich_ui or not RICH_UI_AVAILABLE:
            print("AI features require Rich Terminal UI")
            return True

        # Show AI features overview
        ai_content = []
        ai_content.append("🤖 [bold bright_blue]AI-Powered Features[/bold bright_blue]")
        ai_content.append("")
        ai_content.append("✨ [bold]Available AI Features:[/bold]")
        ai_content.append("  🎯 [bright_cyan]generate[/bright_cyan] - Generate flashcards from text")
        ai_content.append("  💡 [bright_cyan]suggest[/bright_cyan] - Get related content suggestions")
        ai_content.append("  🔧 [bright_cyan]enhance[/bright_cyan] - Enhance existing flashcards")
        ai_content.append("  🎯 [bright_cyan]ai predict[/bright_cyan] - Predict card difficulty")
        ai_content.append("")
        ai_content.append("🚀 [bold]AI Capabilities:[/bold]")
        ai_content.append("  • Intelligent content extraction from text")
        ai_content.append("  • Automatic difficulty prediction")
        ai_content.append("  • Smart tag generation")
        ai_content.append("  • Related content suggestions")
        ai_content.append("  • Flashcard enhancement recommendations")
        ai_content.append("")
        ai_content.append("💡 [dim]Example: 'generate' to create cards from text[/dim]")

        from rich.panel import Panel
        ai_panel = Panel(
            "\n".join(ai_content),
            title="🤖 AI Features",
            border_style="bright_blue",
            padding=(1, 2)
        )

        self.rich_ui.console.print(ai_panel)
        return True

    def ai_generate_content(self, args: List[str] = None) -> bool:
        """Generate flashcards from text using AI."""
        if not self.rich_ui or not RICH_UI_AVAILABLE:
            print("AI generation requires Rich Terminal UI")
            return True

        try:
            ai_interface = RichAIInterface(self.rich_ui.console)

            # Get text input
            if args and len(args) > 0:
                # Text provided as arguments
                text = " ".join(args)
            else:
                # Get text from user
                text = self.rich_ui.console.input("\n[bold bright_yellow]Enter text to generate flashcards from:[/bold bright_yellow]\n")

            if not text.strip():
                self.rich_ui.show_warning("No text provided for generation", "AI Generation")
                return True

            # Get deck name
            deck_name = self.rich_ui.console.input("\n[bold bright_cyan]Deck name (default: AI Generated Deck):[/bold bright_cyan] ") or "AI Generated Deck"

            # Generate flashcards
            generated_deck = ai_interface.generate_flashcards_from_text(text, deck_name)

            if generated_deck:
                # Save the generated deck
                self.storage.save_deck(generated_deck)
                self.current_deck = generated_deck
                self.rich_ui.show_success(f"Generated deck '{deck_name}' with {len(generated_deck.flashcards)} cards!", "AI Generation Complete")

        except Exception as e:
            self.rich_ui.show_error(f"AI generation error: {e}", "AI Error")

        return True

    def ai_suggest_content(self, args: List[str] = None) -> bool:
        """Get AI suggestions for related content."""
        if not self.current_deck:
            if self.rich_ui:
                self.rich_ui.show_error("No deck loaded. Use 'load' command first.", "No Deck Loaded")
            else:
                print("No deck loaded. Use 'load' command first.")
            return True

        if not self.rich_ui or not RICH_UI_AVAILABLE:
            print("AI suggestions require Rich Terminal UI")
            return True

        try:
            ai_interface = RichAIInterface(self.rich_ui.console)

            # Get suggestion count
            count = 5
            if args and len(args) > 0:
                try:
                    count = int(args[0])
                    count = max(1, min(count, 20))  # Limit between 1 and 20
                except ValueError:
                    pass

            # Generate suggestions
            suggestions = ai_interface.suggest_related_content(self.current_deck, count)

            if suggestions:
                self.rich_ui.show_success(f"Generated {len(suggestions)} content suggestions!", "AI Suggestions")

        except Exception as e:
            self.rich_ui.show_error(f"AI suggestion error: {e}", "AI Error")

        return True

    def ai_enhance_cards(self, args: List[str] = None) -> bool:
        """Enhance existing flashcards with AI suggestions."""
        if not self.current_deck:
            if self.rich_ui:
                self.rich_ui.show_error("No deck loaded. Use 'load' command first.", "No Deck Loaded")
            else:
                print("No deck loaded. Use 'load' command first.")
            return True

        if not self.rich_ui or not RICH_UI_AVAILABLE:
            print("AI enhancement requires Rich Terminal UI")
            return True

        try:
            ai_interface = RichAIInterface(self.rich_ui.console)

            # Enhance cards
            results = ai_interface.enhance_existing_cards(self.current_deck)

            if results:
                self.rich_ui.show_success(f"Enhanced {results.get('applied', 0)} cards with AI suggestions!", "AI Enhancement Complete")

        except Exception as e:
            self.rich_ui.show_error(f"AI enhancement error: {e}", "AI Error")

        return True

    def exit_app(self, args: List[str] = None) -> bool:
        """Exit the application."""
        if self.rich_ui:
            self.rich_ui.show_success("Thanks for using FlashGenie! 👋", "Goodbye")
        else:
            print("Thanks for using FlashGenie!")
        return False
