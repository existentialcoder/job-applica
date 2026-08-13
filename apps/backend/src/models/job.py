import enum

from sqlalchemy import JSON, Column, Date, Enum, Float, ForeignKey, Integer, Table, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base_class import Base
from .board import Board
from .company import Company
from .skill import Skill
from .user import User

job_skill_table = Table(
    'job_skill',
    Base.metadata,
    Column('job_id', Integer, ForeignKey('jobs.id', ondelete='CASCADE'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True),
)


class ApplicationStatus(enum.StrEnum):
    SAVED = 'Saved'
    APPLIED = 'Applied'
    PHONE_SCREEN = 'Phone Screen'
    INTERVIEW = 'Interview'
    TECHNICAL = 'Technical'
    OFFER = 'Offer'
    REJECTED = 'Rejected'
    WITHDRAWN = 'Withdrawn'


class JobPosition(enum.StrEnum):
    INTERN = 'Intern'
    JUNIOR = 'Junior'
    MID = 'Mid'
    SENIOR = 'Senior'
    LEAD = 'Lead'
    MANAGER = 'Manager'


class JobWorkModel(enum.StrEnum):
    ON_SITE = 'On-site'
    REMOTE = 'Remote'
    HYBRID = 'Hybrid'


class SourcePlatform(enum.StrEnum):
    LINKEDIN = 'LinkedIn'
    INDEED = 'Indeed'
    GLASSDOOR = 'Glassdoor'
    MONSTER = 'Monster'
    ZIPRECRUITER = 'ZipRecruiter'
    JOBSCAN = 'Jobscan'
    OTHER = 'Other'


class Job(Base):
    __tablename__ = 'jobs'
    title: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(Text, nullable=False, default='Saved')
    position: Mapped[JobPosition] = mapped_column(Enum(JobPosition), default=JobPosition.INTERN, nullable=True)
    category: Mapped[str] = mapped_column(Text, nullable=True)
    salary_range: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    years_of_experience: Mapped[dict] = mapped_column(JSON, nullable=True)

    source_url: Mapped[str] = mapped_column(Text, nullable=True)
    source_platform: Mapped[SourcePlatform] = mapped_column(Enum(SourcePlatform, name='sourceplatform'), nullable=True)
    applied_date: Mapped[Date] = mapped_column(Date, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    ats_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ats_resume_id: Mapped[int | None] = mapped_column(ForeignKey('resumes.id', ondelete='SET NULL'), nullable=True)
    ats_report: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    user: Mapped['User'] = relationship('User')
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    company: Mapped['Company'] = relationship('Company')
    company_id: Mapped[int] = mapped_column(ForeignKey('companies.id'), nullable=True)

    required_skills: Mapped[list['Skill']] = relationship('Skill', secondary=job_skill_table)
    work_model: Mapped[JobWorkModel] = mapped_column(
        Enum(JobWorkModel, name='jobworkmodel'), default=JobWorkModel.ON_SITE, nullable=False
    )

    location: Mapped[dict | None] = mapped_column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))
    board: Mapped['Board'] = relationship('Board')
    board_id: Mapped[int | None] = mapped_column(ForeignKey('boards.id', ondelete='SET NULL'), nullable=True)

    def __repr__(self):
        return f'<Job id={self.id} title={self.title}>'
