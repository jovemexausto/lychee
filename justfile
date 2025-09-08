# justfile

# Default task (runs when you just type `just`)
default:
    @echo "Hello, these are your options:"
    just --list

# Setup environment
setup:
    uv sync
    uv run pre-commit install

# bump minor version
bump-version:
    sed -i -E 's/(version\s*=\s*")([0-9]+)\.([0-9]+)\.([0-9]+)"/\1\2.\3.'$(( $(sed -nE 's/version\s*=\s*"([0-9]+)\.([0-9]+)\.([0-9]+)"/\3/p' pyproject.toml) + 1 ))'"/' pyproject.toml

# Install and turn lychee globally available on the system
install-as-local-tool:
    just bump-version
    uv tool install .

# Run checks
lint:
    uv run black --check monorepo
    uv run isort --check-only monorepo
    uv run mypy monorepo

# Auto-fix formatting
format:
    uv run black monorepo
    uv run isort monorepo
