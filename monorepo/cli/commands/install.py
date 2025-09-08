import asyncclick as click
from rich.console import Console

from monorepo.core.project import MonorepoProject
from monorepo.utils.logging import get_logger

console = Console()
logger = get_logger(__name__)


@click.command()
@click.option("--services", "-s", is_flag=True, default=True, help="Install dependencies for services.")
# @click.option(
#     "--packages", "-p",
#     is_flag=True,
#     default=True,
#     help="Install dependencies for packages."
# )
@click.pass_context
async def install(
    ctx: click.Context,
    services: bool,
    # packages: bool
):
    """Install dependencies for services and packages."""
    try:
        working_dir = ctx.obj["working_dir"]
        project = MonorepoProject(working_dir)

        if services:
            console.print("[blue]Installing service dependencies...[/blue]")
            for name, service in project.services.items():
                console.print(f"  Installing for service: {name}")
                await service.install_dependencies()
            console.print("[green]✅ Service dependencies installed.[/green]")

        # if packages:
        #     console.print("[blue]Installing package dependencies...[/blue]")
        #     for name, package in project.packages.items():
        #         console.print(f"  Installing for package: {name}")
        #         package.install_dependencies()
        #     console.print("[green]✅ Package dependencies installed.[/green]")

        console.print("[bold green]All dependencies installed successfully.[/bold green]")

    except Exception as e:
        logger.error(f"Failed to install dependencies: {e}")
        console.print(f"[red]❌ Failed to install dependencies: {e}[/red]")
        await ctx.aexit(1)
