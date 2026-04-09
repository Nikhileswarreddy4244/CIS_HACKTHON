"""
routes/files.py
---------------
CRUD endpoints for files:
  GET    /api/files          – list all files
  GET    /api/files/{id}     – get single file
  DELETE /api/files/{id}     – delete file + all versions
  GET    /api/timeline       – recent activity feed
"""

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services.file_service import get_all_files, get_file_by_id, delete_file
from app.schemas import FileOut, TimelineEvent
from app.models.version_model import Version

router = APIRouter(prefix="/api", tags=["files"])


@router.get("/files", response_model=list[FileOut])
def list_files(db: Session = Depends(get_db)):
    """Return all files ordered by last updated."""
    return get_all_files(db)


@router.get("/files/{file_id}", response_model=FileOut)
def get_file(file_id: int, db: Session = Depends(get_db)):
    """Return metadata for a single file."""
    return get_file_by_id(db, file_id)


@router.delete("/files/{file_id}", status_code=204)
def remove_file(file_id: int, db: Session = Depends(get_db)):
    """Delete a file and ALL of its versions from the DB and disk."""
    delete_file(db, file_id)


@router.get("/files/{file_id}/download")
async def download_current_version(file_id: int, db: Session = Depends(get_db)):
    """
    Download the current (latest) version of a file.
    Streams raw bytes with Content-Disposition: attachment so the browser
    saves it immediately.
    """
    from pathlib import Path
    from fastapi import HTTPException, status
    from app.utils.storage_utils import read_file

    file = get_file_by_id(db, file_id)
    version = (
        db.query(Version)
        .filter(
            Version.file_id == file_id,
            Version.version_number == file.current_version,
        )
        .first()
    )
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No file content found. Please upload the file first.",
        )

    content = await read_file(Path(version.storage_path))
    return Response(
        content=content,
        media_type=file.mime_type or "application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{file.original_name}"',
            "Content-Length": str(len(content)),
        },
    )


@router.get("/timeline", response_model=list[TimelineEvent])
def get_timeline(limit: int = 50, db: Session = Depends(get_db)):
    """
    Return the most recent *limit* version events across all files,
    formatted as a feed for the frontend timeline component.
    """
    rows = (
        db.query(Version)
        .order_by(Version.created_at.desc())
        .limit(limit)
        .all()
    )

    events: list[TimelineEvent] = []
    for v in rows:
        event_type = "upload"
        if v.message and v.message.startswith("Restored"):
            event_type = "restore"
        events.append(
            TimelineEvent(
                id=v.id,
                type=event_type,
                description=v.message or f"Version {v.version_number} created",
                version=v.version_number,
                time=v.created_at.isoformat() if v.created_at else "",
                file_id=v.file_id,
            )
        )
    return events
