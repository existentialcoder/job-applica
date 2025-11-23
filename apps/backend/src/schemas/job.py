from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

from .base import BaseSchema
from .company import CompanyBase
from .skill import SkillBaseLean


class JobStatus(str, Enum):
    Open = 'Open'
    Closed = 'Closed'
    Pending = 'Pending'


class JobPosition(str, Enum):
    Intern = 'Intern'
    Junior = 'Junior'
    Mid = 'Mid'
    Senior = 'Senior'
    Lead = 'Lead'
    Manager = 'Manager'


class YearsOfExperience(BaseModel):
    min: Optional[int] = Field(None, ge=0, description='Minimum years of experience')
    max: Optional[int] = Field(None, ge=0, description='Maximum years of experience')


class JobBase(BaseSchema):
    title: str
    company: Optional[CompanyBase] = None
    status: JobStatus = JobStatus.Open
    position: JobPosition = JobPosition.Intern
    category: Optional[str] = None
    salary_range: Optional[str] = None

    # Avoid mutable defaults
    required_skills: List[SkillBaseLean] = Field(default_factory=list)

    description: str = ''
    years_of_experience: Optional[YearsOfExperience] = None

    model_config = {'from_attributes': True}


class JobCreate(BaseModel):
    title: str
    company_id: Optional[int] = None
    status: JobStatus = JobStatus.Open
    position: JobPosition = JobPosition.Intern
    category: Optional[str] = None
    salary_range: Optional[str] = None

    # Avoid mutable default list
    required_skills: List[str] = Field(default_factory=list)

    description: str
    years_of_experience: Optional[YearsOfExperience] = None


class JobUpdate(JobCreate):
    title: Optional[str] = None
    company_id: Optional[int] = None
    status: Optional[JobStatus] = None
    position: Optional[JobPosition] = None
    category: Optional[str] = None
    salary_range: Optional[str] = None

    # Note: leaving this field name as-is per your request
    required_skills: Optional[List[str]] = None

    description: Optional[str] = None
    years_of_experience: Optional[YearsOfExperience] = None


class JobFilterParams(BaseSchema):
    query: Optional[str] = Field(None, description='Search query string')
    title: Optional[str] = Field(None, description='Job title')
    company: Optional[str] = Field(None, description='Company name')
    location: Optional[str] = Field(None, description='Job location')
