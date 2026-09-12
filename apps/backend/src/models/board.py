from typing import Any

from sqlalchemy import Boolean, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base_class import Base

MANDATORY_STAGE_KEYS = [
    'Saved',
    'Applied',
    'Phone Screen',
    'Interview',
    'Offer',
    'Accepted',
    'Rejected',
    'Withdrawn',
    'Ghosted',
    'Archived',
]


class Board(Base):
    __tablename__ = 'boards'

    name: Mapped[str] = mapped_column(Text, nullable=False)
    color: Mapped[str | None] = mapped_column(String(30), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    stages: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text('false'))

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    def __repr__(self) -> str:
        return f'<Board id={self.id} name={self.name}>'
