"""
models/file_model.py
--------------------
SQLAlchemy ORM model for stored files.
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=True)
    size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # bytes

    # Latest version number (denormalised for fast reads)
    current_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # SHA-256 hash of the latest content (for duplicate detection)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=True, index=True)

    # Owner (optional – wire up to User model when auth is added)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ──────────────────────────────
    versions: Mapped[list["Version"]] = relationship(  # noqa: F821
        "Version",
        back_populates="file",
        cascade="all, delete-orphan",
        order_by="Version.version_number.desc()",
    )

    def __repr__(self) -> str:
        return f"<File id={self.id} name={self.name!r} v{self.current_version}>"
