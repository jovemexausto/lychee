import json

import asyncclick as click

from pathlib import Path
from lychee.application.use_cases.generate_schemas import GenerateSchemasUseCase
from lychee.application.use_cases.add_schema import AddSchemaUseCase
from lychee.application.use_cases.update_schema import UpdateSchemaUseCase
from lychee.core.utils import get_logger

logger = get_logger(__name__)


@click.group()
def schema():
    """Manage JSON schemas and type generation."""


@schema.command()
@click.argument("name")
@click.argument("schema_file")
@click.pass_context
async def add(ctx: click.Context, name, schema_file):
    """Add a new schema and generate Python types."""
    working_dir: Path = ctx.obj["working_dir"]
    with open(schema_file, "r") as f:
        schema = json.load(f)
    usecase = AddSchemaUseCase()
    await usecase.run(working_dir, name, schema)
    logger.info(f"Added schema {name} and generated types.")


@schema.command()
@click.argument("name")
@click.argument("schema_file")
@click.pass_context
async def update(ctx, name, schema_file):
    """Update an existing schema and regenerate Python types."""
    working_dir: Path = ctx.obj["working_dir"]
    with open(schema_file, "r") as f:
        schema = json.load(f)
    usecase = UpdateSchemaUseCase()
    await usecase.run(working_dir, name, schema)
    logger.info(f"Updated schema {name} and re-generated types.")


@schema.command()
@click.pass_context
async def generate(ctx):
    """Regenerate Python types for all schemas."""
    working_dir: Path = ctx.obj["working_dir"]
    usecase = GenerateSchemasUseCase()
    await usecase.run(working_dir)
    logger.info("[green]Generated types and mounted schemas for all services.[/green]")


@schema.command()
@click.pass_context
async def list(ctx):
    """List all available schemas."""
    working_dir: Path = ctx.obj["working_dir"]
    from lychee.core.project import LycheeProject  # local import for config read

    project = LycheeProject(working_dir)
    schemas_dir = working_dir / project.config.schemas.dir
    files = sorted(schemas_dir.glob("*.schema.json"))
    for file in files:
        logger.info(file.name)
