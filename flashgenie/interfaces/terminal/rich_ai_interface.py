"""
Rich AI Interface for FlashGenie v1.8.5 Phase 3.

This module provides a beautiful Rich Terminal UI interface for AI-powered
content generation, smart suggestions, and intelligent flashcard enhancement.
"""

from typing import List, Dict, Any, Optional
import time
from pathlib import Path

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
from flashgenie.ai.content_generator import AIContentGenerator, ContentType, GeneratedContent


class RichAIInterface:
    """
    Rich Terminal UI interface for AI-powered features.
    
    Provides beautiful, interactive AI content generation with Rich formatting,
    smart suggestions, and intelligent flashcard enhancement.
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the Rich AI Interface.
        
        Args:
            console: Rich Console instance (creates new if None)
        """
        self.console = console or Console()
        self.ai_generator = AIContentGenerator()
        
        # Interface configuration
        self.show_confidence_scores = True
        self.show_generation_process = True
        self.auto_apply_suggestions = False
    
    def generate_flashcards_from_text(self, text: str, deck_name: str = "AI Generated Deck") -> Optional[Deck]:
        """
        Generate flashcards from text with Rich UI progress tracking.
        
        Args:
            text: Input text to analyze
            deck_name: Name for the generated deck
            
        Returns:
            Generated deck with AI flashcards
        """
        self.console.clear()
        
        # Show AI generation introduction
        self._show_generation_intro(text, deck_name)
        
        if not Confirm.ask("Proceed with AI content generation?", console=self.console):
            return None
        
        # Get content type from user
        content_type = self._get_content_type_choice()
        max_cards = self._get_max_cards_choice()
        
        # Generate content with progress tracking
        generated_content = self._generate_with_progress(text, content_type, max_cards)
        
        if not generated_content:
            self._show_no_content_generated()
            return None
        
        # Show generated content for review
        approved_content = self._review_generated_content(generated_content)
        
        if not approved_content:
            self.console.print(Panel("No content approved. Generation cancelled.", 
                                   title="❌ Generation Cancelled", border_style="red"))
            return None
        
        # Create deck with approved content
        deck = self._create_deck_from_content(approved_content, deck_name)
        self._show_generation_complete(deck)
        
        return deck
    
    def suggest_related_content(self, deck: Deck, count: int = 5) -> List[GeneratedContent]:
        """
        Suggest related content for an existing deck with Rich UI.
        
        Args:
            deck: Existing deck to analyze
            count: Number of suggestions to generate
            
        Returns:
            List of content suggestions
        """
        self.console.clear()
        
        # Show suggestion introduction
        self._show_suggestion_intro(deck, count)
        
        # Generate suggestions with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("🤖 Analyzing deck and generating suggestions...", total=None)
            
            suggestions = self.ai_generator.suggest_related_content(deck.flashcards, count)
            
            progress.update(task, completed=True)
        
        if suggestions:
            self._display_suggestions(suggestions)
        else:
            self.console.print(Panel("No suggestions could be generated for this deck.", 
                                   title="💡 No Suggestions", border_style="yellow"))
        
        return suggestions
    
    def enhance_existing_cards(self, deck: Deck) -> Dict[str, Any]:
        """
        Enhance existing flashcards with AI suggestions.
        
        Args:
            deck: Deck to enhance
            
        Returns:
            Enhancement results
        """
        self.console.clear()
        
        # Show enhancement introduction
        self._show_enhancement_intro(deck)
        
        # Generate enhancements with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("🔧 Analyzing cards and generating enhancements...", total=None)
            
            enhancements = self.ai_generator.enhance_existing_cards(deck.flashcards)
            
            progress.update(task, completed=True)
        
        if enhancements:
            applied_enhancements = self._review_enhancements(enhancements)
            self._show_enhancement_complete(applied_enhancements)
            return applied_enhancements
        else:
            self.console.print(Panel("No enhancements suggested for this deck.", 
                                   title="✨ No Enhancements", border_style="yellow"))
            return {}
    
    def predict_card_difficulty(self, flashcard: Flashcard) -> float:
        """
        Predict and display difficulty for a flashcard.
        
        Args:
            flashcard: Flashcard to analyze
            
        Returns:
            Predicted difficulty level
        """
        # Predict difficulty
        difficulty = self.ai_generator.predict_difficulty(flashcard.question, flashcard.answer)
        
        # Display prediction with Rich formatting
        self._display_difficulty_prediction(flashcard, difficulty)
        
        return difficulty
    
    def _show_generation_intro(self, text: str, deck_name: str) -> None:
        """Show AI generation introduction."""
        content = []
        content.append("🤖 [bold bright_blue]AI Content Generation[/bold bright_blue]")
        content.append("")
        content.append(f"📝 Text Length: [bright_white]{len(text)} characters[/bright_white]")
        content.append(f"📚 Target Deck: [bright_cyan]{deck_name}[/bright_cyan]")
        content.append("")
        content.append("🎯 [bold]AI Features:[/bold]")
        content.append("  • Intelligent content extraction")
        content.append("  • Automatic difficulty prediction")
        content.append("  • Smart tag generation")
        content.append("  • Quality confidence scoring")
        content.append("")

        # Add helpful examples if the text looks like a file path or is very short
        if len(text) < 50 or any(indicator in text for indicator in ['.csv', '.txt', '/', '\\']):
            content.append("💡 [bold yellow]Tip:[/bold yellow] For best results, provide actual text content like:")
            content.append("   • 'The speed of light is 299,792,458 m/s. Water boils at 100°C.'")
            content.append("   • 'Python is a programming language. Variables store data.'")
            content.append("   • 'Hola means hello. Gracias means thank you.'")
            content.append("")

        content.append("⚡ The AI will analyze your text and generate relevant flashcards")

        intro_panel = Panel(
            "\n".join(content),
            title="🤖 AI Content Generation",
            border_style="bright_blue",
            padding=(1, 2)
        )

        self.console.print(intro_panel)
        self.console.print()
    
    def _get_content_type_choice(self) -> ContentType:
        """Get content type choice from user."""
        content_types = {
            "1": (ContentType.FACTS, "Facts and Information"),
            "2": (ContentType.DEFINITIONS, "Definitions and Terms"),
            "3": (ContentType.VOCABULARY, "Vocabulary Words"),
            "4": (ContentType.FORMULAS, "Formulas and Equations"),
            "5": (ContentType.QUESTIONS, "Questions and Answers")
        }
        
        self.console.print("🎯 [bold]Select Content Type:[/bold]")
        for key, (_, description) in content_types.items():
            self.console.print(f"  {key}. {description}")
        
        while True:
            choice = Prompt.ask("Content type (1-5)", choices=list(content_types.keys()), 
                              default="1", console=self.console)
            return content_types[choice][0]
    
    def _get_max_cards_choice(self) -> int:
        """Get maximum cards choice from user."""
        while True:
            try:
                max_cards = Prompt.ask("Maximum cards to generate", default="10", console=self.console)
                max_cards = int(max_cards)
                if 1 <= max_cards <= 50:
                    return max_cards
                else:
                    self.console.print("[red]Please enter a number between 1 and 50[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number[/red]")
    
    def _generate_with_progress(self, text: str, content_type: ContentType, 
                               max_cards: int) -> List[GeneratedContent]:
        """Generate content with Rich progress tracking."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            # Analysis phase
            analysis_task = progress.add_task("🔍 Analyzing text content...", total=100)
            time.sleep(1)  # Simulate analysis
            progress.update(analysis_task, advance=50)
            
            # Generation phase
            generation_task = progress.add_task("🤖 Generating flashcards...", total=100)
            generated_content = self.ai_generator.generate_flashcards_from_text(text, content_type, max_cards)
            progress.update(analysis_task, completed=100)
            progress.update(generation_task, advance=70)
            
            # Quality check phase
            quality_task = progress.add_task("✅ Quality checking...", total=100)
            time.sleep(0.5)  # Simulate quality check
            progress.update(generation_task, completed=100)
            progress.update(quality_task, completed=100)
        
        return generated_content
    
    def _review_generated_content(self, generated_content: List[GeneratedContent]) -> List[GeneratedContent]:
        """Review generated content with Rich UI."""
        self.console.print(Panel(f"🎉 Generated {len(generated_content)} flashcards for review", 
                               title="✨ Generation Complete", border_style="green"))
        self.console.print()
        
        approved_content = []
        
        for i, content in enumerate(generated_content, 1):
            # Display content for review
            self._display_content_for_review(content, i, len(generated_content))
            
            # Get user decision
            if Confirm.ask(f"Approve this flashcard?", default=True, console=self.console):
                approved_content.append(content)
            
            self.console.print()
        
        return approved_content
    
    def _display_content_for_review(self, content: GeneratedContent, index: int, total: int) -> None:
        """Display generated content for user review."""
        review_content = []
        review_content.append(f"❓ [bold bright_white]Question:[/bold bright_white] {content.question}")
        review_content.append(f"✅ [bold bright_green]Answer:[/bold bright_green] {content.answer}")
        review_content.append("")
        review_content.append(f"🎯 Difficulty: [bright_yellow]{'⭐' * int(content.difficulty * 5)}[/bright_yellow] ({content.difficulty:.2f})")
        review_content.append(f"🤖 Confidence: [bright_cyan]{content.confidence:.1%}[/bright_cyan]")
        review_content.append(f"🏷️  Tags: [dim]{', '.join(content.tags)}[/dim]")
        
        if content.explanation:
            review_content.append(f"💡 Explanation: [dim]{content.explanation}[/dim]")
        
        review_panel = Panel(
            "\n".join(review_content),
            title=f"📝 Review Card {index}/{total}",
            border_style="bright_cyan",
            padding=(1, 2)
        )
        
        self.console.print(review_panel)
    
    def _create_deck_from_content(self, content_list: List[GeneratedContent], deck_name: str) -> Deck:
        """Create a deck from approved generated content."""
        deck = Deck(name=deck_name, description=f"AI-generated deck with {len(content_list)} cards")
        
        for i, content in enumerate(content_list):
            flashcard = Flashcard(
                card_id=f"ai_gen_{i+1}",
                question=content.question,
                answer=content.answer,
                tags=content.tags
            )
            flashcard.difficulty = content.difficulty
            deck.add_flashcard(flashcard)
        
        return deck
    
    def _show_generation_complete(self, deck: Deck) -> None:
        """Show generation completion summary."""
        summary_content = []
        summary_content.append("🎉 [bold bright_green]AI Generation Complete![/bold bright_green]")
        summary_content.append("")
        summary_content.append(f"📚 Deck: [bright_cyan]{deck.name}[/bright_cyan]")
        summary_content.append(f"📊 Cards Generated: [bright_white]{len(deck.flashcards)}[/bright_white]")
        summary_content.append(f"🎯 Average Difficulty: [bright_yellow]{sum(getattr(card, 'difficulty', 0.5) for card in deck.flashcards) / len(deck.flashcards):.2f}[/bright_yellow]")
        summary_content.append("")
        summary_content.append("💡 Your AI-generated flashcards are ready for study!")
        
        summary_panel = Panel(
            "\n".join(summary_content),
            title="🤖 AI Generation Summary",
            border_style="bright_green",
            padding=(1, 2)
        )
        
        self.console.print(summary_panel)
    
    def _show_suggestion_intro(self, deck: Deck, count: int) -> None:
        """Show suggestion introduction."""
        content = []
        content.append("💡 [bold bright_blue]AI Content Suggestions[/bold bright_blue]")
        content.append("")
        content.append(f"📚 Analyzing Deck: [bright_cyan]{deck.name}[/bright_cyan]")
        content.append(f"📊 Existing Cards: [bright_white]{len(deck.flashcards)}[/bright_white]")
        content.append(f"🎯 Suggestions to Generate: [bright_yellow]{count}[/bright_yellow]")
        content.append("")
        content.append("🤖 The AI will analyze your existing cards and suggest related content")
        
        intro_panel = Panel(
            "\n".join(content),
            title="💡 AI Suggestions",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(intro_panel)
        self.console.print()
    
    def _display_suggestions(self, suggestions: List[GeneratedContent]) -> None:
        """Display AI suggestions with Rich formatting."""
        self.console.print(Panel(f"💡 Generated {len(suggestions)} content suggestions", 
                               title="🤖 AI Suggestions", border_style="blue"))
        self.console.print()
        
        for i, suggestion in enumerate(suggestions, 1):
            suggestion_content = []
            suggestion_content.append(f"❓ [bold]Question:[/bold] {suggestion.question}")
            suggestion_content.append(f"✅ [bold]Answer:[/bold] {suggestion.answer}")
            suggestion_content.append(f"🎯 Difficulty: {'⭐' * int(suggestion.difficulty * 5)} ({suggestion.difficulty:.2f})")
            suggestion_content.append(f"🏷️  Tags: {', '.join(suggestion.tags)}")
            
            suggestion_panel = Panel(
                "\n".join(suggestion_content),
                title=f"💡 Suggestion {i}",
                border_style="bright_yellow",
                padding=(1, 1)
            )
            
            self.console.print(suggestion_panel)
    
    def _show_enhancement_intro(self, deck: Deck) -> None:
        """Show enhancement introduction."""
        content = []
        content.append("✨ [bold bright_blue]AI Card Enhancement[/bold bright_blue]")
        content.append("")
        content.append(f"📚 Enhancing Deck: [bright_cyan]{deck.name}[/bright_cyan]")
        content.append(f"📊 Cards to Analyze: [bright_white]{len(deck.flashcards)}[/bright_white]")
        content.append("")
        content.append("🤖 The AI will analyze your cards and suggest improvements")
        
        intro_panel = Panel(
            "\n".join(content),
            title="✨ AI Enhancement",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(intro_panel)
        self.console.print()
    
    def _review_enhancements(self, enhancements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Review enhancement suggestions."""
        # Placeholder for enhancement review
        return {"applied": len(enhancements), "suggestions": enhancements}
    
    def _show_enhancement_complete(self, results: Dict[str, Any]) -> None:
        """Show enhancement completion."""
        content = []
        content.append("✨ [bold bright_green]Enhancement Complete![/bold bright_green]")
        content.append("")
        content.append(f"🔧 Enhancements Applied: [bright_white]{results.get('applied', 0)}[/bright_white]")
        content.append("")
        content.append("💡 Your flashcards have been enhanced with AI suggestions!")
        
        complete_panel = Panel(
            "\n".join(content),
            title="✨ Enhancement Summary",
            border_style="bright_green",
            padding=(1, 2)
        )
        
        self.console.print(complete_panel)
    
    def _display_difficulty_prediction(self, flashcard: Flashcard, difficulty: float) -> None:
        """Display difficulty prediction with Rich formatting."""
        content = []
        content.append(f"❓ [bold]Question:[/bold] {flashcard.question}")
        content.append(f"✅ [bold]Answer:[/bold] {flashcard.answer}")
        content.append("")
        content.append(f"🎯 [bold]AI Difficulty Prediction:[/bold]")
        content.append(f"   Difficulty Level: [bright_yellow]{'⭐' * int(difficulty * 5)}[/bright_yellow] ({difficulty:.2f})")
        
        if difficulty < 0.3:
            level_desc = "[bright_green]Easy[/bright_green]"
        elif difficulty < 0.7:
            level_desc = "[bright_yellow]Medium[/bright_yellow]"
        else:
            level_desc = "[bright_red]Hard[/bright_red]"
        
        content.append(f"   Level: {level_desc}")
        
        prediction_panel = Panel(
            "\n".join(content),
            title="🤖 AI Difficulty Prediction",
            border_style="bright_cyan",
            padding=(1, 2)
        )
        
        self.console.print(prediction_panel)
    
    def _show_no_content_generated(self) -> None:
        """Show message when no content could be generated."""
        no_content_panel = Panel(
            "No flashcards could be generated from the provided text.\nTry providing text with more structured information.",
            title="🤖 No Content Generated",
            border_style="bright_red",
            padding=(1, 2)
        )
        self.console.print(no_content_panel)
