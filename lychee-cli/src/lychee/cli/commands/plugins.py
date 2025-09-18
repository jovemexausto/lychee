import asyncclick as click

from lychee.core.project import LycheeProject
from lychee.infrastructure.plugins.entrypoint_registry import EntryPointPluginRegistry
from lychee.core.utils import get_logger

logger = get_logger(__name__)


@click.group()
def plugins():
    """Inspect Lychee plugins discovered via entry points."""


@plugins.command("list")
@click.pass_context
async def list_plugins(ctx: click.Context):
    """List discovered language runtimes and schema compilers."""
    working_dir = ctx.obj["working_dir"]
    project = LycheeProject(working_dir)

    registry = EntryPointPluginRegistry.from_config(project.config, include_builtins=True)

    logger.info("Discovered language runtime plugins:")
    for rt in registry.list_language_runtimes():
        try:
            name = rt.language()
        except Exception:
            name = "<unknown>"
        logger.info(f"- {name} ({rt.__class__.__module__}.{rt.__class__.__name__})")

    logger.info("Discovered schema compiler plugins:")
    for comp in registry.list_schema_compilers():
        logger.info(f"- {comp.__class__.__module__}.{comp.__class__.__name__}")
