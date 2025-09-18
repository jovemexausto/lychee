from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Iterable, Optional

import pytest

from lychee.application.use_cases.generate_schemas import GenerateSchemasUseCase
from lychee.application.ports.schema_compiler import SchemaCompilerPort
from lychee.infrastructure.plugins.entrypoint_registry import EntryPointPluginRegistry
from lychee.infrastructure.fs.symlink_manager import FSSymlinkManager


class FakeCompiler(SchemaCompilerPort):
    def supports(self, schema_format: str, target_language: str) -> bool:
        return True

    async def compile(self, schema_path: Path, output_dir: Path, project_path: Path, options=None) -> None:  # noqa: E501
        output_dir.mkdir(parents=True, exist_ok=True)
        # write a marker file to simulate generated code
        (output_dir / f"{schema_path.stem.replace('.schema','')}.py").write_text("# generated\n")


class FakeRegistry(EntryPointPluginRegistry):
    def __init__(self):  # type: ignore[no-untyped-def]
        # do not call parent
        self._language_runtimes = []
        self._schema_compilers = [FakeCompiler()]

    @classmethod
    def from_config(cls, config, include_builtins: bool = True):  # type: ignore[override]
        return cls()


class RecordingSymlinkManager(FSSymlinkManager):
    def __init__(self):  # type: ignore[no-untyped-def]
        self.calls: list[tuple[Path, Path]] = []

    def ensure(self, source: Path, target: Path) -> None:  # type: ignore[override]
        self.calls.append((source, target))
        super().ensure(source, target)


def test_generate_schemas_and_mounts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # Given a temporary project
    root = tmp_path
    (root / "schemas").mkdir()
    (root / "services" / "foo").mkdir(parents=True)

    # Create lychee.yaml with explicit service and languages
    lychee_yaml = {
        "version": 1.0,
        "project": {"languages": ["python"]},
        "schemas": {"dir": "schemas", "output_path": ".lychee", "format": "json_schema"},
        "services": {
            "foo": {
                "type": "python",
                "path": str(Path("services/foo")),
                "runtime": {"port": 8001, "entry_point": "main:app"},
                "schemas": {"mount_dir": "models"},
            }
        },
    }
    (root / "lychee.yaml").write_text(json.dumps(lychee_yaml), encoding="utf-8")

    # Create one schema
    msg_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Message",
        "type": "object",
        "properties": {"message": {"type": "string"}},
        "required": ["message"],
    }
    (root / "schemas" / "message.schema.json").write_text(json.dumps(msg_schema), encoding="utf-8")

    # Monkeypatch the registry
    monkeypatch.setattr(EntryPointPluginRegistry, "from_config", classmethod(lambda cls, cfg, include_builtins=True: FakeRegistry()))  # noqa: E501

    # Spy symlink manager
    rec_sm = RecordingSymlinkManager()
    usecase = GenerateSchemasUseCase(symlinks=rec_sm)

    # When: run generation
    asyncio.run(usecase.run(root))

    # Then: generated file exists
    assert (root / ".lychee" / "python" / "message.py").exists()
    # And symlink mount was attempted to service mount dir
    assert rec_sm.calls, "Expected at least one symlink ensure call"
    src, dst = rec_sm.calls[0]
    assert src == (root / ".lychee" / "python")
    assert dst == (root / "services" / "foo" / "models")
