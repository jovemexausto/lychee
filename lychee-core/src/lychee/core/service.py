import asyncio
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from lychee.core.config.models import ServiceConfig
from lychee.core.utils import get_logger
from lychee.infrastructure.plugins.entrypoint_registry import EntryPointPluginRegistry
from lychee.infrastructure.process.asyncio_manager import (
    AsyncioProcessManagerAdapter,
)
from lychee.application.ports.process_manager import ProcessHandle

if TYPE_CHECKING:
    from lychee.core.project import LycheeProject

logger = get_logger(__name__)


class LycheeService:
    """Represents a service in the monorepo with language adapter integration."""

    def __init__(
        self, name: str, path: Path, config: ServiceConfig, project: "LycheeProject"
    ):
        self.name = name
        self.path = path.resolve()
        self.config = config
        self.project = project
        # Ports and registry (honor allowlist from lychee.yaml if present)
        self._plugin_registry = EntryPointPluginRegistry.from_config(
            self.project.config, include_builtins=True
        )
        self._pm = AsyncioProcessManagerAdapter()
        self._runtime = self._create_language_runtime()
        self._process_handle: Optional[ProcessHandle] = None

    def _create_language_runtime(self):
        """Create language runtime plugin for this service."""
        runtime = self._plugin_registry.get_language_runtime(self.config.type)
        if not runtime:
            raise RuntimeError(f"No runtime plugin found for language: {self.config.type}")
        return runtime

    def get_process(self) -> Optional[asyncio.subprocess.Process]:
        """Get the subprocess object for the service (native from handle)."""
        return self._process_handle.native if self._process_handle else None

    def get_pid(self) -> Optional[int]:
        """Get the PID of the service process."""
        return self._process_handle.pid if self.is_running else None

    @property
    def is_running(self) -> bool:
        """Check if the service is currently running."""
        return self._pm.is_running(self._process_handle)

    @property
    def port(self) -> Optional[int]:
        """Get the port the service runs on."""
        return self.config.runtime.port if self.config.runtime else None

    async def start(self, mode: str = "native") -> None:
        """Start the service using language adapter."""
        if self.is_running:
            logger.warning(f"Service {self.name} is already running")
            return

        if mode == "docker":
            await self._start_docker()
        else:
            await self.install_dependencies()
            await self._start_native()

    async def stop(self) -> None:
        """Stop the service."""
        if self._process_handle:
            await self._runtime.stop(self._process_handle)
            self._process_handle = None

    async def restart(self, mode: str = "native") -> None:
        """Restart the service."""
        await self.stop()
        await self.start(mode)

    async def _start_native(self) -> None:
        """Start the service natively using language runtime plugin."""
        env = self._build_environment()
        handle = await self._runtime.start(
            service_path=str(self.path),
            service_config=self.config.model_dump(),
            env=env,
        )
        self._process_handle = handle
        logger.debug(
            f"Service {self.name} started with PID {handle.pid} using runtime {self.config.type}"
        )

    async def _start_docker(self) -> None:
        """Start the service using Docker."""
        raise NotImplementedError("Docker startup not yet implemented")

    def _build_environment(self) -> Dict[str, str]:
        """Build the environment variables for the service process."""
        env = os.environ.copy()
        # Set adapter's built-in env variables
        adapter_env = self._runtime.environment(str(self.path), self.config.model_dump())
        env.update(adapter_env)
        # Set global lychee.yml variables
        if self.project.config.environment:
            env.update(self.project.config.environment)
        # Set local service variables
        if self.config.environment:
            env.update(self.config.environment)
        return env

    async def install_dependencies(self) -> None:
        """Install service dependencies using language adapter."""
        if self._runtime:
            await self._runtime.install(str(self.path), self.config.model_dump())
            logger.info(f"📦 Installed dependencies for {self.name}")
        else:
            logger.warning(
                f"Cannot install dependencies - no runtime for {self.config.type}"
            )

    async def build(self) -> None:
        """Build the service using language adapter."""
        if self._runtime:
            await self._runtime.build(str(self.path), self.config.model_dump())
            logger.info(f"Built service {self.name}")
        else:
            logger.warning(f"Cannot build - no runtime for {self.config.type}")

    async def test(self) -> None:
        """Run tests for the service using language adapter."""
        if self._runtime:
            await self._runtime.test(str(self.path), self.config.model_dump())
            logger.info(f"Ran tests for {self.name}")
        else:
            logger.warning(f"Cannot run tests - no runtime for {self.config.type}")

    async def validate(self) -> List[str]:
        """Validate service configuration and structure."""
        errors = []
        # Validation is delegated to runtime where applicable (optional)
        # For now, skip runtime-specific validation to keep behavior minimal.
        return errors

    async def detect_framework(self) -> Optional[str]:
        """Auto-detect the framework used by this service."""
        if self._runtime:
            return await self._runtime.detect_framework(str(self.path))
        return None

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the service."""
        return {
            "name": self.name,
            "running": self.is_running,
            "port": self.port,
            "path": str(self.path),
            "type": self.config.type,
            "framework": self.config.framework,
            "detected_framework": None,
            "has_runtime": self._runtime is not None,
        }
