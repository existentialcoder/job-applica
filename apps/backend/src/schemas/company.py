from pydantic import BaseModel, Field, EmailStr, HttpUrl
from .base import BaseSchema

class Company(BaseModel):
    name: str = Field(..., max_length=100)
    website: HttpUrl | None = None
    email: EmailStr | None = None
    size: int | None = None
    industry: str | None = None
    description: str | None = None

class CompanyBase(Company, BaseSchema):
    pass


class CompanyCreate(Company):
    pass


class CompanyUpdate(Company):
    pass
