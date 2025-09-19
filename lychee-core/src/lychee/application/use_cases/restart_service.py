from __future__ import annotations

import os
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


class RestartServiceUseCase:
    def __init__(
        self,
        config_repo: Optional[ConfigRepositoryPort] = None,
        project_repo: Optional[ProjectRepositoryPort] = None,
    ) -> None:
        self._config_repo = config_repo or YamlConfigRepository()
        self._project_repo = project_repo or ProjectRepository()

    async def run(self, root: Path, service_name: str) -> None:
        cfg = self._config_repo.load(root)
        registry = EntryPointPluginRegistry.from_config(cfg, include_builtins=True)
        project = self._project_repo.build(cfg, root)
        svc = project.get_service(service_name)
        runtime = registry.get_language_runtime(svc.language)
        if not runtime:
            raise RuntimeError(f"No runtime for language={svc.language} (service {service_name})")

        # Stop first if running
        handle = runtime_orchestrator.get_handle(service_name)
        if handle:
            await runtime_orchestrator.stop_service(service_name, runtime)

        env = self._build_env(cfg, svc)
        await runtime_orchestrator.start_service(svc, runtime, env)
        logger.info(f"Service '{service_name}' restarted")

    def _build_env(self, cfg, svc) -> Dict[str, str]:
        env = os.environ.copy()
        proj_env = getattr(cfg, "environment", None) or {}
        env.update(proj_env)
        env.update(svc.environment or {})
        return env
