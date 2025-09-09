It's great that you're building a monorepo manager\! Adding support for shared **packages** (or libraries) within your monorepo is a crucial next step for code reuse and consistency.

Based on your project structure, here's how you can approach adding support for shared Python and TypeScript packages:

## Strategy for Shared Packages

The core idea is to treat these shared packages as first-class "services" or components within your monorepo, but with a different purpose: **consumption by other services rather than direct execution**.

You'll need to:

1.  **Define a standard location** for these packages.
2.  **Configure them in your `lychee.yaml`** similar to how services are defined.
3.  **Integrate with package managers** (Poetry/pip for Python, npm/yarn for TypeScript) to handle local dependencies.
4.  **Potentially leverage schema generation** for cross-language package interactions.

## Implementation Steps

Here's a breakdown of how to implement this, focusing on the necessary code modifications and additions.

### 1\. Project Structure Adjustments

Consider adding a dedicated directory for shared packages:

```
monorepo-manager/
├── ...
├── packages/                 # New directory for shared packages
│   ├── __init__.py
│   ├── python/
│   │   ├── shared_utils/     # Example Python package
│   │   │   ├── pyproject.toml
│   │   │   ├── src/
│   │   │   │   └── shared_utils/
│   │   │   │       ├── __init__.py
│   │   │   │       └── ...
│   │   │   └── tests/
│   │   ├── another_lib/
│   │   │   ├── ...
│   ├── typescript/
│   │   ├── shared_types/     # Example TypeScript package
│   │   │   ├── package.json
│   │   │   ├── src/
│   │   │   │   └── index.ts
│   │   │   └── tests/
│   │   ├── ui_components/
│   │   │   ├── ...
├── monorepo/
│   ├── ...
└── assets/
    ├── schemas/
    │   ├── monorepo.schema.json
    │   ├── service.schema.json
    │   ├── package.schema.json   # New schema for packages
    │   └── ...
    └── templates/
        ├── lychee.yaml
        ├── services.yml
        ├── packages.yml          # New config file/structure for packages
        └── ...
```

### 2\. Configuration Schema and Models

You'll need to define how packages are represented in your configuration.

#### `assets/schemas/package.schema.json` (New File)

```json
{
  "type": "object",
  "properties": {
    "path": {
      "type": "string",
      "description": "Relative path to the package directory within the monorepo."
    },
    "type": {
      "type": "string",
      "enum": ["python", "typescript"],
      "description": "The language/type of the package."
    },
    "dependencies": {
      "type": "object",
      "properties": {
        "packages": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Names of other monorepo packages this package depends on."
        },
        "services": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Names of monorepo services this package provides components for."
        }
      },
      "additionalProperties": false
    },
    "exports": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of entry points or modules exported by the package."
    },
    "build": {
      "type": "object",
      "properties": {
        "command": { "type": "string" },
        "output_dir": { "type": "string" }
      },
      "additionalProperties": false
    },
    "test": {
      "type": "object",
      "properties": {
        "command": { "type": "string" }
      },
      "additionalProperties": false
    }
  },
  "required": ["path", "type"],
  "additionalProperties": true
}
```

#### `monorepo/config/models.py` (Update)

Add a `PackageConfig` model and include it in your main `MonorepoConfig`.

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

# ... other imports

class PackageDependencies(BaseModel):
    packages: List[str] = Field(default_factory=list)
    services: List[str] = Field(default_factory=list)

class PackageBuild(BaseModel):
    command: Optional[str] = None
    output_dir: Optional[str] = None

class PackageTest(BaseModel):
    command: Optional[str] = None

class PackageConfig(BaseModel):
    path: str = Field(...)
    type: str = Field(...)  # "python" or "typescript"
    dependencies: PackageDependencies = Field(default_factory=PackageDependencies)
    exports: List[str] = Field(default_factory=list)
    build: Optional[PackageBuild] = None
    test: Optional[PackageTest] = None
    # Add any other package-specific configurations here

class MonorepoConfig(BaseModel):
    version: str = "1.0"
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    services: Dict[str, ServiceConfig] = Field(default_factory=dict)
    packages: Dict[str, PackageConfig] = Field(default_factory=dict) # Add this line
    env: Optional[Dict[str, str]] = None

    # ... rest of the MonorepoConfig
```

#### `assets/templates/lychee.yaml` (Example)

You might want a section for packages in your root config file.

```yaml
version: 1.0

project:
  name: MyMonorepo
  version: 0.1.0
  description: A polyglot monorepo

services:
  api:
    path: services/api
    type: python
    framework: fastapi
    runtime:
      port: 8000
    dependencies:
      services: []

packages:
  shared-utils:
    path: packages/python/shared_utils
    type: python
    dependencies:
      packages: [] # No internal package dependencies for this example
    exports:
      - src/shared_utils

  shared-types:
    path: packages/typescript/shared_types
    type: typescript
    dependencies:
      packages: []
    exports:
      - dist/index.d.ts # Assuming build output
```

### 3\. `MonorepoProject` Class Updates

Modify `MonorepoProject` to load and manage packages.

#### `monorepo/core/project.py` (Update)

```python
# ... existing imports ...
from monorepo.config.models import MonorepoConfig, ServiceConfig, PackageConfig # Add PackageConfig
# ... other imports ...

class MonorepoProject:
    # ... existing __init__, load, create methods ...

    def __init__(self, path: Path, config: MonorepoConfig):
        self.path = path.resolve()
        self.config = config
        self._services: Dict[str, Service] = {}
        self._packages: Dict[str, Package] = {} # New attribute for packages
        self._load_services()
        self._load_packages() # New method call

    # ... existing _load_services method ...

    def _load_services(self) -> None:
        """Load all services from configuration."""
        self._services = {}
        if not self.config.services:
            return
        for name, service_config in self.config.services.items():
            service_path = self.path / service_config.path
            service = Service(
                name=name,
                path=service_path,
                config=service_config,
                project=self
            )
            self._services[name] = service

    def _load_packages(self) -> None: # New method
        """Load all packages from configuration."""
        self._packages = {}
        if not self.config.packages:
            return
        for name, package_config in self.config.packages.items():
            package_path = self.path / package_config.path
            package = Package(
                name=name,
                path=package_path,
                config=package_config,
                project=self
            )
            self._packages[name] = package

    @property
    def services(self) -> Dict[str, Service]:
        """Get all services in the project."""
        return self._services.copy()

    @property # New property for packages
    def packages(self) -> Dict[str, Package]:
        """Get all packages in the project."""
        return self._packages.copy()

    def get_service(self, name: str) -> Optional[Service]:
        """Get a specific service by name."""
        return self._services.get(name)

    def get_package(self, name: str) -> Optional[Package]: # New method
        """Get a specific package by name."""
        return self._packages.get(name)

    # ... rest of MonorepoProject class ...
```

### 4\. New `Package` Class

Create a new class to represent a shared package, similar to `Service`.

#### `monorepo/core/package.py` (New File)

```python
"""Core package management functionality for shared libraries."""

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

from monorepo.config.models import PackageConfig
from monorepo.utils.logging import get_logger
from monorepo.utils.process import ProcessManager # Assuming you have this for services too

if TYPE_CHECKING:
    from monorepo.core.project import MonorepoProject

logger = get_logger(__name__)

class Package:
    """Represents a shared package in the monorepo."""

    def __init__(
        self,
        name: str,
        path: Path,
        config: PackageConfig,
        project: "MonorepoProject"
    ):
        self.name = name
        self.path = path.resolve()
        self.config = config
        self.project = project
        self._process_manager = ProcessManager() # Might not be needed if packages aren't long-running

    @property
    def is_installed(self) -> bool:
        """Check if the package is installed locally (e.g., via symlink or published)."""
        # This depends on your strategy. For local development, it might mean it's built.
        # For more complex setups, you might check if it's symlinked into a virtual env.
        return True # Placeholder

    def install_dependencies(self) -> None:
        """Install package dependencies (e.g., pyproject.toml or package.json)."""
        if self.config.type == "python":
            self._install_python_dependencies()
        elif self.config.type == "typescript":
            self._install_typescript_dependencies()
        else:
            logger.warning(f"No dependency installation defined for package type: {self.config.type}")

    def _install_python_dependencies(self) -> None:
        """Install Python package dependencies using Poetry."""
        pyproject_path = self.path / "pyproject.toml"
        if pyproject_path.exists():
            logger.info(f"Installing Python dependencies for package '{self.name}' using Poetry...")
            # You might want to install into a shared venv or the consuming service's venv
            # For now, assuming local install within the package itself
            subprocess.run(["poetry", "install"], cwd=self.path, check=True)
        else:
            logger.warning(f"No pyproject.toml found for Python package '{self.name}' at {self.path}")

    def _install_typescript_dependencies(self) -> None:
        """Install TypeScript package dependencies using npm/yarn."""
        package_json_path = self.path / "package.json"
        if package_json_path.exists():
            package_manager = self.project.config.project.package_managers.get("typescript", "npm")
            logger.info(f"Installing TypeScript dependencies for package '{self.name}' using {package_manager}...")
            subprocess.run([package_manager, "install"], cwd=self.path, check=True)
        else:
            logger.warning(f"No package.json found for TypeScript package '{self.name}' at {self.path}")

    def build(self) -> None:
        """Build the package if a build command is defined."""
        if self.config.build and self.config.build.command:
            logger.info(f"Building package '{self.name}' with command: '{self.config.build.command}'...")
            # Execute the build command
            # For Python, this might be 'poetry build' or similar.
            # For TypeScript, 'npm run build' or 'tsc'.
            # Consider capturing output and handling errors.
            command_parts = self.config.build.command.split()
            subprocess.run(command_parts, cwd=self.path, check=True)
            logger.info(f"Package '{self.name}' built successfully.")
        else:
            logger.info(f"No build command defined for package '{self.name}'. Skipping build.")

    def test(self) -> None:
        """Run tests for the package if a test command is defined."""
        if self.config.test and self.config.test.command:
            logger.info(f"Running tests for package '{self.name}' with command: '{self.config.test.command}'...")
            command_parts = self.config.test.command.split()
            subprocess.run(command_parts, cwd=self.path, check=True)
            logger.info(f"Package '{self.name}' tests passed.")
        else:
            logger.info(f"No test command defined for package '{self.name}'. Skipping tests.")

    # Add other methods as needed, e.g., for publishing to a local registry if applicable.
```

### 5\. Integrate with CLI Commands

You'll want to add commands to manage these packages, such as installing, building, and testing them.

#### `monorepo/cli/commands/build.py` (Update)

Modify the `build` command to also build packages.

```python
# ... existing imports ...
from monorepo.core.project import MonorepoProject
from monorepo.utils.logging import get_logger
from monorepo.utils.output import console # Assuming console is defined elsewhere

logger = get_logger(__name__)

@click.group()
def build():
    """Build services and packages."""
    pass

@build.command(name="all") # Renamed to 'all' to avoid conflict with package/service build methods
@click.option(
    "--services", "-s",
    is_flag=True,
    default=True,
    help="Build services."
)
@click.option(
    "--packages", "-p",
    is_flag=True,
    default=True,
    help="Build packages."
)
@click.option(
    "--service-name", "-sn",
    multiple=True,
    help="Specific service(s) to build."
)
@click.option(
    "--package-name", "-pn",
    multiple=True,
    help="Specific package(s) to build."
)
@click.pass_context
def build_all(
    ctx: click.Context,
    services: bool,
    packages: bool,
    service_name: List[str],
    package_name: List[str]
):
    """Build all services and/or packages in the monorepo."""
    try:
        working_dir = ctx.obj["working_dir"]
        project = MonorepoProject(working_dir)

        if services:
            target_services = service_name if service_name else project.services.keys()
            for svc_name in target_services:
                service = project.get_service(svc_name)
                if service:
                    console.print(f"[blue]Building service: {svc_name}...[/blue]")
                    service.build()
                    console.print(f"[green]✅ Service '{svc_name}' built.[/green]")
                else:
                    console.print(f"[yellow]Warning: Service '{svc_name}' not found.[/yellow]")

        if packages: # New section for packages
            target_packages = package_name if package_name else project.packages.keys()
            for pkg_name in target_packages:
                package = project.get_package(pkg_name)
                if package:
                    console.print(f"[blue]Building package: {pkg_name}...[/blue]")
                    package.build()
                    console.print(f"[green]✅ Package '{pkg_name}' built.[/green]")
                else:
                    console.print(f"[yellow]Warning: Package '{pkg_name}' not found.[/yellow]")

        console.print("[bold green]All selected items built successfully.[/bold green]")

    except Exception as e:
        logger.error(f"Failed to build: {e}")
        console.print(f"[red]❌ Failed to build: {e}[/red]")
        ctx.exit(1)

# Add this to your main cli.py to register the build group
# from monorepo.cli.commands.build import build
# cli.add_command(build)

# You might also want individual build commands for services/packages
# e.g., `build service <name>` and `build package <name>`
```

#### `monorepo/cli/commands/test.py` (Update)

Similarly, update the `test` command.

```python
# ... existing imports ...
from monorepo.core.project import MonorepoProject
from monorepo.utils.logging import get_logger
from monorepo.utils.output import console

logger = get_logger(__name__)

@click.group()
def test():
    """Run tests for services and packages."""
    pass

@test.command(name="all")
@click.option(
    "--services", "-s",
    is_flag=True,
    default=True,
    help="Test services."
)
@click.option(
    "--packages", "-p",
    is_flag=True,
    default=True,
    help="Test packages."
)
@click.option(
    "--service-name", "-sn",
    multiple=True,
    help="Specific service(s) to test."
)
@click.option(
    "--package-name", "-pn",
    multiple=True,
    help="Specific package(s) to test."
)
@click.pass_context
def test_all(
    ctx: click.Context,
    services: bool,
    packages: bool,
    service_name: List[str],
    package_name: List[str]
):
    """Run tests for all services and/or packages in the monorepo."""
    try:
        working_dir = ctx.obj["working_dir"]
        project = MonorepoProject(working_dir)

        if services:
            target_services = service_name if service_name else project.services.keys()
            for svc_name in target_services:
                service = project.get_service(svc_name)
                if service:
                    console.print(f"[blue]Testing service: {svc_name}...[/blue]")
                    service.test()
                    console.print(f"[green]✅ Service '{svc_name}' tests passed.[/green]")
                else:
                    console.print(f"[yellow]Warning: Service '{svc_name}' not found.[/yellow]")

        if packages: # New section for packages
            target_packages = package_name if package_name else project.packages.keys()
            for pkg_name in target_packages:
                package = project.get_package(pkg_name)
                if package:
                    console.print(f"[blue]Testing package: {pkg_name}...[/blue]")
                    package.test()
                    console.print(f"[green]✅ Package '{pkg_name}' tests passed.[/green]")
                else:
                    console.print(f"[yellow]Warning: Package '{pkg_name}' not found.[/yellow]")

        console.print("[bold green]All selected items tested successfully.[/bold green]")

    except Exception as e:
        logger.error(f"Failed to test: {e}")
        console.print(f"[red]❌ Failed to test: {e}[/red]")
        ctx.exit(1)

# Add this to your main cli.py to register the test group
# from monorepo.cli.commands.test import test
# cli.add_command(test)
```

#### Add an `install` Command

A command to install dependencies for all services and packages.

#### `monorepo/cli/commands/install.py` (New File)

```python
import asyncclick as click
from rich.console import Console

from monorepo.core.project import MonorepoProject
from monorepo.utils.logging import get_logger

console = Console()
logger = get_logger(__name__)

@click.command()
@click.option(
    "--services", "-s",
    is_flag=True,
    default=True,
    help="Install dependencies for services."
)
@click.option(
    "--packages", "-p",
    is_flag=True,
    default=True,
    help="Install dependencies for packages."
)
@click.pass_context
def install(
    ctx: click.Context,
    services: bool,
    packages: bool
):
    """Install dependencies for services and packages."""
    try:
        working_dir = ctx.obj["working_dir"]
        project = MonorepoProject(working_dir)

        if services:
            console.print("[blue]Installing service dependencies...[/blue]")
            for name, service in project.services.items():
                console.print(f"  Installing for service: {name}")
                service.install_dependencies()
            console.print("[green]✅ Service dependencies installed.[/green]")

        if packages:
            console.print("[blue]Installing package dependencies...[/blue]")
            for name, package in project.packages.items():
                console.print(f"  Installing for package: {name}")
                package.install_dependencies()
            console.print("[green]✅ Package dependencies installed.[/green]")

        console.print("[bold green]All dependencies installed successfully.[/bold green]")

    except Exception as e:
        logger.error(f"Failed to install dependencies: {e}")
        console.print(f"[red]❌ Failed to install dependencies: {e}[/red]")
        ctx.exit(1)

# Add to monorepo/cli/main.py:
# from monorepo.cli.commands.install import install
# cli.add_command(install)
```

### 6\. Handling Local Package Dependencies

This is the trickiest part and depends on your desired development workflow:

- **Python:**

  - **Poetry:** You can configure `pyproject.toml` in your consuming services to point to local paths for dependencies (e.g., using `poetry add ../../packages/python/shared_utils`). This requires careful path management.
  - **Editable Installs:** Your `install` command could run `pip install -e <path_to_package>` for Python packages.
  - **Virtual Environments:** Consider how virtual environments interact. You might need to ensure services use the correct virtual environment that has packages installed.

- **TypeScript:**

  - **`npm link` / `yarn link`:** You can automate `npm link` or `yarn link` from within your `install` command to create symlinks in the `node_modules` of consuming services to your local package directories.
  - **Workspace Protocols:** If using npm or Yarn workspaces, your `package.json` files would define dependencies using workspace protocols (e.g., `"shared-utils": "workspace:*"`), and the package manager handles the linking. Your `install` command would then just run `npm install` or `yarn install` at the root or within each service.
  - **Bundling/Transpiling:** For TypeScript packages, you'll typically want to build them (e.g., to a `dist` folder) and then have services consume the built artifacts. Your `build` commands will be critical here.

**Recommendation:** For TypeScript, using npm/Yarn workspaces is often the most robust approach. For Python, editable installs or carefully managed local path dependencies in `pyproject.toml` are common.

### Example Workflow

1.  **Initialize Monorepo:** `monorepo init my-monorepo`
2.  **Add a Python package:** Create `packages/python/my_lib` with `pyproject.toml` and source code. Add it to `lychee.yaml`.
3.  **Add a TypeScript package:** Create `packages/typescript/my_types` with `package.json` and source code. Add it to `lychee.yaml`.
4.  **Add a service that uses them:** Create a service (e.g., `services/my_app`) and configure its `dependencies.packages` in `lychee.yaml` to include `my_lib` and `my_types`.
5.  **Install Dependencies:** `monorepo install` (This should install dependencies for services and packages, and potentially link packages).
6.  **Build Packages:** `monorepo build package` (or `monorepo build -pn my_lib -pn my_types`)
7.  **Build Service:** `monorepo build service` (or `monorepo build -sn my_app`)
8.  **Develop Service:** `monorepo dev start -s my_app`

This setup provides a solid foundation for managing shared code across different services and languages within your monorepo. Remember to flesh out the error handling and logging for each new command and class.
