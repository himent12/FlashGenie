"""
Command dispatcher for FlashGenie CLI.

This module routes CLI commands to their appropriate handlers.
"""

from flashgenie.interfaces.cli.handlers.core_handlers import (
    handle_help_command,
    handle_search_command,
    handle_accessibility_command,
    handle_debug_command,
    handle_performance_command,
    handle_import_command,
    handle_quiz_command,
    handle_list_command,
    handle_stats_command,
    handle_export_command
)

from flashgenie.interfaces.cli.handlers.advanced_handlers import (
    handle_plan_command,
    handle_velocity_command,
    handle_graph_command,
    handle_achievements_command,
    handle_suggest_command
)

from flashgenie.interfaces.cli.handlers.plugin_handlers import (
    handle_plugins_command,
    handle_pdk_command,
    handle_marketplace_command
)


class CommandDispatcher:
    """Dispatches CLI commands to appropriate handlers."""
    
    def __init__(self):
        """Initialize the command dispatcher."""
        self.command_map = {
            # Help and utility commands
            'help': handle_help_command,
            'search': handle_search_command,
            'accessibility': handle_accessibility_command,
            'debug': handle_debug_command,
            'performance': handle_performance_command,

            # Core commands
            'import': handle_import_command,
            'quiz': handle_quiz_command,
            'list': handle_list_command,
            'stats': handle_stats_command,
            'export': handle_export_command,
            
            # Advanced learning commands
            'plan': handle_plan_command,
            'velocity': handle_velocity_command,
            'graph': handle_graph_command,
            'achievements': handle_achievements_command,
            'suggest': handle_suggest_command,
            
            # Plugin system commands
            'plugins': handle_plugins_command,
            'pdk': handle_pdk_command,
            'marketplace': handle_marketplace_command,
        }
    
    def dispatch(self, command: str, args) -> None:
        """
        Dispatch a command to its appropriate handler.
        
        Args:
            command: The command name
            args: Parsed command arguments
        """
        if command in self.command_map:
            handler = self.command_map[command]
            handler(args)
        else:
            # No command specified, start interactive mode
            self._start_interactive_mode()
    
    def _start_interactive_mode(self) -> None:
        """Start the interactive terminal UI."""
        from flashgenie.interfaces.cli.terminal_ui import TerminalUI
        
        print("🧞‍♂️ Welcome to FlashGenie!")
        print("Starting interactive mode...")
        print("Type 'help' for available commands or 'quit' to exit.")
        print("=" * 50)
        
        ui = TerminalUI()
        ui.start()
    
    def get_available_commands(self) -> list:
        """Get list of available commands."""
        return list(self.command_map.keys())
    
    def is_valid_command(self, command: str) -> bool:
        """Check if a command is valid."""
        return command in self.command_map
