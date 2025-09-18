from __future__ import annotations

from pathlib import Path
from typing import Dict

from lychee.application.ports.config_repository import ConfigDTO
from lychee.application.ports.project_repository import ProjectRepositoryPort
from lychee.domain.project import Project
from lychee.domain.service import Runtime, Service


class ProjectRepository(ProjectRepositoryPort):
    """Builds a domain Project aggregate from a LycheeConfig DTO."""

    def build(self, config: ConfigDTO, root: Path) -> Project:
        # Expecting `config` to be a `LycheeConfig` from core.config.models
        root = root.resolve()
        project = Project(root=root, languages=list(getattr(config.project, "languages", []) or []))

        services_cfg: Dict[str, any] = getattr(config, "services", {}) or {}
        for name, svc_cfg in services_cfg.items():
            # `svc_cfg` may be a Pydantic model; use getattr for safety
            rel = getattr(svc_cfg, "path", name)
            path = (root / rel).resolve()
            language = getattr(svc_cfg, "type", "")
            framework = getattr(svc_cfg, "framework", None)

            runtime_cfg = getattr(svc_cfg, "runtime", None)
            runtime = Runtime(
                port=getattr(runtime_cfg, "port", None) if runtime_cfg else None,
                entry_point=getattr(runtime_cfg, "entry_point", None) if runtime_cfg else None,
                version_info={
                    k: v
                    for k, v in {
                        "python_version": getattr(runtime_cfg, "python_version", None) if runtime_cfg else None,
                        "node_version": getattr(runtime_cfg, "node_version", None) if runtime_cfg else None,
                    }.items()
                    if v is not None
                },
            )

            deps_cfg = getattr(svc_cfg, "dependencies", None)
            depends_on_services = list(getattr(deps_cfg, "services", []) or [])
            depends_on_schemas = list(getattr(deps_cfg, "schemas", []) or [])

            schemas_cfg = getattr(svc_cfg, "schemas", None)
            schemas_mount_dir = getattr(schemas_cfg, "mount_dir", None) if schemas_cfg else None
            environment = dict(getattr(svc_cfg, "environment", {}) or {})

            service = Service(
                name=name,
                path=path,
                language=language,
                framework=framework,
                runtime=runtime,
                depends_on_services=depends_on_services,
                depends_on_schemas=depends_on_schemas,
                schemas_mount_dir=schemas_mount_dir,
                environment=environment,
            )
            project.add_service(service)

        return project
