"""
services/file_service.py
-------------------------
Business logic for managing files (CRUD + upload workflow).
"""

from pathlib import Path

from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status

from app.models.file_model import File
from app.models.version_model import Version
from app.services.duplicate_checker import is_exact_duplicate, find_duplicate_file
from app.services.security_scanner import scan_file
from app.utils.hash_utils import hash_bytes
from app.utils.storage_utils import (
    delete_file_storage,
    get_version_path,
    save_upload,
)


# ── Read ───────────────────────────────────────────────────────────────────────

def get_all_files(db: Session) -> list[File]:
    """Return all files ordered by most recently updated."""
    return db.query(File).order_by(File.updated_at.desc()).all()


def get_file_by_id(db: Session, file_id: int) -> File:
    """Return file or raise 404."""
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return file


# ── Upload (Create or New Version) ────────────────────────────────────────────

async def handle_upload(
    db: Session,
    upload: UploadFile,
    message: str | None = None,
    author: str | None = None,
) -> tuple[File, Version, bool]:
    """
    Process an uploaded file:
      1. Read bytes & compute SHA-256 hash.
      2. GLOBAL duplicate check — if ANY file in the system already has
         this exact content (same hash), reject with 409 regardless of name.
      3. Look for an existing file with the same name.
         - If found → create a new version.
         - If not found → create a new File record + version 1.
    Returns (file, version, is_new_file).
    Raises 409 on any duplicate content.
    """
    file_bytes = await upload.read()
    content_hash = hash_bytes(file_bytes)
    original_name = upload.filename or "unnamed"
    mime_type = upload.content_type or "application/octet-stream"

    # ── Security scan (runs first — before anything is stored) ───────────────
    scan_result = scan_file(original_name, file_bytes)
    if not scan_result.is_safe:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=scan_result.user_message,
        )

    # ── Global duplicate-content check (hash across ALL files) ──────────────
    # This blocks re-uploads of identical bytes under a DIFFERENT filename.
    global_duplicate = find_duplicate_file(db, content_hash)
    if global_duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"This file already exists in your vault under the name "
                f"\u201c{global_duplicate.name}\u201d. "
                f"You cannot upload the same file with a different name. "
                f"If you want to update it, please upload a changed version of \u201c{global_duplicate.name}\u201d instead."
            ),
        )

    # ── Check for existing file by name (for versioning) ───────────────────
    existing_file: File | None = (
        db.query(File).filter(File.name == original_name).first()
    )

    if existing_file:
        # Per-file duplicate check (same name + same content = already caught
        # above by the global check, but kept as a safety net)
        if is_exact_duplicate(db, content_hash, file_id=existing_file.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"\u201c{existing_file.name}\u201d already has a version with this exact content. "
                    f"No new version was created because nothing has changed. "
                    f"Please make changes to the file before uploading it again."
                ),
            )
        # Create new version
        from app.services.version_service import create_version
        version = await create_version(
            db, existing_file, file_bytes, message=message, author=author
        )
        return existing_file, version, False

    else:
        # Brand-new file — create File record + version 1
        new_file = File(
            name=original_name,
            original_name=original_name,
            mime_type=mime_type,
            size=len(file_bytes),
            content_hash=content_hash,
            current_version=1,
        )
        db.add(new_file)
        db.flush()  # get new_file.id

        dest_path: Path = get_version_path(new_file.id, 1, original_name)
        await save_upload(file_bytes, dest_path)

        first_version = Version(
            file_id=new_file.id,
            version_number=1,
            storage_path=str(dest_path),
            size=len(file_bytes),
            content_hash=content_hash,
            message=message or "Initial upload",
            author=author,
        )
        db.add(first_version)
        db.commit()
        db.refresh(new_file)
        return new_file, first_version, True


# ── Delete ─────────────────────────────────────────────────────────────────────

def delete_file(db: Session, file_id: int) -> None:
    """Delete a file and all its versions from DB and disk."""
    file = get_file_by_id(db, file_id)
    delete_file_storage(file_id)
    db.delete(file)
    db.commit()
