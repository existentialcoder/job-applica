from typing import Any
from sqlalchemy import String, ForeignKey, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from ..db.base_class import Base

DEFAULT_STAGES = [
    {"key": "Saved", "label": "Saved", "color": "bg-slate-500"},
    {"key": "Applied", "label": "Applied", "color": "bg-blue-500"},
    {"key": "Phone Screen", "label": "Phone Screen", "color": "bg-amber-500"},
    {"key": "Interview", "label": "Interview", "color": "bg-amber-500"},
    {"key": "Technical", "label": "Technical", "color": "bg-orange-500"},
    {"key": "Offer", "label": "Offer", "color": "bg-emerald-500"},
    {"key": "Rejected", "label": "Rejected", "color": "bg-red-500"},
    {"key": "Withdrawn", "label": "Withdrawn", "color": "bg-zinc-400"},
]


class Board(Base):
    __tablename__ = 'boards'

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str | None] = mapped_column(String(30), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    stages: Mapped[list[Any]] = mapped_column(
        JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb")
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text('false')
    )

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    def __repr__(self) -> str:
        return f'<Board id={self.id} name={self.name}>'
