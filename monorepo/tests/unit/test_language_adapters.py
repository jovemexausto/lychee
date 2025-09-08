"""Tests for language adapters."""

import asyncio
import json
from pathlib import Path

from monorepo.config.models import RuntimeConfig, ServiceConfig
from monorepo.languages.python import PythonAdapter

# from monorepo.languages.typescript import TypeScriptAdapter


def test_framework_detection_fastapi(temp_dir: Path):
    """Test FastAPI framework detection."""
    # Create requirements.txt with FastAPI
    (temp_dir / "requirements.txt").write_text("fastapi==0.68.0\n")

    config = ServiceConfig(type="python", path=".")
    adapter = PythonAdapter(temp_dir, config)

    assert adapter.detect_framework() == "fastapi"


def test_framework_detection_flask(temp_dir: Path):
    """Test Flask framework detection."""
    # Create requirements.txt with Flask
    (temp_dir / "requirements.txt").write_text("flask==2.0.0\n")

    config = ServiceConfig(type="python", path=".")
    adapter = PythonAdapter(temp_dir, config)

    assert adapter.detect_framework() == "flask"


def test_get_start_command_fastapi(temp_dir: Path):
    """Test FastAPI start command generation."""
    config = ServiceConfig(
        type="python", path=".", runtime=RuntimeConfig(port=8000, entry_point="app.main:app", framework="fastapi")
    )
    adapter = PythonAdapter(temp_dir, config)

    cmd = adapter.get_start_command()
    expected = ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    assert cmd == expected


# def test_generate_pydantic_model(temp_dir: Path):
#     """Test Pydantic model generation."""
#     schema = {
#         "title": "User",
#         "type": "object",
#         "properties": {"id": {"type": "integer"}, "name": {"type": "string"}, "email": {"type": "string"}},
#         "required": ["id", "name"],
#     }

#     config = ServiceConfig(type="python", path=".")
#     adapter = PythonAdapter(temp_dir, config)

#     schema_path = temp_dir / "user.schema.json"
#     with schema_path.open("w") as f:
#         json.dump(schema, f)

#     output_path = temp_dir / "user.py"
#     asyncio.run(adapter.generate_types_from_schema(schema_path, output_path))

#     assert output_path.exists()
#     content = output_path.read_text()
#     assert "class User(BaseModel):" in content
#     assert "id: int" in content
#     assert "name: str" in content
#     assert "email: Optional[str] = None" in content


# def test_framework_detection_nextjs(temp_dir: Path):
#     """Test Next.js framework detection."""
#     package_json = {"name": "test-app", "dependencies": {"next": "12.0.0", "react": "17.0.0"}}

#     with (temp_dir / "package.json").open("w") as f:
#         json.dump(package_json, f)

#     config = ServiceConfig(type="typescript", path=".")
#     adapter = TypeScriptAdapter(temp_dir, config)

#     assert adapter.detect_framework() == "nextjs"


# def test_framework_detection_express(temp_dir: Path):
#     """Test Express framework detection."""
#     package_json = {"name": "test-api", "dependencies": {"express": "4.17.1"}}

#     with (temp_dir / "package.json").open("w") as f:
#         json.dump(package_json, f)

#     config = ServiceConfig(type="typescript", path=".")
#     adapter = TypeScriptAdapter(temp_dir, config)

#     assert adapter.detect_framework() == "express"


# def test_get_start_command_nextjs(temp_dir: Path):
#     """Test Next.js start command generation."""
#     # Create package.json
#     package_json = {"dependencies": {"next": "12.0.0"}}
#     with (temp_dir / "package.json").open("w") as f:
#         json.dump(package_json, f)

#     config = ServiceConfig(type="typescript", path=".", framework="nextjs")
#     adapter = TypeScriptAdapter(temp_dir, config)

#     cmd = adapter.get_start_command()
#     assert cmd == ["npm", "run", "dev"]


# def test_generate_typescript_interface(temp_dir: Path):
#     """Test TypeScript interface generation."""
#     schema = {
#         "title": "User",
#         "type": "object",
#         "description": "User data model",
#         "properties": {
#             "id": {"type": "integer"},
#             "name": {"type": "string"},
#             "email": {"type": "string", "description": "User email address"},
#         },
#         "required": ["id", "name"],
#     }

#     config = ServiceConfig(type="typescript", path=".")
#     adapter = TypeScriptAdapter(temp_dir, config)

#     schema_path = temp_dir / "user.schema.json"
#     with schema_path.open("w") as f:
#         json.dump(schema, f)

#     output_path = temp_dir / "user.ts"
#     adapter.generate_types_from_schema(schema_path, output_path)

#     assert output_path.exists()
#     content = output_path.read_text()
#     assert "export interface User {" in content
#     assert "id: number;" in content
#     assert "name: string;" in content
#     assert "email?: string;" in content
#     assert "/** User email address */" in content
