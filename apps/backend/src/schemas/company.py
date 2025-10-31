from pydantic import BaseModel, Field, EmailStr, HttpUrl
from uuid import UUID
from datetime import datetime
from typing import Optional

class CompanyBase(BaseModel):
    name: str = Field(..., max_length=100)
    website: HttpUrl | None = None
    email: EmailStr | None = None
    location: str
    size: int | None = None
    headquarters: str | None = None
    founded_year: int | None = None
    website: str | None = None
    industry: str | None = None
    description: str | None = None



class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    pass


class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
