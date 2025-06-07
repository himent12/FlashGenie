"""
Enhanced Help System for FlashGenie v1.8.4.

This module provides a comprehensive, searchable help system with Rich Terminal UI
integration, contextual assistance, and categorized command reference.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.tree import Tree
from rich.prompt import Prompt


class CommandCategory(Enum):
    """Command categories for organization."""
    BASIC = "basic"
    DECK_MANAGEMENT = "deck_management"
    STUDY_SESSION = "study_session"
    IMPORT_EXPORT = "import_export"
    ANALYTICS = "analytics"
    ACCESSIBILITY = "accessibility"
    DEVELOPER = "developer"
    PERFORMANCE = "performance"


@dataclass
class CommandInfo:
    """Information about a command."""
    name: str
    category: CommandCategory
    syntax: str
    description: str
    examples: List[str]
    aliases: List[str] = None
    permissions: str = "user"
    related_commands: List[str] = None
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.related_commands is None:
            self.related_commands = []


class HelpSystem:
    """
    Comprehensive help system for FlashGenie with Rich Terminal UI.
    
    Provides categorized commands, searchable reference, contextual help,
    and beautiful Rich formatting.
    """
    
    def __init__(self, console: Console):
        """
        Initialize help system.
        
        Args:
            console: Rich console instance
        """
        self.console = console
        self.commands = self._initialize_commands()
        self.categories = self._organize_by_category()
    
    def _initialize_commands(self) -> Dict[str, CommandInfo]:
        """Initialize the complete command database."""
        commands = {}
        
        # Basic Commands
        commands["help"] = CommandInfo(
            name="help",
            category=CommandCategory.BASIC,
            syntax="python -m flashgenie help [command]",
            description="Show help information for FlashGenie commands",
            examples=[
                "python -m flashgenie help",
                "python -m flashgenie help list",
                "python -m flashgenie help import"
            ],
            aliases=["--help", "-h"],
            related_commands=["version", "info"]
        )
        
        commands["version"] = CommandInfo(
            name="version",
            category=CommandCategory.BASIC,
            syntax="python -m flashgenie version",
            description="Display FlashGenie version and system information",
            examples=["python -m flashgenie version"],
            aliases=["--version", "-v"]
        )
        
        # Deck Management Commands
        commands["list"] = CommandInfo(
            name="list",
            category=CommandCategory.DECK_MANAGEMENT,
            syntax="python -m flashgenie list [--format FORMAT]",
            description="List all flashcard decks with beautiful Rich tables",
            examples=[
                "python -m flashgenie list",
                "python -m flashgenie list --format table",
                "python -m flashgenie list --format json"
            ],
            aliases=["ls"],
            related_commands=["stats", "info"]
        )
        
        commands["create"] = CommandInfo(
            name="create",
            category=CommandCategory.DECK_MANAGEMENT,
            syntax="python -m flashgenie create NAME [--description DESC]",
            description="Create a new flashcard deck",
            examples=[
                'python -m flashgenie create "Spanish Vocabulary"',
                'python -m flashgenie create "Math Formulas" --description "Basic algebra formulas"'
            ],
            related_commands=["add", "import"]
        )
        
        commands["delete"] = CommandInfo(
            name="delete",
            category=CommandCategory.DECK_MANAGEMENT,
            syntax="python -m flashgenie delete DECK_NAME [--confirm]",
            description="Delete a flashcard deck (requires confirmation)",
            examples=[
                'python -m flashgenie delete "Old Deck" --confirm',
                'python -m flashgenie delete "Test Deck"'
            ],
            aliases=["remove", "rm"],
            related_commands=["list", "backup"]
        )
        
        # Import/Export Commands
        commands["import"] = CommandInfo(
            name="import",
            category=CommandCategory.IMPORT_EXPORT,
            syntax="python -m flashgenie import FILE --name NAME [--format FORMAT]",
            description="Import flashcards from CSV, JSON, or other formats with Rich progress",
            examples=[
                'python -m flashgenie import deck.csv --name "My Deck"',
                'python -m flashgenie import cards.json --name "JSON Deck" --format json',
                'python -m flashgenie import anki_deck.apkg --name "Anki Import"'
            ],
            related_commands=["export", "create"]
        )
        
        commands["export"] = CommandInfo(
            name="export",
            category=CommandCategory.IMPORT_EXPORT,
            syntax="python -m flashgenie export DECK_NAME [--format FORMAT] [--output FILE]",
            description="Export flashcard deck to various formats",
            examples=[
                'python -m flashgenie export "Spanish Vocabulary"',
                'python -m flashgenie export "Math" --format json --output math_backup.json',
                'python -m flashgenie export "History" --format csv'
            ],
            related_commands=["import", "backup"]
        )
        
        # Study Session Commands
        commands["quiz"] = CommandInfo(
            name="quiz",
            category=CommandCategory.STUDY_SESSION,
            syntax="python -m flashgenie quiz DECK_NAME [--count N] [--timed] [--mode MODE]",
            description="Start an adaptive quiz session with spaced repetition",
            examples=[
                'python -m flashgenie quiz "Spanish Vocabulary"',
                'python -m flashgenie quiz "Math" --count 20 --timed',
                'python -m flashgenie quiz "History" --mode review'
            ],
            aliases=["study", "practice"],
            related_commands=["stats", "review"]
        )
        
        commands["review"] = CommandInfo(
            name="review",
            category=CommandCategory.STUDY_SESSION,
            syntax="python -m flashgenie review DECK_NAME [--difficult-only]",
            description="Review cards marked for review or difficult cards",
            examples=[
                'python -m flashgenie review "Spanish Vocabulary"',
                'python -m flashgenie review "Math" --difficult-only'
            ],
            related_commands=["quiz", "stats"]
        )
        
        # Analytics Commands
        commands["stats"] = CommandInfo(
            name="stats",
            category=CommandCategory.ANALYTICS,
            syntax="python -m flashgenie stats [DECK_NAME] [--detailed] [--export]",
            description="Show comprehensive statistics with Rich formatting",
            examples=[
                "python -m flashgenie stats",
                'python -m flashgenie stats "Spanish Vocabulary" --detailed',
                "python -m flashgenie stats --export stats.json"
            ],
            aliases=["statistics", "analytics"],
            related_commands=["list", "progress"]
        )
        
        commands["progress"] = CommandInfo(
            name="progress",
            category=CommandCategory.ANALYTICS,
            syntax="python -m flashgenie progress DECK_NAME [--timeframe DAYS]",
            description="Show learning progress over time with charts",
            examples=[
                'python -m flashgenie progress "Spanish Vocabulary"',
                'python -m flashgenie progress "Math" --timeframe 30'
            ],
            related_commands=["stats", "analytics"]
        )
        
        # Accessibility Commands
        commands["accessibility"] = CommandInfo(
            name="accessibility",
            category=CommandCategory.ACCESSIBILITY,
            syntax="python -m flashgenie accessibility [--enable MODE] [--disable MODE] [--status]",
            description="Configure accessibility features (screen reader, high contrast, audio)",
            examples=[
                "python -m flashgenie accessibility --status",
                "python -m flashgenie accessibility --enable high_contrast",
                "python -m flashgenie accessibility --enable screen_reader"
            ],
            aliases=["a11y"],
            related_commands=["config", "settings"]
        )
        
        # Developer Commands
        commands["debug"] = CommandInfo(
            name="debug",
            category=CommandCategory.DEVELOPER,
            syntax="python -m flashgenie debug [--enable] [--disable] [--console]",
            description="Enable debug mode with performance monitoring and console",
            examples=[
                "python -m flashgenie debug --enable",
                "python -m flashgenie debug --console",
                "python -m flashgenie debug --disable"
            ],
            permissions="developer",
            related_commands=["performance", "profile"]
        )
        
        commands["performance"] = CommandInfo(
            name="performance",
            category=CommandCategory.PERFORMANCE,
            syntax="python -m flashgenie performance [--dashboard] [--optimize] [--monitor]",
            description="Performance monitoring, optimization, and dashboard",
            examples=[
                "python -m flashgenie performance --dashboard",
                "python -m flashgenie performance --optimize",
                "python -m flashgenie performance --monitor"
            ],
            permissions="developer",
            related_commands=["debug", "profile"]
        )
        
        commands["profile"] = CommandInfo(
            name="profile",
            category=CommandCategory.DEVELOPER,
            syntax="python -m flashgenie profile COMMAND [--output FILE]",
            description="Profile command execution for performance analysis",
            examples=[
                'python -m flashgenie profile quiz "Test Deck"',
                'python -m flashgenie profile import deck.csv --output profile.json'
            ],
            permissions="developer",
            related_commands=["debug", "performance"]
        )
        
        return commands
    
    def _organize_by_category(self) -> Dict[CommandCategory, List[CommandInfo]]:
        """Organize commands by category."""
        categories = {}
        for category in CommandCategory:
            categories[category] = []
        
        for command in self.commands.values():
            categories[command.category].append(command)
        
        return categories
    
    def show_main_help(self) -> None:
        """Show the main help menu with Rich formatting."""
        # Welcome header
        welcome_text = Text()
        welcome_text.append("🧞‍♂️ FlashGenie v1.8.4 - Command Reference", style="bold bright_blue")
        
        welcome_panel = Panel(
            welcome_text,
            title="Welcome to FlashGenie",
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(welcome_panel)
        
        # Quick start section
        quick_start = self._create_quick_start_section()
        self.console.print(quick_start)
        
        # Command categories
        categories_panel = self._create_categories_overview()
        self.console.print(categories_panel)
        
        # Usage tips
        tips_panel = self._create_usage_tips()
        self.console.print(tips_panel)
    
    def _create_quick_start_section(self) -> Panel:
        """Create quick start section."""
        content = []
        
        content.append(Text("🚀 Quick Start Commands", style="bold bright_green"))
        content.append(Text(""))
        
        quick_commands = [
            ("Get help", "python -m flashgenie help"),
            ("List decks", "python -m flashgenie list"),
            ("Import deck", 'python -m flashgenie import deck.csv --name "My Deck"'),
            ("Start quiz", 'python -m flashgenie quiz "My Deck"'),
            ("View stats", "python -m flashgenie stats")
        ]
        
        for desc, cmd in quick_commands:
            line = Text()
            line.append(f"  {desc}: ", style="bright_white")
            line.append(cmd, style="bright_cyan")
            content.append(line)
        
        return Panel(
            Group(*content),
            title="🚀 Quick Start",
            border_style="bright_green",
            padding=(1, 2)
        )
    
    def _create_categories_overview(self) -> Panel:
        """Create command categories overview."""
        content = []
        
        content.append(Text("📋 Command Categories", style="bold bright_yellow"))
        content.append(Text(""))
        
        category_info = {
            CommandCategory.BASIC: ("🔰", "Basic Commands", "help, version, info"),
            CommandCategory.DECK_MANAGEMENT: ("📚", "Deck Management", "list, create, delete"),
            CommandCategory.IMPORT_EXPORT: ("📁", "Import/Export", "import, export, backup"),
            CommandCategory.STUDY_SESSION: ("🎯", "Study Sessions", "quiz, review, practice"),
            CommandCategory.ANALYTICS: ("📊", "Analytics", "stats, progress, reports"),
            CommandCategory.ACCESSIBILITY: ("♿", "Accessibility", "accessibility, a11y"),
            CommandCategory.DEVELOPER: ("🔧", "Developer Tools", "debug, profile, test"),
            CommandCategory.PERFORMANCE: ("⚡", "Performance", "performance, optimize, monitor")
        }
        
        for category, (icon, name, commands) in category_info.items():
            if self.categories[category]:  # Only show categories with commands
                line = Text()
                line.append(f"  {icon} ", style="bright_white")
                line.append(f"{name}: ", style="bold bright_white")
                line.append(commands, style="bright_cyan")
                content.append(line)
        
        content.append(Text(""))
        content.append(Text("💡 Use 'python -m flashgenie help CATEGORY' for category details", style="dim"))
        content.append(Text("🔍 Use 'python -m flashgenie search TERM' to search commands", style="dim"))
        
        return Panel(
            Group(*content),
            title="📋 Command Categories",
            border_style="bright_yellow",
            padding=(1, 2)
        )
    
    def _create_usage_tips(self) -> Panel:
        """Create usage tips section."""
        content = []
        
        content.append(Text("💡 Usage Tips", style="bold bright_magenta"))
        content.append(Text(""))
        
        tips = [
            "All commands support --help for detailed information",
            "Use Tab completion for command and file names",
            "Rich Terminal UI provides beautiful, accessible output",
            "Enable accessibility features with 'accessibility --enable'",
            "Monitor performance with 'performance --dashboard'",
            "Search commands with 'search TERM' for quick reference"
        ]
        
        for tip in tips:
            content.append(Text(f"  • {tip}", style="bright_white"))
        
        return Panel(
            Group(*content),
            title="💡 Usage Tips",
            border_style="bright_magenta",
            padding=(1, 2)
        )
    
    def show_command_help(self, command_name: str) -> None:
        """Show detailed help for a specific command."""
        if command_name not in self.commands:
            self._show_command_not_found(command_name)
            return
        
        cmd = self.commands[command_name]
        self._display_command_details(cmd)
    
    def _display_command_details(self, cmd: CommandInfo) -> None:
        """Display detailed information about a command."""
        # Command header
        header_text = Text()
        header_text.append(f"🔧 {cmd.name}", style="bold bright_blue")
        if cmd.aliases:
            header_text.append(f" (aliases: {', '.join(cmd.aliases)})", style="dim")
        
        # Main info
        content = []
        content.append(header_text)
        content.append(Text(""))
        content.append(Text(cmd.description, style="bright_white"))
        content.append(Text(""))
        
        # Syntax
        content.append(Text("📝 Syntax:", style="bold bright_green"))
        content.append(Text(f"  {cmd.syntax}", style="bright_cyan"))
        content.append(Text(""))
        
        # Examples
        if cmd.examples:
            content.append(Text("💡 Examples:", style="bold bright_yellow"))
            for example in cmd.examples:
                content.append(Text(f"  {example}", style="bright_cyan"))
            content.append(Text(""))
        
        # Related commands
        if cmd.related_commands:
            content.append(Text("🔗 Related Commands:", style="bold bright_magenta"))
            related_text = Text("  ")
            for i, related in enumerate(cmd.related_commands):
                if i > 0:
                    related_text.append(", ")
                related_text.append(related, style="bright_cyan")
            content.append(related_text)
        
        panel = Panel(
            Group(*content),
            title=f"Command: {cmd.name}",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def _show_command_not_found(self, command_name: str) -> None:
        """Show command not found message with suggestions."""
        content = []
        content.append(Text(f"❌ Command '{command_name}' not found", style="bold bright_red"))
        content.append(Text(""))
        
        # Find similar commands
        similar = self._find_similar_commands(command_name)
        if similar:
            content.append(Text("💡 Did you mean:", style="bright_yellow"))
            for cmd in similar[:3]:  # Show top 3 matches
                content.append(Text(f"  • {cmd}", style="bright_cyan"))
            content.append(Text(""))
        
        content.append(Text("Use 'python -m flashgenie help' to see all commands", style="dim"))
        
        panel = Panel(
            Group(*content),
            title="Command Not Found",
            border_style="bright_red",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def _find_similar_commands(self, query: str) -> List[str]:
        """Find commands similar to the query."""
        from difflib import SequenceMatcher
        
        similarities = []
        for cmd_name in self.commands.keys():
            ratio = SequenceMatcher(None, query.lower(), cmd_name.lower()).ratio()
            if ratio > 0.3:  # Threshold for similarity
                similarities.append((ratio, cmd_name))
        
        # Sort by similarity and return command names
        similarities.sort(reverse=True)
        return [cmd for _, cmd in similarities]
    
    def search_commands(self, query: str) -> None:
        """Search commands by name, description, or examples."""
        matches = []
        query_lower = query.lower()
        
        for cmd in self.commands.values():
            # Search in name, description, and examples
            if (query_lower in cmd.name.lower() or
                query_lower in cmd.description.lower() or
                any(query_lower in example.lower() for example in cmd.examples)):
                matches.append(cmd)
        
        if not matches:
            self._show_no_search_results(query)
            return
        
        self._display_search_results(query, matches)
    
    def _display_search_results(self, query: str, matches: List[CommandInfo]) -> None:
        """Display search results."""
        content = []
        content.append(Text(f"🔍 Search Results for '{query}'", style="bold bright_blue"))
        content.append(Text(f"Found {len(matches)} matching commands", style="dim"))
        content.append(Text(""))
        
        for cmd in matches:
            # Command name and category
            line = Text()
            line.append(f"  🔧 {cmd.name}", style="bold bright_cyan")
            line.append(f" ({cmd.category.value})", style="dim")
            content.append(line)
            
            # Description
            content.append(Text(f"     {cmd.description}", style="bright_white"))
            content.append(Text(""))
        
        content.append(Text("💡 Use 'help COMMAND' for detailed information", style="dim"))
        
        panel = Panel(
            Group(*content),
            title=f"Search Results: {query}",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def _show_no_search_results(self, query: str) -> None:
        """Show no search results message."""
        content = []
        content.append(Text(f"🔍 No results found for '{query}'", style="bold bright_yellow"))
        content.append(Text(""))
        content.append(Text("💡 Try:", style="bright_white"))
        content.append(Text("  • Using different keywords", style="dim"))
        content.append(Text("  • Checking spelling", style="dim"))
        content.append(Text("  • Using 'help' to see all commands", style="dim"))
        
        panel = Panel(
            Group(*content),
            title="No Search Results",
            border_style="bright_yellow",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def show_category_help(self, category_name: str) -> None:
        """Show help for a specific category."""
        try:
            category = CommandCategory(category_name.lower())
        except ValueError:
            self._show_category_not_found(category_name)
            return
        
        commands_in_category = self.categories[category]
        if not commands_in_category:
            self._show_empty_category(category_name)
            return
        
        self._display_category_commands(category, commands_in_category)
    
    def _display_category_commands(self, category: CommandCategory, commands: List[CommandInfo]) -> None:
        """Display all commands in a category."""
        category_names = {
            CommandCategory.BASIC: ("🔰", "Basic Commands"),
            CommandCategory.DECK_MANAGEMENT: ("📚", "Deck Management"),
            CommandCategory.IMPORT_EXPORT: ("📁", "Import/Export"),
            CommandCategory.STUDY_SESSION: ("🎯", "Study Sessions"),
            CommandCategory.ANALYTICS: ("📊", "Analytics"),
            CommandCategory.ACCESSIBILITY: ("♿", "Accessibility"),
            CommandCategory.DEVELOPER: ("🔧", "Developer Tools"),
            CommandCategory.PERFORMANCE: ("⚡", "Performance")
        }
        
        icon, name = category_names[category]
        
        content = []
        content.append(Text(f"{icon} {name}", style="bold bright_blue"))
        content.append(Text(""))
        
        for cmd in commands:
            # Command name and syntax
            content.append(Text(f"🔧 {cmd.name}", style="bold bright_cyan"))
            content.append(Text(f"   {cmd.description}", style="bright_white"))
            content.append(Text(f"   Syntax: {cmd.syntax}", style="dim"))
            if cmd.aliases:
                content.append(Text(f"   Aliases: {', '.join(cmd.aliases)}", style="dim"))
            content.append(Text(""))
        
        content.append(Text("💡 Use 'help COMMAND' for detailed information", style="dim"))
        
        panel = Panel(
            Group(*content),
            title=f"{icon} {name}",
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def _show_category_not_found(self, category_name: str) -> None:
        """Show category not found message."""
        content = []
        content.append(Text(f"❌ Category '{category_name}' not found", style="bold bright_red"))
        content.append(Text(""))
        content.append(Text("Available categories:", style="bright_white"))
        
        for category in CommandCategory:
            content.append(Text(f"  • {category.value}", style="bright_cyan"))
        
        panel = Panel(
            Group(*content),
            title="Category Not Found",
            border_style="bright_red",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def _show_empty_category(self, category_name: str) -> None:
        """Show empty category message."""
        content = []
        content.append(Text(f"📭 No commands found in category '{category_name}'", style="bold bright_yellow"))
        content.append(Text(""))
        content.append(Text("Use 'help' to see all available commands", style="dim"))
        
        panel = Panel(
            Group(*content),
            title="Empty Category",
            border_style="bright_yellow",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    def get_contextual_help(self, context: str) -> List[str]:
        """Get contextual help suggestions based on current task."""
        context_mappings = {
            "import": ["import", "create", "list"],
            "study": ["quiz", "review", "stats"],
            "export": ["export", "backup", "stats"],
            "debug": ["debug", "performance", "profile"],
            "accessibility": ["accessibility", "help"],
            "new_user": ["help", "list", "import", "quiz"]
        }

        return context_mappings.get(context, ["help", "list"])

    def show_contextual_help(self, context: str) -> None:
        """Show contextual help based on current task."""
        suggestions = self.get_contextual_help(context)

        content = []
        content.append(Text(f"💡 Contextual Help for '{context}'", style="bold bright_blue"))
        content.append(Text(""))

        content.append(Text("Suggested commands:", style="bright_white"))
        for cmd_name in suggestions:
            if cmd_name in self.commands:
                cmd = self.commands[cmd_name]
                line = Text()
                line.append(f"  🔧 {cmd.name}: ", style="bold bright_cyan")
                line.append(cmd.description, style="bright_white")
                content.append(line)

        content.append(Text(""))
        content.append(Text("💡 Use 'help COMMAND' for detailed information", style="dim"))

        panel = Panel(
            Group(*content),
            title=f"💡 Contextual Help: {context}",
            border_style="bright_blue",
            padding=(1, 2)
        )

        self.console.print(panel)

    def show_interactive_help_menu(self) -> None:
        """Show an interactive help menu with navigation."""
        from rich.prompt import Prompt

        while True:
            self.console.clear()
            self.show_main_help()

            self.console.print()
            choice = Prompt.ask(
                "Enter command name, category, or 'q' to quit",
                default="q"
            )

            if choice.lower() in ['q', 'quit', 'exit']:
                break
            elif choice in self.commands:
                self.show_command_help(choice)
                Prompt.ask("Press Enter to continue", default="")
            elif choice in [cat.value for cat in CommandCategory]:
                self.show_category_help(choice)
                Prompt.ask("Press Enter to continue", default="")
            elif choice:
                self.search_commands(choice)
                Prompt.ask("Press Enter to continue", default="")

    def create_command_tree(self) -> Tree:
        """Create a tree view of all commands organized by category."""
        tree = Tree("📋 FlashGenie Commands", style="bold bright_blue")

        category_names = {
            CommandCategory.BASIC: ("🔰", "Basic Commands"),
            CommandCategory.DECK_MANAGEMENT: ("📚", "Deck Management"),
            CommandCategory.IMPORT_EXPORT: ("📁", "Import/Export"),
            CommandCategory.STUDY_SESSION: ("🎯", "Study Sessions"),
            CommandCategory.ANALYTICS: ("📊", "Analytics"),
            CommandCategory.ACCESSIBILITY: ("♿", "Accessibility"),
            CommandCategory.DEVELOPER: ("🔧", "Developer Tools"),
            CommandCategory.PERFORMANCE: ("⚡", "Performance")
        }

        for category, commands in self.categories.items():
            if commands:  # Only show categories with commands
                icon, name = category_names[category]
                category_branch = tree.add(f"{icon} {name}", style="bold bright_yellow")

                for cmd in commands:
                    cmd_text = f"🔧 {cmd.name}"
                    if cmd.aliases:
                        cmd_text += f" ({', '.join(cmd.aliases)})"
                    category_branch.add(cmd_text, style="bright_cyan")

        return tree

    def show_command_tree(self) -> None:
        """Display the command tree."""
        tree = self.create_command_tree()

        panel = Panel(
            tree,
            title="📋 Command Tree",
            border_style="bright_blue",
            padding=(1, 2)
        )

        self.console.print(panel)
