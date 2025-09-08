"""Schema file watcher."""

import asyncio
from pathlib import Path
from typing import Callable, Optional

from watchfiles import Change, awatch

from monorepo.utils.logging import get_logger

logger = get_logger(__name__)


class SchemaWatcher:
    """Watches schema files for changes and triggers regeneration."""

    def __init__(self, schema_dir: Path, on_change_callback: Callable[[Path], None]):
        self.schema_dir = schema_dir
        self.on_change_callback = on_change_callback
        self._task: Optional[asyncio.Task] = None
        self._running = False

    def start(self) -> None:
        """Start watching schema files."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._watch_loop())
        logger.info(f"Started watching schema directory: {self.schema_dir}")

    def stop(self) -> None:
        """Stop watching schema files."""
        self._running = False

        if self._task:
            self._task.cancel()
            self._task = None

        logger.info("Stopped schema file watcher")

    async def _watch_loop(self) -> None:
        """Main watch loop."""
        try:
            async for changes in awatch(self.schema_dir, watch_filter=self._filter_schema_files):
                if not self._running:
                    break

                for change_type, file_path in changes:
                    if change_type in ("added", "modified"):
                        schema_file = Path(file_path)
                        logger.info(f"Schema file changed: {schema_file.name}")

                        # Debounce rapid changes
                        await asyncio.sleep(0.1)

                        # Call the callback
                        try:
                            self.on_change_callback(schema_file)
                        except Exception as e:
                            logger.error(f"Error processing schema change: {e}")

        except asyncio.CancelledError:
            logger.debug("Schema watcher task cancelled")
        except Exception as e:
            logger.error(f"Schema watcher error: {e}")

    def _filter_schema_files(self, change: Change, path: str) -> bool:
        """Filter to only watch schema files."""
        return path.endswith(".schema.json")
