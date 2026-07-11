from typing import Any, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, Table, Column, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from ..db.base_class import Base

if TYPE_CHECKING:
    from .skill import Skill
    from .connected_account import ConnectedAccount

user_skill_table = Table(
    'user_skill',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True),
)


class User(Base):
    __tablename__ = 'users'

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    signup_key: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    plan: Mapped[str] = mapped_column(String(50), nullable=False, default='free')
    settings: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )

    skills: Mapped[list['Skill']] = relationship('Skill', secondary=user_skill_table, lazy='selectin')
    connected_accounts: Mapped[list['ConnectedAccount']] = relationship(
        'ConnectedAccount', back_populates='user', lazy='selectin', cascade='all, delete-orphan'
    )

    def get_connected_account(self, provider: str) -> 'ConnectedAccount | None':
        return next((a for a in self.connected_accounts if a.provider == provider), None)

    def __repr__(self) -> str:
        return f'<User(user_name={self.user_name}, email={self.email})>'
