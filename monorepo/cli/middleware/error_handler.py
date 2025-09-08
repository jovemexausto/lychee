"""
Middleware for handling and logging command-line errors.
"""

import functools
import sys

import asyncclick as click
from rich.console import Console

# Assumes that the rich console has been set up elsewhere, e.g., in cli.py
console = Console()


def handle_errors(func):
    """
    A decorator that wraps a CLI command to handle exceptions gracefully.
    It logs the full traceback and prints a user-friendly error message.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except click.ClickException as e:
            # Click exceptions are handled by Click, so just re-raise
            raise e
        except Exception as e:
            from monorepo.utils.logging import get_logger

            logger = get_logger("monorepo")

            logger.exception("An unexpected error occurred:")
            console.print(f"[red]Error: {e}[/red]")

            # Exit with a non-zero status code to indicate failure
            sys.exit(1)

    return wrapper
