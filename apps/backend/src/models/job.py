import enum
from sqlalchemy import Enum, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base_class import Base
from .company import Company
from .skill import Skill
from .location import Location

from sqlalchemy import Table, Column

job_skill_table = Table(
    'job_skill',
    Base.metadata,
    Column('job_id', Integer, ForeignKey('jobs.id', ondelete='CASCADE'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True),
)

class JobStatus(str, enum.Enum):
    OPEN = 'Open'
    CLOSED = 'Closed'
    PENDING = 'Pending'


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

class Job(Base):
    __tablename__ = 'jobs'
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        default=JobStatus.OPEN,
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
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    
    years_of_experience: Mapped[dict] = mapped_column(JSON, nullable=True)

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
