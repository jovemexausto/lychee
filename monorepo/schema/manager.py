import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional, Set

from monorepo.core.project import MonorepoProject
from monorepo.languages.registry import language_registry
from monorepo.schema.validator import SchemaValidator
from monorepo.schema.watcher import SchemaWatcher
from monorepo.utils.fs import ensure_symlink, find_broken_symlinks, list_symlinks
from monorepo.utils.logging import get_logger
from monorepo.utils.process import ProcessManager

logger = get_logger(__name__)


class SchemaManager:
    """Manages schemas and type generation for the monorepo."""

    def __init__(self, project: MonorepoProject):
        self.project = project
        self.validator = SchemaValidator()
        self.process = ProcessManager()
        self.watcher: Optional[SchemaWatcher] = None

    async def initialize(self) -> None:
        """Initialize the schema management system."""
        # Create schema directories
        await self._create_schema_directories()

        # Load existing schemas
        await self._load_schemas()

        # Generate types for existing schemas
        await self.generate_all_types()

        # Start watching if enabled
        # TODO: decidir como implement o watcher / hot reloading
        # if self.project.config.schemas.generation.on_change:
        #     self.start_watching()

    async def _create_schema_directories(self) -> None:
        """Create necessary directories for schema management."""
        schema_dir = self.project.path / self.project.config.schemas.dir
        schema_dir.mkdir(exist_ok=True)

        # Create output directories for generated types
        shared_dir = self.project.path / self.project.config.schemas.output_path
        shared_dir.mkdir(exist_ok=True)

        for language in self.project.config.project.languages:
            language_dir = shared_dir / language
            language_dir.mkdir(exist_ok=True)

    async def _load_schemas(self) -> None:
        """Load all schema definitions."""
        schema_dir = self.project.path / self.project.config.schemas.dir

        for schema_file in schema_dir.glob("*.schema.json"):
            try:
                with schema_file.open() as f:
                    schema = json.load(f)

                # Validate schema
                validation_errors = self.validator.validate_schema(schema)
                if validation_errors:
                    logger.warning(f"Schema validation warnings for {schema_file.name}: {validation_errors}")

                logger.debug(f"Loaded schema: '{schema_file.name}'")

            except Exception as e:
                logger.error(f"Failed to load schema {schema_file.name}: {e}")

    async def add_schema(self, name: str, schema: Dict) -> Path:
        """Add a new schema definition."""
        # Validate schema
        validation_errors = self.validator.validate_schema(schema)
        if validation_errors:
            raise ValueError(f"Invalid schema: {validation_errors}")

        # Save schema file
        schema_file = self.project.path / "schemas" / f"{name}.schema.json"
        with schema_file.open("w") as f:
            json.dump(schema, f, indent=2)

        logger.info(f"Added schema: {name}")

        # Generate types
        await self.generate_types_for_schema(schema_file)

        return schema_file

    async def update_schema(self, name: str, schema: Dict) -> None:
        """Update an existing schema."""
        schema_file = self.project.path / "schemas" / f"{name}.schema.json"

        if not schema_file.exists():
            raise ValueError(f"Schema {name} does not exist")

        # Load current schema for comparison
        with schema_file.open() as f:
            current_schema = json.load(f)

        # Check for breaking changes
        breaking_changes = self._check_breaking_changes(current_schema, schema)
        if breaking_changes:
            raise ValueError(f"Breaking changes detected: {breaking_changes}")

        # Update schema
        with schema_file.open("w") as f:
            json.dump(schema, f, indent=2)

        logger.info(f"Updated schema: {name}")

        # Regenerate types
        await self.generate_types_for_schema(schema_file)

    async def generate_all_types(self) -> None:
        """Generate types for all schemas."""
        schema_dir = self.project.path / "schemas"

        for schema_file in schema_dir.glob("*.schema.json"):
            await self.generate_types_for_schema(schema_file)

        # After generating all types, (re)mount_dir into services
        self._mount_types_for_services()

    def _mount_types_for_services(self) -> None:
        """Symlink generated types into service schemas.mount_dir locations."""
        for service_key, service in self.project.get_all_services().items():
            mount_dir = getattr(getattr(service.config, "schemas", None), "mount_dir", None)
            if not mount_dir:
                continue
            language = getattr(service.config, "type", None)
            if not language:
                continue
            source = self.project.path / self.project.config.schemas.output_path / language
            target = service.path / mount_dir
            try:
                # Find and remove broken symlinks in the service directory
                broken_links = find_broken_symlinks(service.path)
                for broken_link in broken_links:
                    logger.info(f"Removing broken symlink: {broken_link}")
                    broken_link.unlink()

                # Find all existing symlinks in the service directory
                existing_symlinks = list_symlinks(service.path)
                for symlink in existing_symlinks:
                    # If the symlink points to a different source but has the same target name, remove it
                    if symlink == target and symlink.resolve() != source.resolve():
                        logger.info(f"Removing outdated symlink: {symlink} (pointing to {symlink.resolve()})")
                        symlink.unlink()

                # Create the new symlink
                ensure_symlink(source, target)
                logger.info(f"🧩 Schemas linked into {service_key}: {target} -> {source}")
            except Exception as e:
                logger.error(f"Failed to mount types for service {service_key}: {e}")

    async def generate_types_for_schema(self, schema_path: Path) -> None:
        """Generate types for a specific schema."""
        try:
            schema_name = schema_path.stem.replace(".schema", "")

            for language in self.project.config.project.languages:
                output_dir = self.project.path / self.project.config.schemas.output_path / language
                output_dir.mkdir(parents=True, exist_ok=True)
                adapter_class = language_registry.get_adapter_class(language)
                if not adapter_class:
                    return
                await adapter_class.generate_types_from_schema(
                    schema_path=schema_path,
                    output_path=output_dir,
                    project_path=self.project.path,
                )

            logger.info(f"📝 Generated types for schema: [blue]'{schema_name}'[/blue]")
        except Exception as e:
            logger.error(f"Failed to generate types for {schema_path.name}: {e}")

    def validate_all_schemas(self) -> Dict[str, List[str]]:
        """Validate all schemas and return any errors."""
        results = {}
        schema_dir = self.project.path / "schemas"

        for schema_file in schema_dir.glob("*.schema.json"):
            try:
                with schema_file.open() as f:
                    schema = json.load(f)

                errors = self.validator.validate_schema(schema)
                if errors:
                    results[schema_file.name] = errors

            except Exception as e:
                results[schema_file.name] = [f"Failed to load schema: {e}"]

        return results

    def get_schema_dependencies(self, schema_name: str) -> Set[str]:
        """Get services that depend on a specific schema."""
        dependencies = set()
        # This would be populated from the configuration
        # For now, return empty set as proof of concept
        return dependencies

    def start_watching(self) -> None:
        """Start watching schema files for changes."""
        if self.watcher is None:

            def on_change(path: Path):
                loop = asyncio.get_running_loop()
                return loop.run_until_complete(self._on_schema_change(path))

            self.watcher = SchemaWatcher(schema_dir=self.project.path / "schemas", on_change_callback=on_change)
            self.watcher.start()
            logger.info("Started watching schema files for changes")

    def stop_watching(self) -> None:
        """Stop watching schema files."""
        if self.watcher:
            self.watcher.stop()
            self.watcher = None
            logger.info("Stopped watching schema files")

    async def _on_schema_change(self, schema_file: Path) -> None:
        """Handle schema file changes."""
        logger.info(f"Schema file changed: {schema_file.name}")

        # Regenerate types
        await self.generate_types_for_schema(schema_file)

        # Notify dependent services (would trigger restart in development)
        dependencies = self.get_schema_dependencies(schema_file.stem.replace(".schema", ""))
        if dependencies:
            logger.info(f"Services affected by schema change: {dependencies}")

    def _check_breaking_changes(self, old_schema: Dict, new_schema: Dict) -> List[str]:
        """Check for breaking changes between schema versions."""
        breaking_changes = []

        old_props = old_schema.get("properties", {})
        new_props = new_schema.get("properties", {})
        old_required = set(old_schema.get("required", []))
        new_required = set(new_schema.get("required", []))

        # Check for removed properties
        removed_props = set(old_props.keys()) - set(new_props.keys())
        for prop in removed_props:
            breaking_changes.append(f"Removed property: {prop}")

        # Check for newly required properties
        newly_required = new_required - old_required
        for prop in newly_required:
            breaking_changes.append(f"Property '{prop}' is now required")

        # Check for type changes
        for prop in old_props:
            if prop in new_props:
                old_type = old_props[prop].get("type")
                new_type = new_props[prop].get("type")
                if old_type != new_type:
                    breaking_changes.append(f"Type changed for '{prop}': {old_type} -> {new_type}")

        return breaking_changes
