from __future__ import annotations

from typing import Dict, Optional

from lychee.application.ports.process_manager import ProcessHandle, ProcessManagerPort
from lychee.core.utils.process import ProcessManager as CoreProcessManager


class AsyncioProcessManagerAdapter(ProcessManagerPort):
    """Adapter that wraps the existing core ProcessManager to satisfy the port."""

    def __init__(self) -> None:
        self._impl = CoreProcessManager()

    async def start(
        self, cmd: list[str], cwd: str, env: Optional[Dict[str, str]] = None
    ) -> ProcessHandle:
        proc = await self._impl.start_process(cmd=cmd, cwd=cwd, env=env)
        return ProcessHandle(pid=proc.pid, native=proc)

    async def stop(self, handle: ProcessHandle, timeout: int = 10) -> None:
        await self._impl.stop_process(handle.native, timeout=timeout)

    def is_running(self, handle: Optional[ProcessHandle]) -> bool:
        if handle is None:
            return False
        return self._impl.is_process_running(handle.native)

    async def run(self, cmd: list[str], cwd: str) -> None:
        await self._impl.run_command(cmd=cmd, cwd=cwd)
