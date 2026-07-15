from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date

from .base import BaseSchema
from .company import CompanyBase, CompanyCreate
from .skill import SkillBaseLean


class ApplicationStatus(str, Enum):
    Saved = 'Saved'
    Applied = 'Applied'
    PhoneScreen = 'Phone Screen'
    Interview = 'Interview'
    Technical = 'Technical'
    Offer = 'Offer'
    Rejected = 'Rejected'
    Withdrawn = 'Withdrawn'


class JobPosition(str, Enum):
    Intern = 'Intern'
    Junior = 'Junior'
    Mid = 'Mid'
    Senior = 'Senior'
    Lead = 'Lead'
    Manager = 'Manager'


class SourcePlatform(str, Enum):
    LinkedIn = 'LinkedIn'
    Indeed = 'Indeed'
    Glassdoor = 'Glassdoor'
    Monster = 'Monster'
    ZipRecruiter = 'ZipRecruiter'
    Jobscan = 'Jobscan'
    Other = 'Other'


class YearsOfExperience(BaseModel):
    min: Optional[int] = Field(None, ge=0)
    max: Optional[int] = Field(None, ge=0)


class LocationBase(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

    model_config = {'from_attributes': True}

    @field_validator('*', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        return None if v == '' else v

    @classmethod
    def from_string(cls, s: str) -> 'LocationBase':
        parts = [p.strip() or None for p in s.split(',')]
        return cls(
            city=parts[0] if len(parts) > 0 else None,
            state=parts[1] if len(parts) > 1 else None,
            country=parts[2] if len(parts) > 2 else None,
        )


class JobBase(BaseSchema):
    title: str
    company: Optional[CompanyBase] = None
    location: Optional[LocationBase] = None
    status: str = 'Saved'
    position: Optional[JobPosition] = None
    category: Optional[str] = None
    salary_range: Optional[str] = None
    work_model: Optional[str] = None
    board_id: Optional[int] = None

    required_skills: List[SkillBaseLean] = Field(default_factory=list)

    description: Optional[str] = None
    years_of_experience: Optional[YearsOfExperience] = None

    source_url: Optional[str] = None
    source_platform: Optional[SourcePlatform] = None
    applied_date: Optional[date] = None
    notes: Optional[str] = None

    ats_score: Optional[float] = None
    ats_resume_id: Optional[int] = None
    ats_report: Optional[dict] = None

    model_config = {'from_attributes': True}


def _coerce_location(v):
    if isinstance(v, str) and v.strip():
        return LocationBase.from_string(v)
    return v


class JobCreate(BaseModel):
    title: str
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    company: Optional[CompanyCreate] = None
    location: Optional[LocationBase] = None

    @field_validator('location', mode='before')
    @classmethod
    def coerce_location(cls, v):
        return _coerce_location(v)
    status: str = 'Saved'
    position: Optional[JobPosition] = None
    category: Optional[str] = None
    salary_range: Optional[str] = None
    work_model: Optional[str] = 'On-site'
    board_id: Optional[int] = None

    required_skills: List[str] = Field(default_factory=list)

    description: Optional[str] = None
    years_of_experience: Optional[YearsOfExperience] = None

    source_url: Optional[str] = None
    source_platform: Optional[SourcePlatform] = None
    applied_date: Optional[date] = None
    notes: Optional[str] = None

    ats_score: Optional[float] = None
    ats_report: Optional[dict] = None
    ats_resume_id: Optional[int] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    location: Optional[LocationBase] = None

    @field_validator('location', mode='before')
    @classmethod
    def coerce_location(cls, v):
        return _coerce_location(v)
    status: Optional[str] = None
    position: Optional[JobPosition] = None
    category: Optional[str] = None
    salary_range: Optional[str] = None
    work_model: Optional[str] = None
    board_id: Optional[int] = None

    required_skills: Optional[List[str]] = None

    description: Optional[str] = None
    years_of_experience: Optional[YearsOfExperience] = None

    source_url: Optional[str] = None
    source_platform: Optional[SourcePlatform] = None
    applied_date: Optional[date] = None
    notes: Optional[str] = None


class PageExtractRequest(BaseModel):
    page_text: str
    url: str


class JobExtractResult(BaseModel):
    is_job_page: bool
    title: Optional[str] = None
    company: Optional[CompanyCreate] = None
    location: Optional[LocationBase] = None
    description: Optional[str] = None
    salary_range: Optional[str] = None
    work_model: Optional[str] = None
    position: Optional[str] = None
    years_of_experience: Optional[dict] = None
    required_skills: List[str] = Field(default_factory=list)


class JobFilterParams(BaseModel):
    query: Optional[str] = Field(None, description='Search query string')
    title: Optional[str] = Field(None, description='Job title filter')
    company: Optional[str] = Field(None, description='Company name filter')
    location: Optional[str] = Field(None, description='Location filter')
    status: Optional[str] = Field(None, description='Application status filter')
    source_platform: Optional[SourcePlatform] = Field(None, description='Source platform filter')
    source_url: Optional[str] = Field(None, description='Exact source URL match')
    board_id: Optional[int] = Field(None, description='Board ID filter')
