"""Pydantic models for configuration."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RuntimeConfig(BaseModel):
    """Runtime configuration for a service."""

    python_version: Optional[str] = None
    entry_point: Optional[str] = None
    port: Optional[int] = None
    node_version: Optional[str] = None
    replicas: int = 1


class ServiceDependenciesConfig(BaseModel):
    """Service dependencies configuration."""

    services: List[str] = Field(default_factory=list)


class ServiceSchemasConfig(BaseModel):
    """Type generation output config."""

    mount_dir: Optional[str] = None


class ServiceConfig(BaseModel):
    """Configuration for a single service."""

    type: str  # python, typescript, etc.
    path: str
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)
    dependencies: ServiceDependenciesConfig = Field(
        default_factory=ServiceDependenciesConfig
    )
    schemas: ServiceSchemasConfig = Field(default_factory=ServiceSchemasConfig)
    framework: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    environment: Optional[Dict[str, str]] = None


class WorkspaceConfig(BaseModel):
    """Workspace configuration."""

    root: str = "."
    services_dir: str = "./services"
    apps_dir: str = "./apps"
    shared_dir: str = "./shared"
    tools_dir: str = "./tools"


class ProjectConfig(BaseModel):
    """Project-level configuration."""

    languages: List[str] = Field(default_factory=list)
    workspace: WorkspaceConfig = Field(default_factory=WorkspaceConfig)


class SchemaGenerationConfig(BaseModel):
    """Schema generation configuration."""

    auto: bool = True
    on_change: bool = True


class SchemasConfig(BaseModel):
    """Schema management configuration."""

    enabled: bool = False
    format: str = "json_schema"
    dir: str = "schemas"
    output_path: str = "generated/schemas"
    generation: SchemaGenerationConfig = Field(default_factory=SchemaGenerationConfig)


class PluginConfig(BaseModel):
    """Plugin configuration."""

    name: str
    version: str
    config: Optional[Dict[str, Any]] = None


class LycheeConfig(BaseModel):
    """Main monorepo configuration."""

    version: float
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    schemas: SchemasConfig = Field(default_factory=SchemasConfig)
    environment: Optional[Dict[str, str]] = None
    services: Optional[Dict[str, ServiceConfig]] = None
    plugins: List[PluginConfig] = Field(default_factory=list)

    class Config:
        """Pydantic configuration."""

        extra = "allow"  # Allow additional fields


__all__ = [
    "RuntimeConfig",
    "ServiceDependenciesConfig",
    "ServiceSchemasConfig",
    "ServiceConfig",
    "WorkspaceConfig",
    "ProjectConfig",
    "SchemaGenerationConfig",
    "SchemasConfig",
    "PluginConfig",
    "LycheeConfig",
]
