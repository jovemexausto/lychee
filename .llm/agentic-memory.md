# Lychee Agentic Memory

## Core Philosophy

- Lychee is a modular suite: each tool (Contracts, Compose) has a single, clear responsibility.
- All orchestration and type-safety flows from a single source of truth: JSON Schema and `service.yml`.

## Real-World Pain Points (from 003-real-world-pain-points.md)

- Manual service creation and type sharing are error-prone and tedious.
- Tooling fragmentation and context switching slow down development.
- Lychee solves this with template-based scaffolding, contract-driven type generation, and a unified CLI.
- Environment normalization and one-command onboarding (`lychee onboard`) are key for developer experience.
- Schema producers and centralized type distribution keep contracts in sync across languages.

## Pivoting to Suite (from 006-pivoting.md)

- Lychee is split into two main tools:
  - **Lychee Contracts:** Generates types from schemas, manages symlinks, watches for changes.
  - **Lychee Compose:** Orchestrates services, manages dependencies, provides TUI dashboard, handles hot reloading.
- Each tool is independently usable but designed to work together.
- All planning, task generation, and agent instructions are in `.specify/`.

## Agentic Patterns

- Schema-first: all code and contracts are generated from schemas.
- TDD by default: failing tests before implementation.
- Strict separation: CLI, core, and templates are modular.
- Composable workflows: tools can be called independently or orchestrated.

## Next Steps

- Document the suite philosophy and tool boundaries in `.github/copilot-instructions.md`.
- Ensure planning and task templates reflect the split.
- Add/update example `service.yml` and schemas in `examples/`.
- Update onboarding docs to reflect the agentic, modular approach.

## Plugins System (for LLMs)

- Entry-point registry is the discoverability mechanism. Third-party packages expose entry points and are auto-loaded at runtime.
- Built-ins remain enabled by default so core flows keep working without any external plugins.

__Entry point groups__
- `lychee.language_runtimes` → implements `LanguageRuntimePort`
- `lychee.schema_compilers` → implements `SchemaCompilerPort`

__Ports (public surface for plugins)__ in `lychee-core/src/lychee/application/ports/`:
- `language_runtime.py` → `LanguageRuntimePort`
- `schema_compiler.py` → `SchemaCompilerPort`
- `process_manager.py` → `ProcessManagerPort`, `ProcessHandle`
- `plugin_registry.py` → `PluginRegistryPort`

__Infrastructure adapters (built-ins)__ in `lychee-core/src/lychee/infrastructure/`:
- `languages/python_runtime_adapter.py` → wraps `lychee.core.languages.python.PythonAdapter` as `LanguageRuntimePort`
- `schema/quicktype_python_compiler.py` → JSON Schema → Python via `pnpm quicktype`
- `process/asyncio_manager.py` → wraps `lychee.core.utils.process.ProcessManager` as `ProcessManagerPort`

__Registry implementation__
- `infrastructure/plugins/entrypoint_registry.py` → `EntryPointPluginRegistry`
- Accepts instances, classes (no-arg), or factories returning a plugin.
- Respects an optional allowlist from `LycheeConfig.plugins` using `EntryPointPluginRegistry.from_config(config)`.

__Core wiring__
- `core/service.py` now uses `EntryPointPluginRegistry.from_config(project.config)` to resolve language runtimes and manage processes via `ProcessHandle`.
- `core/schema/manager.py` uses the same registry to resolve schema compilers during type generation.

__Config__ (`lychee.yaml`)
- Optional `plugins` allowlist (by entry point name):

```yaml
plugins:
  - name: "my-lychee-plugin"
    version: ">=0.1,<1.0"  # advisory
    config:
      some_option: true
```

Note: current implementation uses `name` for allowlisting. Version/config are placeholders for future behavior.

__CLI__
- `lychee plugins list` prints discovered language runtimes and schema compilers using the same registry (honors allowlist).

__Common tasks__
- To add a new runtime/compiler: implement the appropriate Port, expose via entry points, install the package (e.g., `uv pip install -e .`).
- To restrict which external plugins load: set `plugins:` in `lychee.yaml` with the desired entry point `name`s.
