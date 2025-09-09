"""
Middleware for handling and logging command-line errors.
"""

import functools
import sys

import asyncclick as click

from monorepo.utils.logging import get_logger


def handle_errors(func):
    """
    A decorator that wraps a CLI command to handle exceptions gracefully.
    It logs the full traceback and prints a user-friendly error message.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger("lychee")
        try:
            return func(*args, **kwargs)
        except click.ClickException as e:
            # Click exceptions are handled by Click, so just re-raise
            raise e
        except KeyboardInterrupt:
            logger.print("\n[yellow]Operation cancelled by user[/yellow]")
            sys.exit(1)
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            sys.exit(1)

    return wrapper
