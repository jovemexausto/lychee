import json

import asyncclick as click

from monorepo.core.project import MonorepoProject
from monorepo.schema.manager import SchemaManager
from monorepo.utils.logging import get_logger

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
    working_dir = ctx.obj["working_dir"]
    project = MonorepoProject(working_dir)
    manager = SchemaManager(project)
    with open(schema_file, "r") as f:
        schema = json.load(f)
        await manager.add_schema(name, schema)
    logger.info(f"Added schema {name} and generated types.")


@schema.command()
@click.argument("name")
@click.argument("schema_file")
@click.pass_context
async def update(ctx, name, schema_file):
    """Update an existing schema and regenerate Python types."""
    working_dir = ctx.obj["working_dir"]
    project = MonorepoProject(working_dir)
    manager = SchemaManager(project)
    with open(schema_file, "r") as f:
        schema = json.load(f)
    await manager.update_schema(name, schema)
    logger.info(f"Updated schema {name} and re-generated types.")


@schema.command()
@click.pass_context
async def generate(ctx):
    """Regenerate Python types for all schemas."""
    working_dir = ctx.obj["working_dir"]
    project = MonorepoProject(working_dir)
    manager = SchemaManager(project)
    await manager.initialize()
    logger.info("[green]Generated Python types for all schemas.[/green]")


@schema.command()
@click.pass_context
async def list(ctx):
    """List all available schemas."""
    working_dir = ctx.obj["working_dir"]
    project = MonorepoProject(working_dir)
    schemas_dir = working_dir / project.config.schemas.dir
    files = sorted(schemas_dir.glob("*.schema.json"))
    for file in files:
        logger.info(file.name)
