"""
services/duplicate_checker.py
------------------------------
Detects duplicate or near-duplicate file uploads by comparing content hashes.
"""

from sqlalchemy.orm import Session

from app.models.file_model import File
from app.models.version_model import Version


def find_duplicate_file(db: Session, content_hash: str) -> File | None:
    """
    Return an existing File whose latest content hash matches *content_hash*,
    or None if no duplicate is found.
    """
    return db.query(File).filter(File.content_hash == content_hash).first()


def find_duplicate_version(db: Session, file_id: int, content_hash: str) -> Version | None:
    """
    Return an existing Version of *file_id* whose hash matches *content_hash*.
    Useful to warn users they are re-uploading identical content.
    """
    return (
        db.query(Version)
        .filter(Version.file_id == file_id, Version.content_hash == content_hash)
        .first()
    )


def is_exact_duplicate(db: Session, content_hash: str, file_id: int | None = None) -> bool:
    """
    Quick boolean check.
    If *file_id* is given, check only within that file's versions.
    Otherwise, check across all files.
    """
    if file_id is not None:
        return find_duplicate_version(db, file_id, content_hash) is not None
    return find_duplicate_file(db, content_hash) is not None
