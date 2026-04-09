"""
utils/storage_utils.py
-----------------------
Low-level disk I/O helpers for saving, reading, and deleting versioned files.
"""

import os
import shutil
import aiofiles
from pathlib import Path

# Base storage directory — override via env
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "./storage"))


def ensure_storage_dir() -> None:
    """Create the storage directory tree if it doesn't exist."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def get_version_path(file_id: int, version_number: int, original_name: str) -> Path:
    """
    Return the canonical path for a versioned file:
      storage/<file_id>/v<version_number>_<original_name>
    """
    folder = STORAGE_DIR / str(file_id)
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"v{version_number}_{original_name}"


async def save_upload(file_bytes: bytes, dest: Path) -> int:
    """
    Asynchronously write *file_bytes* to *dest*.
    Returns the number of bytes written.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(dest, "wb") as f:
        await f.write(file_bytes)
    return len(file_bytes)


async def read_file(path: Path) -> bytes:
    """Asynchronously read and return the contents of *path*."""
    async with aiofiles.open(path, "rb") as f:
        return await f.read()


def copy_version(src: Path, dest: Path) -> None:
    """Copy a stored version file to a new path (used when restoring)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def delete_file_storage(file_id: int) -> None:
    """Remove the entire storage folder for a given file_id."""
    folder = STORAGE_DIR / str(file_id)
    if folder.exists():
        shutil.rmtree(folder)


def delete_version_file(path: Path) -> None:
    """Delete a single version file from disk."""
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


def file_exists(path: Path) -> bool:
    """Return True if the path exists on disk."""
    return path.is_file()


def get_file_size(path: Path) -> int:
    """Return file size in bytes, or 0 if not found."""
    try:
        return path.stat().st_size
    except FileNotFoundError:
        return 0
