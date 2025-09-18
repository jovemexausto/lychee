from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from lychee.application.ports.schema_compiler import SchemaCompilerPort
from lychee.core.utils.process import process_manager


class QuicktypePythonCompiler(SchemaCompilerPort):
    """Compile JSON Schema to Python (Pydantic-friendly) types using quicktype via pnpm."""

    def supports(self, schema_format: str, target_language: str) -> bool:
        return schema_format.lower() in {"json_schema", "json-schema"} and target_language.lower() == "python"

    async def compile(
        self,
        schema_path: Path,
        output_dir: Path,
        project_path: Path,
        options: Optional[Dict] = None,
    ) -> None:
        schema_name = schema_path.stem.replace(".schema", "")
        output_dir.mkdir(parents=True, exist_ok=True)
        full_generated_path = output_dir / f"{schema_name}.py"

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
            raise RuntimeError("Empty output from quicktype.")
