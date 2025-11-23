from pydantic import BaseModel, HttpUrl
from .base import BaseSchema

class SkillBase(BaseSchema):
    name: str
    label: str
    logo_url: HttpUrl | None = None
    description: str | None = None

class SkillBaseLean(BaseModel):
    name: str
    label: str
    logo_url: HttpUrl | None = None
    model_config = {'from_attributes': True}

class SkillCreate(BaseModel):
    label: str
    logo_url: HttpUrl | None = None
    description: str | None = None

class SkillFilterParams():
    name: str | None
    label: str | None
