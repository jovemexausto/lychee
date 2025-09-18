from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict


class SchemaCompilerPort(ABC):
    """Port for compiling schemas into language-specific types."""

    @abstractmethod
    def supports(self, schema_format: str, target_language: str) -> bool:  # noqa: D401
        """Return True if the compiler supports the (format -> language) pair."""

    @abstractmethod
    async def compile(
        self,
        schema_path: Path,
        output_dir: Path,
        project_path: Path,
        options: Dict | None = None,
    ) -> None:  # noqa: D401
        """Compile schema into types at the given output_dir."""
