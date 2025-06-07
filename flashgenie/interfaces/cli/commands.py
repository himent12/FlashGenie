"""
Command handlers for the CLI interface.

This module provides command handling functionality for
the terminal-based user interface.
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
from flashgenie.interfaces.cli.formatters import OutputFormatter
from flashgenie.utils.exceptions import FlashGenieError


class CommandHandler:
    """
    Handles CLI commands and user interactions.
    """
    
    def __init__(self):
        """Initialize the command handler."""
        self.formatter = OutputFormatter()
        self.storage = DataStorage()
        self.quiz_engine = QuizEngine()
        self.tag_manager = TagManager()
        self.collection_manager = SmartCollectionManager(self.tag_manager)
        self.current_deck: Optional[Deck] = None
        
        # Command registry
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
            'exit': self.exit_app,
            'quit': self.exit_app,
        }
    
    def handle_command(self, command: str, args: List[str] = None) -> bool:
        """
        Handle a user command.
        
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
                print(self.formatter.error(str(e)))
                return True
            except Exception as e:
                print(self.formatter.error(f"Unexpected error: {e}"))
                return True
        else:
            print(self.formatter.error(f"Unknown command: {command}"))
            print("Type 'help' for available commands.")
            return True
    
    def show_help(self, args: List[str] = None) -> bool:
        """Show help information."""
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
  exit/quit            - Exit the application

Quiz Modes:
  spaced    - Spaced repetition (default)
  random    - Random order
  sequential - Sequential order
  difficult - Difficult cards first

Tag Commands:
  tags                 - Show tag statistics
  tags create <path>   - Create new tag (e.g., "Science > Biology")
  tags suggest         - Suggest tags for untagged cards

Examples:
  load "My Spanish Deck"
  import flashcards.csv
  quiz spaced
  autotag
  tags create "Math > Algebra"
  collections
        """
        print(help_text)
        return True
    
    def list_decks(self, args: List[str] = None) -> bool:
        """List all available decks."""
        decks = self.storage.list_decks()
        
        if not decks:
            print(self.formatter.info("No decks found. Import some flashcards to get started!"))
            return True
        
        print(self.formatter.header("Available Decks"))
        
        headers = ["Name", "Cards", "Due", "Modified"]
        rows = []
        
        for deck in decks:
            rows.append([
                deck["name"],
                str(deck["card_count"]),
                str(deck["due_count"]),
                deck["modified_at"][:10]  # Just the date part
            ])
        
        print(self.formatter.table(headers, rows))
        return True
    
    def load_deck(self, args: List[str]) -> bool:
        """Load a deck by name or ID."""
        if not args:
            print(self.formatter.error("Please specify a deck name or ID"))
            return True
        
        deck_identifier = " ".join(args)
        
        # Try to load by name first
        deck = self.storage.load_deck_by_name(deck_identifier)
        
        if deck is None:
            # Try to load by ID
            try:
                deck = self.storage.load_deck(deck_identifier)
            except FlashGenieError:
                print(self.formatter.error(f"Deck '{deck_identifier}' not found"))
                return True
        
        self.current_deck = deck
        print(self.formatter.success(f"Loaded deck: {deck.name}"))
        print(self.formatter.deck_summary({
            "name": deck.name,
            "card_count": len(deck.flashcards),
            "due_count": deck.due_count,
            "description": deck.description,
            "tags": deck.tags
        }))
        
        return True
    
    def import_file(self, args: List[str]) -> bool:
        """Import flashcards from a file."""
        if not args:
            print(self.formatter.error("Please specify a file path"))
            return True
        
        file_path = Path(" ".join(args))
        
        if not file_path.exists():
            print(self.formatter.error(f"File not found: {file_path}"))
            return True
        
        try:
            # Determine importer based on file extension
            if file_path.suffix.lower() == '.csv':
                importer = CSVImporter()
            elif file_path.suffix.lower() in ['.txt', '.text']:
                importer = TXTImporter()
            else:
                print(self.formatter.error(f"Unsupported file format: {file_path.suffix}"))
                return True
            
            print(f"Importing from {file_path}...")
            deck = importer.import_file(file_path)
            
            # Save the imported deck
            self.storage.save_deck(deck)
            self.current_deck = deck
            
            print(self.formatter.success(f"Successfully imported {len(deck.flashcards)} flashcards"))
            print(self.formatter.deck_summary({
                "name": deck.name,
                "card_count": len(deck.flashcards),
                "due_count": deck.due_count,
                "description": deck.description,
                "tags": deck.tags
            }))
            
        except FlashGenieError as e:
            print(self.formatter.error(f"Import failed: {e}"))
        
        return True
    
    def start_quiz(self, args: List[str] = None) -> bool:
        """Start a quiz session."""
        if self.current_deck is None:
            print(self.formatter.error("No deck loaded. Use 'load' command first."))
            return True
        
        if not self.current_deck.flashcards:
            print(self.formatter.error("The current deck is empty."))
            return True
        
        # Determine quiz mode
        mode = QuizMode.SPACED_REPETITION  # default
        if args:
            mode_str = args[0].lower()
            mode_map = {
                'spaced': QuizMode.SPACED_REPETITION,
                'random': QuizMode.RANDOM,
                'sequential': QuizMode.SEQUENTIAL,
                'difficult': QuizMode.DIFFICULT_FIRST
            }
            mode = mode_map.get(mode_str, QuizMode.SPACED_REPETITION)
        
        # Start quiz session
        session = self.quiz_engine.start_session(self.current_deck, mode)
        
        print(self.formatter.header(f"Quiz: {self.current_deck.name}"))
        print(f"Mode: {mode.value.replace('_', ' ').title()}")
        print(self.formatter.print_separator())
        
        # Quiz loop
        while True:
            question = self.quiz_engine.get_next_question()
            
            if question is None:
                break
            
            # Display question
            print(self.formatter.quiz_question(
                question.flashcard.question,
                question.question_number,
                session.max_questions
            ))
            
            # Get user answer
            try:
                user_answer = input("Your answer: ").strip()
            except KeyboardInterrupt:
                print("\n" + self.formatter.info("Quiz interrupted by user"))
                break
            
            if user_answer.lower() in ['quit', 'exit']:
                break
            
            # Ask for confidence rating
            confidence = None
            try:
                confidence_input = input("How confident were you? (1=Very Low, 2=Low, 3=Medium, 4=High, 5=Very High, or press Enter to skip): ").strip()
                if confidence_input and confidence_input.isdigit():
                    confidence = int(confidence_input)
                    if not 1 <= confidence <= 5:
                        confidence = None
            except (ValueError, KeyboardInterrupt):
                confidence = None

            # Submit answer with confidence
            correct = self.quiz_engine.submit_answer(question, user_answer, confidence=confidence)

            # Show result
            result_text = self.formatter.quiz_result(
                correct,
                question.flashcard.answer,
                user_answer if not correct else None
            )

            # Add difficulty adjustment info if available
            if hasattr(question.flashcard, 'metadata') and 'difficulty_updates' in question.flashcard.metadata:
                recent_updates = question.flashcard.metadata['difficulty_updates']
                if recent_updates:
                    latest_update = recent_updates[-1]
                    if latest_update.get('reason'):
                        result_text += f"\n{self.formatter.dim('Difficulty adjusted: ' + latest_update['reason'])}"

            print(result_text)
            
            # Show progress
            stats = self.quiz_engine.get_session_stats()
            print(f"\nProgress: {self.formatter.progress_bar(stats['questions_answered'], session.max_questions)}")
            
            input("\nPress Enter to continue...")
            self.formatter.clear_screen()
        
        # End session and show final stats
        completed_session = self.quiz_engine.end_session()
        
        if completed_session and completed_session.questions:
            print(self.formatter.header("Quiz Complete!"))
            print(self.formatter.quiz_stats(
                completed_session.correct_answers,
                completed_session.total_questions,
                completed_session.accuracy / 100
            ))
            
            # Save updated deck
            self.storage.save_deck(self.current_deck)
        
        return True
    
    def show_stats(self, args: List[str] = None) -> bool:
        """Show statistics for the current deck."""
        if self.current_deck is None:
            print(self.formatter.error("No deck loaded. Use 'load' command first."))
            return True

        deck = self.current_deck

        print(self.formatter.header(f"Statistics: {deck.name}"))

        # Get comprehensive performance summary
        performance = deck.get_performance_summary()

        if not performance:
            print(self.formatter.info("No performance data available"))
            return True

        # Basic stats
        stats_data = [
            ["Total Cards", str(performance['total_cards'])],
            ["Reviewed Cards", str(performance['reviewed_cards'])],
            ["Due for Review", str(performance['due_cards'])],
            ["Total Reviews", str(performance.get('total_reviews', 0))],
            ["Average Accuracy", f"{performance['average_accuracy']:.1%}"],
            ["Average Difficulty", f"{performance['average_difficulty']:.2f}"],
        ]

        if performance.get('average_response_time', 0) > 0:
            stats_data.append(["Avg Response Time", f"{performance['average_response_time']:.1f}s"])

        print(self.formatter.table(["Metric", "Value"], stats_data))

        # Difficulty distribution
        distribution = performance.get('difficulty_distribution', {})
        if distribution:
            print(f"\nDifficulty Distribution:")
            print(f"Easy (0.0-0.33): {distribution.get('easy', 0)} cards")
            print(f"Medium (0.33-0.67): {distribution.get('medium', 0)} cards")
            print(f"Hard (0.67-1.0): {distribution.get('hard', 0)} cards")

        # Show cards with recent difficulty adjustments
        recent_adjustments = []
        for card in deck.flashcards:
            if (hasattr(card, 'metadata') and 'difficulty_updates' in card.metadata and
                card.metadata['difficulty_updates']):
                recent_adjustments.append(card)

        if recent_adjustments:
            print(f"\nRecent Difficulty Adjustments: {len(recent_adjustments)} cards")
            for card in recent_adjustments[:3]:  # Show first 3
                latest_update = card.metadata['difficulty_updates'][-1]
                print(f"  {card.question[:40]}... - {latest_update.get('reason', 'Adjusted')}")

        # Show tag distribution
        tag_counts = {}
        for card in deck.flashcards:
            for tag in card.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        if tag_counts:
            print(f"\nTop Tags:")
            sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            for tag, count in sorted_tags[:5]:
                print(f"  {tag}: {count} cards")

        return True

    def show_collections(self, args: List[str] = None) -> bool:
        """Show smart collections and their statistics."""
        if self.current_deck is None:
            print(self.formatter.error("No deck loaded. Use 'load' command first."))
            return True

        print(self.formatter.header("Smart Collections"))

        collections = self.collection_manager.list_collections()
        if not collections:
            print(self.formatter.info("No smart collections available."))
            return True

        for collection_name in collections:
            collection = self.collection_manager.get_collection(collection_name)
            if collection:
                stats = collection.get_statistics(self.current_deck)
                print(f"\n{self.formatter.highlight(collection_name)}")
                print(f"  Description: {collection.criteria.description}")
                print(f"  Cards: {stats['total_cards']}")
                print(f"  Due: {stats.get('due_cards', 0)}")
                if stats['total_cards'] > 0:
                    print(f"  Avg Difficulty: {stats['avg_difficulty']:.2f}")
                    print(f"  Avg Accuracy: {stats['avg_accuracy']:.1%}")

        return True

    def auto_tag_deck(self, args: List[str] = None) -> bool:
        """Automatically tag cards in the current deck."""
        if self.current_deck is None:
            print(self.formatter.error("No deck loaded. Use 'load' command first."))
            return True

        print("Analyzing cards for automatic tagging...")
        tagged_count = self.current_deck.auto_tag_cards(self.tag_manager)

        if tagged_count > 0:
            print(self.formatter.success(f"Added tags to {tagged_count} cards"))
            # Save the updated deck
            self.storage.save_deck(self.current_deck)
        else:
            print(self.formatter.info("No new tags were added"))

        return True

    def manage_tags(self, args: List[str] = None) -> bool:
        """Manage tags and tag hierarchies."""
        if not args:
            # Show tag statistics
            stats = self.tag_manager.get_tag_statistics()
            print(self.formatter.header("Tag Statistics"))
            print(f"Total tags: {stats['total_tags']}")
            print(f"Total aliases: {stats['total_aliases']}")
            print(f"Auto-tag rules: {stats['total_rules']}")
            print(f"Hierarchy depth: {stats['hierarchy_depth']}")

            if self.current_deck:
                # Show tags used in current deck
                all_tags = set()
                for card in self.current_deck.flashcards:
                    all_tags.update(card.tags)

                if all_tags:
                    print(f"\nTags in current deck:")
                    for tag in sorted(all_tags):
                        count = sum(1 for card in self.current_deck.flashcards if tag in card.tags)
                        print(f"  {tag}: {count} cards")

            return True

        command = args[0].lower()

        if command == "create" and len(args) >= 2:
            # Create new tag or hierarchy
            tag_path = args[1]
            description = " ".join(args[2:]) if len(args) > 2 else ""

            try:
                if ">" in tag_path:
                    # Hierarchical tag
                    tag = self.tag_manager.create_hierarchical_tag(tag_path, {tag_path.split(">")[-1].strip(): description})
                else:
                    # Simple tag
                    tag = self.tag_manager.create_tag(tag_path, description=description)

                print(self.formatter.success(f"Created tag: {tag.name}"))
            except ValueError as e:
                print(self.formatter.error(str(e)))

        elif command == "suggest" and self.current_deck:
            # Suggest tags for untagged cards
            untagged_cards = [card for card in self.current_deck.flashcards if not card.tags]

            if not untagged_cards:
                print(self.formatter.info("All cards have tags"))
                return True

            print(f"Suggesting tags for {len(untagged_cards)} untagged cards:")

            for i, card in enumerate(untagged_cards[:5]):  # Show first 5
                suggestions = self.tag_manager.suggest_tags(card.question, card.answer)
                if suggestions:
                    print(f"\nCard: {card.question[:50]}...")
                    print(f"Suggested tags: {', '.join(suggestions)}")

        else:
            print(self.formatter.error("Usage: tags [create <tag_path> [description] | suggest]"))

        return True

    def exit_app(self, args: List[str] = None) -> bool:
        """Exit the application."""
        print(self.formatter.success("Thanks for using FlashGenie!"))
        return False
    
    def get_user_input(self, prompt: str) -> str:
        """Get user input with prompt."""
        try:
            return input(f"{prompt}: ").strip()
        except KeyboardInterrupt:
            print("\n" + self.formatter.info("Operation cancelled"))
            return ""
