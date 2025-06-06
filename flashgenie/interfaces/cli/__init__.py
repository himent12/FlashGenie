"""
Command-line interface for FlashGenie.

This package provides terminal-based user interface components
for interacting with FlashGenie through the command line.
"""

from flashgenie.interfaces.cli.terminal_ui import TerminalUI
from flashgenie.interfaces.cli.commands import CommandHandler
from flashgenie.interfaces.cli.formatters import OutputFormatter

__all__ = ["TerminalUI", "CommandHandler", "OutputFormatter"]
