from __future__ import annotations

from abc import ABC, abstractmethod

from lychee.domain.project import Project
from .config_repository import ConfigDTO
from pathlib import Path


class ProjectRepositoryPort(ABC):
    """Port to construct a domain Project from a configuration DTO."""

    @abstractmethod
    def build(self, config: ConfigDTO, root: Path) -> Project:  # noqa: D401
        """Build a Project aggregate from the loaded configuration DTO."""
