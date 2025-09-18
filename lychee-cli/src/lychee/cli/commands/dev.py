"""Development server commands."""

from pathlib import Path
from typing import List, Optional

import asyncclick as click

from lychee.application.use_cases.start_dev_server import StartDevServerUseCase
from lychee.application.use_cases.stop_dev_server import StopDevServerUseCase
from lychee.application.use_cases.restart_service import RestartServiceUseCase
from lychee.application.services.runtime_orchestrator import runtime_orchestrator
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
        working_dir: Path = ctx.obj["working_dir"]

        # Parse services
        service_list: List[str] = []
        if services:
            service_list = [s.strip() for s in services.split(",")]

        # New application use-case for starting services
        usecase = StartDevServerUseCase()
        await usecase.run(
            root=working_dir,
            services=service_list or None,
            mode=mode,
            enable_proxy=(not no_proxy),
            enable_dashboard=(not no_dashboard),
        )

        # If not background, block to keep process alive (CTRL+C to stop)
        if not background:
            await click.sleep(10**12)  # effectively wait forever until signal

    except Exception as e:
        logger.error(f"Failed to start development server: {e}")
        await ctx.aexit(1)


@dev.command()
@click.pass_context
async def stop(ctx: click.Context):
    """Stop all development servers."""
    try:
        working_dir: Path = ctx.obj["working_dir"]
        usecase = StopDevServerUseCase()
        await usecase.run(working_dir)
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
        working_dir: Path = ctx.obj["working_dir"]
        usecase = RestartServiceUseCase()
        await usecase.run(working_dir, service_name)
        logger.info(f"✅ Service '{service_name}' restarted")

    except Exception as e:
        logger.info(f"❌ Failed to restart service: {e}")
        await ctx.aexit(1)


@dev.command()
@click.pass_context
async def status(ctx: click.Context):
    """Show status of all services."""
    try:
        # NOTE: In-process orchestrator only; background mode is not yet persisted across processes.
        info = runtime_orchestrator.status()
        if not info:
            logger.info("No services running in this process context.")
            return
        logger.info("[bold]Service Status (in-process):[/bold]")
        for service, data in info.items():
            logger.info(f"  {service}: running (PID: {data.get('pid','N/A')})")

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
