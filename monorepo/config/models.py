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


class ServiceDependencies(BaseModel):
    """Service dependencies configuration."""

    services: List[str] = Field(default_factory=list)
    external: List[str] = Field(default_factory=list)


class ApiConfig(BaseModel):
    """API configuration for a service."""

    prefix: Optional[str] = None
    docs: bool = False
    cors: bool = False
    rate_limiting: bool = False
    authentication: bool = False
    websockets: bool = False


class ServiceSchemasConfig(BaseModel):
    mount_dir: Optional[str] = None  # symlink path for the generated types


class ServiceConfig(BaseModel):
    """Configuration for a single service."""

    type: str  # python, typescript, etc.
    path: str
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)
    dependencies: ServiceDependencies = Field(default_factory=ServiceDependencies)
    schemas: ServiceSchemasConfig = Field(default_factory=ServiceSchemasConfig)
    framework: Optional[str] = None
    api: Optional[ApiConfig] = None
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
    package_managers: Dict[str, str] = Field(default_factory=dict)
    workspace: WorkspaceConfig = Field(default_factory=WorkspaceConfig)


class PortsConfig(BaseModel):
    """Port configuration."""

    range: List[int] = Field(default_factory=lambda: [8000, 9000])
    proxy: int = 4000
    auto_assign: bool = True


class WatchConfig(BaseModel):
    """File watching configuration."""

    enabled: bool = True
    debounce: int = 200
    ignore: List[str] = Field(
        default_factory=lambda: [".git", "node_modules", "__pycache__"]
    )


class DevelopmentConfig(BaseModel):
    """Development configuration."""

    mode: str = "hybrid"
    auto_start: bool = True
    health_checks: bool = True
    ports: PortsConfig = Field(default_factory=PortsConfig)
    watch: WatchConfig = Field(default_factory=WatchConfig)


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


class DefaultServiceConfig(BaseModel):
    """Default service configuration."""

    healthcheck: str = "/health"
    metrics: str = "/metrics"
    restart_policy: str = "on_failure"


class DefaultDockerConfig(BaseModel):
    """Default Docker configuration."""

    auto_generate: bool = True
    multi_stage: bool = True
    optimization: str = "development"


class DefaultsConfig(BaseModel):
    """Default configurations."""

    service: DefaultServiceConfig = Field(default_factory=DefaultServiceConfig)
    docker: DefaultDockerConfig = Field(default_factory=DefaultDockerConfig)


class PluginConfig(BaseModel):
    """Plugin configuration."""

    name: str
    version: str
    config: Optional[Dict[str, Any]] = None


class ToolsConfig(BaseModel):
    """Tools configuration."""

    cli: Dict[str, Any] = Field(default_factory=dict)


class MonorepoConfig(BaseModel):
    """Main monorepo configuration."""

    version: float

    includes: List[str] = Field(default_factory=list)

    project: ProjectConfig = Field(default_factory=ProjectConfig)
    development: DevelopmentConfig = Field(default_factory=DevelopmentConfig)
    schemas: SchemasConfig = Field(default_factory=SchemasConfig)
    defaults: DefaultsConfig = Field(default_factory=DefaultsConfig)

    environment: Optional[Dict[str, str]] = None
    plugins: List[PluginConfig] = Field(default_factory=list)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)

    # Services loaded from separate file
    services: Optional[Dict[str, ServiceConfig]] = None

    class Config:
        """Pydantic configuration."""

        extra = "allow"  # Allow additional fields
