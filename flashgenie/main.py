"""
Main entry point for FlashGenie application.

This module provides the main entry point and command-line interface
for the FlashGenie flashcard application.
"""

import sys
import logging
from pathlib import Path
from flashgenie import __version__

from flashgenie.interfaces.cli.argument_parser import create_argument_parser
from flashgenie.interfaces.cli.command_dispatcher import CommandDispatcher
from flashgenie.utils.logging_config import setup_logging
from flashgenie.utils.exceptions import (
    FlashGenieError, ConfigurationError, PluginError, SecurityError
)


def main():
    """Main entry point for the FlashGenie application."""
    logger = None

    try:
        # Parse command line arguments
        parser = create_argument_parser()
        args = parser.parse_args()

        # Setup logging
        log_level = 'DEBUG' if getattr(args, 'verbose', False) else getattr(args, 'log_level', 'INFO')
        setup_logging(log_level)
        logger = logging.getLogger(__name__)

        logger.info(f"Starting FlashGenie v{__version__}")
        logger.debug(f"Command: {getattr(args, 'command', 'unknown')}")

        # Validate environment
        _validate_environment()

        # Dispatch command to appropriate handler
        dispatcher = CommandDispatcher()
        dispatcher.dispatch(args.command, args)

        logger.info("FlashGenie completed successfully")

    except KeyboardInterrupt:
        print("\n👋 FlashGenie interrupted. Goodbye!")
        if logger:
            logger.info("Application interrupted by user")
        sys.exit(0)

    except ConfigurationError as e:
        print(f"⚙️ Configuration error: {e}")
        if logger:
            logger.error(f"Configuration error: {e}")
        sys.exit(2)

    except PluginError as e:
        print(f"🔌 Plugin error: {e}")
        if logger:
            logger.error(f"Plugin error: {e}")
        sys.exit(3)

    except SecurityError as e:
        print(f"🔒 Security error: {e}")
        if logger:
            logger.error(f"Security error: {e}")
        sys.exit(4)

    except FlashGenieError as e:
        print(f"❌ FlashGenie error: {e}")
        if logger:
            logger.error(f"FlashGenie error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        print("Please report this issue at: https://github.com/himent12/FlashGenie/issues")
        if logger:
            logger.exception("Unexpected error occurred")
        sys.exit(1)


def _validate_environment():
    """Validate the runtime environment."""
    # Check Python version
    if sys.version_info < (3, 8):
        raise ConfigurationError("Python 3.8 or higher is required")

    # Check for required directories
    from flashgenie.config import DATA_DIR, DECKS_DIR

    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        DECKS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise ConfigurationError(f"Cannot create required directories: {e}")


if __name__ == "__main__":
    main()
