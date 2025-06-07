"""
Core command handlers for FlashGenie CLI.

This module contains handlers for basic FlashGenie operations like import, quiz, list, stats, and export.
"""

import sys
from pathlib import Path
from flashgenie.utils.exceptions import FlashGenieError


def handle_import_command(args) -> None:
    """Handle the import command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.data.importers import CSVImporter, TextImporter
    
    storage = DataStorage()
    
    try:
        file_path = Path(args.file)
        if not file_path.exists():
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
            importer = TextImporter()
        else:
            print(f"Error: Unsupported file format '{format_type}'")
            print("Supported formats: csv, txt")
            sys.exit(1)
        
        # Import the file
        print(f"Importing from {file_path}...")
        deck = importer.import_file(file_path, args.name)
        
        # Save the deck
        storage.save_deck(deck)
        
        print(f"✅ Successfully imported {len(deck.flashcards)} cards into deck '{deck.name}'")
        
    except FlashGenieError as e:
        print(f"Import failed: {e}")
        sys.exit(1)


def handle_quiz_command(args) -> None:
    """Handle the quiz command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.core.quiz_engine import QuizEngine
    from flashgenie.interfaces.terminal_ui import TerminalUI
    
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
    """Handle the list command."""
    from flashgenie.data.storage import DataStorage
    
    storage = DataStorage()
    
    try:
        decks = storage.list_decks()
        
        if not decks:
            print("No decks found. Import some flashcards to get started.")
            return
        
        print("📚 **Your Flashcard Decks**")
        print("=" * 50)
        
        for deck_info in decks:
            print(f"📖 **{deck_info['name']}**")
            print(f"   Cards: {deck_info['card_count']}")
            print(f"   Created: {deck_info['created_at'].strftime('%Y-%m-%d %H:%M')}")
            print(f"   Modified: {deck_info['modified_at'].strftime('%Y-%m-%d %H:%M')}")
            
            if args.detailed:
                # Load full deck for detailed stats
                deck = storage.load_deck(deck_info['id'])
                if deck:
                    # Calculate basic stats
                    total_cards = len(deck.flashcards)
                    if total_cards > 0:
                        avg_difficulty = sum(card.difficulty for card in deck.flashcards) / total_cards
                        print(f"   Average difficulty: {avg_difficulty:.2f}")
                        
                        # Tag distribution
                        all_tags = []
                        for card in deck.flashcards:
                            all_tags.extend(card.tags)
                        
                        if all_tags:
                            unique_tags = list(set(all_tags))
                            print(f"   Tags: {', '.join(unique_tags[:5])}")
                            if len(unique_tags) > 5:
                                print(f"         ... and {len(unique_tags) - 5} more")
            
            print()
        
        print(f"Total: {len(decks)} deck{'s' if len(decks) != 1 else ''}")
        
    except FlashGenieError as e:
        print(f"Failed to list decks: {e}")
        sys.exit(1)


def handle_stats_command(args) -> None:
    """Handle the stats command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.core.analytics import AnalyticsEngine
    
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
                analytics = AnalyticsEngine()
                analytics_data = analytics.generate_deck_analytics(deck)
                
                if analytics_data:
                    print(f"\n📈 **Learning Analytics**")
                    print(f"Study sessions: {analytics_data.get('total_sessions', 0)}")
                    print(f"Total study time: {analytics_data.get('total_time', 0)} minutes")
                    print(f"Average accuracy: {analytics_data.get('average_accuracy', 0):.1%}")
                    
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
                most_recent = max(decks, key=lambda d: d['modified_at'])
                print(f"Most recent activity: {most_recent['name']} ({most_recent['modified_at'].strftime('%Y-%m-%d %H:%M')})")
        
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
