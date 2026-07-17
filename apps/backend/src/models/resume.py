from sqlalchemy import Integer, ForeignKey, Text, Boolean
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

    def __repr__(self) -> str:
        return f'<Resume id={self.id} user={self.user_id} name={self.original_name}>'
