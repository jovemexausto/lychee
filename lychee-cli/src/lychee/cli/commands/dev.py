"""Development server commands."""

from typing import List, Optional

import asyncclick as click

from lychee.core.project import LycheeProject
from lychee.core.server.development import DevelopmentServer
from lychee.core.utils import get_logger

logger = get_logger(__name__)


@click.group()
def dev():
    """Development workflow commands."""
    pass


@dev.command()
@click.option(
    "--services", "-s", help="Comma-separated list of services to start", default=None
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["native", "hybrid", "docker"]),
    default="hybrid",
    help="Development mode",
)
@click.option("--port", "-p", type=int, help="Proxy port (default: from config)")
@click.option("--no-proxy", is_flag=True, help="Disable development proxy")
@click.option("--no-dashboard", is_flag=True, help="Disable development dashboard")
@click.option("--background", "-b", is_flag=True, help="Run in background (daemon mode)")
@click.pass_context
async def start(
    ctx: click.Context,
    services: Optional[str],
    mode: str,
    port: Optional[int],
    no_proxy: bool,
    no_dashboard: bool,
    background: bool,
):
    """Start development servers for services."""
    try:
        # Load project
        working_dir = ctx.obj["working_dir"]
        project = LycheeProject(working_dir)
        await project.validate()

        # Parse services
        service_list: List[str] = []
        if services:
            service_list = [s.strip() for s in services.split(",")]

        # Create development server
        dev_server = DevelopmentServer(
            project=project,
            mode=mode,
            proxy_port=port,
            enable_proxy=not no_proxy,
            enable_dashboard=not no_dashboard,
        )

        if background:
            dev_server.start_background(service_list)
        else:
            await dev_server.start(service_list)
    except Exception as e:
        logger.error(f"Failed to start development server: {e}")
        await ctx.aexit(1)


@dev.command()
@click.pass_context
async def stop(ctx: click.Context):
    """Stop all development servers."""
    try:
        working_dir = ctx.obj["working_dir"]
        project = LycheeProject(working_dir)

        dev_server = DevelopmentServer(project)
        dev_server.stop_all()

        logger.info("✅ Development servers stopped")

    except Exception as e:
        logger.error(f"❌ Failed to stop development servers: {e}")
        await ctx.aexit(1)


@dev.command()
@click.argument("service_name")
@click.pass_context
async def restart(ctx: click.Context, service_name: str):
    """Restart a specific service."""
    try:
        working_dir = ctx.obj["working_dir"]
        project = LycheeProject(working_dir)

        dev_server = DevelopmentServer(project)
        dev_server.restart_service(service_name)

        logger.info(f"✅ Service '{service_name}' restarted")

    except Exception as e:
        logger.info(f"❌ Failed to restart service: {e}")
        await ctx.aexit(1)


@dev.command()
@click.pass_context
async def status(ctx: click.Context):
    """Show status of all services."""
    try:
        working_dir = ctx.obj["working_dir"]
        project = LycheeProject(working_dir)

        dev_server = DevelopmentServer(project)
        status_info = dev_server.get_status()

        # Display status in a nice format
        logger.info("[bold]Service Status:[/bold]")
        for service, info in status_info.items():
            status_color = "green" if info["status"] == "running" else "red"
            logger.print(
                f"  {service}: [{status_color}]{info['status']}[/{status_color}] "
                f"(PID: {info.get('pid', 'N/A')})"
            )

    except Exception as e:
        logger.error(f"❌ Failed to get status: {e}")
        await ctx.aexit(1)


@dev.command()
@click.argument("service_name")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.option("--lines", "-n", type=int, default=100, help="Number of lines to show")
@click.pass_context
async def logs(ctx: click.Context, service_name: str, follow: bool, lines: int):
    """Show logs for a service."""
    try:
        working_dir = ctx.obj["working_dir"]
        project = LycheeProject(working_dir)

        dev_server = DevelopmentServer(project)

        # if follow:
        #     dev_server.follow_logs(service_name)
        # else:
        #     logs_content = dev_server.get_logs(service_name, lines)
        #     console.print(logs_content)
        # TODO: to be implemented

    except Exception as e:
        logger.error(f"[red]❌ Failed to get logs: {e}[/red]")
        await ctx.aexit(1)
