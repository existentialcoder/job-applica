from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from ..db.base_class import Base


class ConnectedAccount(Base):
    __tablename__ = 'connected_accounts'

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # 'google' | 'linkedin'
    provider_user_id: Mapped[str] = mapped_column(Text, nullable=False)
    provider_email: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Encrypted at rest via src/core/crypto.py
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Full list of OAuth scopes currently granted, e.g.:
    # ["openid","email","profile","https://www.googleapis.com/auth/gmail.readonly"]
    scopes: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    connected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship('User', back_populates='connected_accounts')

    __table_args__ = (
        UniqueConstraint('user_id', 'provider', name='uq_connected_accounts_user_provider'),
        Index('ix_connected_accounts_provider_uid', 'provider', 'provider_user_id', unique=True),
    )

    # ── Scope helpers ─────────────────────────────────────────────────────────

    @property
    def has_gmail(self) -> bool:
        return 'https://www.googleapis.com/auth/gmail.readonly' in (self.scopes or [])

    @property
    def has_calendar(self) -> bool:
        return 'https://www.googleapis.com/auth/calendar.events' in (self.scopes or [])

    def __repr__(self) -> str:
        return f'<ConnectedAccount user={self.user_id} provider={self.provider}>'
