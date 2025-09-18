from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from lychee.application.use_cases.generate_schemas import GenerateSchemasUseCase
from lychee.core.utils.logging import get_logger

logger = get_logger(__name__)


class AddSchemaUseCase:
    """Adds a new schema file and regenerates types/mounts.

    This use-case writes the provided schema JSON into `schemas/{name}.schema.json`
    and reuses GenerateSchemasUseCase to refresh artifacts.
    """

    def __init__(self, generator: Optional[GenerateSchemasUseCase] = None) -> None:
        self._generator = generator or GenerateSchemasUseCase()

    async def run(self, root: Path, name: str, schema: Dict) -> None:
        schemas_dir = root / "schemas"
        schemas_dir.mkdir(parents=True, exist_ok=True)
        schema_path = schemas_dir / f"{name}.schema.json"

        # Basic sanity check
        if not isinstance(schema, dict):
            raise ValueError("Schema must be a JSON object (dict)")

        schema_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
        logger.info(f"Added schema: {schema_path.relative_to(root)}")

        # Regenerate all types and remount
        await self._generator.run(root)
