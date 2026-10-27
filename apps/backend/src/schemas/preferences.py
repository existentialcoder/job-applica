from typing import Literal

from pydantic import BaseModel, Field, model_validator

from ..models.job import JobPosition, JobWorkModel

JobType = Literal['Full-time', 'Part-time', 'Contract']


class PreferredLocation(BaseModel):
    city: str | None = None
    country: str | None = None


class JobPreferences(BaseModel):
    model_config = {'from_attributes': True}

    target_titles: list[str] = []
    locations: list[PreferredLocation] = []
    work_models: list[JobWorkModel] = []
    seniority: list[JobPosition] = []
    job_types: list[JobType] = []
    salary_min: int | None = Field(None, ge=0)
    salary_currency: str | None = Field(None, min_length=3, max_length=3)
    salary_period: Literal['year', 'month', 'hour'] | None = None
    notice_period_days: int | None = Field(None, ge=0)
    open_to_relocation: bool = False
    needs_visa_sponsorship: bool = False

    @model_validator(mode='after')
    def _salary_needs_currency(self) -> 'JobPreferences':
        if self.salary_min is not None and not self.salary_currency:
            raise ValueError('salary_currency is required with salary_min')
        return self
