"""
Main entry point for FlashGenie application.

This module provides the main entry point and command-line interface
for the FlashGenie flashcard application.
"""

import sys
import argparse
from pathlib import Path

from flashgenie.interfaces.cli.terminal_ui import TerminalUI
from flashgenie.config import APP_NAME, APP_VERSION
from flashgenie.utils.logging_config import setup_logging


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='flashgenie',
        description=f'{APP_NAME} - Intelligent flashcard learning with spaced repetition',
        epilog='For more information, visit: https://github.com/himent12/FlashGenie'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'{APP_NAME} 1.0.0'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set logging level'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import flashcards from file')
    import_parser.add_argument('file', help='File to import')
    import_parser.add_argument('--name', help='Name for the imported deck')
    import_parser.add_argument('--format', choices=['csv', 'txt'], help='Force file format')
    
    # Quiz command
    quiz_parser = subparsers.add_parser('quiz', help='Start a quiz session')
    quiz_parser.add_argument('deck', nargs='?', help='Deck name or ID')
    quiz_parser.add_argument('--mode', choices=['spaced', 'random', 'sequential', 'difficult'],
                           default='spaced', help='Quiz mode')
    quiz_parser.add_argument('--max-questions', type=int, help='Maximum number of questions')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all decks')
    list_parser.add_argument('--detailed', action='store_true', help='Show detailed information')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('deck', nargs='?', help='Deck name or ID')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export deck data')
    export_parser.add_argument('deck', help='Deck name or ID')
    export_parser.add_argument('output', help='Output file path')
    export_parser.add_argument('--format', choices=['csv', 'json'], default='csv',
                              help='Export format')
    
    return parser


def handle_import_command(args) -> None:
    """Handle the import command."""
    from flashgenie.data.importers.csv_importer import CSVImporter
    from flashgenie.data.importers.txt_importer import TXTImporter
    from flashgenie.data.storage import DataStorage
    from flashgenie.utils.exceptions import FlashGenieError
    
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    try:
        # Determine importer
        if args.format:
            file_format = args.format
        else:
            file_format = file_path.suffix.lower().lstrip('.')
        
        if file_format == 'csv':
            importer = CSVImporter()
        elif file_format in ['txt', 'text']:
            importer = TXTImporter()
        else:
            print(f"Error: Unsupported file format: {file_format}")
            sys.exit(1)
        
        # Import deck
        print(f"Importing from {file_path}...")
        deck = importer.import_file(file_path, deck_name=args.name)
        
        # Save deck
        storage = DataStorage()
        storage.save_deck(deck)
        
        print(f"Successfully imported {len(deck.flashcards)} flashcards into deck '{deck.name}'")
        
    except FlashGenieError as e:
        print(f"Import failed: {e}")
        sys.exit(1)


def handle_quiz_command(args) -> None:
    """Handle the quiz command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.core.quiz_engine import QuizEngine, QuizMode
    from flashgenie.utils.exceptions import FlashGenieError
    
    storage = DataStorage()
    
    try:
        # Load deck
        if args.deck:
            deck = storage.load_deck_by_name(args.deck)
            if deck is None:
                deck = storage.load_deck(args.deck)
        else:
            # Show deck selection
            decks = storage.list_decks()
            if not decks:
                print("No decks available. Import some flashcards first!")
                sys.exit(1)
            
            print("Available decks:")
            for i, deck_info in enumerate(decks, 1):
                print(f"{i}. {deck_info['name']} ({deck_info['card_count']} cards)")
            
            choice = input("Select deck number: ").strip()
            if not choice.isdigit() or not (1 <= int(choice) <= len(decks)):
                print("Invalid selection")
                sys.exit(1)
            
            deck_info = decks[int(choice) - 1]
            deck = storage.load_deck(deck_info['deck_id'])
        
        # Start quiz using terminal UI
        ui = TerminalUI()
        ui.command_handler.current_deck = deck
        
        mode_map = {
            'spaced': 'spaced',
            'random': 'random',
            'sequential': 'sequential',
            'difficult': 'difficult'
        }
        
        ui.command_handler.handle_command('quiz', [mode_map[args.mode]])
        
    except FlashGenieError as e:
        print(f"Quiz failed: {e}")
        sys.exit(1)


def handle_list_command(args) -> None:
    """Handle the list command."""
    from flashgenie.data.storage import DataStorage
    
    storage = DataStorage()
    decks = storage.list_decks()
    
    if not decks:
        print("No decks found.")
        return
    
    if args.detailed:
        for deck in decks:
            print(f"\nDeck: {deck['name']}")
            print(f"  ID: {deck['deck_id']}")
            print(f"  Cards: {deck['card_count']}")
            print(f"  Due: {deck['due_count']}")
            print(f"  Created: {deck['created_at']}")
            print(f"  Modified: {deck['modified_at']}")
            if deck['description']:
                print(f"  Description: {deck['description']}")
            if deck['tags']:
                print(f"  Tags: {', '.join(deck['tags'])}")
    else:
        print(f"{'Name':<30} {'Cards':<8} {'Due':<6} {'Modified'}")
        print("-" * 55)
        for deck in decks:
            print(f"{deck['name']:<30} {deck['card_count']:<8} {deck['due_count']:<6} {deck['modified_at'][:10]}")


def handle_stats_command(args) -> None:
    """Handle the stats command."""
    # TODO: Implement stats command
    print("Stats command not yet implemented")


def handle_export_command(args) -> None:
    """Handle the export command."""
    # TODO: Implement export command
    print("Export command not yet implemented")


def main():
    """Main entry point for the application."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Setup logging
    log_level = 'DEBUG' if args.verbose else args.log_level
    setup_logging(log_level)
    
    # Handle commands
    if args.command == 'import':
        handle_import_command(args)
    elif args.command == 'quiz':
        handle_quiz_command(args)
    elif args.command == 'list':
        handle_list_command(args)
    elif args.command == 'stats':
        handle_stats_command(args)
    elif args.command == 'export':
        handle_export_command(args)
    else:
        # No command specified, start interactive mode
        ui = TerminalUI()
        ui.start()


if __name__ == "__main__":
    main()
