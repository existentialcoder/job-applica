from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base_class import Base


class UserProfile(Base):
    """The user's own profile: seeded from their first CV, then edited by them. Contains no contact details."""

    __tablename__ = 'user_profiles'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    source_resume_id: Mapped[int | None] = mapped_column(ForeignKey('resumes.id', ondelete='SET NULL'), nullable=True)
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
    # field name -> 'auto' | 'user'; a 'user' field is never overwritten without the user accepting the change
    field_sources: Mapped[dict[str, str]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    extracted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ProfileContact(Base):
    """Contact details, kept apart from user_profiles because they must never reach an LLM.

    Values are encrypted at rest via src/core/crypto.py.
    """

    __tablename__ = 'profile_contacts'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    # A CV email that differs from the account email (e.g. OAuth signups)
    secondary_email: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    github_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(Text, nullable=True)


class JobPreference(Base):
    __tablename__ = 'job_preferences'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    target_titles: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default=text("'{}'")
    )
    # [{city, country, radius_km}]
    locations: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb")
    )
    # JobWorkModel / JobPosition values; text[] rather than enum[] so adding an enum value needs no migration
    work_models: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default=text("'{}'")
    )
    seniority: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list, server_default=text("'{}'"))
    job_types: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list, server_default=text("'{}'"))
    # BigInteger: yearly amounts in some currencies (IDR, VND) exceed int32
    salary_min: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    salary_period: Mapped[str | None] = mapped_column(String(10), nullable=True)
    notice_period_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    open_to_relocation: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text('false')
    )
    needs_visa_sponsorship: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text('false')
    )
    industries_include: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default=text("'{}'")
    )
    industries_exclude: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default=text("'{}'")
    )
    weekly_job_suggestions: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text('false')
    )

    __table_args__ = (
        CheckConstraint("salary_period IN ('year', 'month', 'hour')", name='ck_job_preferences_salary_period'),
        CheckConstraint('salary_max >= salary_min', name='ck_job_preferences_salary_range'),
    )
