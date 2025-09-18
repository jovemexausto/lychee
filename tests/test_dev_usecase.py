from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from lychee.application.use_cases.start_dev_server import StartDevServerUseCase
from lychee.application.services.runtime_orchestrator import runtime_orchestrator
from lychee.application.ports.language_runtime import LanguageRuntimePort
from lychee.infrastructure.plugins.entrypoint_registry import EntryPointPluginRegistry


class RecordingRuntime(LanguageRuntimePort):
    def __init__(self):
        self.started: List[tuple[str, Dict[str, Any], Dict[str, str]]] = []
        self.stopped: List[int] = []

    def language(self) -> str:
        return "python"

    async def detect_framework(self, service_path: str) -> Optional[str]:
        return None

    async def install(self, service_path: str, service_config: Dict[str, Any]) -> None:
        # no-op
        return None

    async def start(self, service_path: str, service_config: Dict[str, Any], env: Dict[str, str]):
        # Simulate a process handle with pid incrementing
        pid = 1234 + len(self.started)
        self.started.append((service_path, service_config, env))
        from lychee.application.ports.process_manager import ProcessHandle

        return ProcessHandle(pid=pid, native={"service_path": service_path})

    async def stop(self, handle):  # type: ignore[no-untyped-def]
        self.stopped.append(handle.pid)

    async def build(self, service_path: str, service_config: Dict[str, Any]) -> None:
        return None

    async def test(self, service_path: str, service_config: Dict[str, Any]) -> None:
        return None

    def environment(self, service_path: str, service_config: Dict[str, Any]) -> Dict[str, str]:
        return {}


class FakeRegistry(EntryPointPluginRegistry):
    def __init__(self, runtime: RecordingRuntime):  # type: ignore[no-untyped-def]
        self._rt = runtime
        self._language_runtimes = [runtime]
        self._schema_compilers = []

    @classmethod
    def from_config(cls, config, include_builtins: bool = True):  # type: ignore[override]
        # default runtime if not injected
        return cls(RecordingRuntime())

    def get_language_runtime(self, language: str):  # type: ignore[override]
        return self._rt


def test_dev_start_topo_order_and_python_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # Given a project with foo depends on bar
    root = tmp_path
    (root / "services" / "bar").mkdir(parents=True)
    (root / "services" / "foo").mkdir(parents=True)

    lychee_yaml = {
        "version": 1.0,
        "project": {"languages": ["python"], "workspace": {"services_dir": "services"}},
        "schemas": {"dir": "schemas", "output_path": ".lychee", "format": "json_schema"},
        "environment": {"MY_GLOBAL_ENV": "orange"},
        "services": {
            "bar": {
                "type": "python",
                "path": str(Path("services/bar")),
                "runtime": {"python_version": "3.11", "port": 8001, "entry_point": "main:app"},
                "schemas": {"mount_dir": "models"},
            },
            "foo": {
                "type": "python",
                "path": str(Path("services/foo")),
                "dependencies": {"services": ["bar"]},
                "runtime": {"python_version": "3.11", "port": 8002, "entry_point": "main:app"},
                "schemas": {"mount_dir": "models"},
                "environment": {"FOO": "1"},
            },
        },
    }
    (root / "lychee.yaml").write_text(json.dumps(lychee_yaml), encoding="utf-8")

    # Patch registry to recording runtime
    rec_rt = RecordingRuntime()
    monkeypatch.setattr(EntryPointPluginRegistry, "from_config", classmethod(lambda cls, cfg, include_builtins=True: FakeRegistry(rec_rt)))  # noqa: E501

    # When
    usecase = StartDevServerUseCase()
    asyncio.run(usecase.run(root=root, services=None, mode="native", enable_proxy=False, enable_dashboard=False))

    # Then: bar should start before foo
    assert len(rec_rt.started) == 2
    assert rec_rt.started[0][0].endswith("services/bar")  # service_path order
    assert rec_rt.started[1][0].endswith("services/foo")

    # And runtime received python_version in config for foo
    foo_cfg = rec_rt.started[1][1]
    assert foo_cfg["runtime"]["python_version"] == "3.11"

    # And env composition includes global and service env
    foo_env = rec_rt.started[1][2]
    assert foo_env.get("MY_GLOBAL_ENV") == "orange"
    assert foo_env.get("FOO") == "1"

    # Cleanup orchestrator for isolation
    asyncio.run(runtime_orchestrator.stop_all({"bar": rec_rt, "foo": rec_rt}))
