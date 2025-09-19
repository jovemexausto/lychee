from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from lychee.application.services.runtime_orchestrator import runtime_orchestrator
from lychee.application.ports.config_repository import ConfigRepositoryPort
from lychee.application.ports.project_repository import ProjectRepositoryPort
from lychee.infrastructure.config.yaml_config_repository import YamlConfigRepository
from lychee.infrastructure.project.project_repository import ProjectRepository
from lychee.infrastructure.plugins.entrypoint_registry import EntryPointPluginRegistry
from lychee.core.utils.logging import get_logger

logger = get_logger(__name__)


class StartDevServerUseCase:
    """Start services in dependency order using runtime plugins."""

    def __init__(
        self,
        config_repo: Optional[ConfigRepositoryPort] = None,
        project_repo: Optional[ProjectRepositoryPort] = None,
    ) -> None:
        self._config_repo = config_repo or YamlConfigRepository()
        self._project_repo = project_repo or ProjectRepository()

    async def run(
        self,
        root: Path,
        services: Optional[List[str]] = None,
        mode: str = "hybrid",
        enable_proxy: bool = False,
        enable_dashboard: bool = False,
    ) -> None:
        cfg = self._config_repo.load(root)
        registry = EntryPointPluginRegistry.from_config(cfg, include_builtins=True)
        project = self._project_repo.build(cfg, root)

        # Compute start order
        order = project.topo_order()
        if services:
            # Filter to subset but preserve topo order
            want = {s for s in services}
            order = [s for s in order if s in want]

        # Map service name -> runtime
        runtime_by_service: Dict[str, Any] = {}
        for name in order:
            svc = project.get_service(name)
            runtime = registry.get_language_runtime(svc.language)
            if not runtime:
                logger.error(f"No runtime for language={svc.language} (service {name})")
                continue
            runtime_by_service[name] = runtime

        # Start sequentially (maintain current behavior); parallelization could be added later
        for name in order:
            svc = project.get_service(name)
            runtime = runtime_by_service.get(name)
            if not runtime:
                continue
            env = self._build_env(cfg, svc)
            try:
                # Ensure environment & dependencies are ready
                await runtime.install(str(svc.path), {
                    "type": svc.language,
                    "path": str(svc.path),
                    "framework": svc.framework,
                    "runtime": {
                        "port": svc.runtime.port,
                        "entry_point": svc.runtime.entry_point,
                        **svc.runtime.version_info,
                    },
                })
                await runtime_orchestrator.start_service(svc, runtime, env)
                logger.info(f"Started service '{name}'")
            except Exception as e:
                logger.error(f"Failed to start service '{name}': {e}")

        # Optionally block forever to keep process open when used from CLI
        if enable_dashboard or enable_proxy:
            await asyncio.Future()

    def _build_env(self, cfg, svc) -> Dict[str, str]:
        env = os.environ.copy()
        proj_env = getattr(cfg, "environment", None) or {}
        env.update(proj_env)
        env.update(svc.environment or {})
        return env
