# """TypeScript language adapter."""

# import json
# import subprocess
# from pathlib import Path
# from typing import Dict, List, Optional

# from monorepo.languages.base import LanguageAdapter
# from monorepo.utils.logging import get_logger

# logger = get_logger(__name__)


# class TypeScriptAdapter(LanguageAdapter):
#     """TypeScript language adapter."""

#     @property
#     def language(self) -> str:
#         return "typescript"

#     def detect_framework(self) -> Optional[str]:
#         """Auto-detect TypeScript framework."""
#         package_json = self.service_path / "package.json"

#         if not package_json.exists():
#             return None

#         with package_json.open() as f:
#             package_data = json.load(f)

#         dependencies = {**package_data.get("dependencies", {}), **package_data.get("devDependencies", {})}

#         # Check for frameworks
#         if "next" in dependencies:
#             return "nextjs"
#         elif "express" in dependencies:
#             return "express"
#         elif "@nestjs/core" in dependencies:
#             return "nestjs"
#         elif "react" in dependencies and "react-dom" in dependencies:
#             return "react"
#         elif "vue" in dependencies:
#             return "vue"
#         elif "@angular/core" in dependencies:
#             return "angular"

#         return None

#     def get_start_command(self) -> List[str]:
#         """Get TypeScript service start command."""
#         framework = self.service_config.framework or self.detect_framework()
#         package_manager = self._get_package_manager()

#         if framework == "nextjs":
#             return [package_manager, "run", "dev"]
#         elif framework == "express":
#             if (self.service_path / "tsconfig.json").exists():
#                 return ["tsx", "watch", self.service_config.runtime.entry_point or "src/index.ts"]
#             else:
#                 return ["node", self.service_config.runtime.entry_point or "src/index.js"]
#         elif framework == "nestjs":
#             return [package_manager, "run", "start:dev"]
#         elif framework == "react":
#             return [package_manager, "run", "start"]
#         else:
#             return [package_manager, "run", "dev"]

#     def get_build_command(self) -> List[str]:
#         """Get TypeScript build command."""
#         package_manager = self._get_package_manager()

#         # Check if there's a build script
#         package_json = self.service_path / "package.json"
#         if package_json.exists():
#             with package_json.open() as f:
#                 package_data = json.load(f)
#                 scripts = package_data.get("scripts", {})

#                 if "build" in scripts:
#                     return [package_manager, "run", "build"]

#         # Fallback to TypeScript compiler
#         if (self.service_path / "tsconfig.json").exists():
#             return ["tsc"]

#         return [package_manager, "run", "build"]

#     def get_test_command(self) -> List[str]:
#         """Get TypeScript test command."""
#         package_manager = self._get_package_manager()

#         package_json = self.service_path / "package.json"
#         if package_json.exists():
#             with package_json.open() as f:
#                 package_data = json.load(f)
#                 scripts = package_data.get("scripts", {})

#                 if "test" in scripts:
#                     return [package_manager, "run", "test"]

#         # Check for common test frameworks
#         if (self.service_path / "jest.config.js").exists():
#             return ["jest"]
#         elif (self.service_path / "vitest.config.ts").exists():
#             return ["vitest", "run"]

#         return [package_manager, "test"]

#     def install_dependencies(self) -> None:
#         """Install TypeScript/Node.js dependencies."""
#         package_manager = self._get_package_manager()

#         if (self.service_path / "package.json").exists():
#             subprocess.run([package_manager, "install"], cwd=self.service_path, check=True)

#     def generate_types_from_schema(self, schema_path: Path, output_path: Path) -> None:
#         """Generate TypeScript interfaces from JSON schema."""
#         with schema_path.open() as f:
#             schema = json.load(f)

#         # Generate TypeScript interface
#         interface_code = self._generate_typescript_interface(schema)

#         # Ensure output directory exists
#         output_path.parent.mkdir(parents=True, exist_ok=True)

#         # Write interface to file
#         with output_path.open("w") as f:
#             f.write(interface_code)

#         logger.info(f"Generated TypeScript types: {output_path}")

#     def get_environment_variables(self) -> Dict[str, str]:
#         """Get TypeScript-specific environment variables."""
#         env = {
#             "NODE_ENV": "development",
#         }

#         # Add TypeScript specific vars
#         if (self.service_path / "tsconfig.json").exists():
#             env["TS_NODE_PROJECT"] = str(self.service_path / "tsconfig.json")

#         return env

#     def validate_service(self) -> List[str]:
#         """Validate TypeScript service."""
#         errors = super().validate_service()

#         # Check for package.json
#         if not (self.service_path / "package.json").exists():
#             errors.append("No package.json found in service directory")

#         # Check for TypeScript files
#         has_ts_files = any(
#             [
#                 list(self.service_path.glob("*.ts")),
#                 list(self.service_path.glob("**/*.ts")),
#                 list(self.service_path.glob("*.tsx")),
#                 list(self.service_path.glob("**/*.tsx")),
#             ]
#         )

#         if not has_ts_files and not any(self.service_path.glob("*.js")):
#             errors.append("No TypeScript or JavaScript files found")

#         return errors

#     def _get_package_manager(self) -> str:
#         """Determine which package manager to use."""
#         # Check for lock files to determine package manager
#         if (self.service_path / "pnpm-lock.yaml").exists():
#             return "pnpm"
#         elif (self.service_path / "yarn.lock").exists():
#             return "yarn"
#         else:
#             return "npm"
