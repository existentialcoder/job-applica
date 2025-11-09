from pydantic import BaseModel, Field
from .base import BaseSchema
from typing import Optional

class Skill(BaseModel):
    name: str
class SkillBase(Skill, BaseSchema):
    name: str

class SkillCreate(Skill):
    pass
