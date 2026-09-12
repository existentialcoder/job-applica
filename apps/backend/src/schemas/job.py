import enum
from datetime import datetime
from typing import ClassVar

from fastapi import Query
from pydantic import BaseModel, Field, HttpUrl, ValidationInfo, field_validator

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
    applied_date: datetime | None = None
    notes: str | None = None

    ats_score: float | None = None
    ats_resume_id: int | None = None
    ats_report: dict | None = None

    model_config = {'from_attributes': True}


class JobCreate(BaseModel):
    title: str
    company_id: int | None = None
    company_name: str | None = None
    company: CompanyCreate | None = None
    location: LocationBase | None = None

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
    applied_date: datetime | None = None
    notes: str | None = None

    ats_score: float | None = None
    ats_report: dict | None = None
    ats_resume_id: int | None = None


class JobUpdate(BaseModel):
    title: str | None = None
    company_id: int | None = None
    company_name: str | None = None
    location: LocationBase | None = None

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
    applied_date: datetime | None = None
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
    company: list[str] | None = Field(Query(None), description='Company name filter')
    city: list[str] | None = Field(Query(None), description='City filter')
    state: list[str] | None = Field(Query(None), description='State filter')
    country: list[str] | None = Field(Query(None), description='Country filter')
    status: list[str] | None = Field(Query(None), description='Application status filter')
    source_platform: SourcePlatform | None = Field(None, description='Source platform filter')
    board_id: list[str] | None = Field(Query(None), description='Board ID filter')
    position: list[str] | None = Field(Query(None), description='List of positions to filter')
    work_model: list[str] | None = Field(Query(None), description='List of work models to filter')
    created_from: datetime | None = Field(None, description='Filter jobs created after this date')
    created_to: datetime | None = Field(None, description='Filter jobs created before this date')
    applied_from: datetime | None = Field(None, description='Filter jobs applied after this date')
    applied_to: datetime | None = Field(None, description='Filter jobs applied before this date')
    ats_score_min: float | None = Field(None, description='Minimum ATS score filter', ge=0.0)
    ats_score_max: float | None = Field(None, description='Maximum ATS score filter', le=100.0)
    source_url: HttpUrl | None = Field(None, description='Filter jobs by source URL')

    _LIST_FIELDS: ClassVar[set[str]] = {
        'company',
        'city',
        'state',
        'country',
        'status',
        'board_id',
        'position',
        'work_model',
    }
    _DATE_FIELDS: ClassVar[set[str]] = {'created_from', 'created_to', 'applied_from', 'applied_to'}

    @field_validator('*', mode='after')
    @classmethod
    def parse_field_as_required(cls, v, info: ValidationInfo):
        if v is None or v == '':
            return None

        if info.field_name in cls._DATE_FIELDS:
            if isinstance(v, str):
                try:
                    return datetime.fromisoformat(v)
                except ValueError:
                    raise ValueError(f"Invalid date format for {info.field_name}. Expected YYYY-MM-DD or ISO format.")
            elif isinstance(v, datetime):
                return v
            else:
                raise ValueError(f"Invalid type for {info.field_name}. Expected string or datetime.")

        if info.field_name not in cls._LIST_FIELDS:
            return v

        items = [v] if isinstance(v, str) else v
        parts = [part for item in items for part in (item.split(',') if isinstance(item, str) else [item])]
        return [int(part) for part in parts] if info.field_name == 'board_id' else parts


class JobTimeLineBase(BaseSchema):
    from_status: str | None = None
    to_status: str
