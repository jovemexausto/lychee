"""Initialize a new monorepo project."""

from pathlib import Path
from typing import Optional

import asyncclick as click
from rich.console import Console
from rich.prompt import Confirm, Prompt

from monorepo.core.project import MonorepoProject
from monorepo.templates.manager import TemplateManager
from monorepo.utils.logging import get_logger

console = Console()
logger = get_logger(__name__)


@click.command()
@click.argument("name", required=False)
@click.option("--template", "-t", help="Project template to use", default="basic")
@click.option("--path", "-p", type=click.Path(path_type=Path), help="Directory to create project in", default=".")
@click.option("--force", "-f", is_flag=True, help="Force initialization even if directory is not empty")
@click.option("--interactive", "-i", is_flag=True, default=True, help="Interactive setup (default: true)")
@click.pass_context
def init(ctx: click.Context, name: Optional[str], template: str, path: Path, force: bool, interactive: bool):
    """Initialize a new monorepo project.

    NAME is the name of the project. If not provided, will be prompted.
    """
    console.print("[bold blue]🚀 Monorepo Manager - Project Initialization[/bold blue]")

    # Get project name
    if not name and interactive:
        name = Prompt.ask("Project name", default=path.name)
    elif not name:
        name = path.name

    # Check if directory is empty
    if path.exists() and any(path.iterdir()) and not force:
        if interactive:
            if not Confirm.ask(f"Directory '{path}' is not empty. Continue anyway?", default=False):
                console.print("[yellow]Initialization cancelled[/yellow]")
                return
        else:
            console.print(f"[red]Error: Directory '{path}' is not empty. " f"Use --force to override.[/red]")
            ctx.exit(1)

    try:
        # Initialize project
        template_manager = TemplateManager()
        MonorepoProject.create(name=name, path=path, template=template, template_manager=template_manager)
        logger.info(f"[green]✅ Successfully initialized '{name}' at {path}[/green]")

    except Exception as e:
        logger.error(f"❌ Failed to initialize project: {e}")
        ctx.exit(1)
