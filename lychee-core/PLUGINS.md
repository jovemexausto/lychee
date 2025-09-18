# Lychee Plugins (Entry Points)

Lychee supports a first-class plugin system using Python entry points, so the community can publish plugins as pip-installable packages that depend only on `lychee-core`.

This document explains how to build and publish plugins.

## Entry point groups

Lychee discovers plugins using these entry point groups:

- `lychee.language_runtimes`: Provide language runtimes (start/build/test/install/detect) by implementing `LanguageRuntimePort`.
- `lychee.schema_compilers`: Provide schema compilers (e.g., JSON Schema → Python/TS) by implementing `SchemaCompilerPort`.

## Minimal examples

### Language Runtime Plugin (Python)

`my_pkg/python_plugin.py`:

```python
from lychee.application.ports.language_runtime import LanguageRuntimePort
from lychee.application.ports.process_manager import ProcessHandle, ProcessManagerPort
from typing import Any, Dict, Optional

class MyLangRuntime(LanguageRuntimePort):
    def __init__(self, pm: ProcessManagerPort | None = None):
        self._pm = pm  # optional: resolve your own process manager if needed

    def language(self) -> str:
        return "mylang"

    async def detect_framework(self, service_path: str) -> Optional[str]:
        return None

    async def install(self, service_path: str, service_config: Dict[str, Any]) -> None:
        pass

    async def start(self, service_path: str, service_config: Dict[str, Any], env: Dict[str, str]) -> ProcessHandle:
        # example no-op: call some binary here
        raise NotImplementedError

    async def stop(self, handle: ProcessHandle) -> None:
        # Use the ProcessManagerPort if you manage processes
        raise NotImplementedError

    async def build(self, service_path: str, service_config: Dict[str, Any]) -> None:
        pass

    async def test(self, service_path: str, service_config: Dict[str, Any]) -> None:
        pass

    def environment(self, service_path: str, service_config: Dict[str, Any]) -> Dict[str, str]:
        return {}

# Factory function (recommended)

def make_plugin() -> LanguageRuntimePort:
    return MyLangRuntime()
```

`pyproject.toml`:

```toml
[project]
name = "my-lychee-mylang-runtime"
version = "0.1.0"
dependencies = ["lychee-core>=0.1.0"]

[project.entry-points."lychee.language_runtimes"]
mylang = "my_pkg.python_plugin:make_plugin"
```

### Schema Compiler Plugin

`my_pkg/quicktype_ts.py`:

```python
from pathlib import Path
from typing import Dict, Optional
from lychee.application.ports.schema_compiler import SchemaCompilerPort

class QuicktypeTS(SchemaCompilerPort):
    def supports(self, schema_format: str, target_language: str) -> bool:
        return schema_format.lower() in {"json_schema", "json-schema"} and target_language.lower() == "typescript"

    async def compile(self, schema_path: Path, output_dir: Path, project_path: Path, options: Optional[Dict] = None) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        # Run your toolchain here, e.g., pnpm quicktype → .ts
        raise NotImplementedError
```

`pyproject.toml`:

```toml
[project]
name = "my-lychee-quicktype-ts"
version = "0.1.0"
dependencies = ["lychee-core>=0.1.0"]

[project.entry-points."lychee.schema_compilers"]
quicktype_ts = "my_pkg.quicktype_ts:QuicktypeTS"
```

## How Lychee loads plugins

- Lychee uses `importlib.metadata.entry_points(group=...)` to discover entry points at runtime.
- The object can be one of:
  - An instance of the expected port interface (`LanguageRuntimePort` / `SchemaCompilerPort`).
  - A class implementing the respective port (will be instantiated with no arguments).
  - A factory callable that returns an instance implementing the port.
- Built-in defaults remain available (Python runtime and Quicktype→Python compiler) so Lychee works out of the box.

## Testing a plugin locally

- Install your plugin in the same environment as Lychee (editable recommended):

```bash
uv pip install -e path/to/your/plugin
```

- Run Lychee as usual (e.g., `lychee schema generate`, `lychee dev start`).
- Lychee will auto-discover your entry points at process start.

## Version compatibility

- Target `lychee-core` as your only dependency.
- Follow semantic versioning and specify compatible ranges, e.g., `lychee-core >=0.1,<0.2`.
- Avoid importing infrastructure internals; rely on the public ports in `lychee.application.ports`.

## Troubleshooting

- If your plugin is not discovered, verify that:
  - The package is installed in the active environment.
  - The entry point group and path are correct.
  - Import errors inside your plugin are not preventing load (check Lychee logs).
