from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol

# We intentionally don't import Pydantic models here in the port.
# The concrete adapter may return a concrete DTO type; the project repository
# adapter will know how to map that DTO into domain models.


class ConfigDTO(Protocol):
    ...


class ConfigRepositoryPort(ABC):
    """Port to load monorepo configuration from disk (e.g., lychee.yaml)."""

    @abstractmethod
    def load(self, root: Path) -> ConfigDTO:  # noqa: D401
        """Load the configuration DTO from the given root directory."""
