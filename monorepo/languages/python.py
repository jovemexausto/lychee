"""Async Python language adapter."""

import asyncio
import shutil
import subprocess
import tomllib
from pathlib import Path
from typing import Dict, List, Optional, Set

from monorepo.languages.base import LanguageAdapter
from monorepo.utils.logging import get_logger
from monorepo.utils.process import process_manager

logger = get_logger(__name__)

DEFAULT_PYTHON_VERSION = "3.12"


class PythonAdapter(LanguageAdapter):
    """Python language adapter."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dependency_cache: Optional[Set[str]] = None

    @property
    def language(self) -> str:
        return "python"

    @property
    def supported_frameworks(self) -> List[str]:
        """Return list of supported frameworks for this language."""
        return ["fastapi", "flask"]

    @property
    def required_tools(self) -> List[str]:
        """Return list of required tools/executables for this language."""
        return ["python3", "uv"]

    async def detect_framework(self) -> Optional[str]:
        """Auto-detect Python framework."""
        for framework in self.supported_frameworks:
            if await self._has_dependency(framework):
                return framework
        return None

    async def get_start_command(self) -> List[str]:
        """Get Python service start command."""
        python_path = await self._get_python_executable()

        framework = self.service_config.framework or await self.detect_framework()
        port = self._get_port()
        entry_point = self._get_entry_point()

        # should user be able to define custom command on configs ?
        command_map = {
            "fastapi": [
                str(python_path),
                "-m",
                "uvicorn",
                entry_point,
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                str(port),
                "--app-dir",
                str(self.service_path),
            ],
            "flask": [
                str(python_path),
                "-m",
                "flask",
                "run",
                "--host",
                "0.0.0.0",
                "--port",
                str(port),
            ],
        }

        if framework in command_map:
            return command_map[framework]

        # Default Python script execution
        return [str(python_path), entry_point or "main.py"]

    async def get_build_command(self) -> List[str]:
        """Get Python build command."""
        python_path = await self._get_python_executable()
        # TODO: should'nt this come from ServiceConfig ?
        return [str(python_path), "-m", "build"]

    async def get_test_command(self) -> List[str]:
        """Get Python test command."""
        python_path = await self._get_python_executable()
        # Check for pytest
        if await self._file_exists("pytest.ini") or await self._has_dependency("pytest"):
            return [str(python_path), "-m", "pytest", "-v"]

        # Check for unittest
        if any(map(self._directory_exists, ["test", "tests"])):
            return [str(python_path), "-m", "unittest", "discover", "-p", '"test*"']

        return ['echo "No tests or testing modules found."']

    async def install_dependencies(self) -> None:
        """Install Python dependencies asynchronously."""
        # Ensure .python-version file is up to date with the service definition
        python_version = getattr(
            self.service_config.runtime, "python_version", DEFAULT_PYTHON_VERSION
        )
        python_version_file = Path(self.service_path) / ".python-version"
        await self._write_file_async(python_version_file, python_version)

        # Ensure the service has its own virtual environment with the right python version
        global_python = str(shutil.which("python3") or shutil.which("python"))
        await self._run_command_async([global_python, "-m", "pip", "install", "uv"])
        await self._run_command_async([global_python, "-m", "uv", "venv"])

        if await self._file_exists("pyproject.toml"):
            await self._install_with_uv()

        elif await self._file_exists("requirements.txt"):
            await self._install_with_pip()

        else:
            logger.warning(
                "No dependency file found. Consider adding pyproject.toml or requirements.txt."
            )

    @classmethod
    async def generate_types_from_schema(
        cls, schema_path: Path, output_path: Path, project_path: Path
    ) -> None:
        """Generate Pydantic models from JSON schema."""
        schema_name = schema_path.stem.replace(".schema", "")
        full_generated_path = output_path / f"{schema_name}.py"

        command = [
            "pnpm",
            "quicktype",
            "-s",
            "schema",
            str(schema_path),
            "-l",
            "python",
            "-o",
            str(full_generated_path),
            "--just-types",
            "--pydantic-base-model",
        ]

        await process_manager.run_command(command, str(project_path))

        if not full_generated_path.exists():
            raise RuntimeError(f"Empty output from quicktype.")

    def get_environment_variables(self) -> Dict[str, str]:
        """Get Python-specific environment variables."""
        return {
            "PYTHONPATH": str(self.service_path),
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PIP_NO_CACHE_DIR": "1",
        }

    async def validate_service(self) -> List[str]:
        """Validate Python service asynchronously."""
        errors: List[str] = (
            await super().validate_service()
            if hasattr(super(), "validate_service")
            else []
        )

        # Check for Python files
        python_files = [
            f
            for f in self.service_path.glob("**/*.py")
            if ".venv" not in f.parts and "node_modules" not in f.parts
        ]
        if not python_files:
            errors.append("No Python files found in service directory")

        # Check Python syntax
        syntax_errors = await self._check_python_syntax(python_files)
        errors.extend(syntax_errors)

        # Check for dependency files
        has_deps = any(
            [
                await self._file_exists("requirements.txt"),
                await self._file_exists("pyproject.toml"),
                await self._file_exists("setup.py"),
            ]
        )

        if not has_deps:
            errors.append(
                "No dependency file found (requirements.txt, pyproject.toml, or setup.py)"
            )

        # Validate dependency file format
        if await self._file_exists("pyproject.toml"):
            toml_errors = await self._validate_pyproject_toml()
            errors.extend(toml_errors)

        return errors

    async def _has_dependency(self, package_name: str) -> bool:
        """Check if a package is listed in dependencies."""
        if self._dependency_cache is None:
            await self._build_dependency_cache()

        if self._dependency_cache is None:
            raise RuntimeError(
                "Can't check dependencies for automatic framework detection."
            )

        return package_name.lower() in self._dependency_cache

    async def _build_dependency_cache(self) -> None:
        """Build cache of all dependencies."""
        dependencies = set()

        # Check requirements.txt
        if await self._file_exists("requirements.txt"):
            content = await self._read_file_async(self.service_path / "requirements.txt")
            for line in content.splitlines():
                line = line.strip().lower()
                if line and not line.startswith("#"):
                    # Extract package name (before ==, >=, etc.)
                    pkg_name = (
                        line.split("==")[0]
                        .split(">=")[0]
                        .split("<=")[0]
                        .split("~=")[0]
                        .strip()
                    )
                    dependencies.add(pkg_name)

        # Check pyproject.toml
        if await self._file_exists("pyproject.toml"):
            content = await self._read_file_async(self.service_path / "pyproject.toml")
            try:
                data = tomllib.loads(content)
                # Poetry dependencies
                if (
                    "tool" in data
                    and "poetry" in data["tool"]
                    and "dependencies" in data["tool"]["poetry"]
                ):
                    dependencies.update(
                        dep.lower()
                        for dep in data["tool"]["poetry"]["dependencies"].keys()
                    )

                # PEP 621 dependencies
                if "project" in data and "dependencies" in data["project"]:
                    for dep in data["project"]["dependencies"]:
                        pkg_name = (
                            dep.split("==")[0]
                            .split(">=")[0]
                            .split("<=")[0]
                            .split("~=")[0]
                            .strip()
                            .lower()
                        )
                        dependencies.add(pkg_name)
            except Exception as e:
                logger.warning(f"Failed to parse pyproject.toml: {e}")

        self._dependency_cache = dependencies

    async def _get_python_executable(self) -> Path:
        """Get the Python executable path."""
        # Check virtual environment first
        venv_path = self.service_path / ".venv"

        for bin_dir in ["bin", "Scripts"]:
            for python_name in ["python3", "python"]:
                python_path = venv_path / bin_dir / python_name
                if python_path.exists():
                    return python_path

        raise RuntimeError("Python executable not found.")

    async def _get_tool_path(self, tool: str) -> Optional[Path]:
        """Get path to a tool (poetry, etc.)."""
        venv_path = self.service_path / ".venv"
        if venv_path.exists():
            for bin_dir in ["bin", "Scripts"]:
                tool_path = venv_path / bin_dir / tool
                if tool_path.exists():
                    return tool_path

        # Check system PATH
        system_tool = shutil.which(tool)
        return Path(system_tool) if system_tool else None

    async def _file_exists(self, filename: str) -> bool:
        """Check if file exists asynchronously."""
        return (self.service_path / filename).exists()

    async def _directory_exists(self, dirname: str) -> bool:
        """Check if directory exists asynchronously."""
        return (self.service_path / dirname).is_dir()

    @classmethod
    async def _read_file_async(cls, file_path: Path) -> str:
        """Read file content asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, file_path.read_text, "utf-8")

    @classmethod
    async def _write_file_async(cls, file_path: Path, content: str) -> None:
        """Write file content asynchronously."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, file_path.write_text, content, "utf-8")

    async def _run_command_async(
        self, cmd: List[str], **kwargs
    ) -> subprocess.CompletedProcess:
        """Run command asynchronously."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=kwargs.get("cwd", self.service_path),
            env={**kwargs.get("env", {})},
        )

        stdout, stderr = await process.communicate()

        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode or 0,
            stdout=stdout.decode(),
            stderr=stderr.decode(),
        )

    async def _install_with_uv(self) -> None:
        """Install dependencies using modern tools (uv/poetry)."""
        python_path = await self._get_python_executable()
        global_uv = str(shutil.which("uv"))
        process = await self._run_command_async(
            [global_uv, "sync"],
            env={
                "UV_PROJECT_ENVIRONMENT": str(python_path).split("/bin")[0],
            },
        )
        process.check_returncode()

    async def _install_with_pip(self) -> None:
        """Install dependencies using pip."""
        python_path = await self._get_python_executable()
        await self._run_command_async(
            [str(python_path), "-m", "pip", "install", "-r", "requirements.txt"]
        )

    async def _has_build_system(self, build_system: str) -> bool:
        """Check if pyproject.toml has specific build system."""
        if not await self._file_exists("pyproject.toml"):
            return False

        try:
            content = await self._read_file_async(self.service_path / "pyproject.toml")
            data = tomllib.loads(content)

            if build_system == "poetry":
                return "tool" in data and "poetry" in data["tool"]

            build_backend = data.get("build-system", {}).get("build-backend", "")
            return build_system in build_backend
        except Exception:
            return False

    async def _check_python_syntax(self, python_files: List[Path]) -> List[str]:
        """Check Python syntax for files."""
        errors = []
        global_python = str(shutil.which("python3") or shutil.which("python"))

        for file_path in python_files:
            try:
                result = await self._run_command_async(
                    [str(global_python), "-m", "py_compile", str(file_path)]
                )
                if result.returncode != 0:
                    errors.append(f"Syntax error in {file_path}: {result.stderr.strip()}")
            except Exception as e:
                errors.append(f"Failed to check syntax for {file_path}: {e}")

        return errors

    async def _validate_pyproject_toml(self) -> List[str]:
        """Validate pyproject.toml format."""
        errors = []
        try:
            content = await self._read_file_async(self.service_path / "pyproject.toml")
            tomllib.loads(content)
        except tomllib.TOMLDecodeError as e:
            errors.append(f"Invalid pyproject.toml format: {e}")
        except Exception as e:
            errors.append(f"Failed to read pyproject.toml: {e}")

        return errors

    def _get_port(self) -> Optional[int]:
        """Get service port."""
        if self.service_config.runtime and self.service_config.runtime.port:
            return self.service_config.runtime.port

        if not self.service_config.framework:
            return None

        import random

        port = 8000 + random.choice(range(100))
        logger.warning(
            f"No port configured for {self.service_config.path}, using random port {port}"
        )
        return port

    def _get_entry_point(self) -> str:
        """Get service entry point."""
        if self.service_config.runtime and self.service_config.runtime.entry_point:
            return self.service_config.runtime.entry_point
        return "main:app"
