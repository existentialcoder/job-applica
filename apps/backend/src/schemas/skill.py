from pydantic import BaseModel, Field
from typing import Optional

class SkillBase(BaseModel):
    name: str
    proficiency_level: int = Field(..., ge=1, le=10)


class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    class Config:
        from_attributes = True
