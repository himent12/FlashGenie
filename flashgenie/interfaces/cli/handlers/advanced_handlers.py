"""
Advanced command handlers for FlashGenie CLI.

This module contains handlers for advanced learning features like adaptive planning,
velocity tracking, knowledge graphs, achievements, and content suggestions.
"""

import sys
from pathlib import Path
from flashgenie.utils.exceptions import FlashGenieError


def handle_plan_command(args) -> None:
    """Handle the adaptive study plan command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.core.contextual_learning_engine import ContextualLearningEngine
    
    storage = DataStorage()
    
    try:
        # Load deck
        deck = storage.load_deck_by_name(args.deck)
        if deck is None:
            deck = storage.load_deck(args.deck)
        if deck is None:
            print(f"Error: Deck '{args.deck}' not found")
            sys.exit(1)
        
        # Create study plan
        engine = ContextualLearningEngine()
        context = {
            'available_time': args.time,
            'energy_level': args.energy,
            'environment': args.environment
        }
        
        print(f"🎯 **Creating adaptive study plan for '{deck.name}'**")
        print(f"Available time: {args.time} minutes")
        print(f"Energy level: {args.energy}/5")
        print(f"Environment: {args.environment}")
        print("=" * 50)
        
        plan = engine.create_study_plan(deck, context)
        
        if plan:
            print(f"📋 **Recommended Study Plan**")
            print(f"Estimated completion: {plan.get('estimated_time', args.time)} minutes")
            print(f"Recommended cards: {plan.get('card_count', 0)}")
            print(f"Focus areas: {', '.join(plan.get('focus_areas', []))}")
            
            if plan.get('recommendations'):
                print(f"\n💡 **Recommendations:**")
                for rec in plan['recommendations']:
                    print(f"   • {rec}")
            
            if plan.get('session_structure'):
                print(f"\n📚 **Session Structure:**")
                for phase in plan['session_structure']:
                    print(f"   {phase['name']}: {phase['duration']} min - {phase['description']}")
        else:
            print("Unable to create study plan. Please try again with different parameters.")
        
    except FlashGenieError as e:
        print(f"Study planning failed: {e}")
        sys.exit(1)


def handle_velocity_command(args) -> None:
    """Handle the learning velocity analysis command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.core.learning_velocity_tracker import LearningVelocityTracker
    
    storage = DataStorage()
    
    try:
        # Load deck
        deck = storage.load_deck_by_name(args.deck)
        if deck is None:
            deck = storage.load_deck(args.deck)
        if deck is None:
            print(f"Error: Deck '{args.deck}' not found")
            sys.exit(1)
        
        # Analyze learning velocity
        tracker = LearningVelocityTracker()
        
        print(f"📈 **Learning Velocity Analysis for '{deck.name}'**")
        print("=" * 50)
        
        velocity_data = tracker.analyze_deck_velocity(deck)
        
        if velocity_data:
            print(f"Current velocity: {velocity_data.get('current_velocity', 0):.2f} cards/day")
            print(f"Average velocity: {velocity_data.get('average_velocity', 0):.2f} cards/day")
            print(f"Velocity trend: {velocity_data.get('trend', 'stable')}")
            
            if args.predict and velocity_data.get('predictions'):
                print(f"\n🔮 **Mastery Predictions:**")
                predictions = velocity_data['predictions']
                print(f"Estimated mastery date: {predictions.get('mastery_date', 'Unknown')}")
                print(f"Days to mastery: {predictions.get('days_to_mastery', 'Unknown')}")
                print(f"Confidence: {predictions.get('confidence', 0):.1%}")
            
            if args.trends and velocity_data.get('trends'):
                print(f"\n📊 **Learning Trends:**")
                trends = velocity_data['trends']
                for period, data in trends.items():
                    print(f"   {period}: {data.get('velocity', 0):.2f} cards/day ({data.get('change', 'no change')})")
            
            # Performance insights
            if velocity_data.get('insights'):
                print(f"\n💡 **Insights:**")
                for insight in velocity_data['insights']:
                    print(f"   • {insight}")
        else:
            print("Insufficient data for velocity analysis. Complete more study sessions to see trends.")
        
    except FlashGenieError as e:
        print(f"Velocity analysis failed: {e}")
        sys.exit(1)


def handle_graph_command(args) -> None:
    """Handle the knowledge graph generation command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.core.knowledge_graph import KnowledgeGraph
    
    storage = DataStorage()
    
    try:
        # Load deck
        deck = storage.load_deck_by_name(args.deck)
        if deck is None:
            deck = storage.load_deck(args.deck)
        if deck is None:
            print(f"Error: Deck '{args.deck}' not found")
            sys.exit(1)
        
        # Generate knowledge graph
        graph = KnowledgeGraph()
        
        print(f"🕸️ **Generating knowledge graph for '{deck.name}'**")
        print("=" * 50)
        
        graph_data = graph.build_graph(deck)
        
        if graph_data:
            print(f"Nodes: {graph_data.get('node_count', 0)}")
            print(f"Connections: {graph_data.get('edge_count', 0)}")
            print(f"Clusters: {graph_data.get('cluster_count', 0)}")
            
            # Show key concepts
            if graph_data.get('key_concepts'):
                print(f"\n🔑 **Key Concepts:**")
                for concept in graph_data['key_concepts'][:10]:
                    print(f"   • {concept['name']} (connections: {concept.get('connections', 0)})")
            
            # Show learning paths
            if graph_data.get('learning_paths'):
                print(f"\n🛤️ **Suggested Learning Paths:**")
                for i, path in enumerate(graph_data['learning_paths'][:3], 1):
                    print(f"   {i}. {' → '.join(path['concepts'])}")
            
            # Export if requested
            if args.export:
                export_path = Path(args.export)
                
                if args.format == 'json':
                    import json
                    with open(export_path, 'w') as f:
                        json.dump(graph_data, f, indent=2)
                elif args.format == 'html':
                    graph.export_html(graph_data, export_path)
                
                print(f"\n✅ Graph exported to {export_path}")
        else:
            print("Unable to generate knowledge graph. Deck may be too small or lack connections.")
        
    except FlashGenieError as e:
        print(f"Knowledge graph generation failed: {e}")
        sys.exit(1)


def handle_achievements_command(args) -> None:
    """Handle the achievements command."""
    from flashgenie.core.achievement_system import AchievementSystem
    
    try:
        achievement_system = AchievementSystem()
        
        print("🏆 **Your Achievements**")
        print("=" * 50)
        
        achievements = achievement_system.get_user_achievements()
        
        if achievements:
            # Show unlocked achievements
            unlocked = [a for a in achievements if a.get('unlocked')]
            if unlocked:
                print(f"🎉 **Unlocked ({len(unlocked)}):**")
                for achievement in unlocked:
                    print(f"   🏅 {achievement['name']}")
                    print(f"      {achievement['description']}")
                    print(f"      Unlocked: {achievement.get('unlock_date', 'Unknown')}")
                    print()
            
            # Show progress on locked achievements
            locked = [a for a in achievements if not a.get('unlocked')]
            if locked and args.progress:
                print(f"🔒 **In Progress ({len(locked)}):**")
                for achievement in locked:
                    progress = achievement.get('progress', 0)
                    target = achievement.get('target', 100)
                    percentage = (progress / target * 100) if target > 0 else 0
                    
                    print(f"   📊 {achievement['name']}")
                    print(f"      {achievement['description']}")
                    print(f"      Progress: {progress}/{target} ({percentage:.1f}%)")
                    print()
        
        # Show study streaks
        if args.streaks:
            streaks = achievement_system.get_study_streaks()
            if streaks:
                print(f"🔥 **Study Streaks:**")
                print(f"   Current streak: {streaks.get('current_streak', 0)} days")
                print(f"   Longest streak: {streaks.get('longest_streak', 0)} days")
                print(f"   This week: {streaks.get('week_streak', 0)} days")
                print(f"   This month: {streaks.get('month_streak', 0)} days")
        
        if not achievements:
            print("No achievements yet. Start studying to unlock your first achievements!")
        
    except FlashGenieError as e:
        print(f"Failed to load achievements: {e}")
        sys.exit(1)


def handle_suggest_command(args) -> None:
    """Handle the content suggestions command."""
    from flashgenie.data.storage import DataStorage
    from flashgenie.core.content_recommender import ContentRecommender
    
    storage = DataStorage()
    
    try:
        # Load deck
        deck = storage.load_deck_by_name(args.deck)
        if deck is None:
            deck = storage.load_deck(args.deck)
        if deck is None:
            print(f"Error: Deck '{args.deck}' not found")
            sys.exit(1)
        
        # Generate suggestions
        recommender = ContentRecommender()
        
        print(f"💡 **Content Suggestions for '{deck.name}'**")
        print("=" * 50)
        
        if args.cards > 0:
            # Suggest new cards
            card_suggestions = recommender.suggest_cards(deck, count=args.cards)
            
            if card_suggestions:
                print(f"📝 **Suggested Cards ({len(card_suggestions)}):**")
                for i, suggestion in enumerate(card_suggestions, 1):
                    print(f"   {i}. Q: {suggestion['question']}")
                    print(f"      A: {suggestion['answer']}")
                    print(f"      Reason: {suggestion.get('reason', 'Content gap identified')}")
                    print()
        
        if args.topics:
            # Suggest related topics
            topic_suggestions = recommender.suggest_topics(deck)
            
            if topic_suggestions:
                print(f"🎯 **Related Topics:**")
                for topic in topic_suggestions:
                    print(f"   • {topic['name']}")
                    print(f"     {topic['description']}")
                    print(f"     Relevance: {topic.get('relevance', 0):.1%}")
                    print()
        
        if args.gaps:
            # Identify content gaps
            gaps = recommender.identify_content_gaps(deck)
            
            if gaps:
                print(f"🔍 **Content Gaps Identified:**")
                for gap in gaps:
                    print(f"   • {gap['area']}")
                    print(f"     {gap['description']}")
                    print(f"     Priority: {gap.get('priority', 'medium')}")
                    print()
        
        if not any([args.cards > 0, args.topics, args.gaps]):
            print("No suggestions requested. Use --cards, --topics, or --gaps to get recommendations.")
        
    except FlashGenieError as e:
        print(f"Content suggestions failed: {e}")
        sys.exit(1)
