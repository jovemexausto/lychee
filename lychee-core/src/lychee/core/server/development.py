"""
The core development server for orchestrating services in the monorepo.
"""

import asyncio
import re
import signal
import sys
from typing import Any, Dict, List, Optional

from lychee.core.project import LycheeProject
from lychee.core.service import LycheeService
from lychee.core.utils import get_logger

logger = get_logger(__name__)


class DevelopmentServer:
    """
    Manages the lifecycle of services for the development environment.
    """

    def __init__(
        self,
        project: LycheeProject,
        mode: str = "hybrid",
        proxy_port: Optional[int] = None,
        enable_proxy: bool = True,
        enable_dashboard: bool = True,
    ):
        self.project = project
        self.mode = mode
        self.proxy_port = proxy_port
        self.enable_proxy = enable_proxy
        self.enable_dashboard = enable_dashboard
        self._monitored_services: Dict[str, LycheeService] = {}
        self._is_stopping = False

        self._start_order = self.project.get_build_order()
        self._service_config = self.project.config.services or {}

    async def start(self, services_to_start: Optional[List[str]] = None):
        """
        Starts the development server and all specified services.
        """
        loop = asyncio.get_running_loop()

        loop.add_signal_handler(
            signal.SIGINT, lambda: asyncio.create_task(self._stop_all_async())
        )
        loop.add_signal_handler(
            signal.SIGTERM, lambda: asyncio.create_task(self._stop_all_async())
        )

        try:
            if not services_to_start:
                services_to_start = self._start_order

            tasks = []
            for name in services_to_start:
                service = self.project.get_service(name)
                if service:
                    tasks.append(self._start_and_monitor_service(service))
                else:
                    logger.warning(f"Service '{name}' not found in project. Skipping.")

            if self.enable_proxy:
                tasks.append(self._start_proxy_server())
            if self.enable_dashboard:
                tasks.append(self._start_dashboard())

            await asyncio.gather(*tasks, return_exceptions=True)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error during server start: {e}")
            await self._stop_all_async()
            sys.exit(1)

    def start_background(self, services_to_start: Optional[List[str]] = None):
        """
        Starts the development server in a background process.
        """
        logger.info("Background mode is not yet implemented.")
        logger.info("Please run `lychee dev start` to use the interactive mode.")

    async def _stop_all_async(self):
        """
        Stops all currently running services gracefully.
        """
        if self._is_stopping:
            return

        self._is_stopping = True
        logger.info("[yellow]Gracefully shutting down services[/]")

        tasks = [
            self._stop_service(service) for service in self._monitored_services.values()
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("[green]All services have been stopped.[/]")

    def stop_all(self):
        """
        Synchronous wrapper to allow for easy shutdown from sync contexts.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(self._stop_all_async())

    async def _start_and_monitor_service(self, service: LycheeService):
        """
        Starts a service and sets up monitoring for its logs and health.
        """
        try:
            logger.info(f"Starting service '{service.name}'")

            await service.start(self.mode)

            process = service.get_process()

            if not process:
                logger.error(f"Service '{service.name}' process not found after start.")
                return

            self._monitored_services[service.name] = service

            asyncio.create_task(self._read_logs(service.name, process.stdout, "stdout"))  # type: ignore
            asyncio.create_task(self._read_logs(service.name, process.stderr, "stderr"))  # type: ignore

            await process.wait()
            if process.returncode != 0:
                logger.warning(
                    f"[yellow]🚨 Service '{service.name}' exited with code {process.returncode}[/yellow]"
                )
            else:
                logger.info(
                    f"🏁 [blue]Service '{service.name}' exited with code {process.returncode}[/]"
                )

        except Exception as e:
            logger.error(
                f"[red]Failed to start or monitor service '{service.name}': {e}[/red]"
            )
            if service.name in self._monitored_services:
                await self._stop_service(service)

    async def _stop_service(self, service: LycheeService):
        """
        Stops a single service.
        """
        if service.name not in self._monitored_services:
            return

        logger.info(f"[orange3]Stopping service '{service.name}'[/]")
        await service.stop()

        del self._monitored_services[service.name]
        logger.info(f"[green]Service '{service.name}' stopped.[/]")

    def restart_service(self, service_name: str):
        """
        Restarts a specified service.
        """
        service = self.project.get_service(service_name)
        if not service:
            logger.warning(f"Service '{service_name}' not found.")
            return

        asyncio.run(self._restart_service_async(service))

    async def _restart_service_async(self, service: LycheeService):
        """
        Asynchronously restarts a service.
        """
        if not service.is_running:
            logger.warning(
                f"Service '{service.name}' is not running, starting it instead."
            )
            await self._start_and_monitor_service(service)
        else:
            await self._stop_service(service)
            await self._start_and_monitor_service(service)

    def get_status(self) -> Dict[str, Any]:
        """
        Returns the real-time status of all managed services.
        """
        status_info = {}
        for service_name in self._start_order:
            service = self.project.get_service(service_name)
            if not service:
                status_info[service_name] = {"status": "not_found", "pid": "N/A"}
            else:
                status = "running" if service.is_running else "stopped"
                pid = service.get_pid() if service.is_running else "N/A"
                status_info[service_name] = {"status": status, "pid": pid}
        return status_info

    def _extract_log_level_and_message(
        self, line: str, default="INFO"
    ) -> tuple[str, str]:
        match = re.match(r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL):\s*(.*)", line)
        if match:
            level, message = match.groups()
            return level, message.strip()
        return default, line.strip()  # Default to INFO if no level is found

    async def _read_logs(
        self, service_name: str, stream: asyncio.StreamReader, stream_type: str
    ):
        """
        Reads logs from a service's stdout or stderr.
        """
        service_logger = get_logger(service_name)

        while True:
            line = await stream.readline()
            if not line:
                break
            decoded_line = line.decode("utf-8").strip()
            default_level = "ERROR" if stream_type == "stderr" else "INFO"
            level, message = self._extract_log_level_and_message(
                decoded_line, default=default_level
            )
            if message:
                log_method = getattr(service_logger, level.lower(), service_logger.info)
                log_method(message)

    async def _start_proxy_server(self):
        """
        Placeholder for the development proxy server.
        """
        logger.info("✏️ TODO: add development proxy.")
        await asyncio.Future()

    async def _start_dashboard(self):
        """
        Placeholder for the Terminal UI dashboard.
        """
        logger.info("✏️ TODO: add dashboard.")
        await asyncio.Future()
