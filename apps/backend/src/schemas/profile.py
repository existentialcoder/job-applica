from datetime import datetime
from typing import Any, get_args

from pydantic import BaseModel, field_validator

from ..models.job import JobPosition, JobWorkModel
from .preferences import JobType

_KNOWN = {
    'work_model': [m.value for m in JobWorkModel],
    'job_type': list(get_args(JobType)),
    'seniority': [p.value for p in JobPosition],
}


def _squash(value: str) -> str:
    return ''.join(c for c in value.lower() if c.isalpha())


class ExperienceEntry(BaseModel):
    title: str
    company: str | None = None
    company_website: str | None = None
    start: str | None = None  # 'YYYY-MM'
    end: str | None = None  # None while the role is ongoing
    highlights: list[str] = []
    work_model: JobWorkModel | None = None
    job_type: JobType | None = None
    seniority: JobPosition | None = None

    @field_validator('work_model', 'job_type', 'seniority', mode='before')
    @classmethod
    def _known_or_none(cls, value: Any, info) -> str | None:
        # The AI writes 'Onsite' or 'full time'; anything that isn't one of ours is dropped, not a failed CV.
        if not isinstance(value, str):
            return None
        return next((k for k in _KNOWN[info.field_name] if _squash(k) == _squash(value)), None)


class EducationEntry(BaseModel):
    institution: str
    degree: str | None = None
    field: str | None = None
    start: str | None = None
    end: str | None = None


class Language(BaseModel):
    name: str
    level: str | None = None  # CEFR level (A1–C2) or 'Native', as the CV states it


class Certification(BaseModel):
    name: str
    issuer: str | None = None
    year: int | None = None


class Award(BaseModel):
    title: str
    issuer: str | None = None
    year: int | None = None


class Location(BaseModel):
    city: str | None = None
    country: str | None = None


class ExtractedProfile(BaseModel):
    """What one CV says about its owner, as returned by the extraction call (no contact details)."""

    headline: str | None = None
    summary: str | None = None
    years_experience: int | None = None
    experience: list[ExperienceEntry] = []
    education: list[EducationEntry] = []
    skills: list[str] = []
    languages: list[Language] = []
    certifications: list[Certification] = []
    awards: list[Award] = []
    location: Location | None = None  # where the person lives; goes to contact details, not the snapshot

    def current_role(self) -> ExperienceEntry | None:
        """The role with no end date, else the one that started last."""
        ongoing = [e for e in self.experience if not e.end]
        return max(ongoing or self.experience, key=lambda e: e.start or '', default=None)


class ContactDetails(BaseModel):
    email: str | None = None
    secondary_email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    city: str | None = None
    country: str | None = None


class ProfileFields(BaseModel):
    headline: str | None = None
    current_title: str | None = None
    current_company: str | None = None
    years_experience: int | None = None
    summary: str | None = None
    experience: list[ExperienceEntry] = []
    education: list[EducationEntry] = []
    languages: list[Language] = []
    certifications: list[Certification] = []
    awards: list[Award] = []


class ProfileUpdate(ProfileFields):
    contacts: ContactDetails = ContactDetails()
    confirm: bool = False


class ProfileResponse(ProfileFields):
    contacts: ContactDetails
    auto_filled: list[str]  # fields still exactly as extracted from the CV
    company_logos: dict[str, str | None]  # experience company name -> the tracker company's logo
    source_resume_name: str | None
    confirmed_at: datetime | None
