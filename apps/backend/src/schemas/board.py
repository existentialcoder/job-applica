from pydantic import BaseModel

from .base import BaseSchema


class StageSchema(BaseModel):
    key: str
    label: str
    color: str

    model_config = {'from_attributes': True}


class BoardBase(BaseSchema):
    name: str
    color: str | None = None
    description: str | None = None
    stages: list[StageSchema] = []
    is_default: bool = False
    number_of_jobs: int = 0

    model_config = {'from_attributes': True}


class BoardCreate(BaseModel):
    name: str
    color: str | None = None
    description: str | None = None
    stages: list[StageSchema] | None = None


class BoardUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    description: str | None = None
    stages: list[StageSchema] | None = None
    key_renames: dict[str, str] | None = None
