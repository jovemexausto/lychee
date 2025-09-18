from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ProcessHandle:
    pid: int
    # Opaque handle to the underlying process object (asyncio.subprocess.Process, etc.)
    native: object


class ProcessManagerPort(ABC):
    """Port for starting/stopping and checking processes in a technology-agnostic way."""

    @abstractmethod
    async def start(self, cmd: list[str], cwd: str, env: Optional[Dict[str, str]] = None) -> ProcessHandle:  # noqa: D401
        """Start a process and return its handle."""

    @abstractmethod
    async def stop(self, handle: ProcessHandle, timeout: int = 10) -> None:  # noqa: D401
        """Stop a process referenced by the handle."""

    @abstractmethod
    def is_running(self, handle: Optional[ProcessHandle]) -> bool:  # noqa: D401
        """Return whether the process is still running."""

    @abstractmethod
    async def run(self, cmd: list[str], cwd: str) -> None:  # noqa: D401
        """Run a command to completion (fire-and-wait)."""
