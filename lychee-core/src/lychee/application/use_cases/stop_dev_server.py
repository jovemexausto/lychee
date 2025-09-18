from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from lychee.application.services.runtime_orchestrator import runtime_orchestrator
from lychee.application.ports.config_repository import ConfigRepositoryPort
from lychee.application.ports.project_repository import ProjectRepositoryPort
from lychee.infrastructure.config.yaml_config_repository import YamlConfigRepository
from lychee.infrastructure.project.project_repository import ProjectRepository
from lychee.infrastructure.plugins.entrypoint_registry import EntryPointPluginRegistry
from lychee.core.utils.logging import get_logger

logger = get_logger(__name__)


class StopDevServerUseCase:
    def __init__(
        self,
        config_repo: Optional[ConfigRepositoryPort] = None,
        project_repo: Optional[ProjectRepositoryPort] = None,
    ) -> None:
        self._config_repo = config_repo or YamlConfigRepository()
        self._project_repo = project_repo or ProjectRepository()

    async def run(self, root: Path) -> None:
        cfg = self._config_repo.load(root)
        registry = EntryPointPluginRegistry.from_config(cfg, include_builtins=True)
        project = self._project_repo.build(cfg)
        runtime_by_service: Dict[str, any] = {}
        for name, svc in project.services.items():
            rt = registry.get_language_runtime(svc.language)
            if rt:
                runtime_by_service[name] = rt
        await runtime_orchestrator.stop_all(runtime_by_service)
        logger.info("Development services stopped.")
