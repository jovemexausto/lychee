"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest

from monorepo.config.models import MonorepoConfig, ProjectConfig, ServiceConfig
from monorepo.core.project import MonorepoProject


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_config() -> MonorepoConfig:
    """Sample monorepo configuration for tests."""
    return MonorepoConfig(
        name="test-monorepo",
        version="1.0.0",
        project=ProjectConfig(languages=["python", "typescript"]),
        services={
            "auth-service": ServiceConfig(type="python", framework="fastapi", path="./services/auth"),
            "frontend": ServiceConfig(type="typescript", framework="nextjs", path="./apps/web"),
        },
    )


@pytest.fixture
def sample_project(temp_dir: Path, sample_config: MonorepoConfig) -> MonorepoProject:
    """Sample monorepo project for tests."""
    # Create basic project structure
    (temp_dir / "services" / "auth").mkdir(parents=True)
    (temp_dir / "apps" / "web").mkdir(parents=True)

    # Create config file
    config_file = temp_dir / "monorepo.yml"
    with config_file.open("w") as f:
        f.write(
            """
name: test-monorepo
version: 1.0.0
project:
  languages: [python, typescript]
"""
        )

    # Create services config
    services_config = temp_dir / ".monorepo" / "services.yml"
    services_config.parent.mkdir(exist_ok=True)
    with services_config.open("w") as f:
        f.write(
            """
services:
  auth-service:
    type: python
    framework: fastapi
    path: ./services/auth
  frontend:
    type: typescript
    framework: nextjs
    path: ./apps/web
"""
        )

    return MonorepoProject(temp_dir, sample_config)
