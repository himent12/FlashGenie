"""
Core command handlers for FlashGenie CLI.

This module contains handlers for basic FlashGenie operations like import, quiz, list, stats, and export.
Enhanced for v1.8.4 with Rich Terminal UI and Interactive Shell.
"""

import sys
from pathlib import Path
from flashgenie.utils.exceptions import FlashGenieError

# Rich UI components for enhanced terminal interface
try:
    from ...terminal import RichTerminalUI
    from ...terminal.help_system import HelpSystem
    RICH_UI_AVAILABLE = True
except ImportError:
    RICH_UI_AVAILABLE = False
    print("Warning: Rich UI not available, falling back to basic terminal interface")


def handle_help_command(args) -> None:
    """Handle the help command with Rich Terminal UI."""
    if RICH_UI_AVAILABLE:
        ui = RichTerminalUI()
        help_system = HelpSystem(ui.console)

        if hasattr(args, 'command') and args.command:
            # Show help for specific command
            help_system.show_command_help(args.command)
        elif hasattr(args, 'category') and args.category:
            # Show help for category
            help_system.show_category_help(args.category)
        else:
            # Show main help menu
            help_system.show_main_help()
    else:
        # Fallback help
        print("FlashGenie v1.8.4 - Intelligent Flashcard Learning")
        print("=" * 50)
        print("Available commands:")
        print("  help     - Show this help message")
        print("  version  - Show version information")
        print("  list     - List all flashcard decks")
        print("  import   - Import flashcards from file")
        print("  export   - Export flashcard deck")
        print("  quiz     - Start a quiz session")
        print("  stats    - Show statistics")
        print("")
        print("Use 'python -m flashgenie COMMAND --help' for command-specific help")


def handle_search_command(args) -> None:
    """Handle the search command for finding commands."""
    if RICH_UI_AVAILABLE:
        ui = RichTerminalUI()
        help_system = HelpSystem(ui.console)
        help_system.search_commands(args.query)
    else:
        print(f"Search functionality requires Rich Terminal UI")
        print("Available commands: help, version, list, import, export, quiz, stats")


def handle_accessibility_command(args) -> None:
    """Handle accessibility configuration command."""
    if RICH_UI_AVAILABLE:
        ui = RichTerminalUI()

        if hasattr(args, 'enable') and args.enable:
            ui.enable_accessibility_mode(args.enable)
        elif hasattr(args, 'disable') and args.disable:
            ui.disable_accessibility_mode(args.disable)
        elif hasattr(args, 'status') and args.status:
            ui.show_accessibility_menu()
        elif hasattr(args, 'test') and args.test:
            # Test accessibility features
            ui.show_info("Testing accessibility features...", "Accessibility Test")
            ui.announce("Screen reader test announcement")
            ui.show_success("Accessibility test completed", "Test Complete")
        else:
            ui.show_accessibility_menu()
    else:
        print("Accessibility features require Rich Terminal UI")


def handle_debug_command(args) -> None:
    """Handle debug mode command."""
    if RICH_UI_AVAILABLE:
        ui = RichTerminalUI()

        if hasattr(args, 'enable') and args.enable:
            ui.toggle_debug_mode()
            ui.show_success("Debug mode enabled", "Debug")
        elif hasattr(args, 'disable') and args.disable:
            ui.debug_mode = False
            ui.show_info("Debug mode disabled", "Debug")
        elif hasattr(args, 'console') and args.console:
            ui.show_debug_panel()
        else:
            ui.toggle_debug_mode()
    else:
        print("Debug features require Rich Terminal UI")


def handle_performance_command(args) -> None:
    """Handle performance monitoring command."""
    if RICH_UI_AVAILABLE:
        ui = RichTerminalUI()

        if hasattr(args, 'dashboard') and args.dashboard:
            ui.show_performance_dashboard()
        elif hasattr(args, 'optimize') and args.optimize:
            result = ui.optimize_performance()
            ui.show_success(f"Performance optimized: {result.get('memory_freed_mb', 0):.1f}MB freed", "Optimization")
        elif hasattr(args, 'monitor') and args.monitor:
            ui.show_info("Performance monitoring enabled", "Performance")
            ui.show_performance_dashboard()
        else:
            ui.show_performance_dashboard()
    else:
        print("Performance features require Rich Terminal UI")


def handle_import_command(args) -> None:
    """Handle the import command with enhanced Rich UI."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.data.importers import CSVImporter, TXTImporter

    # Initialize UI
    if RICH_UI_AVAILABLE:
        ui = RichTerminalUI()
        ui.navigation.push_context("import", "Import Flashcards")

    storage = DataStorage()

    try:
        file_path = Path(args.file)
        if not file_path.exists():
            if RICH_UI_AVAILABLE:
                ui.show_error(f"File '{args.file}' not found", "Import Error")
            else:
                print(f"Error: File '{args.file}' not found")
            sys.exit(1)

        # Determine format
        if args.format:
            format_type = args.format
        else:
            format_type = file_path.suffix.lower().lstrip('.')

        # Select appropriate importer
        if format_type == 'csv':
            importer = CSVImporter()
        elif format_type in ['txt', 'text']:
            importer = TXTImporter()
        else:
            error_msg = f"Unsupported file format '{format_type}'\nSupported formats: csv, txt"
            if RICH_UI_AVAILABLE:
                ui.show_error(error_msg, "Format Error")
            else:
                print(f"Error: {error_msg}")
            sys.exit(1)

        # Import the file with progress indication
        if RICH_UI_AVAILABLE:
            with ui.widgets.create_status_indicator(f"Importing from {file_path.name}..."):
                deck = importer.import_file(file_path, deck_name=args.name)
                storage.save_deck(deck)

            # Show success message with details
            success_msg = f"Successfully imported {len(deck.flashcards)} cards into deck '{deck.name}'"
            ui.show_success(success_msg, "Import Complete")

            # Show deck summary
            deck_stats = {
                "Name": deck.name,
                "Cards": len(deck.flashcards),
                "File": str(file_path),
                "Format": format_type.upper()
            }
            stats_panel = ui.widgets.create_stats_panel(deck_stats, "Import Summary")
            ui.console.print(stats_panel)
        else:
            print(f"Importing from {file_path}...")
            deck = importer.import_file(file_path, deck_name=args.name)
            storage.save_deck(deck)
            print(f"✅ Successfully imported {len(deck.flashcards)} cards into deck '{deck.name}'")

    except FlashGenieError as e:
        if RICH_UI_AVAILABLE:
            ui.show_error(str(e), "Import Failed")
        else:
            print(f"Import failed: {e}")
        sys.exit(1)


def handle_quiz_command(args) -> None:
    """Handle the quiz command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.core.study_system.quiz_engine import QuizEngine
    from flashgenie.interfaces.cli.terminal_ui import TerminalUI
    
    storage = DataStorage()
    
    try:
        if args.deck:
            # Load specific deck
            deck = storage.load_deck_by_name(args.deck)
            if deck is None:
                deck = storage.load_deck(args.deck)
            if deck is None:
                print(f"Error: Deck '{args.deck}' not found")
                sys.exit(1)
        else:
            # Interactive deck selection
            decks = storage.list_decks()
            if not decks:
                print("No decks found. Import some flashcards first.")
                sys.exit(1)
            
            print("Available decks:")
            for i, deck_info in enumerate(decks, 1):
                print(f"{i}. {deck_info['name']} ({deck_info['card_count']} cards)")
            
            while True:
                try:
                    choice = int(input("\nSelect a deck (number): ")) - 1
                    if 0 <= choice < len(decks):
                        deck = storage.load_deck(decks[choice]['id'])
                        break
                    else:
                        print("Invalid selection. Please try again.")
                except (ValueError, KeyboardInterrupt):
                    print("\nQuiz cancelled.")
                    sys.exit(0)
        
        # Start quiz
        quiz_engine = QuizEngine()
        quiz_config = {
            'mode': args.mode,
            'max_questions': args.max_questions
        }
        
        print(f"\n🎯 Starting quiz: {deck.name}")
        print(f"Mode: {args.mode}")
        if args.max_questions:
            print(f"Max questions: {args.max_questions}")
        print("=" * 50)
        
        # Run quiz session
        session = quiz_engine.create_session(deck, quiz_config)
        ui = TerminalUI()
        ui.run_quiz_session(session)
        
    except FlashGenieError as e:
        print(f"Quiz failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nQuiz interrupted.")
        sys.exit(0)


def handle_list_command(args) -> None:
    """Handle the list command with enhanced Rich UI."""
    from flashgenie.data.storage import DataStorage

    # Initialize UI
    if RICH_UI_AVAILABLE:
        ui = RichTerminalUI()
        ui.navigation.push_context("list", "Deck List")

    storage = DataStorage()

    try:
        decks = storage.list_decks()

        if not decks:
            if RICH_UI_AVAILABLE:
                ui.show_info("No decks found. Import some flashcards to get started.", "Empty Library")
            else:
                print("No decks found. Import some flashcards to get started.")
            return

        if RICH_UI_AVAILABLE:
            # Create enhanced table display
            headers = ["Name", "Cards", "Created", "Modified"]
            rows = []

            for deck_info in decks:
                # Handle both datetime objects and strings
                created_at = deck_info['created_at']
                modified_at = deck_info['modified_at']

                if hasattr(created_at, 'strftime'):
                    created = created_at.strftime('%Y-%m-%d')
                else:
                    created = str(created_at)[:10]  # Take first 10 chars if string

                if hasattr(modified_at, 'strftime'):
                    modified = modified_at.strftime('%Y-%m-%d')
                else:
                    modified = str(modified_at)[:10]  # Take first 10 chars if string

                row = [
                    deck_info['name'],
                    str(deck_info['card_count']),
                    created,
                    modified
                ]

                if args.detailed:
                    # Load full deck for detailed stats
                    deck = storage.load_deck(deck_info['id'])
                    if deck and len(deck.flashcards) > 0:
                        avg_difficulty = sum(card.difficulty for card in deck.flashcards) / len(deck.flashcards)
                        row.append(f"{avg_difficulty:.2f}")

                rows.append(row)

            if args.detailed:
                headers.append("Avg Difficulty")

            # Create and display table
            table = ui.widgets.create_table("📚 Your Flashcard Decks", headers, rows)
            ui.console.print(table)

            # Show summary stats
            total_cards = sum(deck_info['card_count'] for deck_info in decks)
            summary_stats = {
                "Total Decks": len(decks),
                "Total Cards": total_cards,
                "Average Cards per Deck": f"{total_cards / len(decks):.1f}" if decks else "0"
            }

            if decks:
                most_recent = max(decks, key=lambda d: d['modified_at'] if hasattr(d['modified_at'], 'strftime') else d['modified_at'])
                modified_str = most_recent['modified_at'].strftime('%Y-%m-%d') if hasattr(most_recent['modified_at'], 'strftime') else str(most_recent['modified_at'])[:10]
                summary_stats["Most Recent"] = f"{most_recent['name']} ({modified_str})"

            stats_panel = ui.widgets.create_stats_panel(summary_stats, "Library Summary")
            ui.console.print(stats_panel)

        else:
            # Fallback to basic display
            print("📚 **Your Flashcard Decks**")
            print("=" * 50)

            for deck_info in decks:
                print(f"📖 **{deck_info['name']}**")
                print(f"   Cards: {deck_info['card_count']}")

                # Handle both datetime objects and strings
                created_str = deck_info['created_at'].strftime('%Y-%m-%d %H:%M') if hasattr(deck_info['created_at'], 'strftime') else str(deck_info['created_at'])
                modified_str = deck_info['modified_at'].strftime('%Y-%m-%d %H:%M') if hasattr(deck_info['modified_at'], 'strftime') else str(deck_info['modified_at'])

                print(f"   Created: {created_str}")
                print(f"   Modified: {modified_str}")
                print()

            print(f"Total: {len(decks)} deck{'s' if len(decks) != 1 else ''}")

    except FlashGenieError as e:
        if RICH_UI_AVAILABLE:
            ui.show_error(str(e), "List Error")
        else:
            print(f"Failed to list decks: {e}")
        sys.exit(1)


def handle_stats_command(args) -> None:
    """Handle the stats command."""
    from flashgenie.data.storage import DataStorage
    # Analytics engine not available in current structure
    # from flashgenie.core.analytics import AnalyticsEngine
    
    storage = DataStorage()
    
    try:
        if args.deck:
            # Show stats for specific deck
            deck = storage.load_deck_by_name(args.deck)
            if deck is None:
                deck = storage.load_deck(args.deck)
            if deck is None:
                print(f"Error: Deck '{args.deck}' not found")
                sys.exit(1)
            
            print(f"📊 **Statistics for '{deck.name}'**")
            print("=" * 50)
            
            # Basic stats
            total_cards = len(deck.flashcards)
            print(f"Total cards: {total_cards}")
            
            if total_cards > 0:
                avg_difficulty = sum(card.difficulty for card in deck.flashcards) / total_cards
                print(f"Average difficulty: {avg_difficulty:.2f}")
                
                # Difficulty distribution
                easy_cards = sum(1 for card in deck.flashcards if card.difficulty < 0.4)
                medium_cards = sum(1 for card in deck.flashcards if 0.4 <= card.difficulty <= 0.7)
                hard_cards = sum(1 for card in deck.flashcards if card.difficulty > 0.7)
                
                print(f"\nDifficulty distribution:")
                print(f"   Easy (< 0.4): {easy_cards} cards ({easy_cards/total_cards*100:.1f}%)")
                print(f"   Medium (0.4-0.7): {medium_cards} cards ({medium_cards/total_cards*100:.1f}%)")
                print(f"   Hard (> 0.7): {hard_cards} cards ({hard_cards/total_cards*100:.1f}%)")
                
                # Tag analysis
                all_tags = []
                for card in deck.flashcards:
                    all_tags.extend(card.tags)
                
                if all_tags:
                    from collections import Counter
                    tag_counts = Counter(all_tags)
                    print(f"\nMost common tags:")
                    for tag, count in tag_counts.most_common(5):
                        print(f"   {tag}: {count} cards")
            
            # Analytics if available
            try:
                # Analytics engine not available in current structure
                # analytics = AnalyticsEngine()
                # analytics_data = analytics.generate_deck_analytics(deck)

                # if analytics_data:
                #     print(f"\n📈 **Learning Analytics**")
                #     print(f"Study sessions: {analytics_data.get('total_sessions', 0)}")
                #     print(f"Total study time: {analytics_data.get('total_time', 0)} minutes")
                #     print(f"Average accuracy: {analytics_data.get('average_accuracy', 0):.1%}")
                pass

            except Exception:
                # Analytics not available or failed
                pass
        
        else:
            # Show overall stats
            decks = storage.list_decks()
            
            print("📊 **FlashGenie Statistics**")
            print("=" * 50)
            
            total_decks = len(decks)
            total_cards = sum(deck_info['card_count'] for deck_info in decks)
            
            print(f"Total decks: {total_decks}")
            print(f"Total cards: {total_cards}")
            
            if total_cards > 0:
                avg_cards_per_deck = total_cards / total_decks
                print(f"Average cards per deck: {avg_cards_per_deck:.1f}")
            
            if decks:
                # Most recent activity
                most_recent = max(decks, key=lambda d: d['modified_at'] if hasattr(d['modified_at'], 'strftime') else d['modified_at'])
                modified_str = most_recent['modified_at'].strftime('%Y-%m-%d %H:%M') if hasattr(most_recent['modified_at'], 'strftime') else str(most_recent['modified_at'])
                print(f"Most recent activity: {most_recent['name']} ({modified_str})")
        
    except FlashGenieError as e:
        print(f"Stats failed: {e}")
        sys.exit(1)


def handle_export_command(args) -> None:
    """Handle the export command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.data.exporters import CSVExporter, JSONExporter
    
    storage = DataStorage()
    
    try:
        # Load deck
        deck = storage.load_deck_by_name(args.deck)
        if deck is None:
            deck = storage.load_deck(args.deck)
        if deck is None:
            print(f"Error: Deck '{args.deck}' not found")
            sys.exit(1)
        
        # Select appropriate exporter
        if args.format == 'csv':
            exporter = CSVExporter()
        elif args.format == 'json':
            exporter = JSONExporter()
        else:
            print(f"Error: Unsupported export format '{args.format}'")
            print("Supported formats: csv, json")
            sys.exit(1)
        
        # Export the deck
        output_path = Path(args.output)
        print(f"Exporting '{deck.name}' to {output_path}...")
        
        exporter.export_deck(deck, output_path)
        
        print(f"✅ Successfully exported {len(deck.flashcards)} cards to {output_path}")
        
    except FlashGenieError as e:
        print(f"Export failed: {e}")
        sys.exit(1)
