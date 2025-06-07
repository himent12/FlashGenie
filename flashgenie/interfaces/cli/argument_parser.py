"""
Command-line argument parser for FlashGenie.

This module provides the argument parser configuration for all CLI commands.
"""

import argparse
from flashgenie.config import APP_NAME, APP_VERSION


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
        version=f'{APP_NAME} {APP_VERSION}'
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
    
    # Core commands
    _add_core_commands(subparsers)
    
    # Advanced learning commands
    _add_advanced_commands(subparsers)
    
    # Plugin system commands
    _add_plugin_commands(subparsers)
    
    return parser


def _add_core_commands(subparsers):
    """Add core FlashGenie commands."""
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


def _add_advanced_commands(subparsers):
    """Add advanced learning feature commands."""
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


def _add_plugin_commands(subparsers):
    """Add plugin system commands."""
    # Plugin management
    plugins_parser = subparsers.add_parser('plugins', help='Manage FlashGenie plugins')
    plugins_parser.add_argument('action', choices=['list', 'discover', 'enable', 'disable', 'install', 'uninstall', 'info'],
                               help='Plugin action to perform')
    plugins_parser.add_argument('--name', help='Plugin name (for enable/disable/uninstall/info)')
    plugins_parser.add_argument('--path', help='Plugin path (for install)')
    plugins_parser.add_argument('--category', choices=['official', 'community', 'local', 'development'],
                               default='local', help='Plugin category (for install)')

    # Plugin Development Kit
    pdk_parser = subparsers.add_parser('pdk', help='Plugin Development Kit - tools for plugin developers')
    pdk_parser.add_argument('action', choices=['create', 'validate', 'test', 'package'],
                           help='PDK action to perform')
    pdk_parser.add_argument('--name', help='Plugin name (for create)')
    pdk_parser.add_argument('--type', choices=['importer', 'exporter', 'theme', 'quiz_mode', 'ai_enhancement', 'analytics', 'integration'],
                           help='Plugin type (for create)')
    pdk_parser.add_argument('--author', default='Plugin Developer', help='Plugin author (for create)')
    pdk_parser.add_argument('--path', help='Plugin path (for validate/test/package)')
    pdk_parser.add_argument('--output', help='Output directory (for package)')
    pdk_parser.add_argument('--test-mode', choices=['basic', 'detailed', 'comprehensive'],
                           default='basic', help='Test mode (for test)')

    # Plugin Marketplace
    marketplace_parser = subparsers.add_parser('marketplace', help='Plugin marketplace - discover and install community plugins')
    marketplace_parser.add_argument('action', choices=['search', 'featured', 'install', 'rate', 'recommendations', 'stats'],
                                   help='Marketplace action to perform')
    marketplace_parser.add_argument('--query', help='Search query (for search)')
    marketplace_parser.add_argument('--type', choices=['importer', 'exporter', 'theme', 'quiz_mode', 'ai_enhancement', 'analytics', 'integration'],
                                   help='Plugin type filter (for search)')
    marketplace_parser.add_argument('--name', help='Plugin name (for install/rate)')
    marketplace_parser.add_argument('--rating', type=float, help='Rating 1.0-5.0 (for rate)')
    marketplace_parser.add_argument('--review', help='Review text (for rate)')
    marketplace_parser.add_argument('--user-id', help='User ID (for rate)')
    marketplace_parser.add_argument('--free-only', action='store_true', help='Show only free plugins (for search)')
    marketplace_parser.add_argument('--min-rating', type=float, default=0.0, help='Minimum rating filter (for search)')
