import enum
from sqlalchemy import Enum, String, Integer, ForeignKey, JSON, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base_class import Base
from .company import Company
from .user import User
from .skill import Skill
from .location import Location

from sqlalchemy import Table, Column

job_skill_table = Table(
    'job_skill',
    Base.metadata,
    Column('job_id', Integer, ForeignKey('jobs.id', ondelete='CASCADE'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True),
)

class ApplicationStatus(str, enum.Enum):
    SAVED = 'Saved'
    APPLIED = 'Applied'
    PHONE_SCREEN = 'Phone Screen'
    INTERVIEW = 'Interview'
    TECHNICAL = 'Technical'
    OFFER = 'Offer'
    REJECTED = 'Rejected'
    WITHDRAWN = 'Withdrawn'


class JobPosition(str, enum.Enum):
    INTERN = 'Intern'
    JUNIOR = 'Junior'
    MID = 'Mid'
    SENIOR = 'Senior'
    LEAD = 'Lead'
    MANAGER = 'Manager'

class JobWorkModel(str, enum.Enum):
    ON_SITE = 'On-site'
    REMOTE = 'Remote'
    HYBRID = 'Hybrid'

class SourcePlatform(str, enum.Enum):
    LINKEDIN = 'LinkedIn'
    INDEED = 'Indeed'
    GLASSDOOR = 'Glassdoor'
    MONSTER = 'Monster'
    ZIPRECRUITER = 'ZipRecruiter'
    JOBSCAN = 'Jobscan'
    OTHER = 'Other'

class Job(Base):
    __tablename__ = 'jobs'
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name='applicationstatus'),
        default=ApplicationStatus.SAVED,
        create_constraint=True,
        nullable=False
    )
    position: Mapped[JobPosition] = mapped_column(
        Enum(JobPosition),
        default=JobPosition.INTERN,
        create_constraint=True,
        nullable=True
    )
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    salary_range: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    years_of_experience: Mapped[dict] = mapped_column(JSON, nullable=True)

    source_url: Mapped[str] = mapped_column(Text, nullable=True)
    source_platform: Mapped[SourcePlatform] = mapped_column(
        Enum(SourcePlatform, name='sourceplatform'),
        nullable=True
    )
    applied_date: Mapped[Date] = mapped_column(Date, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    user: Mapped['User'] = relationship('User')
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    company: Mapped['Company'] = relationship('Company')
    company_id: Mapped[int] = mapped_column(ForeignKey('companies.id'), nullable=True)

    required_skills: Mapped[list['Skill']] = relationship(
        'Skill',
        secondary=job_skill_table
    )
    work_model: Mapped[JobWorkModel] = mapped_column(
        Enum(JobWorkModel, name='jobworkmodel'),
        default=JobWorkModel.ON_SITE,
        create_constraint=True,
        nullable=False
    )

    location: Mapped['Location'] = relationship('Location')
    location_id: Mapped[int] = mapped_column(ForeignKey('locations.id'), nullable=True)

    def __repr__(self):
        return f'<Job id={self.id} title={self.title}>'
