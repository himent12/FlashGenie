"""
Rich Quiz Interface for FlashGenie v1.8.5 Phase 1.

This module provides a beautiful Rich Terminal UI quiz experience with
interactive question display, real-time progress tracking, and enhanced feedback.
"""

from typing import List, Dict, Any, Optional, Tuple
import time
from datetime import datetime, timedelta
from enum import Enum

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich.columns import Columns

from flashgenie.core.content_system.flashcard import Flashcard
from flashgenie.core.content_system.deck import Deck
from flashgenie.core.study_system.quiz_engine import QuizEngine, QuizMode
from flashgenie.utils.fuzzy_matching import FuzzyMatchResult, MatchType


class QuizState(Enum):
    """Quiz session states."""
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ConfidenceLevel(Enum):
    """User confidence levels."""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


class RichQuizInterface:
    """
    Rich Terminal UI Quiz Interface.
    
    Provides a beautiful, interactive quiz experience with Rich formatting,
    real-time progress tracking, and enhanced user feedback.
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the Rich Quiz Interface.
        
        Args:
            console: Rich Console instance (creates new if None)
        """
        self.console = console or Console()
        self.quiz_engine = QuizEngine()
        
        # Quiz session state
        self.current_deck: Optional[Deck] = None
        self.current_card: Optional[Flashcard] = None
        self.quiz_state = QuizState.STARTING
        self.session_stats = {
            'total_cards': 0,
            'current_card': 0,
            'correct_answers': 0,
            'incorrect_answers': 0,
            'skipped_cards': 0,
            'start_time': None,
            'end_time': None,
            'total_time': 0,
            'average_response_time': 0,
            'confidence_scores': [],
            'difficulty_adjustments': 0
        }
        
        # Rich UI components
        self.layout = Layout()
        self.progress_task = None
        
        # Quiz configuration
        self.show_hints = True
        self.show_tags = True
        self.show_difficulty = True
        self.timed_mode = False
        self.time_limit = 30  # seconds per question
    
    def start_quiz_session(self, deck: Deck, mode: QuizMode = QuizMode.SPACED_REPETITION,
                          card_count: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Start a Rich quiz session.
        
        Args:
            deck: Deck to quiz from
            mode: Quiz mode (adaptive, random, sequential, etc.)
            card_count: Number of cards to quiz (None for all due cards)
            **kwargs: Additional quiz configuration
            
        Returns:
            Quiz session results
        """
        self.current_deck = deck
        self.quiz_state = QuizState.STARTING
        
        # Configure quiz options
        self.timed_mode = kwargs.get('timed', False)
        self.time_limit = kwargs.get('time_limit', 30)
        self.show_hints = kwargs.get('show_hints', True)
        self.show_tags = kwargs.get('show_tags', True)
        self.show_difficulty = kwargs.get('show_difficulty', True)
        
        # Initialize quiz engine
        cards_to_quiz = self.quiz_engine.select_cards_for_quiz(deck, mode, card_count)
        
        if not cards_to_quiz:
            self._show_no_cards_message()
            return self.session_stats
        
        # Initialize session stats
        self.session_stats.update({
            'total_cards': len(cards_to_quiz),
            'current_card': 0,
            'correct_answers': 0,
            'incorrect_answers': 0,
            'skipped_cards': 0,
            'start_time': datetime.now(),
            'confidence_scores': [],
            'difficulty_adjustments': 0
        })
        
        # Show quiz introduction
        self._show_quiz_introduction(deck, mode, len(cards_to_quiz))
        
        if not Confirm.ask("Ready to start the quiz?", console=self.console):
            self.quiz_state = QuizState.CANCELLED
            return self.session_stats
        
        # Start the quiz
        self.quiz_state = QuizState.IN_PROGRESS
        return self._run_quiz_loop(cards_to_quiz)
    
    def _show_quiz_introduction(self, deck: Deck, mode: QuizMode, card_count: int) -> None:
        """Show quiz introduction with Rich formatting."""
        self.console.clear()
        
        # Create introduction panel
        intro_content = []
        intro_content.append(f"📚 Deck: [bold bright_cyan]{deck.name}[/bold bright_cyan]")
        intro_content.append(f"🎯 Mode: [bold bright_yellow]{mode.value.title()}[/bold bright_yellow]")
        intro_content.append(f"📊 Cards: [bold bright_green]{card_count}[/bold bright_green]")
        
        if self.timed_mode:
            intro_content.append(f"⏱️  Time Limit: [bold bright_red]{self.time_limit}s per question[/bold bright_red]")
        
        intro_content.append("")
        intro_content.append("🎮 [bold]Quiz Controls:[/bold]")
        intro_content.append("  • Type your answer and press Enter")
        intro_content.append("  • Type 'skip' to skip a question")
        intro_content.append("  • Type 'hint' for a hint (if available)")
        intro_content.append("  • Type 'quit' to exit the quiz")
        
        intro_panel = Panel(
            "\n".join(intro_content),
            title="🧞‍♂️ FlashGenie Quiz Session",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(intro_panel)
        self.console.print()
    
    def _run_quiz_loop(self, cards: List[Flashcard]) -> Dict[str, Any]:
        """Run the main quiz loop with Rich UI."""
        try:
            for i, card in enumerate(cards):
                self.current_card = card
                self.session_stats['current_card'] = i + 1
                
                # Show question and get answer
                result = self._present_question(card, i + 1, len(cards))
                
                if result == 'quit':
                    self.quiz_state = QuizState.CANCELLED
                    break
                elif result == 'skip':
                    self.session_stats['skipped_cards'] += 1
                    continue
                
                # Process answer and show feedback
                self._process_answer_and_feedback(card, result)
                
                # Brief pause before next question
                time.sleep(1)
            
            # Quiz completed
            self.quiz_state = QuizState.COMPLETED
            self.session_stats['end_time'] = datetime.now()
            self._show_quiz_completion()
            
        except KeyboardInterrupt:
            self.quiz_state = QuizState.CANCELLED
            self._show_quiz_cancelled()
        
        return self.session_stats
    
    def _present_question(self, card: Flashcard, current: int, total: int) -> str:
        """Present a question with Rich formatting."""
        self.console.clear()
        
        # Create progress bar
        progress_percentage = ((current - 1) / total) * 100
        progress_bar = "█" * int(progress_percentage / 5) + "░" * (20 - int(progress_percentage / 5))
        
        # Create question layout
        question_content = []
        
        # Progress header
        question_content.append(f"📊 Progress: [{progress_bar}] {current}/{total} ({progress_percentage:.1f}%)")
        question_content.append("")
        
        # Question
        question_content.append(f"❓ [bold bright_white]{card.question}[/bold bright_white]")
        question_content.append("")
        
        # Optional information
        if self.show_difficulty and hasattr(card, 'difficulty'):
            difficulty_stars = "⭐" * int(card.difficulty * 5)
            question_content.append(f"🎯 Difficulty: {difficulty_stars} ({card.difficulty:.2f})")
        
        if self.show_tags and card.tags:
            tags_display = " ".join([f"[dim]#{tag}[/dim]" for tag in card.tags])
            question_content.append(f"🏷️  Tags: {tags_display}")
        
        if self.timed_mode:
            question_content.append(f"⏱️  Time Limit: [bold bright_red]{self.time_limit}s[/bold bright_red]")
        
        question_content.append("")
        question_content.append("💡 [dim]Type 'hint' for a hint, 'skip' to skip, or 'quit' to exit[/dim]")
        
        # Create question panel
        question_panel = Panel(
            "\n".join(question_content),
            title=f"🎯 Question {current}/{total}",
            border_style="bright_cyan",
            padding=(1, 2)
        )
        
        self.console.print(question_panel)
        
        # Get user input
        start_time = time.time()
        
        if self.timed_mode:
            # TODO: Implement timed input with Rich
            answer = Prompt.ask(
                "\n[bold bright_yellow]Your answer[/bold bright_yellow]",
                console=self.console
            )
        else:
            answer = Prompt.ask(
                "\n[bold bright_yellow]Your answer[/bold bright_yellow]",
                console=self.console
            )
        
        response_time = time.time() - start_time
        
        # Handle special commands
        if answer.lower() in ['quit', 'exit', 'q']:
            return 'quit'
        elif answer.lower() in ['skip', 's']:
            return 'skip'
        elif answer.lower() in ['hint', 'h']:
            self._show_hint(card)
            return self._present_question(card, current, total)  # Re-present question
        
        # Store response time
        if not hasattr(card, 'response_time'):
            card.response_time = response_time
        
        return answer
    
    def _show_hint(self, card: Flashcard) -> None:
        """Show hint for the current card."""
        hint_text = "💡 No hint available for this card."
        
        # Generate hint based on answer
        if hasattr(card, 'hint') and card.hint:
            hint_text = f"💡 Hint: {card.hint}"
        elif len(card.answer) > 3:
            # Generate simple hint from answer
            hint_chars = card.answer[0] + "_" * (len(card.answer) - 2) + card.answer[-1]
            hint_text = f"💡 Hint: {hint_chars} ({len(card.answer)} letters)"
        
        hint_panel = Panel(
            hint_text,
            title="💡 Hint",
            border_style="bright_yellow",
            padding=(0, 1)
        )
        
        self.console.print(hint_panel)
        self.console.print()
        input("Press Enter to continue...")
    
    def _process_answer_and_feedback(self, card: Flashcard, user_answer: str) -> None:
        """Process answer and show Rich feedback with fuzzy matching support."""
        # Check if answer is correct using enhanced matching
        is_correct, fuzzy_result = self.quiz_engine._check_answer_enhanced(card, user_answer)

        # Handle fuzzy matching suggestions
        if not is_correct and fuzzy_result and self.quiz_engine.should_suggest(fuzzy_result):
            suggestion_accepted = self._show_fuzzy_suggestion(fuzzy_result, user_answer)
            if suggestion_accepted:
                is_correct = True

        # Update stats
        if is_correct:
            self.session_stats['correct_answers'] += 1
        else:
            self.session_stats['incorrect_answers'] += 1

        # Get confidence level
        confidence = self._get_confidence_level()
        self.session_stats['confidence_scores'].append(confidence.value)

        # Show feedback
        self._show_answer_feedback(card, user_answer, is_correct, confidence, fuzzy_result)

        # Update card difficulty (placeholder for now)
        if hasattr(card, 'difficulty'):
            old_difficulty = card.difficulty
            # Simple difficulty adjustment logic
            if is_correct and confidence.value >= 4:
                card.difficulty = max(0.0, card.difficulty - 0.1)
            elif not is_correct:
                card.difficulty = min(1.0, card.difficulty + 0.1)

            if abs(card.difficulty - old_difficulty) > 0.05:
                self.session_stats['difficulty_adjustments'] += 1
    
    def _show_fuzzy_suggestion(self, fuzzy_result: FuzzyMatchResult, user_answer: str) -> bool:
        """
        Show fuzzy matching suggestion and get user confirmation.

        Args:
            fuzzy_result: The fuzzy matching result
            user_answer: The user's original answer

        Returns:
            True if user accepts the suggestion, False otherwise
        """
        if not fuzzy_result.suggestion:
            return False

        # Create suggestion panel
        suggestion_content = []
        suggestion_content.append(f"🤔 Your answer: [bright_yellow]{user_answer}[/bright_yellow]")
        suggestion_content.append(f"💡 {fuzzy_result.suggestion}")
        suggestion_content.append("")
        suggestion_content.append(f"📊 Match confidence: {fuzzy_result.confidence:.1%}")
        suggestion_content.append(f"🎯 Match type: {fuzzy_result.match_type.value.replace('_', ' ').title()}")

        suggestion_panel = Panel(
            "\n".join(suggestion_content),
            title="🔍 Fuzzy Match Suggestion",
            border_style="bright_yellow",
            padding=(1, 2)
        )

        self.console.print(suggestion_panel)

        # Ask user if they accept the suggestion
        return Confirm.ask(
            "Accept this as correct?",
            console=self.console,
            default=True
        )

    def _check_answer(self, correct_answer: str, user_answer: str) -> bool:
        """Legacy method - Check if user answer is correct (simple string comparison)."""
        return correct_answer.lower().strip() == user_answer.lower().strip()
    
    def _get_confidence_level(self) -> ConfidenceLevel:
        """Get user confidence level with Rich prompt."""
        self.console.print()
        confidence_text = """
[bold]How confident were you in your answer?[/bold]
1️⃣  Very Low    2️⃣  Low    3️⃣  Medium    4️⃣  High    5️⃣  Very High
        """
        self.console.print(confidence_text)
        
        while True:
            try:
                choice = Prompt.ask(
                    "Confidence level (1-5)",
                    choices=["1", "2", "3", "4", "5"],
                    console=self.console
                )
                return ConfidenceLevel(int(choice))
            except (ValueError, KeyError):
                self.console.print("[red]Please enter a number from 1 to 5[/red]")
    
    def _show_answer_feedback(self, card: Flashcard, user_answer: str,
                            is_correct: bool, confidence: ConfidenceLevel,
                            fuzzy_result: Optional[FuzzyMatchResult] = None) -> None:
        """Show Rich feedback for the answer with enhanced information."""
        # Create feedback content
        feedback_content = []

        if is_correct:
            feedback_content.append("✅ [bold bright_green]Correct![/bold bright_green]")
            feedback_content.append(f"Your answer: [bright_green]{user_answer}[/bright_green]")

            # Show fuzzy match information if applicable
            if fuzzy_result and fuzzy_result.match_type != MatchType.EXACT:
                if fuzzy_result.match_type == MatchType.CASE_INSENSITIVE:
                    feedback_content.append("📝 [dim]Case-insensitive match[/dim]")
                elif fuzzy_result.match_type in [MatchType.MINOR_TYPO, MatchType.MODERATE_TYPO]:
                    feedback_content.append(f"🔍 [dim]Fuzzy match ({fuzzy_result.match_type.value.replace('_', ' ')})[/dim]")
                    feedback_content.append(f"📊 [dim]Match confidence: {fuzzy_result.confidence:.1%}[/dim]")
        else:
            feedback_content.append("❌ [bold bright_red]Incorrect[/bold bright_red]")
            feedback_content.append(f"Your answer: [bright_red]{user_answer}[/bright_red]")

            # Show all valid answers
            if len(card.valid_answers) > 1:
                feedback_content.append(f"✅ [bold]Valid answers:[/bold]")
                for i, valid_answer in enumerate(card.valid_answers, 1):
                    feedback_content.append(f"  {i}. [bright_green]{valid_answer}[/bright_green]")
            else:
                feedback_content.append(f"Correct answer: [bright_green]{card.answer}[/bright_green]")

            # Show fuzzy match information if there was a close match
            if fuzzy_result and fuzzy_result.confidence > 0.3:
                feedback_content.append("")
                feedback_content.append(f"🔍 [dim]Closest match: {fuzzy_result.matched_answer} ({fuzzy_result.confidence:.1%} confidence)[/dim]")

        feedback_content.append("")
        feedback_content.append(f"🎯 Confidence: {'⭐' * confidence.value} ({confidence.name.title()})")

        # Show difficulty adjustment if applicable
        if hasattr(card, 'difficulty'):
            feedback_content.append(f"📊 Difficulty: {card.difficulty:.2f}")

        # Create feedback panel
        border_style = "bright_green" if is_correct else "bright_red"
        feedback_panel = Panel(
            "\n".join(feedback_content),
            title="📝 Feedback",
            border_style=border_style,
            padding=(1, 2)
        )

        self.console.print(feedback_panel)

        # Brief pause for user to read
        time.sleep(2)
    
    def _show_quiz_completion(self) -> None:
        """Show quiz completion summary with Rich formatting."""
        self.console.clear()
        
        # Calculate final stats
        total_answered = self.session_stats['correct_answers'] + self.session_stats['incorrect_answers']
        accuracy = (self.session_stats['correct_answers'] / total_answered * 100) if total_answered > 0 else 0
        
        duration = self.session_stats['end_time'] - self.session_stats['start_time']
        duration_str = str(duration).split('.')[0]  # Remove microseconds
        
        avg_confidence = sum(self.session_stats['confidence_scores']) / len(self.session_stats['confidence_scores']) if self.session_stats['confidence_scores'] else 0
        
        # Create completion summary
        summary_content = []
        summary_content.append("🎉 [bold bright_green]Quiz Completed![/bold bright_green]")
        summary_content.append("")
        summary_content.append(f"📊 [bold]Results Summary:[/bold]")
        summary_content.append(f"  ✅ Correct: {self.session_stats['correct_answers']}")
        summary_content.append(f"  ❌ Incorrect: {self.session_stats['incorrect_answers']}")
        summary_content.append(f"  ⏭️  Skipped: {self.session_stats['skipped_cards']}")
        summary_content.append(f"  🎯 Accuracy: {accuracy:.1f}%")
        summary_content.append("")
        summary_content.append(f"⏱️  [bold]Time & Performance:[/bold]")
        summary_content.append(f"  📅 Duration: {duration_str}")
        summary_content.append(f"  ⭐ Avg Confidence: {avg_confidence:.1f}/5")
        summary_content.append(f"  🔧 Difficulty Adjustments: {self.session_stats['difficulty_adjustments']}")
        
        completion_panel = Panel(
            "\n".join(summary_content),
            title="🏆 Quiz Complete",
            border_style="bright_green",
            padding=(1, 2)
        )
        
        self.console.print(completion_panel)
        
        # Ask if user wants to review incorrect answers
        if self.session_stats['incorrect_answers'] > 0:
            self.console.print()
            if Confirm.ask("Would you like to review incorrect answers?", console=self.console):
                self._show_review_session()
    
    def _show_review_session(self) -> None:
        """Show review session for incorrect answers (placeholder)."""
        review_panel = Panel(
            "📚 Review session feature will be implemented in Phase 2!",
            title="🔄 Review Session",
            border_style="bright_yellow",
            padding=(1, 2)
        )
        self.console.print(review_panel)
    
    def _show_quiz_cancelled(self) -> None:
        """Show quiz cancellation message."""
        cancel_panel = Panel(
            "Quiz session was cancelled. Your progress has been saved.",
            title="⏹️ Quiz Cancelled",
            border_style="bright_yellow",
            padding=(1, 2)
        )
        self.console.print(cancel_panel)
    
    def _show_no_cards_message(self) -> None:
        """Show message when no cards are available for quiz."""
        no_cards_panel = Panel(
            "No cards are available for quiz. Try importing some flashcards first!",
            title="📭 No Cards Available",
            border_style="bright_red",
            padding=(1, 2)
        )
        self.console.print(no_cards_panel)
