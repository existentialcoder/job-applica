import enum
from datetime import date

from pydantic import BaseModel, Field, field_validator

from .base import BaseSchema
from .company import CompanyBase, CompanyCreate
from .skill import SkillBaseLean


class ApplicationStatus(enum.StrEnum):
    Saved = 'Saved'
    Applied = 'Applied'
    PhoneScreen = 'Phone Screen'
    Interview = 'Interview'
    Technical = 'Technical'
    Offer = 'Offer'
    Rejected = 'Rejected'
    Withdrawn = 'Withdrawn'


class JobPosition(enum.StrEnum):
    Intern = 'Intern'
    Junior = 'Junior'
    Mid = 'Mid'
    Senior = 'Senior'
    Lead = 'Lead'
    Manager = 'Manager'


class SourcePlatform(enum.StrEnum):
    LinkedIn = 'LinkedIn'
    Indeed = 'Indeed'
    Glassdoor = 'Glassdoor'
    Monster = 'Monster'
    ZipRecruiter = 'ZipRecruiter'
    Jobscan = 'Jobscan'
    Other = 'Other'


class YearsOfExperience(BaseModel):
    min: int | None = Field(None, ge=0)
    max: int | None = Field(None, ge=0)


class LocationBase(BaseModel):
    city: str | None = None
    state: str | None = None
    country: str | None = None

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
    company: CompanyBase | None = None
    location: LocationBase | None = None
    status: str = 'Saved'
    position: JobPosition | None = None
    category: str | None = None
    salary_range: str | None = None
    work_model: str | None = None
    board_id: int | None = None

    required_skills: list[SkillBaseLean] = Field(default_factory=list)

    description: str | None = None
    years_of_experience: YearsOfExperience | None = None

    source_url: str | None = None
    source_platform: SourcePlatform | None = None
    applied_date: date | None = None
    notes: str | None = None

    ats_score: float | None = None
    ats_resume_id: int | None = None
    ats_report: dict | None = None

    model_config = {'from_attributes': True}


def _coerce_location(v):
    if isinstance(v, str) and v.strip():
        return LocationBase.from_string(v)
    return v


class JobCreate(BaseModel):
    title: str
    company_id: int | None = None
    company_name: str | None = None
    company: CompanyCreate | None = None
    location: LocationBase | None = None

    @field_validator('location', mode='before')
    @classmethod
    def coerce_location(cls, v):
        return _coerce_location(v)

    status: str = 'Saved'
    position: JobPosition | None = None
    category: str | None = None
    salary_range: str | None = None
    work_model: str | None = 'On-site'
    board_id: int | None = None

    required_skills: list[str] = Field(default_factory=list)

    description: str | None = None
    years_of_experience: YearsOfExperience | None = None

    source_url: str | None = None
    source_platform: SourcePlatform | None = None
    applied_date: date | None = None
    notes: str | None = None

    ats_score: float | None = None
    ats_report: dict | None = None
    ats_resume_id: int | None = None


class JobUpdate(BaseModel):
    title: str | None = None
    company_id: int | None = None
    company_name: str | None = None
    location: LocationBase | None = None

    @field_validator('location', mode='before')
    @classmethod
    def coerce_location(cls, v):
        return _coerce_location(v)

    status: str | None = None
    position: JobPosition | None = None
    category: str | None = None
    salary_range: str | None = None
    work_model: str | None = None
    board_id: int | None = None

    required_skills: list[str] | None = None

    description: str | None = None
    years_of_experience: YearsOfExperience | None = None

    source_url: str | None = None
    source_platform: SourcePlatform | None = None
    applied_date: date | None = None
    notes: str | None = None


class PageExtractRequest(BaseModel):
    page_text: str
    url: str


class JobExtractResult(BaseModel):
    is_job_page: bool
    title: str | None = None
    company: CompanyCreate | None = None
    location: LocationBase | None = None
    description: str | None = None
    salary_range: str | None = None
    work_model: str | None = None
    position: str | None = None
    years_of_experience: dict | None = None
    required_skills: list[str] = Field(default_factory=list)


class JobFilterParams(BaseModel):
    query: str | None = Field(None, description='Search query string')
    title: str | None = Field(None, description='Job title filter')
    company: str | None = Field(None, description='Company name filter')
    location: str | None = Field(None, description='Location filter')
    status: str | None = Field(None, description='Application status filter')
    source_platform: SourcePlatform | None = Field(None, description='Source platform filter')
    source_url: str | None = Field(None, description='Exact source URL match')
    board_id: int | None = Field(None, description='Board ID filter')
