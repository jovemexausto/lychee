"""Base language adapter interface with async support."""

import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from lychee.core.config.models import ServiceConfig
from lychee.core.utils import get_logger

logger = get_logger(__name__)


class LanguageAdapter(ABC):
    """Base class for language-specific adapters with async support."""

    def __init__(self, service_path: Path, service_config: ServiceConfig):
        self.service_path = service_path
        self.service_config = service_config
        self._framework_cache: Optional[str] = None

    @property
    @abstractmethod
    def language(self) -> str:
        """Return the language name."""
        pass

    @property
    def supported_frameworks(self) -> List[str]:
        """Return list of supported frameworks for this language."""
        return []

    @property
    def required_tools(self) -> List[str]:
        """Return list of required tools/executables for this language."""
        return []

    # Async abstract methods
    @abstractmethod
    async def detect_framework(self) -> Optional[str]:
        """Auto-detect the framework used in the service."""
        pass

    @abstractmethod
    async def get_start_command(self) -> List[str]:
        """Get the command to start the service in development."""
        pass

    @abstractmethod
    async def get_build_command(self) -> List[str]:
        """Get the command to build the service."""
        pass

    @abstractmethod
    async def get_test_command(self) -> List[str]:
        """Get the command to run tests."""
        pass

    @abstractmethod
    async def install_dependencies(self) -> None:
        """Install service dependencies."""
        pass

    @classmethod
    @abstractmethod
    async def generate_types_from_schema(
        cls, schema_path: Path, output_path: Path, project_path: Path
    ) -> None:
        """Generate language-specific types from JSON schema."""
        pass

    @abstractmethod
    def get_environment_variables(self) -> Dict[str, str]:
        """Get language-specific environment variables."""
        pass

    # Optional async methods with default implementations
    async def validate_service(self) -> List[str]:
        """Validate service configuration and structure."""
        errors: List[str] = []

        # Basic path validation
        if not self.service_path.exists():
            errors.append(f"Service path does not exist: {self.service_path}")

        if not self.service_path.is_dir():
            errors.append(f"Service path is not a directory: {self.service_path}")

        # Check for required tools
        missing_tools = await self._check_required_tools()
        if missing_tools:
            errors.extend([f"Missing required tool: {tool}" for tool in missing_tools])

        # Framework validation
        try:
            detected_framework = await self.detect_framework()
            if detected_framework and detected_framework not in self.supported_frameworks:
                errors.append(
                    f"Detected framework '{detected_framework}' is not officially supported"
                )
        except Exception as e:
            errors.append(f"Framework detection failed: {e}")

        return errors

    async def clean_build_artifacts(self) -> None:
        """Clean build artifacts and temporary files."""
        # Default implementation - can be overridden by language adapters
        common_artifacts = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".coverage",
            "htmlcov",
            ".pytest_cache",
            ".mypy_cache",
            "dist",
            "build",
            "*.egg-info",
        ]

        for pattern in common_artifacts:
            await self._remove_files_pattern(pattern)

    async def get_lint_command(self) -> Optional[List[str]]:
        """Get the command to lint the code. Return None if not supported."""
        return None

    async def get_format_command(self) -> Optional[List[str]]:
        """Get the command to format the code. Return None if not supported."""
        return None

    async def get_security_scan_command(self) -> Optional[List[str]]:
        """Get the command to run security scanning. Return None if not supported."""
        return None

    async def get_dependency_audit_command(self) -> Optional[List[str]]:
        """Get the command to audit dependencies for vulnerabilities."""
        return None

    async def check_health(self) -> Dict[str, Any]:
        """Check the health of the service and its dependencies."""
        health_info: dict[str, Any] = {
            "service_path_exists": self.service_path.exists(),
            "service_path_readable": (
                self.service_path.is_dir() if self.service_path.exists() else False
            ),
            "language": self.language,
            "framework": None,
            "dependencies_installed": False,
            "validation_status": "sunknown",
            "required_tools": {},
        }

        try:
            # Check framework
            health_info["framework"] = await self.detect_framework()

            # Check required tools
            for tool in self.required_tools:
                health_info["required_tools"][tool] = await self._tool_exists(tool)

            # Check validation status
            health_info["errors"] = await self.validate_service()

            # Check if dependencies are installed (basic heuristic)
            health_info["dependencies_installed"] = (
                await self._dependencies_appear_installed()
            )

        except Exception as e:
            health_info["health_check_error"] = str(e)
            logger.error(f"Health check failed: {e}")

        return health_info

    # Helper methods
    async def _check_required_tools(self) -> List[str]:
        """Check which required tools are missing."""
        missing: List[str] = []
        for tool in self.required_tools:
            if not await self._tool_exists(tool):
                missing.append(tool)
        return missing

    async def _tool_exists(self, tool: str) -> bool:
        """Check if a tool exists in PATH."""
        import shutil

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, shutil.which, tool)
        return result is not None

    async def _dependencies_appear_installed(self) -> bool:
        """Basic heuristic to check if dependencies appear to be installed."""
        # Default implementation - should be overridden by language adapters
        return True

    async def _remove_files_pattern(self, pattern: str) -> None:
        """Remove files matching a pattern."""
        import glob

        loop = asyncio.get_event_loop()

        def remove_pattern():
            files = glob.glob(str(self.service_path / pattern), recursive=True)
            for file_path in files:
                try:
                    path = Path(file_path)
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        import shutil

                        shutil.rmtree(path)
                except Exception as e:
                    logger.warning(f"Failed to remove {file_path}: {e}")

        await loop.run_in_executor(None, remove_pattern)

    # Caching methods
    async def get_framework_cached(self) -> Optional[str]:
        """Get framework with caching."""
        if self._framework_cache is None:
            self._framework_cache = await self.detect_framework()
        return self._framework_cache

    def invalidate_caches(self) -> None:
        """Invalidate all internal caches."""
        self._framework_cache = None

    # Context managers for resource management
    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup resources if needed
        self.invalidate_caches()
