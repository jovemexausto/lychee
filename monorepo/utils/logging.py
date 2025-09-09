import datetime
import os
import re
from typing import Any, Dict

from rich.console import Console
from rich.panel import Panel
from rich.pretty import pprint
from rich.table import Table
from rich.traceback import install as install_rich_tracebacks

# Singleton Rich Console instance
_console = Console(record=True, highlight=True, force_terminal=True)

# Log level priorities for filtering
LOG_LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}


class RichLogger:
    """
    A unified API for console output using the Rich library with proper level filtering.
    """

    def __init__(self, name: str = "__main__", level: str = "INFO"):
        """
        Initializes the logger with console output.

        Args:
            name (str): Logger name for identification
            level (str): Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.level = level.upper()
        self.level_value = LOG_LEVELS.get(self.level, 20)  # Default to INFO
        self._console = _console

        # Install rich tracebacks
        install_rich_tracebacks(show_locals=True, word_wrap=True, max_frames=25)

    def mask_path_relative_to_pwd(self, text, keep_segments=3):
        # Get current working directory
        cwd = os.getcwd()

        path_pattern = r"(?<!\[)(/(?:[^/\s:]+/)*[^/\s:]*)"

        if len(text.split("/")) <= 3:
            return text

        def shorten_path(match):
            full_path = match.group(1)  # Group 1 captures the path itself

            # If path starts with cwd, make it relative
            if full_path.startswith(cwd):
                rel_path = os.path.relpath(full_path, cwd)
            else:
                rel_path = full_path

            parts = rel_path.strip("/").split("/")
            if len(parts) > keep_segments:
                shortened = "/".join(parts[-keep_segments:])
            else:
                shortened = rel_path.strip("/")  # Keep the full relative path if it's short

            # Add the ... prefix only if we actually shortened it
            if len(parts) > keep_segments:
                return f".../{shortened}"
            else:
                return shortened  # Return as is if it wasn't shortened

        # Replace all paths in the string
        masked_text = re.sub(path_pattern, shorten_path, text)
        return masked_text

    def log(self, message: Any, level: str = "INFO", **kwargs: Any) -> None:
        """
        Logs to console if the level is sufficient.

        Args:
            message (Any): Message or Rich object to log
            level (str): Logging level
            kwargs (Any): Additional kwargs for rich.console.Console.print
        """
        level_upper = level.upper()
        level_value = LOG_LEVELS.get(level_upper, 20)  # Default to INFO

        # Skip logging if level is below minimum
        if level_value < self.level_value:
            return

        timestamp = datetime.datetime.now().strftime("%H:%M:%S").center(10)

        # Console output with Rich formatting
        level_colors = {"DEBUG": "blue", "INFO": "green", "WARNING": "yellow", "ERROR": "red", "CRITICAL": "bold red"}
        color = level_colors.get(level_upper, "white")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S").center(10)
        level_str = level.lower().center(10)
        title = ("lychee" if "monorepo" in self.name else self.name).center(10)

        if len(title) > 15:
            title = title[:15] + " ..."
            title = title.rjust(20)

        # Novo formato do prefixo
        prefix = f"[{color}]" f"|{timestamp}" f"|{level_str}" f"|{title}" f"|[/{color}]"

        console_message = message
        if isinstance(message, str):
            console_message = self.mask_path_relative_to_pwd(message)

        # Console output
        if self._console.is_terminal:
            if isinstance(console_message, str):
                self._console.print(f"{prefix} {console_message}", **kwargs)
            else:
                self._console.print(console_message, **kwargs)

    def debug(self, message: Any, **kwargs: Any) -> None:
        """Logs a DEBUG message if level permits."""
        self.log(message, level="DEBUG", **kwargs)

    def info(self, message: Any, **kwargs: Any) -> None:
        """Logs an INFO message if level permits."""
        self.log(message, level="INFO", **kwargs)

    def warning(self, message: Any, **kwargs: Any) -> None:
        """Logs a WARNING message if level permits."""
        self.log(message, level="WARNING", **kwargs)

    def error(self, message: Any, **kwargs: Any) -> None:
        """Logs an ERROR message if level permits."""
        self.log(message, level="ERROR", **kwargs)

    def critical(self, message: Any, **kwargs: Any) -> None:
        """Logs a CRITICAL message if level permits."""
        self.log(message, level="CRITICAL", **kwargs)

    def exception(self, message: Any, **kwargs: Any) -> None:
        """Logs an exception if level permits."""
        if LOG_LEVELS["ERROR"] >= self.level_value:
            self.log(message, level="ERROR", **kwargs)

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Prints directly to console if INFO level permits."""
        if LOG_LEVELS["INFO"] >= self.level_value:
            self._console.print(*args, **kwargs)

    def rule(self, title: str = "", **kwargs: Any) -> None:
        """Draws a horizontal rule to console if INFO level permits."""
        if LOG_LEVELS["INFO"] >= self.level_value:
            self._console.rule(title, **kwargs)

    def table(self, table_obj: Table) -> None:
        """Prints a Rich Table to console if INFO level permits."""
        if LOG_LEVELS["INFO"] >= self.level_value:
            self._console.print(table_obj)

    def panel(self, panel_obj: Panel) -> None:
        """Prints a Rich Panel to console if INFO level permits."""
        if LOG_LEVELS["INFO"] >= self.level_value:
            self._console.print(panel_obj)

    def pprint(self, obj: Any) -> None:
        """Pretty-prints to console if INFO level permits."""
        if LOG_LEVELS["INFO"] >= self.level_value:
            pprint(obj, console=self._console)


_loggers: Dict[str, RichLogger] = {}


def get_logger(name: str, level: str = "INFO") -> RichLogger:
    """
    Returns a RichLogger instance for the specified name.

    Args:
        name (str): Logger name
        level (str): Minimum logging level

    Returns:
        RichLogger: Configured logger instance
    """
    if name not in _loggers:
        _loggers[name] = RichLogger(name, level)
    return _loggers[name]
