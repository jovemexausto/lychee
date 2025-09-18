from __future__ import annotations

import asyncio
from typing import Dict, Optional

from lychee.application.ports.language_runtime import LanguageRuntimePort
from lychee.application.ports.process_manager import ProcessHandle
from lychee.core.utils.logging import get_logger
from lychee.domain.service import Service

logger = get_logger(__name__)


class RuntimeOrchestrator:
    """Holds running service process handles within the current process."""

    def __init__(self) -> None:
        self._handles: Dict[str, ProcessHandle] = {}
        self._lock = asyncio.Lock()

    async def start_service(
        self, service: Service, runtime: LanguageRuntimePort, env: Dict[str, str]
    ) -> ProcessHandle:
        async with self._lock:
            if service.name in self._handles:
                logger.warning(f"Service {service.name} already running")
                return self._handles[service.name]
            handle = await runtime.start(
                service_path=str(service.path),
                service_config={
                    "type": service.language,
                    "path": str(service.path),
                    "framework": service.framework,
                    "runtime": {
                        "port": service.runtime.port,
                        "entry_point": service.runtime.entry_point,
                        **service.runtime.version_info,
                    },
                },
                env=env,
            )
            self._handles[service.name] = handle
            return handle

    async def stop_service(self, name: str, runtime: LanguageRuntimePort) -> None:
        async with self._lock:
            handle = self._handles.get(name)
            if not handle:
                return
            await runtime.stop(handle)
            del self._handles[name]

    async def stop_all(self, runtime_by_service: Dict[str, LanguageRuntimePort]) -> None:
        async with self._lock:
            # copy keys to avoid mutation during iteration
            for name in list(self._handles.keys()):
                runtime = runtime_by_service.get(name)
                if not runtime:
                    logger.warning(f"No runtime found to stop service {name}")
                    continue
                await runtime.stop(self._handles[name])
                del self._handles[name]

    def get_handle(self, name: str) -> Optional[ProcessHandle]:
        return self._handles.get(name)

    def status(self) -> Dict[str, Dict[str, Optional[int]]]:
        return {name: {"pid": handle.pid} for name, handle in self._handles.items()}


# Simple singleton for current process
runtime_orchestrator = RuntimeOrchestrator()
