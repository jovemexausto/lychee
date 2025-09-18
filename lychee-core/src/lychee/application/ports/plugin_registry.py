from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from .language_runtime import LanguageRuntimePort
from .schema_compiler import SchemaCompilerPort


class PluginRegistryPort(ABC):
    """Port for discovering and retrieving plugins (language runtimes, compilers, etc.)."""

    @abstractmethod
    def get_language_runtime(self, language: str) -> Optional[LanguageRuntimePort]:  # noqa: D401
        """Return a language runtime plugin for the given language, if any."""

    @abstractmethod
    def get_schema_compiler(self, schema_format: str, language: str) -> Optional[SchemaCompilerPort]:  # noqa: E501
        """Return a schema compiler that supports the given (format -> language) pair."""

    @abstractmethod
    def list_language_runtimes(self) -> Iterable[LanguageRuntimePort]:  # noqa: D401
        """List all available language runtime plugins."""

    @abstractmethod
    def list_schema_compilers(self) -> Iterable[SchemaCompilerPort]:  # noqa: D401
        """List all available schema compiler plugins."""
