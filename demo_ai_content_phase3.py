#!/usr/bin/env python3
"""
FlashGenie v1.8.5 Phase 3 - AI Content Generation Demo

This script demonstrates the new AI-powered content generation features with
intelligent flashcard creation, smart suggestions, and difficulty prediction.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from flashgenie.interfaces.terminal import RichTerminalUI, RichAIInterface
    from flashgenie.ai.content_generator import AIContentGenerator, ContentType
    from flashgenie.core.content_system.deck import Deck
    from flashgenie.core.content_system.flashcard import Flashcard
    print("✅ FlashGenie AI Content Generation components loaded successfully!")
except ImportError as e:
    print(f"❌ Could not load FlashGenie AI Content Generation: {e}")
    print("Please install dependencies: pip install rich textual prompt-toolkit")
    sys.exit(1)


def create_sample_text_content() -> dict:
    """Create sample text content for AI generation testing."""
    return {
        "science_facts": """
        The speed of light in vacuum is 299,792,458 meters per second.
        Water boils at 100 degrees Celsius or 212 degrees Fahrenheit.
        The chemical symbol for gold is Au, derived from the Latin word aurum.
        Jupiter is the largest planet in our solar system.
        DNA stands for Deoxyribonucleic acid.
        The human brain contains approximately 86 billion neurons.
        Photosynthesis is the process by which plants convert sunlight into energy.
        """,
        
        "spanish_vocabulary": """
        Hola - Hello
        Gracias - Thank you
        Por favor - Please
        ¿Cómo estás? - How are you?
        Me llamo - My name is
        ¿Dónde está? - Where is?
        No entiendo - I don't understand
        Disculpe - Excuse me
        """,
        
        "math_formulas": """
        Area of a circle = πr²
        Quadratic formula: x = (-b ± √(b²-4ac)) / 2a
        Pythagorean theorem: a² + b² = c²
        Slope formula: (y₂-y₁)/(x₂-x₁)
        Distance formula: √[(x₂-x₁)² + (y₂-y₁)²]
        Volume of a sphere: (4/3)πr³
        """,
        
        "history_facts": """
        World War II ended in 1945.
        The Roman Empire was founded in 27 BC.
        The Declaration of Independence was signed in 1776.
        The Berlin Wall fell in 1989.
        Napoleon was defeated at Waterloo in 1815.
        The Renaissance began in Italy during the 14th century.
        """
    }


def demo_ai_content_generator():
    """Demo the AI Content Generator functionality."""
    print("\n🤖 Demo: AI Content Generator")
    print("=" * 40)
    
    ai_generator = AIContentGenerator()
    sample_texts = create_sample_text_content()
    
    for content_name, text in sample_texts.items():
        print(f"\n📝 Testing AI generation with {content_name}...")
        
        # Determine content type
        if "vocabulary" in content_name:
            content_type = ContentType.VOCABULARY
        elif "formulas" in content_name:
            content_type = ContentType.FORMULAS
        elif "facts" in content_name:
            content_type = ContentType.FACTS
        else:
            content_type = ContentType.DEFINITIONS
        
        # Generate content
        generated = ai_generator.generate_flashcards_from_text(text, content_type, max_cards=5)
        
        print(f"✅ Generated {len(generated)} flashcards from {content_name}")
        
        # Show first generated card
        if generated:
            card = generated[0]
            print(f"   Example: Q: {card.question}")
            print(f"            A: {card.answer}")
            print(f"            Difficulty: {card.difficulty:.2f}")
            print(f"            Tags: {', '.join(card.tags)}")


def demo_difficulty_prediction():
    """Demo AI difficulty prediction."""
    print("\n🎯 Demo: AI Difficulty Prediction")
    print("=" * 40)
    
    ai_generator = AIContentGenerator()
    
    # Test cards with varying difficulty
    test_cards = [
        ("What is 2 + 2?", "4"),
        ("What is the capital of France?", "Paris"),
        ("Explain quantum entanglement", "A quantum mechanical phenomenon where particles become interconnected"),
        ("Derive the Schrödinger equation", "iℏ ∂/∂t |ψ⟩ = Ĥ |ψ⟩"),
        ("What does 'hello' mean?", "A greeting")
    ]
    
    for question, answer in test_cards:
        difficulty = ai_generator.predict_difficulty(question, answer)
        print(f"Q: {question}")
        print(f"A: {answer}")
        print(f"🎯 Predicted difficulty: {difficulty:.2f} ({'⭐' * int(difficulty * 5)})")
        print()


def demo_content_suggestions():
    """Demo AI content suggestions."""
    print("\n💡 Demo: AI Content Suggestions")
    print("=" * 40)
    
    ai_generator = AIContentGenerator()
    
    # Create a sample deck
    deck = Deck(name="Sample Science Deck", description="Science flashcards")
    sample_cards = [
        Flashcard("1", "What is gravity?", "A force that attracts objects", ["physics", "forces"]),
        Flashcard("2", "What is photosynthesis?", "Process plants use to make food", ["biology", "plants"]),
        Flashcard("3", "What is H2O?", "Water", ["chemistry", "molecules"])
    ]
    
    for card in sample_cards:
        card.difficulty = 0.4
        deck.add_flashcard(card)
    
    # Generate suggestions
    suggestions = ai_generator.suggest_related_content(deck.flashcards, count=3)
    
    print(f"✅ Generated {len(suggestions)} content suggestions")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. Q: {suggestion.question}")
        print(f"      A: {suggestion.answer}")
        print(f"      Tags: {', '.join(suggestion.tags)}")
        print()


def demo_hint_generation():
    """Demo AI hint generation."""
    print("\n💡 Demo: AI Hint Generation")
    print("=" * 40)
    
    ai_generator = AIContentGenerator()
    
    # Test cards for hint generation
    test_cards = [
        Flashcard("1", "What is the capital of Japan?", "Tokyo", ["geography", "asia"]),
        Flashcard("2", "Who wrote Romeo and Juliet?", "William Shakespeare", ["literature", "shakespeare"]),
        Flashcard("3", "What is the chemical symbol for oxygen?", "O", ["chemistry", "elements"])
    ]
    
    for card in test_cards:
        hints = ai_generator.generate_hints(card)
        print(f"Q: {card.question}")
        print(f"A: {card.answer}")
        print("💡 Generated hints:")
        for i, hint in enumerate(hints, 1):
            print(f"   {i}. {hint}")
        print()


def demo_card_enhancement():
    """Demo AI card enhancement."""
    print("\n✨ Demo: AI Card Enhancement")
    print("=" * 40)
    
    ai_generator = AIContentGenerator()
    
    # Create cards that could be enhanced
    test_cards = [
        Flashcard("1", "Paris", "Capital of France"),  # Poor question format
        Flashcard("2", "What is DNA?", "Genetic material"),  # Could use more context
        Flashcard("3", "Math", "Numbers")  # Very vague
    ]
    
    enhancements = ai_generator.enhance_existing_cards(test_cards)
    
    print(f"✅ Generated enhancement suggestions for {len(enhancements)} cards")
    for enhancement in enhancements:
        print(f"Card: {enhancement['original_question']} -> {enhancement['original_answer']}")
        print("🔧 Suggestions:")
        for suggestion in enhancement['suggestions']:
            print(f"   • {suggestion['suggestion']}")
        print()


def demo_rich_ai_interface():
    """Demo the Rich AI Interface."""
    print("\n🎨 Demo: Rich AI Interface")
    print("=" * 40)
    
    ui = RichTerminalUI()
    ai_interface = RichAIInterface(ui.console)
    
    # Demo difficulty prediction with Rich UI
    test_card = Flashcard("demo", "What is quantum mechanics?", "The branch of physics dealing with atomic and subatomic particles", ["physics", "quantum"])
    
    ui.show_info("Testing Rich AI Interface difficulty prediction...", "AI Demo")
    time.sleep(1)
    
    difficulty = ai_interface.predict_card_difficulty(test_card)
    
    ui.show_success(f"AI predicted difficulty: {difficulty:.2f}", "AI Prediction Complete")


def interactive_ai_demo():
    """Run an interactive demo of the AI Content Generation features."""
    print("\n🎮 Interactive AI Content Generation Demo")
    print("=" * 60)
    
    ui = RichTerminalUI()
    
    while True:
        try:
            options = [
                "AI Content Generator Demo",
                "AI Difficulty Prediction Demo",
                "AI Content Suggestions Demo",
                "AI Hint Generation Demo",
                "AI Card Enhancement Demo",
                "Rich AI Interface Demo",
                "Full AI Generation Test",
                "Exit Demo"
            ]
            
            print("\n📋 AI Content Generation Demo Menu")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                demo_ai_content_generator()
            elif choice == "2":
                demo_difficulty_prediction()
            elif choice == "3":
                demo_content_suggestions()
            elif choice == "4":
                demo_hint_generation()
            elif choice == "5":
                demo_card_enhancement()
            elif choice == "6":
                demo_rich_ai_interface()
            elif choice == "7":
                # Full AI generation test
                ui.show_info("Starting full AI generation test...", "AI Test")
                
                ai_interface = RichAIInterface(ui.console)
                sample_texts = create_sample_text_content()
                
                # Test with science facts
                test_text = sample_texts["science_facts"]
                generated_deck = ai_interface.generate_flashcards_from_text(test_text, "AI Test Deck")
                
                if generated_deck:
                    ui.show_success(f"Generated deck with {len(generated_deck.flashcards)} cards!", "AI Test Complete")
                else:
                    ui.show_warning("AI generation was cancelled or failed", "AI Test")
                    
            elif choice == "8":
                ui.show_success("Thanks for exploring the FlashGenie AI Content Generation! 🎉", "Demo Complete")
                break
            else:
                ui.show_warning("Invalid choice. Please select 1-8.", "Invalid Input")
                
        except KeyboardInterrupt:
            ui.show_info("Demo interrupted. Goodbye! 👋", "Interrupted")
            break
        except Exception as e:
            ui.show_error(f"Demo error: {e}", "Error")


def main():
    """Main demo function."""
    print("🚀 FlashGenie v1.8.5 Phase 3 - AI Content Generation Demo")
    print("=" * 70)
    print("Intelligent Flashcard Creation with AI")
    print("\nThis demo showcases the new AI Content Generation features:")
    print("• 🤖 AI-powered flashcard generation from text")
    print("• 🎯 Intelligent difficulty prediction")
    print("• 💡 Smart content suggestions and related topics")
    print("• ✨ Flashcard enhancement recommendations")
    print("• 🔍 Automatic tag generation and categorization")
    print("• 🎨 Beautiful Rich Terminal UI for AI features")
    print("• 🧠 Pattern recognition and content analysis")
    
    try:
        demo_choice = input("\n🎮 Would you like to run the interactive demo? (y/n): ").strip().lower()
        if demo_choice in ['y', 'yes']:
            interactive_ai_demo()
        else:
            print("\n🎬 Running automatic demo sequence...")
            demo_ai_content_generator()
            demo_difficulty_prediction()
            demo_content_suggestions()
            demo_hint_generation()
            demo_card_enhancement()
            demo_rich_ai_interface()
            
            print("\n✅ AI Content Generation demo completed successfully!")
            print("🎉 FlashGenie v1.8.5 Phase 3 is ready!")
            print("\n💡 To test the actual AI Content Generation, run:")
            print("   python -m flashgenie")
            print("   FlashGenie > ai")
            print("   FlashGenie > generate")
            print("   FlashGenie > suggest")
            print("   FlashGenie > enhance")
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")


if __name__ == "__main__":
    main()
