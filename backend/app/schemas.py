"""
schemas.py
----------
Pydantic v2 response / request schemas shared across all routes.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


# ── File ──────────────────────────────────────────────────────────────────────

class FileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    original_name: str
    mime_type: str | None
    size: int
    current_version: int
    content_hash: str | None
    created_at: datetime
    updated_at: datetime


# ── Version ───────────────────────────────────────────────────────────────────

class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_id: int
    version_number: int
    size: int
    content_hash: str | None
    message: str | None
    author: str | None
    created_at: datetime


# ── Upload response ───────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    file: FileOut
    version: VersionOut
    is_new_file: bool


# ── Timeline ──────────────────────────────────────────────────────────────────

class TimelineEvent(BaseModel):
    id: int
    type: str          # "upload" | "restore" | "delete"
    description: str
    version: int
    time: str          # ISO-8601 string
    file_id: int
