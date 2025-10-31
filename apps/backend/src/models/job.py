# src/models/job.py
from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base_class import Base
from .company import Company
from .skill import Skill

from sqlalchemy import Table, Column

job_skill_table = Table(
    'job_skill',
    Base.metadata,
    Column('job_id', Integer, ForeignKey('jobs.id', ondelete='CASCADE'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True),
)

class Job(Base):
    __tablename__ = 'jobs'
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)

    status: Mapped[str] = mapped_column(String(50), nullable=False)
    position: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    salary_range: Mapped[str] = mapped_column(String(100), nullable=True)
    job_description: Mapped[str] = mapped_column(String(500), nullable=True)
    
    years_of_experience: Mapped[dict] = mapped_column(JSON, nullable=True)

    company: Mapped['Company'] = relationship('Company', back_populates='jobs')
    company_id: Mapped[int] = mapped_column(ForeignKey('companies.id'), nullable=True)

    required_skills: Mapped[list['Skill']] = relationship(
        'Skill',
        secondary=job_skill_table,
        back_populates='jobs',
    )

    def __repr__(self):
        return f'<Job id={self.id} title={self.job_title}>'
