from pydantic import BaseModel, Field, EmailStr, HttpUrl
from .base import BaseSchema


class CompanyFields(BaseModel):
    name: str = Field(..., max_length=100)
    website: HttpUrl | None = None
    email: EmailStr | None = None
    size: int | None = None
    industry: str | None = None
    description: str | None = None
    logo_url: HttpUrl | None = None


class CompanyBase(BaseSchema, CompanyFields):
    """Returned from API responses"""
    pass


class CompanyCreate(CompanyFields):
    """Used for creating a company"""
    pass


class CompanyUpdate(CompanyFields):
    """Used for updating a company"""
    pass
