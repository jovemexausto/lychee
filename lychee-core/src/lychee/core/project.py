import shutil
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from lychee.core.config.loader import ConfigLoader
from lychee.core.config.models import LycheeConfig, ServiceConfig
from lychee.core.service import LycheeService
from lychee.core.templates.manager import TemplateManager
from lychee.core.utils import get_logger

logger = get_logger(__name__)


class LycheeProject:
    """
    Represents the monorepo project and its configuration.

    This class handles loading the project configuration, discovering services,
    providing access to service objects, and managing project structure.
    """

    def __init__(self, path: Path, config: Optional[LycheeConfig] = None):
        self.path = path.resolve()
        self.config_path = self.path / "lychee.yaml"
        self.config = config if config else self._load_config()
        self._services: Dict[str, LycheeService] = {}
        self._load_services()

    @classmethod
    def create(
        cls,
        name: str,
        path: Path,
        template: str = "basic",
        template_manager: Optional[TemplateManager] = None,
    ) -> "LycheeProject":
        """Create a new monorepo project."""
        path = path.resolve()

        # Use template manager to create project structure
        if template_manager is None:
            template_manager = TemplateManager()

        template_manager.create_project(name=name, path=path, template=template)

        # Load the newly created project
        return cls(path)

    def _load_config(self) -> LycheeConfig:
        """Loads the main project configuration file using ConfigLoader."""
        return ConfigLoader(self.config_path).load()

    def _load_services(self) -> None:
        """
        Discovers and loads service configurations from either an explicit list
        in lychee.yaml or by scanning the services directory.
        """
        self._services = {}

        # First, check for services explicitly defined in lychee.yaml
        if self.config.services:
            for service_name, config_data in self.config.services.items():
                try:
                    # Create a ServiceConfig object from the dictionary
                    config = config_data.model_copy()
                    if config.path:
                        service_path = self.path / config.path
                    else:
                        # If no explicity path provided, fallback to own service name
                        service_path = Path(service_name).resolve()

                    service_instance = LycheeService(
                        name=service_name,
                        path=service_path,
                        config=config,
                        project=self,
                    )
                    self._services[service_name] = service_instance
                    logger.debug(f"🧭 Loaded service '{service_name}' from lychee.yaml")
                except Exception as e:
                    logger.error(
                        f"Failed to load explicit service configuration for {service_name}: {e}"
                    )
            return  # Explicit services take precedence, so we stop here.

        # If no explicit services are defined, fall back to directory scanning
        services_dir = self.path / self.config.project.workspace.services_dir
        if not services_dir.is_dir():
            logger.warning(f"Services directory not found: {services_dir}")
            return

        for service_path in services_dir.iterdir():
            if service_path.is_dir():
                service_config_path = service_path / "service.yaml"
                if service_config_path.exists():
                    try:
                        with service_config_path.open("r") as f:
                            config_data = yaml.safe_load(f)

                        service_name = service_path.name
                        config = ServiceConfig(**config_data)

                        service_instance = LycheeService(
                            name=service_name,
                            path=service_path,
                            config=config,
                            project=self,
                        )
                        self._services[service_name] = service_instance
                        rel_path = service_config_path.relative_to(self.path)
                        logger.debug(
                            f"🔍 Discovered service '{service_name}' from {rel_path}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to load service configuration for {service_path.name}: {e}"
                        )

    @property
    def services(self) -> Dict[str, LycheeService]:
        """Get all services in the project."""
        return self._services.copy()

    def get_service(self, name: str) -> Optional[LycheeService]:
        """Gets a service object by name."""
        return self._services.get(name)

    def get_all_services(self) -> Dict[str, LycheeService]:
        """Gets all discovered service objects."""
        return self._services.copy()

    def add_service(self, name: str, service_config: ServiceConfig) -> LycheeService:
        """Add a new service to the project."""
        # Create service directory
        service_path = self.path / service_config.path
        service_path.mkdir(parents=True, exist_ok=True)

        # Create service
        service = LycheeService(
            name=name, path=service_path, config=service_config, project=self
        )

        self._services[name] = service

        # TODO: Implement configuration updates
        return service

    def remove_service(self, name: str) -> None:
        """Remove a service from the project."""
        service = self._services.get(name)
        if not service:
            raise ValueError(f"Service '{name}' not found")

        # Remove from services
        del self._services[name]

        # TODO: Update configuration
        # TODO: Optionally remove service directory

    def get_service_dependencies(self, service_name: str) -> List[LycheeService]:
        """Get dependencies for a service."""
        service = self.get_service(service_name)
        if not service:
            raise ValueError(f"Service '{service_name}' not found")

        dependencies = []
        for dep_name in service.config.dependencies.services:
            dep_service = self.get_service(dep_name)
            if dep_service:
                dependencies.append(dep_service)

        return dependencies

    def get_service_dependents(self, service_name: str) -> List[LycheeService]:
        """Get services that depend on the given service."""
        dependents = []

        for service in self._services.values():
            if service_name in service.config.dependencies.services:
                dependents.append(service)

        return dependents

    async def validate(self) -> None:
        """Validate the project configuration."""
        errors = []

        # Validate services exist
        for name, service in self._services.items():
            if not service.path.exists():
                errors.append(f"Service '{name}' path does not exist: {service.path}")

        # Validate dependencies
        for name, service in self._services.items():
            for dep_name in service.config.dependencies.services:
                if dep_name not in self._services:
                    errors.append(
                        f"Service '{name}' depends on unknown service '{dep_name}'"
                    )

        # Run services' own validators
        for name, service in self._services.items():
            errors.extend(await service.validate())

        for error in errors:
            logger.error(error)

        if errors:
            raise RuntimeError(f"Project validation errors found.")

    def get_build_order(self) -> List[str]:
        """Get the order in which services should be built based on dependencies."""
        visited = set()
        temp_visited = set()
        result = []

        def visit(service_name: str) -> None:
            if service_name in temp_visited:
                raise ValueError(
                    f"Circular dependency detected involving '{service_name}'"
                )

            if service_name in visited:
                return

            temp_visited.add(service_name)

            service = self._services.get(service_name)
            if service:
                for dep_name in service.config.dependencies.services:
                    visit(dep_name)

            temp_visited.remove(service_name)
            visited.add(service_name)
            result.append(service_name)

        for service_name in self._services:
            if service_name not in visited:
                visit(service_name)

        return result

    def cleanup(self) -> None:
        """Clean up temporary files and caches."""
        # Clean up generated files
        generated_dirs = [
            self.path / "shared" / "generated",
            self.path / ".monorepo" / "cache",
            self.path / ".monorepo" / "logs",
        ]

        for dir_path in generated_dirs:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                logger.info(f"Cleaned up {dir_path}")
