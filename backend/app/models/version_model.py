"""
models/version_model.py
-----------------------
SQLAlchemy ORM model for file versions.
Each row represents one snapshot of a file's content.
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class Version(Base):
    __tablename__ = "versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key to parent file
    file_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True
    )

    version_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relative path on disk (inside STORAGE_DIR)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)

    size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # bytes
    content_hash: Mapped[str] = mapped_column(String(64), nullable=True, index=True)

    # Optional commit-style message
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Who created this version
    author: Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Relationships ──────────────────────────────
    file: Mapped["File"] = relationship("File", back_populates="versions")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Version file_id={self.file_id} v{self.version_number}>"
