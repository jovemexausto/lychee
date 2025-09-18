# Plugins Architecture: Entry-Point Registry, Ports, and Adapters

This note documents the new plugin system added to `lychee-core`, how it is wired into the core, and what plugin authors need to know. It is based on the current `git diff` for this branch.

## Summary

- Introduced a first-class, entry-points-based plugin discovery mechanism so the community can ship pip-installable plugins that only depend on `lychee-core`.
- Added Clean Architecture style ports for core boundaries (`LanguageRuntimePort`, `SchemaCompilerPort`, `ProcessManagerPort`, `PluginRegistryPort`).
- Implemented infrastructure adapters and built-in default plugins (Python runtime, Quicktype→Python compiler) that remain enabled by default.
- Wired `core/service.py` and `core/schema/manager.py` to use the plugin registry and ports.
- Authored a plugin author guide at `lychee-core/PLUGINS.md`.

## New Entry-Points-Based Registry

- File: `lychee-core/src/lychee/infrastructure/plugins/entrypoint_registry.py`
- Class: `EntryPointPluginRegistry`
- Discovers third-party plugins from Python entry point groups:
  - `lychee.language_runtimes` → provides implementations of `LanguageRuntimePort`
  - `lychee.schema_compilers` → provides implementations of `SchemaCompilerPort`
- Accepts plugin objects in three forms:
  - Instances of the expected port
  - Classes (no-arg constructor)
  - Callables/factories returning a valid instance
- Keeps built-ins enabled by default so Lychee “just works” without plugins:
  - `PythonRuntimeAdapter` for language runtime
  - `QuicktypePythonCompiler` for schema compiler
- Gracefully logs and skips invalid/broken entry points.

Key API (from `PluginRegistryPort`):
- `get_language_runtime(language: str) -> Optional[LanguageRuntimePort]`
- `get_schema_compiler(schema_format: str, language: str) -> Optional[SchemaCompilerPort]`
- `list_language_runtimes() -> Iterable[LanguageRuntimePort]`
- `list_schema_compilers() -> Iterable[SchemaCompilerPort]`

## Ports (Clean Architecture Boundaries)

- Directory: `lychee-core/src/lychee/application/ports/`
  - `process_manager.py`
    - `ProcessHandle` (dataclass with `pid`, `native`)
    - `ProcessManagerPort` (`start`, `stop`, `is_running`, `run`)
  - `language_runtime.py`
    - `LanguageRuntimePort` (`language`, `detect_framework`, `install`, `start`, `stop`, `build`, `test`, `environment`)
  - `schema_compiler.py`
    - `SchemaCompilerPort` (`supports`, `compile`)
  - `plugin_registry.py`
    - `PluginRegistryPort` (queries and lists for runtimes/compilers)

These ports are the public surface area for plugin authors. Third-party plugins should depend only on `lychee-core` and import from `lychee.application.ports.*`.

## Infrastructure Adapters (Built-ins)

- Process manager adapter
  - File: `lychee-core/src/lychee/infrastructure/process/asyncio_manager.py`
  - Class: `AsyncioProcessManagerAdapter` implements `ProcessManagerPort` by wrapping `lychee.core.utils.process.ProcessManager`

- Python language runtime adapter
  - File: `lychee-core/src/lychee/infrastructure/languages/python_runtime_adapter.py`
  - Class: `PythonRuntimeAdapter` implements `LanguageRuntimePort` by delegating to existing `lychee.core.languages.python.PythonAdapter`

- Quicktype schema compiler (JSON Schema → Python)
  - File: `lychee-core/src/lychee/infrastructure/schema/quicktype_python_compiler.py`
  - Class: `QuicktypePythonCompiler` implements `SchemaCompilerPort` using `pnpm quicktype` to generate Python types

## Core Wiring Changes

- `lychee-core/src/lychee/core/service.py`
  - Replaced direct adapter registry usage with `EntryPointPluginRegistry`
  - Manages processes through `ProcessHandle` and `AsyncioProcessManagerAdapter`
  - Uses selected `LanguageRuntimePort` for `install`, `start`, `stop`, `build`, `test`, `environment`

- `lychee-core/src/lychee/core/schema/manager.py`
  - Introduced `EntryPointPluginRegistry` for resolving `SchemaCompilerPort`
  - Generation flow remains the same; compilers are resolved via the registry

## How Third-Parties Create Plugins

- Language runtime plugin
  - Entry point group: `lychee.language_runtimes`
  - `pyproject.toml`:
    ```toml
    [project.entry-points."lychee.language_runtimes"]
    mylang = "my_pkg.python_plugin:make_plugin"
    ```
  - Factory should return an instance of `LanguageRuntimePort`.

- Schema compiler plugin
  - Entry point group: `lychee.schema_compilers`
  - `pyproject.toml`:
    ```toml
    [project.entry-points."lychee.schema_compilers"]
    quicktype_ts = "my_pkg.quicktype_ts:QuicktypeTS"
    ```

See `lychee-core/PLUGINS.md` for full examples and packaging details.

## Backward Compatibility and Behavior

- Built-in plugins (Python runtime, Quicktype→Python compiler) are enabled by default.
- No behavior change for users: existing commands like `lychee dev start` and `lychee schema generate` continue to work, now powered by plugins under the hood.
- Broken or invalid entry points are logged and skipped; execution continues with valid plugins.

## Suggested Next Steps

- Config allowlist/denylist for plugins in `lychee.yaml` (e.g., names, versions, per-plugin config).
- Additional plugin types (e.g., `DashboardPlugin`, `DevProxyPlugin`) and wiring of flags to them.
- CLI surface for discovery: `lychee plugins list` to show detected language runtimes and schema compilers.

## Diff-Oriented File Map

- Added:
  - `lychee-core/PLUGINS.md`
  - `lychee-core/src/lychee/application/ports/` (new modules for ports)
  - `lychee-core/src/lychee/infrastructure/` (adapters for process, languages, schema)
- Modified:
  - `lychee-core/src/lychee/core/service.py` → now uses `EntryPointPluginRegistry` + runtime port
  - `lychee-core/src/lychee/core/schema/manager.py` → uses `EntryPointPluginRegistry` for schema compilers

## Notes for Reviewers

- Registry groups: `lychee.language_runtimes`, `lychee.schema_compilers` (see `entrypoint_registry.py`).
- Runtime selection: `EntryPointPluginRegistry.get_language_runtime(<service.config.type>)`.
- Compiler selection: `EntryPointPluginRegistry.get_schema_compiler(<format>, <language>)`.
- Processes: handled via `ProcessHandle` and `ProcessManagerPort` to keep core layers decoupled.
