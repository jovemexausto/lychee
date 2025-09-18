from __future__ import annotations

from pathlib import Path

from lychee.application.ports.symlink_manager import SymlinkManagerPort
from lychee.core.utils.fs import ensure_symlink, find_broken_symlinks
from lychee.core.utils import get_logger

logger = get_logger(__name__)


class FSSymlinkManager(SymlinkManagerPort):
    def ensure(self, source: Path, target: Path) -> None:
        try:
            ensure_symlink(source, target)
        except Exception as e:
            logger.error(f"Failed to ensure symlink {target} -> {source}: {e}")
            raise

    def remove_broken(self, root: Path) -> None:
        try:
            for broken in find_broken_symlinks(root):
                logger.info(f"Removing broken symlink: {broken}")
                broken.unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"Failed removing broken symlinks under {root}: {e}")
            raise
