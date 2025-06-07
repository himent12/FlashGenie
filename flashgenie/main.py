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

    # FlashGenie v1.5 Advanced Features

    # Adaptive study planning
    plan_parser = subparsers.add_parser('plan', help='Create adaptive study plan')
    plan_parser.add_argument('deck', help='Deck name or ID')
    plan_parser.add_argument('--time', type=int, default=30, help='Available time in minutes')
    plan_parser.add_argument('--energy', type=int, choices=[1,2,3,4,5], default=3, help='Energy level (1-5)')
    plan_parser.add_argument('--environment', choices=['quiet', 'noisy', 'mobile'], default='quiet', help='Study environment')

    # Learning velocity tracking
    velocity_parser = subparsers.add_parser('velocity', help='Analyze learning velocity')
    velocity_parser.add_argument('deck', help='Deck name or ID')
    velocity_parser.add_argument('--predict', action='store_true', help='Show mastery predictions')
    velocity_parser.add_argument('--trends', action='store_true', help='Show learning trends')

    # Knowledge graph visualization
    graph_parser = subparsers.add_parser('graph', help='Generate knowledge graph')
    graph_parser.add_argument('deck', help='Deck name or ID')
    graph_parser.add_argument('--export', help='Export graph data to file')
    graph_parser.add_argument('--format', choices=['json', 'html'], default='json', help='Export format')

    # Achievement system
    achievements_parser = subparsers.add_parser('achievements', help='View achievements and progress')
    achievements_parser.add_argument('--progress', action='store_true', help='Show achievement progress')
    achievements_parser.add_argument('--streaks', action='store_true', help='Show study streaks')

    # Content recommendations
    suggest_parser = subparsers.add_parser('suggest', help='Get content suggestions')
    suggest_parser.add_argument('deck', help='Deck name or ID')
    suggest_parser.add_argument('--cards', type=int, default=5, help='Number of card suggestions')
    suggest_parser.add_argument('--topics', action='store_true', help='Suggest related topics')
    suggest_parser.add_argument('--gaps', action='store_true', help='Identify content gaps')

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
    from flashgenie.data.storage import DataStorage
    from flashgenie.core.performance_tracker import PerformanceTracker
    from flashgenie.utils.exceptions import FlashGenieError

    storage = DataStorage()

    try:
        # Load deck
        deck = storage.load_deck_by_name(args.deck)
        if deck is None:
            deck = storage.load_deck(args.deck)
        if deck is None:
            print(f"Error: Deck '{args.deck}' not found")
            sys.exit(1)

        # Initialize performance tracker
        tracker = PerformanceTracker()

        print(f"📊 Statistics for '{deck.name}'")
        print("=" * 50)

        # Basic deck statistics
        total_cards = len(deck.flashcards)
        reviewed_cards = len([c for c in deck.flashcards if c.review_count > 0])
        due_cards = len(deck.get_due_cards())
        mastered_cards = len([c for c in deck.flashcards if c.review_count >= 3 and c.calculate_accuracy() >= 0.9])

        print(f"📚 **Deck Overview**:")
        print(f"   Total cards: {total_cards}")
        print(f"   Reviewed cards: {reviewed_cards}")
        print(f"   Due for review: {due_cards}")
        print(f"   Mastered cards: {mastered_cards}")
        print(f"   Mastery rate: {mastered_cards/total_cards*100:.1f}%" if total_cards > 0 else "   Mastery rate: 0.0%")
        print()

        if reviewed_cards > 0:
            # Performance statistics
            total_reviews = sum(c.review_count for c in deck.flashcards)
            total_correct = sum(c.correct_count for c in deck.flashcards)
            overall_accuracy = total_correct / total_reviews if total_reviews > 0 else 0

            print(f"🎯 **Performance**:")
            print(f"   Total reviews: {total_reviews}")
            print(f"   Overall accuracy: {overall_accuracy:.1%}")

            # Response time statistics
            all_response_times = []
            for card in deck.flashcards:
                if card.response_times:
                    all_response_times.extend(card.response_times)

            if all_response_times:
                avg_response_time = sum(all_response_times) / len(all_response_times)
                print(f"   Average response time: {avg_response_time:.1f}s")
            print()

            # Difficulty distribution
            difficulties = [c.difficulty for c in deck.flashcards]
            if difficulties:
                avg_difficulty = sum(difficulties) / len(difficulties)
                print(f"📈 **Difficulty Analysis**:")
                print(f"   Average difficulty: {avg_difficulty:.2f}")
                print(f"   Easy cards (< 0.3): {len([d for d in difficulties if d < 0.3])}")
                print(f"   Medium cards (0.3-0.7): {len([d for d in difficulties if 0.3 <= d < 0.7])}")
                print(f"   Hard cards (≥ 0.7): {len([d for d in difficulties if d >= 0.7])}")
                print()

        # Tag statistics
        all_tags = set()
        for card in deck.flashcards:
            all_tags.update(card.tags)

        if all_tags:
            print(f"🏷️ **Tags**:")
            print(f"   Total tags: {len(all_tags)}")
            print(f"   Most common tags: {', '.join(list(all_tags)[:5])}")

    except FlashGenieError as e:
        print(f"Statistics failed: {e}")
        sys.exit(1)


def handle_export_command(args) -> None:
    """Handle the export command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.utils.exceptions import FlashGenieError
    import json
    import csv

    storage = DataStorage()

    try:
        # Load deck
        deck = storage.load_deck_by_name(args.deck)
        if deck is None:
            deck = storage.load_deck(args.deck)
        if deck is None:
            print(f"Error: Deck '{args.deck}' not found")
            sys.exit(1)

        print(f"📤 Exporting '{deck.name}' to {args.output}...")

        if args.format == 'csv':
            # Export to CSV
            with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Question', 'Answer', 'Tags', 'Difficulty', 'Review Count', 'Accuracy'])

                for card in deck.flashcards:
                    accuracy = card.calculate_accuracy() if card.review_count > 0 else 0.0
                    writer.writerow([
                        card.question,
                        card.answer,
                        ';'.join(card.tags),
                        f"{card.difficulty:.2f}",
                        card.review_count,
                        f"{accuracy:.2f}"
                    ])

        elif args.format == 'json':
            # Export to JSON
            export_data = {
                'deck_name': deck.name,
                'deck_description': deck.description,
                'export_date': datetime.now().isoformat(),
                'total_cards': len(deck.flashcards),
                'cards': []
            }

            for card in deck.flashcards:
                card_data = {
                    'question': card.question,
                    'answer': card.answer,
                    'tags': list(card.tags),
                    'difficulty': card.difficulty,
                    'review_count': card.review_count,
                    'correct_count': card.correct_count,
                    'accuracy': card.calculate_accuracy() if card.review_count > 0 else 0.0,
                    'created_at': card.created_at.isoformat() if card.created_at else None,
                    'last_reviewed': card.last_reviewed.isoformat() if card.last_reviewed else None
                }
                export_data['cards'].append(card_data)

            with open(args.output, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)

        print(f"✅ Successfully exported {len(deck.flashcards)} cards to {args.output}")

    except FlashGenieError as e:
        print(f"Export failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Export failed: {e}")
        sys.exit(1)


def handle_plan_command(args) -> None:
    """Handle the adaptive study planning command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.core.adaptive_study_planner import AdaptiveStudyPlanner, StudyContext, EnergyLevel, Environment
    from flashgenie.core.difficulty_analyzer import DifficultyAnalyzer
    from flashgenie.core.smart_collections import SmartCollectionManager
    from flashgenie.core.tag_manager import TagManager
    from flashgenie.utils.exceptions import FlashGenieError
    from datetime import datetime

    storage = DataStorage()

    try:
        # Load deck
        deck = storage.load_deck_by_name(args.deck)
        if deck is None:
            deck = storage.load_deck(args.deck)
        if deck is None:
            print(f"Error: Deck '{args.deck}' not found")
            sys.exit(1)

        # Initialize components
        tag_manager = TagManager()
        difficulty_analyzer = DifficultyAnalyzer()
        collection_manager = SmartCollectionManager(tag_manager)
        planner = AdaptiveStudyPlanner(difficulty_analyzer, collection_manager)

        # Create study context
        environment_map = {
            'quiet': Environment.QUIET_HOME,
            'noisy': Environment.NOISY_PUBLIC,
            'mobile': Environment.COMMUTING
        }

        context = StudyContext(
            available_time=args.time,
            energy_level=EnergyLevel(args.energy),
            time_of_day=datetime.now(),
            environment=environment_map[args.environment]
        )

        # Generate study plan
        print(f"🧞‍♂️ Creating adaptive study plan for '{deck.name}'...")
        print(f"⏰ Available time: {args.time} minutes")
        print(f"⚡ Energy level: {args.energy}/5")
        print(f"🌍 Environment: {args.environment}")
        print()

        study_plan = planner.plan_session(deck, context)

        # Display plan
        print("📋 **Adaptive Study Plan**")
        print("=" * 50)
        print(f"Session ID: {study_plan.session_id}")
        print(f"Total Duration: {study_plan.total_duration} minutes")
        print(f"Estimated Cards: {study_plan.estimated_cards}")
        print(f"Confidence Score: {study_plan.confidence_score:.2f}")
        print()

        print("📚 **Study Segments**:")
        for i, segment in enumerate(study_plan.segments, 1):
            print(f"{i}. {segment.segment_type.title()} ({segment.estimated_duration} min)")
            print(f"   Cards: {len(segment.cards)}")
            print(f"   Difficulty: {segment.difficulty_range[0]:.2f} - {segment.difficulty_range[1]:.2f}")
            if segment.break_after:
                print(f"   Break: {segment.break_duration} minutes")
            print()

        if study_plan.optimization_notes:
            print("💡 **Optimization Notes**:")
            for note in study_plan.optimization_notes:
                print(f"   • {note}")

    except FlashGenieError as e:
        print(f"Planning failed: {e}")
        sys.exit(1)


def handle_velocity_command(args) -> None:
    """Handle the learning velocity analysis command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.core.learning_velocity_tracker import LearningVelocityTracker
    from flashgenie.utils.exceptions import FlashGenieError

    storage = DataStorage()

    try:
        # Load deck
        deck = storage.load_deck_by_name(args.deck)
        if deck is None:
            deck = storage.load_deck(args.deck)
        if deck is None:
            print(f"Error: Deck '{args.deck}' not found")
            sys.exit(1)

        # Initialize velocity tracker
        tracker = LearningVelocityTracker()

        print(f"📈 Learning Velocity Analysis for '{deck.name}'")
        print("=" * 50)

        # Current velocity
        velocity = tracker.calculate_current_velocity(deck)
        print(f"📊 **Current Velocity**:")
        print(f"   Cards per day: {velocity.cards_per_day:.1f}")
        print(f"   Mastery per day: {velocity.mastery_per_day:.1f}")
        print(f"   Study efficiency: {velocity.study_efficiency:.2f} cards/min")
        print(f"   Learning phase: {velocity.phase.value}")
        print()

        # Mastery prediction
        if args.predict:
            prediction = tracker.predict_mastery_timeline(deck)
            print(f"🔮 **Mastery Prediction**:")
            print(f"   Estimated days to mastery: {prediction.estimated_days_to_mastery}")
            print(f"   Confidence interval: {prediction.confidence_interval[0]}-{prediction.confidence_interval[1]} days")
            print(f"   Recommended daily time: {prediction.recommended_daily_time} minutes")
            print(f"   Confidence score: {prediction.confidence_score:.2f}")

            if prediction.bottleneck_cards:
                print(f"   Bottleneck cards: {len(prediction.bottleneck_cards)}")

            if prediction.acceleration_opportunities:
                print(f"   💡 Acceleration opportunities:")
                for opportunity in prediction.acceleration_opportunities:
                    print(f"      • {opportunity}")
            print()

        # Learning trends
        if args.trends:
            trends = tracker.analyze_learning_trends(deck)
            print(f"📈 **Learning Trends**:")
            print(f"   Velocity trend: {trends['velocity_trend'].value}")
            print(f"   Accuracy trend: {trends['accuracy_trend']:+.3f}")
            print(f"   Efficiency trend: {trends['efficiency_trend']:+.3f}")

            if trends['insights']:
                print(f"   💡 Insights:")
                for insight in trends['insights']:
                    print(f"      • {insight}")

    except FlashGenieError as e:
        print(f"Velocity analysis failed: {e}")
        sys.exit(1)


def handle_graph_command(args) -> None:
    """Handle the knowledge graph generation command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.core.knowledge_graph import KnowledgeGraphBuilder
    from flashgenie.core.tag_manager import TagManager
    from flashgenie.utils.exceptions import FlashGenieError
    import json

    storage = DataStorage()

    try:
        # Load deck
        deck = storage.load_deck_by_name(args.deck)
        if deck is None:
            deck = storage.load_deck(args.deck)
        if deck is None:
            print(f"Error: Deck '{args.deck}' not found")
            sys.exit(1)

        # Initialize knowledge graph builder
        tag_manager = TagManager()
        graph_builder = KnowledgeGraphBuilder(tag_manager)

        print(f"🕸️ Building knowledge graph for '{deck.name}'...")

        # Build graph
        knowledge_graph = graph_builder.build_graph(deck)

        # Display summary
        summary = knowledge_graph.get_mastery_summary()
        print(f"📊 **Knowledge Graph Summary**:")
        print(f"   Total concepts: {summary.get('total_concepts', 0)}")
        print(f"   Total cards: {summary.get('total_cards', 0)}")
        print(f"   Mastered cards: {summary.get('mastered_cards', 0)}")
        print(f"   Overall mastery: {summary.get('overall_mastery_rate', 0):.1%}")
        print(f"   Knowledge gaps: {summary.get('knowledge_gaps', 0)}")
        print(f"   Learning paths: {summary.get('learning_paths', 0)}")
        print()

        # Show mastery distribution
        if 'mastery_distribution' in summary:
            print(f"🎯 **Mastery Distribution**:")
            for level, count in summary['mastery_distribution'].items():
                if count > 0:
                    print(f"   {level}: {count} concepts")
            print()

        # Show learning paths
        if knowledge_graph.learning_paths:
            print(f"🛤️ **Learning Paths**:")
            for path in knowledge_graph.learning_paths:
                print(f"   • {path.name}: {path.estimated_duration} days")
                print(f"     {path.description}")
            print()

        # Show knowledge gaps
        if knowledge_graph.knowledge_gaps:
            print(f"⚠️ **Knowledge Gaps**:")
            for gap in knowledge_graph.knowledge_gaps[:5]:  # Show top 5
                print(f"   • {gap.gap_type}: {gap.description}")
                print(f"     Severity: {gap.severity:.2f}")
            print()

        # Export if requested
        if args.export:
            export_data = knowledge_graph.export_for_visualization()

            if args.format == 'json':
                with open(args.export, 'w') as f:
                    json.dump(export_data, f, indent=2)
                print(f"📁 Graph data exported to {args.export}")
            elif args.format == 'html':
                # Generate HTML visualization (simplified)
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>FlashGenie Knowledge Graph - {deck.name}</title>
                    <script src="https://d3js.org/d3.v7.min.js"></script>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .node {{ stroke: #fff; stroke-width: 2px; }}
                        .link {{ stroke: #999; stroke-opacity: 0.6; }}
                    </style>
                </head>
                <body>
                    <h1>Knowledge Graph: {deck.name}</h1>
                    <div id="graph"></div>
                    <script>
                        const data = {json.dumps(export_data)};
                        // D3.js visualization code would go here
                        console.log('Graph data:', data);
                    </script>
                </body>
                </html>
                """
                with open(args.export, 'w') as f:
                    f.write(html_content)
                print(f"📁 HTML visualization exported to {args.export}")

    except FlashGenieError as e:
        print(f"Graph generation failed: {e}")
        sys.exit(1)


def handle_achievements_command(args) -> None:
    """Handle the achievements command."""
    from flashgenie.core.achievement_system import AchievementEngine
    from flashgenie.utils.exceptions import FlashGenieError

    try:
        # Initialize achievement engine
        achievement_engine = AchievementEngine()

        print("🏆 **FlashGenie Achievements**")
        print("=" * 50)

        # Show user level and points
        level, current_points, points_to_next = achievement_engine.get_user_level_and_points()
        print(f"👤 **Your Progress**:")
        print(f"   Level: {level}")
        print(f"   Points: {current_points}/1000 (to next level)")
        print(f"   Points needed: {points_to_next}")
        print()

        # Show earned achievements
        earned_achievements = achievement_engine.user_achievements
        if earned_achievements:
            print(f"🎖️ **Earned Achievements** ({len(earned_achievements)}):")
            for ua in earned_achievements[-5:]:  # Show last 5
                achievement = achievement_engine.achievements.get(ua.achievement_id)
                if achievement:
                    print(f"   {achievement.badge_icon} {achievement.name}")
                    print(f"      {achievement.description}")
                    print(f"      Earned: {ua.earned_at.strftime('%Y-%m-%d')}")
            print()

        # Show achievement progress
        if args.progress:
            print(f"📊 **Achievement Progress**:")
            # This would require user stats - simplified for now
            available_achievements = list(achievement_engine.achievements.values())[:5]
            for achievement in available_achievements:
                if not achievement.hidden:
                    earned = any(ua.achievement_id == achievement.id for ua in earned_achievements)
                    status = "✅ Earned" if earned else "⏳ In Progress"
                    print(f"   {achievement.badge_icon} {achievement.name} - {status}")
                    print(f"      {achievement.description}")
            print()

        # Show study streaks
        if args.streaks:
            print(f"🔥 **Study Streaks**:")
            leaderboard_stats = achievement_engine.get_leaderboard_stats()

            if leaderboard_stats['current_streaks']:
                print(f"   Current streaks:")
                for streak_type, count in leaderboard_stats['current_streaks'].items():
                    print(f"      {streak_type}: {count} days")

            if leaderboard_stats['best_streaks']:
                print(f"   Best streaks:")
                for streak_type, count in leaderboard_stats['best_streaks'].items():
                    print(f"      {streak_type}: {count} days")
            print()

    except FlashGenieError as e:
        print(f"Achievements failed: {e}")
        sys.exit(1)


def handle_suggest_command(args) -> None:
    """Handle the content suggestions command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.core.content_recommender import ContentRecommendationEngine
    from flashgenie.core.tag_manager import TagManager
    from flashgenie.utils.exceptions import FlashGenieError

    storage = DataStorage()

    try:
        # Load deck
        deck = storage.load_deck_by_name(args.deck)
        if deck is None:
            deck = storage.load_deck(args.deck)
        if deck is None:
            print(f"Error: Deck '{args.deck}' not found")
            sys.exit(1)

        # Initialize content recommender
        tag_manager = TagManager()
        recommender = ContentRecommendationEngine(tag_manager)

        print(f"💡 Content Suggestions for '{deck.name}'")
        print("=" * 50)

        # Card suggestions
        if not args.topics and not args.gaps:
            card_suggestions = recommender.suggest_new_cards(deck, count=args.cards)

            if card_suggestions:
                print(f"📝 **New Card Suggestions** ({len(card_suggestions)}):")
                for i, suggestion in enumerate(card_suggestions, 1):
                    print(f"{i}. Q: {suggestion.suggested_question}")
                    print(f"   A: {suggestion.suggested_answer}")
                    print(f"   Tags: {', '.join(suggestion.suggested_tags)}")
                    print(f"   Difficulty: {suggestion.estimated_difficulty:.2f}")
                    print(f"   Confidence: {suggestion.confidence_score:.2f}")
                    print(f"   Reasoning: {suggestion.reasoning}")
                    print()
            else:
                print("No card suggestions available at this time.")

        # Topic suggestions
        if args.topics:
            topic_suggestions = recommender.suggest_related_topics(deck)

            if topic_suggestions:
                print(f"🎯 **Related Topic Suggestions** ({len(topic_suggestions)}):")
                for i, suggestion in enumerate(topic_suggestions, 1):
                    print(f"{i}. {suggestion.topic_name}")
                    print(f"   Description: {suggestion.description}")
                    print(f"   Estimated cards: {suggestion.estimated_card_count}")
                    print(f"   Priority: {suggestion.priority_score:.2f}")
                    print(f"   Reasoning: {suggestion.reasoning}")
                    print()
            else:
                print("No topic suggestions available.")

        # Content gaps
        if args.gaps:
            prerequisites = recommender.identify_prerequisite_gaps(deck)

            if prerequisites:
                print(f"⚠️ **Prerequisite Gaps** ({len(prerequisites)}):")
                for i, prereq in enumerate(prerequisites, 1):
                    print(f"{i}. {prereq.topic_name}")
                    print(f"   Description: {prereq.description}")
                    print(f"   Priority: {prereq.priority_score:.2f}")
                    print(f"   Reasoning: {prereq.reasoning}")
                    print()
            else:
                print("No significant prerequisite gaps identified.")

            # Study sequence recommendation
            sequence = recommender.recommend_study_sequence(deck)
            if sequence:
                print(f"📚 **Recommended Study Sequence**:")
                for phase in sequence:
                    print(f"   Phase: {phase['phase']}")
                    print(f"   Description: {phase['description']}")
                    print(f"   Topics: {', '.join(phase['topics'][:3])}{'...' if len(phase['topics']) > 3 else ''}")
                    print(f"   Duration: {phase['estimated_duration']} days")
                    print(f"   Focus: {phase['focus']}")
                    print()

    except FlashGenieError as e:
        print(f"Content suggestions failed: {e}")
        sys.exit(1)


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
    elif args.command == 'plan':
        handle_plan_command(args)
    elif args.command == 'velocity':
        handle_velocity_command(args)
    elif args.command == 'graph':
        handle_graph_command(args)
    elif args.command == 'achievements':
        handle_achievements_command(args)
    elif args.command == 'suggest':
        handle_suggest_command(args)
    else:
        # No command specified, start interactive mode
        ui = TerminalUI()
        ui.start()


if __name__ == "__main__":
    main()
