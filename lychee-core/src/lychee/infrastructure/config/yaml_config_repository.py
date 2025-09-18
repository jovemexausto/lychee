from __future__ import annotations

from pathlib import Path

from lychee.application.ports.config_repository import ConfigDTO, ConfigRepositoryPort
from lychee.core.config.loader import ConfigLoader
from lychee.core.config.models import LycheeConfig


class YamlConfigRepository(ConfigRepositoryPort):
    """Loads Lychee configuration (lychee.yaml) as a DTO (LycheeConfig)."""

    def load(self, root: Path) -> ConfigDTO:
        config_path = (root / "lychee.yaml").resolve()
        loader = ConfigLoader(config_path)
        cfg: LycheeConfig = loader.load()
        return cfg
