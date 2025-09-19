from __future__ import annotations

from pathlib import Path
from typing import Optional

from lychee.application.ports.config_repository import ConfigRepositoryPort
from lychee.application.ports.project_repository import ProjectRepositoryPort
from lychee.application.ports.symlink_manager import SymlinkManagerPort
from lychee.infrastructure.config.yaml_config_repository import YamlConfigRepository
from lychee.infrastructure.project.project_repository import ProjectRepository
from lychee.infrastructure.plugins.entrypoint_registry import EntryPointPluginRegistry
from lychee.infrastructure.fs.symlink_manager import FSSymlinkManager
from lychee.core.utils.logging import get_logger

logger = get_logger(__name__)


class GenerateSchemasUseCase:
    """
    Application use-case to compile schemas for all configured languages and mount them
    into each service's configured schemas.mount_dir.
    """

    def __init__(
        self,
        config_repo: Optional[ConfigRepositoryPort] = None,
        project_repo: Optional[ProjectRepositoryPort] = None,
        symlinks: Optional[SymlinkManagerPort] = None,
    ) -> None:
        self._config_repo = config_repo or YamlConfigRepository()
        self._project_repo = project_repo or ProjectRepository()
        self._symlinks = symlinks or FSSymlinkManager()

    async def run(self, root: Path) -> None:
        cfg = self._config_repo.load(root)
        registry = EntryPointPluginRegistry.from_config(cfg, include_builtins=True)
        project = self._project_repo.build(cfg, root)

        schemas_cfg = getattr(cfg, "schemas", None)
        schemas_dir = root / getattr(schemas_cfg, "dir", "schemas")
        output_path = root / getattr(schemas_cfg, "output_path", "generated/schemas")
        schema_format = getattr(schemas_cfg, "format", "json_schema")

        # Compile for each schema file
        for schema_file in sorted(schemas_dir.glob("*.schema.json")):
            try:
                for language in project.languages:
                    compiler = registry.get_schema_compiler(schema_format, language)
                    if not compiler:
                        logger.warning(
                            f"No schema compiler for format={schema_format} -> language={language}"
                        )
                        continue
                    out_dir = output_path / language
                    out_dir.mkdir(parents=True, exist_ok=True)
                    await compiler.compile(
                        schema_path=schema_file,
                        output_dir=out_dir,
                        project_path=root,
                        options=None,
                    )
                logger.info(f"Generated types for schema: {schema_file.name}")
            except Exception as e:
                logger.error(f"Failed generating types for {schema_file.name}: {e}")

        # After generating, mount into services
        for name, service in project.services.items():
            if not service.schemas_mount_dir:
                continue
            language = service.language
            source = output_path / language
            target = service.path / service.schemas_mount_dir
            try:
                # Clean broken symlinks
                self._symlinks.remove_broken(service.path)
                # Ensure fresh symlink
                self._symlinks.ensure(source, target)
                logger.info(f"Schemas linked into {name}: {target} -> {source}")
            except Exception as e:
                logger.error(f"Failed to mount schemas into {name}: {e}")

        logger.info("Schema generation and mounting completed.")
