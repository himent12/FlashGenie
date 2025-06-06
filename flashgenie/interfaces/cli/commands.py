"""
Command handlers for the CLI interface.

This module provides command handling functionality for
the terminal-based user interface.
"""

from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
import sys

from flashgenie.core.deck import Deck
from flashgenie.core.quiz_engine import QuizEngine, QuizMode
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
        self.current_deck: Optional[Deck] = None
        
        # Command registry
        self.commands: Dict[str, Callable] = {
            'help': self.show_help,
            'list': self.list_decks,
            'load': self.load_deck,
            'import': self.import_file,
            'quiz': self.start_quiz,
            'stats': self.show_stats,
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
            
            # Submit answer
            correct = self.quiz_engine.submit_answer(question, user_answer)
            
            # Show result
            print(self.formatter.quiz_result(
                correct,
                question.flashcard.answer,
                user_answer if not correct else None
            ))
            
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
        
        # Basic stats
        total_cards = len(deck.flashcards)
        due_cards = deck.due_count
        reviewed_cards = sum(1 for card in deck.flashcards if card.review_count > 0)
        
        stats_data = [
            ["Total Cards", str(total_cards)],
            ["Due for Review", str(due_cards)],
            ["Reviewed Cards", str(reviewed_cards)],
            ["Average Accuracy", f"{deck.average_accuracy:.1%}"],
        ]
        
        print(self.formatter.table(["Metric", "Value"], stats_data))
        
        # Difficulty distribution
        if deck.flashcards:
            easy_cards = sum(1 for card in deck.flashcards if card.difficulty < 0.3)
            medium_cards = sum(1 for card in deck.flashcards if 0.3 <= card.difficulty < 0.7)
            hard_cards = sum(1 for card in deck.flashcards if card.difficulty >= 0.7)
            
            print(f"\nDifficulty Distribution:")
            print(f"Easy: {easy_cards} cards")
            print(f"Medium: {medium_cards} cards") 
            print(f"Hard: {hard_cards} cards")
        
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
