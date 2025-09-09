import asyncio
import os
import signal
from typing import Dict, List, Optional

import psutil

from monorepo.utils.logging import get_logger

logger = get_logger(__name__)


class ProcessManager:
    """Manages subprocess lifecycle for services."""

    async def start_process(
        self,
        cmd: List[str],
        cwd: str,
        env: Optional[Dict[str, str]] = None,
    ) -> asyncio.subprocess.Process:
        """
        Start a subprocess with the given command and environment.

        Args:
            cmd: List of command arguments to execute.
            cwd: Working directory for the process.
            env: Environment variables for the process.

        Returns:
            The created asyncio.subprocess.Process object.
        """
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                start_new_session=False,  # Ensure process group is created for graceful shutdown
            )
            logger.debug(
                f"Started process with PID {process.pid} and command: {' '.join(cmd)}"
            )
            return process
        except Exception as e:
            logger.error(f"Failed to start process with command {' '.join(cmd)}: {e}")
            raise

    async def stop_process(
        self, process: asyncio.subprocess.Process, timeout: int = 10
    ) -> None:
        """
        Stops a process and all of its descendants gracefully.

        Args:
            process: The asyncio.subprocess.Process object to stop.
            timeout: The time in seconds to wait for graceful termination before force-killing.
        """
        if process.returncode is not None:
            logger.warning(f"Process with PID {process.pid} is already stopped.")
            return

        try:
            parent = psutil.Process(process.pid)
            children = parent.children(recursive=True)

            # Send SIGTERM to all child processes
            for child in children:
                try:
                    os.kill(child.pid, signal.SIGTERM)
                except OSError as e:
                    logger.debug(f"Could not terminate child process {child.pid}: {e}")

            # Send SIGTERM to the parent process
            process.terminate()

            try:
                # Wait for the process to exit gracefully
                await asyncio.wait_for(process.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning(
                    f"Process with PID {process.pid} did not terminate gracefully, force-killing"
                )
                process.kill()
                await process.wait()

            logger.info(f"Stopped process with PID {process.pid}")

        except (psutil.NoSuchProcess, OSError) as e:
            logger.error(f"Failed to stop process {process.pid}: {e}")
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while stopping process {process.pid}: {e}"
            )

    async def run_command(self, cmd: List[str], cwd: str) -> None:
        """
        Run a command and wait for its completion.

        Args:
            cmd: List of command arguments to execute.
            cwd: Working directory for the process.
        """
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.wait()
            logger.debug(f"Completed command: {' '.join(cmd)}")
        except Exception as e:
            logger.error(f"Failed to run command {' '.join(cmd)}: {e}")
            raise

    def is_process_running(self, process: Optional[asyncio.subprocess.Process]) -> bool:
        """
        Check if a process is currently running.

        Args:
            process: The asyncio.subprocess.Process object to check.

        Returns:
            True if the process is running, False otherwise.
        """
        return process is not None and process.returncode is None


process_manager = ProcessManager()
