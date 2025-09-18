# Agentic TODO

## Current Focus

- None (batch completed). Open to next priorities.

## Completed (this batch)

- Plugins allowlist in registry and wiring
  - `lychee-core/src/lychee/infrastructure/plugins/entrypoint_registry.py`: `from_config()` + allowlist by `LycheeConfig.plugins[*].name`
  - `lychee-core/src/lychee/core/service.py`: registry via `EntryPointPluginRegistry.from_config()`
  - `lychee-core/src/lychee/core/schema/manager.py`: registry via `EntryPointPluginRegistry.from_config()`
- CLI plugins command
  - `lychee-cli/src/lychee/cli/commands/plugins.py`: `lychee plugins list`
  - `lychee-cli/src/lychee/cli/main.py`: registered `plugins`
- Config/templates and docs
  - `lychee-core/src/lychee/core/templates/templates/basic/lychee.yaml`: commented `plugins` example
  - `examples/hello-world/lychee.yaml`: commented `plugins` example
  - `.llm/agentic-memory.md`: updated with plugin architecture guidance for LLMs
  - `.llm/007-plugins-architecture-and-registry.md`: architecture note

## Nice to have

- Plugin config payload propagation
  - Thread `LycheeConfig.plugins[*].config` into runtime/compiler initialization.
  - Define a pattern in ports for receiving optional per-plugin options.
- Denylist and version checks
  - Add an explicit denylist alongside the allowlist.
  - Optionally validate installed distribution version against `plugins[*].version`.
  - Emit warnings or block load when constraints are not met.
- Tests for plugin system
  - Unit tests for registry allowlist/denylist behavior.
  - CLI tests for `lychee plugins list` output.
  - Integration test booting a sample external plugin.
- CLI enhancements
  - `lychee plugins list --json` to output machine-readable inventory.
  - `lychee plugins doctor` to surface entry-point import errors and versions.
- Observability
  - Structured logging on plugin load (name, group, distribution, version).
  - Optional debug flag to print why a plugin was skipped (allowlist/denylist/version).
- Additional plugin types
  - Define ports for `DashboardPlugin`, `DevProxyPlugin`, etc., and wire discovery.
- Documentation
  - Expand `lychee-core/PLUGINS.md` with troubleshooting examples and real plugin templates.
  - Add a minimal sample external package under `examples/` to demonstrate local dev.
