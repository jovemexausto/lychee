from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from lychee.application.ports.language_runtime import LanguageRuntimePort
from lychee.application.ports.process_manager import ProcessHandle, ProcessManagerPort
from lychee.core.config.models import ServiceConfig
from lychee.core.languages.python import PythonAdapter


class PythonRuntimeAdapter(LanguageRuntimePort):
    """LanguageRuntimePort implementation backed by the existing PythonAdapter."""

    def __init__(self, process_manager: ProcessManagerPort) -> None:
        self._pm = process_manager

    def language(self) -> str:
        return "python"

    async def detect_framework(self, service_path: str) -> Optional[str]:
        adapter = self._adapter(service_path, {"type": "python", "path": service_path})
        return await adapter.detect_framework()

    async def install(self, service_path: str, service_config: Dict[str, Any]) -> None:
        adapter = self._adapter(service_path, service_config)
        await adapter.install_dependencies()

    async def start(
        self,
        service_path: str,
        service_config: Dict[str, Any],
        env: Dict[str, str],
    ) -> ProcessHandle:
        adapter = self._adapter(service_path, service_config)
        cmd = await adapter.get_start_command()
        handle = await self._pm.start(cmd=cmd, cwd=str(service_path), env=env)
        return handle

    async def stop(self, handle: ProcessHandle) -> None:
        await self._pm.stop(handle)

    async def build(self, service_path: str, service_config: Dict[str, Any]) -> None:
        adapter = self._adapter(service_path, service_config)
        cmd = await adapter.get_build_command()
        await self._pm.run(cmd=cmd, cwd=str(service_path))

    async def test(self, service_path: str, service_config: Dict[str, Any]) -> None:
        adapter = self._adapter(service_path, service_config)
        cmd = await adapter.get_test_command()
        await self._pm.run(cmd=cmd, cwd=str(service_path))

    def environment(self, service_path: str, service_config: Dict[str, Any]) -> Dict[str, str]:
        adapter = self._adapter(service_path, service_config)
        return adapter.get_environment_variables()

    def _adapter(self, service_path: str, service_config: Dict[str, Any]) -> PythonAdapter:
        cfg = self._to_service_config(service_config)
        return PythonAdapter(Path(service_path), cfg)

    def _to_service_config(self, cfg: Dict[str, Any]) -> ServiceConfig:
        # Ensure required keys
        if "type" not in cfg:
            cfg = {**cfg, "type": "python"}
        if "path" not in cfg:
            cfg = {**cfg, "path": str(cfg.get("path", ""))}
        return ServiceConfig(**cfg)
