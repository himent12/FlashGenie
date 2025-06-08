#!/usr/bin/env python3
"""
FlashGenie v1.8.5 Enhanced Features Demonstration

This script demonstrates the new enhanced features:
1. Multiple valid answers per flashcard
2. Intelligent fuzzy matching with typo handling
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from flashgenie.core.content_system.flashcard import Flashcard
from flashgenie.core.content_system.deck import Deck
from flashgenie.core.study_system.quiz_engine import QuizEngine
from flashgenie.utils.fuzzy_matching import FuzzyMatcher, MatchType
from flashgenie.ai.content_generator import AIContentGenerator, ContentType
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def demo_multiple_valid_answers():
    """Demonstrate multiple valid answers functionality."""
    console = Console()
    
    console.print(Panel(
        "🎯 Multiple Valid Answers Demonstration",
        style="bold bright_blue"
    ))
    
    # Create a flashcard with multiple valid answers
    flashcard = Flashcard(
        question="What does 'hello' mean?",
        answer="A greeting"
    )
    
    # Add more valid answers
    flashcard.add_valid_answer("You say it when greeting someone")
    flashcard.add_valid_answer("Greeting expression")
    flashcard.add_valid_answer("Salutation")
    
    console.print(f"📝 Question: [bold]{flashcard.question}[/bold]")
    console.print(f"✅ Valid answers ({len(flashcard.valid_answers)}):")
    
    for i, answer in enumerate(flashcard.valid_answers, 1):
        console.print(f"  {i}. [green]{answer}[/green]")
    
    console.print()
    
    # Test different user inputs
    test_inputs = [
        "A greeting",           # Exact match
        "a greeting",           # Case insensitive
        "greeting expression",  # Alternative answer
        "SALUTATION",          # Case insensitive alternative
        "goodbye"              # Incorrect answer
    ]
    
    console.print("🧪 Testing user inputs:")
    for user_input in test_inputs:
        is_correct = flashcard.is_answer_correct(user_input)
        matched_answer = flashcard.get_matching_answer(user_input)
        
        status = "✅" if is_correct else "❌"
        console.print(f"  {status} '{user_input}' -> {matched_answer or 'No match'}")
    
    console.print()


def demo_fuzzy_matching():
    """Demonstrate fuzzy matching functionality."""
    console = Console()
    
    console.print(Panel(
        "🔍 Fuzzy Matching & Typo Handling Demonstration",
        style="bold bright_yellow"
    ))
    
    # Create fuzzy matcher
    fuzzy_matcher = FuzzyMatcher(sensitivity="medium")
    valid_answers = ["Paris", "The capital of France", "Paris, France"]
    
    console.print(f"✅ Valid answers: {', '.join(valid_answers)}")
    console.print()
    
    # Test different typos and variations
    test_inputs = [
        ("Paris", "Exact match"),
        ("paris", "Case insensitive"),
        ("Pari", "Missing letter"),
        ("Pariz", "Wrong letter"),
        ("Pariss", "Extra letter"),
        ("The capital of france", "Case variation"),
        ("capital of France", "Partial match"),
        ("London", "Completely wrong")
    ]
    
    console.print("🧪 Testing fuzzy matching:")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Input", style="cyan")
    table.add_column("Match Type", style="yellow")
    table.add_column("Confidence", style="green")
    table.add_column("Suggestion", style="blue")
    
    for user_input, description in test_inputs:
        result = fuzzy_matcher.match_answer(user_input, valid_answers)
        
        confidence_str = f"{result.confidence:.1%}" if result.confidence > 0 else "0%"
        match_type = result.match_type.value.replace('_', ' ').title()
        
        suggestion = ""
        if fuzzy_matcher.should_auto_accept(result):
            suggestion = "✅ Auto-accept"
        elif fuzzy_matcher.should_suggest(result):
            suggestion = f"💡 Suggest: {result.matched_answer}"
        else:
            suggestion = "❌ No suggestion"
        
        table.add_row(user_input, match_type, confidence_str, suggestion)
    
    console.print(table)
    console.print()


def demo_quiz_engine_enhancements():
    """Demonstrate quiz engine enhancements."""
    console = Console()
    
    console.print(Panel(
        "🎮 Enhanced Quiz Engine Demonstration",
        style="bold bright_green"
    ))
    
    # Create quiz engine with fuzzy matching
    quiz_engine = QuizEngine()
    
    # Create a flashcard with multiple valid answers
    flashcard = Flashcard(
        question="What is the capital of France?",
        answer="Paris"
    )
    flashcard.add_valid_answer("Paris, France")
    flashcard.add_valid_answer("The capital of France is Paris")
    
    console.print(f"📝 Question: [bold]{flashcard.question}[/bold]")
    console.print(f"✅ Valid answers: {', '.join(flashcard.valid_answers)}")
    console.print()
    
    # Test enhanced answer checking
    test_inputs = [
        "Paris",                    # Exact match
        "paris",                    # Case insensitive
        "Pari",                     # Minor typo
        "Paris France",             # Close but not exact
        "The capital is Paris",     # Different phrasing
        "London"                    # Wrong answer
    ]
    
    console.print("🧪 Testing enhanced answer checking:")
    
    for user_input in test_inputs:
        correct, fuzzy_result = quiz_engine._check_answer_enhanced(flashcard, user_input)
        
        status = "✅" if correct else "❌"
        match_info = ""
        
        if fuzzy_result:
            match_info = f" ({fuzzy_result.match_type.value}, {fuzzy_result.confidence:.1%})"
            
            if not correct and quiz_engine.fuzzy_matcher.should_suggest(fuzzy_result):
                suggestion = quiz_engine.get_fuzzy_suggestion(user_input, flashcard)
                match_info += f" - {suggestion}"
        
        console.print(f"  {status} '{user_input}'{match_info}")
    
    console.print()


def demo_ai_content_generation():
    """Demonstrate AI content generation with multiple answers."""
    console = Console()
    
    console.print(Panel(
        "🤖 AI Content Generation with Multiple Valid Answers",
        style="bold bright_magenta"
    ))
    
    # Create AI content generator
    ai_generator = AIContentGenerator()
    
    # Generate content from sample text
    sample_text = """
    The speed of light is 299,792,458 meters per second.
    Water boils at 100 degrees Celsius.
    Photosynthesis is the process by which plants make food from sunlight.
    """
    
    console.print("📝 Sample text:")
    console.print(f"[dim]{sample_text.strip()}[/dim]")
    console.print()
    
    # Generate flashcards
    generated_content = ai_generator.generate_flashcards_from_text(
        sample_text, ContentType.FACTS, max_cards=3
    )
    
    console.print(f"🎯 Generated {len(generated_content)} flashcards:")
    console.print()
    
    for i, content in enumerate(generated_content, 1):
        console.print(f"[bold bright_cyan]Card {i}:[/bold bright_cyan]")
        console.print(f"  ❓ Question: {content.question}")
        console.print(f"  ✅ Primary Answer: {content.answer}")
        
        if hasattr(content, 'valid_answers') and len(content.valid_answers) > 1:
            console.print(f"  📝 All Valid Answers ({len(content.valid_answers)}):")
            for j, answer in enumerate(content.valid_answers, 1):
                console.print(f"    {j}. {answer}")
        
        console.print(f"  🎯 Difficulty: {content.difficulty:.2f}")
        console.print(f"  🏷️  Tags: {', '.join(content.tags)}")
        console.print(f"  📊 Confidence: {content.confidence:.1%}")
        console.print()


def main():
    """Run all demonstrations."""
    console = Console()
    
    console.print(Panel(
        "🧞‍♂️ FlashGenie v1.8.5 Enhanced Features Demo\n\n"
        "This demonstration showcases the new enhanced features:\n"
        "• Multiple valid answers per flashcard\n"
        "• Intelligent fuzzy matching with typo handling\n"
        "• Enhanced quiz engine with smart suggestions\n"
        "• AI content generation with multiple answer variations",
        title="FlashGenie v1.8.5 Demo",
        style="bold bright_blue"
    ))
    console.print()
    
    try:
        demo_multiple_valid_answers()
        demo_fuzzy_matching()
        demo_quiz_engine_enhancements()
        demo_ai_content_generation()
        
        console.print(Panel(
            "🎉 Demo completed successfully!\n\n"
            "All enhanced features are working correctly:\n"
            "✅ Multiple valid answers support\n"
            "✅ Intelligent fuzzy matching\n"
            "✅ Smart typo handling\n"
            "✅ Enhanced quiz experience\n"
            "✅ AI-powered content generation",
            title="Demo Complete",
            style="bold bright_green"
        ))
        
    except Exception as e:
        console.print(Panel(
            f"❌ Demo failed with error: {e}",
            title="Demo Error",
            style="bold bright_red"
        ))
        raise


if __name__ == "__main__":
    main()
