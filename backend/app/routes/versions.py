"""
routes/versions.py
------------------
Version management endpoints:
  GET    /api/files/{file_id}/versions              – list versions
  GET    /api/files/{file_id}/versions/{version_id} – version detail
  DELETE /api/files/{file_id}/versions/{version_id} – delete a version
  GET    /api/files/{file_id}/versions/{version_id}/download
"""

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services.version_service import (
    get_versions,
    get_version,
    delete_version,
    get_version_bytes,
)
from app.schemas import VersionOut

router = APIRouter(prefix="/api/files/{file_id}/versions", tags=["versions"])


@router.get("", response_model=list[VersionOut])
def list_versions(file_id: int, db: Session = Depends(get_db)):
    """Return all versions of a file, newest first."""
    return get_versions(db, file_id)


@router.get("/{version_id}", response_model=VersionOut)
def version_detail(file_id: int, version_id: int, db: Session = Depends(get_db)):
    """Return metadata for a specific version."""
    return get_version(db, file_id, version_id)


@router.delete("/{version_id}", status_code=204)
def remove_version(file_id: int, version_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific version from disk and DB.
    The current (active) version cannot be deleted.
    """
    delete_version(db, file_id, version_id)


@router.get("/{version_id}/download")
async def download_version(file_id: int, version_id: int, db: Session = Depends(get_db)):
    """Stream the raw file bytes for a specific version."""
    content, filename = await get_version_bytes(db, file_id, version_id)
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
