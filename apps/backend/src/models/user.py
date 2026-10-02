from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base_class import Base

if TYPE_CHECKING:
    from .connected_account import ConnectedAccount
    from .skill import Skill

user_skill_table = Table(
    'user_skill',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True),
    Column('source', String(10), nullable=False, server_default=text("'manual'")),
    Column('resume_id', Integer, ForeignKey('resumes.id', ondelete='SET NULL'), nullable=True),
    CheckConstraint("source IN ('cv', 'manual')", name='ck_user_skill_source'),
)


class User(Base):
    __tablename__ = 'users'

    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[str] = mapped_column(Text, nullable=False)
    user_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True, index=True)
    signup_key: Mapped[str] = mapped_column(Text, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(Text, nullable=True)
    security_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashed_security_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
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


class UserOnboarding(Base):
    __tablename__ = 'user_onboarding'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    step: Mapped[str] = mapped_column(String(32), nullable=False, default='welcome', server_default=text("'welcome'"))
    skipped_steps: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default=text("'{}'")
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dismissed_cards: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default=text("'{}'")
    )
    first_import_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AccountRecovery(Base):
    """Security data kept off users/users.settings so it is never returned to the browser."""

    __tablename__ = 'account_recovery'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    security_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashed_security_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    otp_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    otp_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    otp_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text('0'))


class UsageCounter(Base):
    """Plan-limit counts per period, incremented atomically with INSERT ... ON CONFLICT DO UPDATE."""

    __tablename__ = 'usage_counters'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    resource: Mapped[str] = mapped_column(String(50), nullable=False)
    period: Mapped[str] = mapped_column(String(7), nullable=False)  # 'YYYY-MM'
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text('0'))

    __table_args__ = (UniqueConstraint('user_id', 'resource', 'period', name='uq_usage_counters_user_resource_period'),)
