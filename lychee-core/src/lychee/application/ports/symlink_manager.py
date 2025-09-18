from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class SymlinkManagerPort(ABC):
    """Port for managing symlinks of generated artifacts into services."""

    @abstractmethod
    def ensure(self, source: Path, target: Path) -> None:  # noqa: D401
        """Ensure a symlink exists from target -> source (create or replace)."""

    @abstractmethod
    def remove_broken(self, root: Path) -> None:  # noqa: D401
        """Find and remove any broken symlinks under root."""
