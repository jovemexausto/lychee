"""Main CLI entry point using Click."""

from pathlib import Path
from typing import Optional

import asyncclick as click

from lychee.cli.middleware.error_handler import handle_errors
from lychee.core import __version__
from lychee.core.utils import get_logger

logger = get_logger(__name__)


@click.group()
@click.version_option(__version__)
@click.option(
    "--verbose", "-v", count=True, help="Increase verbosity (can be used multiple times)"
)
@click.option("--quiet", "-q", is_flag=True, help="Suppress output except for errors")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.option(
    "--working-dir",
    "-w",
    type=click.Path(exists=True, path_type=Path),
    help="Working directory",
)
@click.pass_context
def cli(
    ctx: click.Context,
    verbose: int,
    quiet: bool,
    config: Optional[Path],
    working_dir: Optional[Path],
):
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
from lychee.cli.commands.dev import dev

# Import and register commands
from lychee.cli.commands.init import init
from lychee.cli.commands.install import install
from lychee.cli.commands.schema import schema
from lychee.cli.commands.plugins import plugins

cli.add_command(init)
cli.add_command(install)
cli.add_command(dev)
# cli.add_command(build)
# cli.add_command(test)
# cli.add_command(deploy)
cli.add_command(schema)
cli.add_command(plugins)
# cli.add_command(config_cmd)


@handle_errors
def main():
    """Main entry point with error handling."""
    cli()


if __name__ == "__main__":
    main()
