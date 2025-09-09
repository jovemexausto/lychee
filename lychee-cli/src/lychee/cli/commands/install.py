import asyncclick as click

from lychee.core.project import LycheeProject
from lychee.core.utils import get_logger

logger = get_logger(__name__)


@click.command()
@click.option(
    "--services",
    "-s",
    is_flag=True,
    default=True,
    help="Install dependencies for services.",
)
@click.pass_context
async def install(
    ctx: click.Context,
    services: bool,
):
    """Install dependencies for services and packages."""
    try:
        working_dir = ctx.obj["working_dir"]
        project = LycheeProject(working_dir)
        await project.validate()

        if services:
            logger.info("[blue]Installing service dependencies[/blue]")
            for _name, service in project.services.items():
                await service.install_dependencies()

        logger.info("[bold green]All dependencies installed successfully.[/bold green]")

    except Exception as e:
        logger.error(f"Failed to install dependencies: {e}")
        await ctx.aexit(1)
