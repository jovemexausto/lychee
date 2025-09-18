from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .process_manager import ProcessHandle


class LanguageRuntimePort(ABC):
    """Port describing how to interact with a language-specific runtime."""

    @abstractmethod
    def language(self) -> str:  # noqa: D401
        """Return the language name (e.g., 'python', 'typescript')."""

    @abstractmethod
    async def detect_framework(self, service_path: str) -> Optional[str]:  # noqa: D401
        """Auto-detect framework for the service path."""

    @abstractmethod
    async def install(self, service_path: str, service_config: Dict[str, Any]) -> None:  # noqa: D401
        """Install dependencies for a service."""

    @abstractmethod
    async def start(
        self,
        service_path: str,
        service_config: Dict[str, Any],
        env: Dict[str, str],
    ) -> ProcessHandle:  # noqa: D401
        """Start the service and return a process handle."""

    @abstractmethod
    async def stop(self, handle: ProcessHandle) -> None:  # noqa: D401
        """Stop a running service."""

    @abstractmethod
    async def build(self, service_path: str, service_config: Dict[str, Any]) -> None:  # noqa: D401
        """Build a service."""

    @abstractmethod
    async def test(self, service_path: str, service_config: Dict[str, Any]) -> None:  # noqa: D401
        """Run service tests."""

    @abstractmethod
    def environment(self, service_path: str, service_config: Dict[str, Any]) -> Dict[str, str]:  # noqa: D401
        """Return language-specific environment variables."""
