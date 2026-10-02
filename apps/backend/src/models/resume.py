from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base_class import Base


class Resume(Base):
    __tablename__ = 'resumes'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    original_name: Mapped[str] = mapped_column(Text, nullable=False)
    stored_name: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parsed_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default=text('1'))
    replaces_resume_id: Mapped[int | None] = mapped_column(ForeignKey('resumes.id', ondelete='SET NULL'), nullable=True)

    def __repr__(self) -> str:
        return f'<Resume id={self.id} user={self.user_id} name={self.original_name}>'


class ResumeSnapshot(Base):
    """Read-only extracted profile of one CV version, built from redacted text (no contact details)."""

    __tablename__ = 'resume_snapshots'

    resume_id: Mapped[int] = mapped_column(ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    headline: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_company: Mapped[str | None] = mapped_column(Text, nullable=True)
    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb")
    )
    education: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb")
    )
    skills: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list, server_default=text("'{}'"))
    # sha256 of the file's text; an unchanged re-upload reuses the existing snapshot
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
