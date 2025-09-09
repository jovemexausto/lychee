import asyncio
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from monorepo.config.models import ServiceConfig
from monorepo.languages.registry import language_registry
from monorepo.utils.logging import get_logger
from monorepo.utils.process import ProcessManager

if TYPE_CHECKING:
    from monorepo.core.project import MonorepoProject

logger = get_logger(__name__)


class Service:
    """Represents a service in the monorepo with language adapter integration."""

    def __init__(
        self, name: str, path: Path, config: ServiceConfig, project: "MonorepoProject"
    ):
        self.name = name
        self.path = path.resolve()
        self.config = config
        self.project = project
        self._process_manager = ProcessManager()
        self._language_adapter = self._create_language_adapter()
        self._process: Optional[asyncio.subprocess.Process] = None

    def _create_language_adapter(self):
        """Create language adapter for this service."""
        adapter_class = language_registry.get_adapter(self.config)

        if not adapter_class:
            raise RuntimeError(f"No adapter found for language: {self.config.type}")

        return adapter_class

    def get_process(self) -> Optional[asyncio.subprocess.Process]:
        """Get the subprocess object for the service."""
        return self._process

    def get_pid(self) -> Optional[int]:
        """Get the PID of the service process."""
        return (
            self._process.pid
            if self._process and self._process.returncode is None
            else None
        )

    @property
    def is_running(self) -> bool:
        """Check if the service is currently running."""
        return self._process_manager.is_process_running(self._process)

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
        if self._process:
            await self._process_manager.stop_process(self._process)
            self._process = None

    async def restart(self, mode: str = "native") -> None:
        """Restart the service."""
        await self.stop()
        await self.start(mode)

    async def _start_native(self) -> None:
        """Start the service natively using language adapter."""

        cmd = await self._language_adapter.get_start_command()
        env = self._build_environment()

        self._process = await self._process_manager.start_process(
            cmd=cmd,
            cwd=str(self.path),
            env=env,
        )

        pid = self._process.pid

        logger.debug(
            f"Service {self.name} started with PID {pid} and command: {' '.join(cmd)}"
        )

    async def _start_docker(self) -> None:
        """Start the service using Docker."""
        raise NotImplementedError("Docker startup not yet implemented")

    def _build_environment(self) -> Dict[str, str]:
        """Build the environment variables for the service process."""
        env = os.environ.copy()
        # Set adapter's built-in env variables
        adapter_env = self._language_adapter.get_environment_variables()
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
        if self._language_adapter:
            await self._language_adapter.install_dependencies()
            logger.info(f"📦 Installed dependencies for {self.name}")
        else:
            logger.warning(
                f"Cannot install dependencies - no adapter for {self.config.type}"
            )

    async def build(self) -> None:
        """Build the service using language adapter."""
        if self._language_adapter:
            cmd = await self._language_adapter.get_build_command()
            await self._process_manager.run_command(cmd, cwd=str(self.path))
            logger.info(f"Built service {self.name}")
        else:
            logger.warning(f"Cannot build - no adapter for {self.config.type}")

    async def test(self) -> None:
        """Run tests for the service using language adapter."""
        if self._language_adapter:
            cmd = await self._language_adapter.get_test_command()
            await self._process_manager.run_command(cmd, cwd=str(self.path))
            logger.info(f"Ran tests for {self.name}")
        else:
            logger.warning(f"Cannot run tests - no adapter for {self.config.type}")

    async def validate(self) -> List[str]:
        """Validate service configuration and structure."""
        errors = []
        if self._language_adapter:
            adapter_errors = await self._language_adapter.validate_service()
            errors.extend(adapter_errors)
        return errors

    async def detect_framework(self) -> Optional[str]:
        """Auto-detect the framework used by this service."""
        if self._language_adapter:
            return await self._language_adapter.detect_framework()
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
            "detected_framework": self.detect_framework(),
            "has_adapter": self._language_adapter is not None,
        }
