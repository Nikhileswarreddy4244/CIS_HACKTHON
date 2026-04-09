"""
services/version_service.py
----------------------------
Business logic for creating, listing, and restoring file versions.
"""

from pathlib import Path

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.file_model import File
from app.models.version_model import Version
from app.utils.storage_utils import (
    get_version_path,
    copy_version,
    save_upload,
    read_file,
    delete_version_file,
)
from app.utils.hash_utils import hash_bytes


# ── Read ───────────────────────────────────────────────────────────────────────

def get_versions(db: Session, file_id: int) -> list[Version]:
    """Return all versions for *file_id*, newest first."""
    file = _get_file_or_404(db, file_id)
    return (
        db.query(Version)
        .filter(Version.file_id == file.id)
        .order_by(Version.version_number.desc())
        .all()
    )


def get_version(db: Session, file_id: int, version_id: int) -> Version:
    """Return a single version or raise 404."""
    version = (
        db.query(Version)
        .filter(Version.file_id == file_id, Version.id == version_id)
        .first()
    )
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    return version


# ── Create ─────────────────────────────────────────────────────────────────────

async def create_version(
    db: Session,
    file: File,
    file_bytes: bytes,
    message: str | None = None,
    author: str | None = None,
) -> Version:
    """
    Persist a new version of *file* with the given raw bytes.
    Increments file.current_version and updates the content hash.
    """
    new_version_number = file.current_version + 1
    content_hash = hash_bytes(file_bytes)
    dest_path: Path = get_version_path(file.id, new_version_number, file.original_name)

    await save_upload(file_bytes, dest_path)

    version = Version(
        file_id=file.id,
        version_number=new_version_number,
        storage_path=str(dest_path),
        size=len(file_bytes),
        content_hash=content_hash,
        message=message,
        author=author,
    )
    db.add(version)

    # Update parent file metadata
    file.current_version = new_version_number
    file.content_hash = content_hash
    file.size = len(file_bytes)

    db.commit()
    db.refresh(version)
    return version


# ── Restore ────────────────────────────────────────────────────────────────────

async def restore_version(db: Session, file_id: int, version_id: int) -> Version:
    """
    Restore an older version by creating a *new* version whose content matches
    the target version (non-destructive).
    Returns the newly created version.
    """
    file = _get_file_or_404(db, file_id)
    target = get_version(db, file_id, version_id)

    # Read the historical content
    content = await read_file(Path(target.storage_path))

    # Create a new version from that content
    new_version = await create_version(
        db,
        file,
        content,
        message=f"Restored from v{target.version_number}",
        author="system",
    )
    return new_version


# ── Delete ─────────────────────────────────────────────────────────────────────

def delete_version(db: Session, file_id: int, version_id: int) -> None:
    """Delete a specific version (cannot delete the current version)."""
    file = _get_file_or_404(db, file_id)
    version = get_version(db, file_id, version_id)

    if version.version_number == file.current_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the current active version.",
        )

    delete_version_file(Path(version.storage_path))
    db.delete(version)
    db.commit()


# ── Download ───────────────────────────────────────────────────────────────────

async def get_version_bytes(db: Session, file_id: int, version_id: int) -> tuple[bytes, str]:
    """Return (file_bytes, filename) for a version download."""
    version = get_version(db, file_id, version_id)
    content = await read_file(Path(version.storage_path))
    file = _get_file_or_404(db, file_id)
    return content, file.original_name


# ── Private ────────────────────────────────────────────────────────────────────

def _get_file_or_404(db: Session, file_id: int) -> File:
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return file
