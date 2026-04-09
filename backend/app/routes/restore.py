"""
routes/restore.py
-----------------
POST /api/files/{file_id}/versions/{version_id}/restore
  – restore an older version (non-destructive, creates new version).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services.version_service import restore_version
from app.schemas import VersionOut

router = APIRouter(prefix="/api/files/{file_id}/versions", tags=["restore"])


@router.post("/{version_id}/restore", response_model=VersionOut, status_code=201)
async def restore(file_id: int, version_id: int, db: Session = Depends(get_db)):
    """
    Restore a file to an older version.

    Creates a **new** version whose content matches the target version —
    the history is never rewritten.
    Returns the newly created version.
    """
    new_version = await restore_version(db, file_id, version_id)
    return new_version
