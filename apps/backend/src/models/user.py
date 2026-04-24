from typing import Any
from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from ..db.base_class import Base

class User(Base):
    __tablename__ = 'users'
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    signup_key: Mapped[str] = mapped_column(String(255), nullable=False)
    # Nullable: OAuth users have no password
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # OAuth provider IDs
    google_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    linkedin_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Flexible user preferences shared across web app and extension
    settings: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )

    def __repr__(self) -> str:
        return f'<User(user_name={self.user_name}, email={self.email})>'
