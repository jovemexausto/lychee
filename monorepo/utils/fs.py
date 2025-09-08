import os
from pathlib import Path


def ensure_symlink(source: Path, link_name: Path) -> None:
    """
    Create a symlink pointing to source named link_name.
    If link_name exists (file, symlink, or directory), remove it first.
    """
    link_name = Path(link_name)
    source = Path(source)

    if link_name.exists() or link_name.is_symlink():
        if link_name.is_symlink() or link_name.is_file():
            link_name.unlink()
        elif link_name.is_dir():
            # Only remove if it's a symlink dir, not a real dir
            if link_name.is_symlink():
                link_name.unlink()
            else:
                # Actual directories: raise an error for safety
                raise FileExistsError(f"Refusing to overwrite non-symlink directory: {link_name}")
    link_name.parent.mkdir(parents=True, exist_ok=True)
    link_name.symlink_to(source, target_is_directory=source.is_dir())


def find_broken_symlinks(dir_path: Path):
    """
    Return a list of all broken symlinks under dir_path (recursively).
    """
    dir_path = Path(dir_path)
    broken = []
    for p in dir_path.rglob("*"):
        if p.is_symlink() and not p.exists():
            broken.append(p)
    return broken


def list_symlinks(dir_path: Path):
    """
    Return a list of all symlinks under dir_path (recursively).
    """
    dir_path = Path(dir_path)
    return [p for p in dir_path.rglob("*") if p.is_symlink()]
