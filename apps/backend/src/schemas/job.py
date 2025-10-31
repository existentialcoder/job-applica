from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

from .company import Company
from .skill import SkillBase


class JobStatus(str, Enum):
    OPEN = 'Open'
    CLOSED = 'Closed'
    PENDING = 'Pending'


class JobPosition(str, Enum):
    INTERN = 'Intern'
    JUNIOR = 'Junior'
    MID = 'Mid'
    SENIOR = 'Senior'
    LEAD = 'Lead'
    MANAGER = 'Manager'


class YearsOfExperience(BaseModel):
    min: Optional[int] = Field(None, ge=0, description='Minimum years of experience')
    max: Optional[int] = Field(None, ge=0, description='Maximum years of experience')


class JobBase(BaseModel):
    title: str
    company: Optional[Company] = None
    status: JobStatus = JobStatus.OPEN
    position: JobPosition
    category: Optional[str] = None
    salary_range: Optional[str] = None
    required_skills: List[SkillBase] = []
    description: str = ''
    years_of_experience: Optional[YearsOfExperience] = None

    model_config = {'from_attributes': True}


class JobRead(JobBase):
    id: int
    created_at: Optional[date] = None
    updated_at: Optional[date] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    job_title: Optional[str] = None
    status: Optional[JobStatus] = None
    position: Optional[JobPosition] = None
    category: Optional[str] = None
    salary_range: Optional[str] = None
    required_skills: Optional[List[SkillBase]] = None
    job_description: Optional[str] = None
    years_of_experience: Optional[YearsOfExperience] = None
