"""Main CLI entry point using Click."""

import sys
from pathlib import Path
from typing import Optional

import asyncclick as click

from monorepo import __version__
from monorepo.cli.middleware.error_handler import handle_errors
from monorepo.utils.logging import get_logger

logger = get_logger(__name__)


@click.group()
@click.version_option(__version__)
@click.option("--verbose", "-v", count=True, help="Increase verbosity (can be used multiple times)")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output except for errors")
@click.option("--config", "-c", type=click.Path(exists=True, path_type=Path), help="Path to configuration file")
@click.option("--working-dir", "-w", type=click.Path(exists=True, path_type=Path), help="Working directory")
@click.pass_context
def cli(ctx: click.Context, verbose: int, quiet: bool, config: Optional[Path], working_dir: Optional[Path]):
    """Monorepo Manager - A polyglot monorepo manager with schema-driven development."""
    # Setup context
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    ctx.obj["config"] = config
    ctx.obj["working_dir"] = working_dir or Path.cwd()

    # Change working directory if specified
    if working_dir:
        import os

        os.chdir(working_dir)


# from monorepo.cli.commands.build import build
# from monorepo.cli.commands.config import config as config_cmd
# from monorepo.cli.commands.deploy import deploy
from monorepo.cli.commands.dev import dev

# Import and register commands
from monorepo.cli.commands.init import init
from monorepo.cli.commands.install import install
from monorepo.cli.commands.schema import schema

cli.add_command(init)
cli.add_command(install)
cli.add_command(dev)
# cli.add_command(build)
# cli.add_command(test)
# cli.add_command(deploy)
cli.add_command(schema)
# cli.add_command(config_cmd)


@handle_errors
def main():
    """Main entry point with error handling."""
    try:
        cli()
    except KeyboardInterrupt:
        logger.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
