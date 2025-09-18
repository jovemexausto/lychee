# Agentic TODO

## Current Focus

- Milestone 3: Dev server use-cases (continue)

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
- Domain and repositories (Milestone 1)
  - `lychee-core/src/lychee/domain/{project.py, service.py, errors.py}`: Project/Service entities and topo sort
  - Ports: `application/ports/{config_repository.py, project_repository.py, symlink_manager.py}`
  - Infra: `infrastructure/config/yaml_config_repository.py`, `infrastructure/project/project_repository.py`, `infrastructure/fs/symlink_manager.py`
- Use-case: Schemas (Milestone 2) ✅
  - `application/use_cases/generate_schemas.py` orchestrates compile + mount via plugins and symlinks
  - CLI `schema generate` wired to use-case

- Dev server use-cases (Milestone 3) — In progress
  - `application/use_cases/{start_dev_server.py, stop_dev_server.py, restart_service.py}` implemented
  - CLI `dev {start, stop, restart, status}` wired to use-cases and in-process orchestrator
  - TODO: background mode persistence, logs streaming, proxy/dashboard plugins

- Schemas add/update — ✅ Completed
  - Implemented `application/use_cases/{add_schema.py, update_schema.py}`
  - Wired CLI `schema {add, update}` to use-cases
  - Removed legacy manager usage from CLI

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

## Next Actions

- Milestone 3: Dev server use-cases (continue)
  - Add `status` detailed info (running vs stopped, ports) using runtime APIs
  - Implement `logs` (follow and snapshot) with per-service tails
  - Add background mode (daemonization) and persistence of handles (PID file/registry)
  - Introduce Proxy/Dashboard plugin ports and minimal built-ins
  - Retire `core/server/development.py` after parity

## Acceptance Targets

- `examples/hello-world` still works end-to-end:
  - `lychee schema generate` produces types and mounts symlinks
  - `lychee dev start` boots services in dependency order
  - `lychee dev stop`, `lychee dev restart foo`, `lychee dev status` operate via use-cases
