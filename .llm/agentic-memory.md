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
