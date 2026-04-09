"""
routes/upload.py
----------------
POST /api/files/upload  – accept a multipart file upload.
"""

from fastapi import APIRouter, Depends, Form, UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services.file_service import handle_upload
from app.schemas import FileOut, VersionOut, UploadResponse

router = APIRouter(prefix="/api/files", tags=["upload"])


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_file(
    file: UploadFile = FastAPIFile(..., description="File to upload"),
    message: str | None = Form(None, description="Optional commit message"),
    author: str | None = Form(None, description="Optional author name"),
    db: Session = Depends(get_db),
):
    """
    Upload a new file or a new version of an existing file.

    - If a file with the same name already exists, a new version is created.
    - If the content is identical to an existing version a **409** is returned.
    - Returns the file metadata and the newly created version.
    """
    file_obj, version_obj, is_new = await handle_upload(
        db, file, message=message, author=author
    )
    return UploadResponse(
        file=FileOut.model_validate(file_obj),
        version=VersionOut.model_validate(version_obj),
        is_new_file=is_new,
    )
