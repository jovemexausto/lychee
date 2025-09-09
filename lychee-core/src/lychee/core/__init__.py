"""Lychee - A polyglot monorepo manager with schema-driven development."""

__version__ = "0.1.1"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .config.models import *
from .languages.adapter import LanguageAdapter
from .project import LycheeProject
from .service import LycheeService
