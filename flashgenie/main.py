"""
Main entry point for FlashGenie application.

This module provides the main entry point and command-line interface
for the FlashGenie flashcard application.
"""

import sys
from flashgenie.interfaces.cli.argument_parser import create_argument_parser
from flashgenie.interfaces.cli.command_dispatcher import CommandDispatcher
from flashgenie.utils.logging_config import setup_logging
from flashgenie.utils.exceptions import FlashGenieError


def main():
    """Main entry point for the FlashGenie application."""
    try:
        # Parse command line arguments
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # Setup logging
        log_level = 'DEBUG' if args.verbose else args.log_level
        setup_logging(log_level)
        
        # Dispatch command to appropriate handler
        dispatcher = CommandDispatcher()
        dispatcher.dispatch(args.command, args)
        
    except KeyboardInterrupt:
        print("\n👋 FlashGenie interrupted. Goodbye!")
        sys.exit(0)
    except FlashGenieError as e:
        print(f"❌ FlashGenie error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        print("Please report this issue at: https://github.com/himent12/FlashGenie/issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
