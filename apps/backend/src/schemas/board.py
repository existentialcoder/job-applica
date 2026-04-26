from pydantic import BaseModel
from typing import Optional, List, Dict
from .base import BaseSchema


class StageSchema(BaseModel):
    key: str
    label: str
    color: str

    model_config = {'from_attributes': True}


class BoardBase(BaseSchema):
    name: str
    color: Optional[str] = None
    description: Optional[str] = None
    stages: List[StageSchema] = []
    is_default: bool = False

    model_config = {'from_attributes': True}


class BoardCreate(BaseModel):
    name: str
    color: Optional[str] = None
    description: Optional[str] = None
    stages: Optional[List[StageSchema]] = None


class BoardUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    stages: Optional[List[StageSchema]] = None
    key_renames: Optional[Dict[str, str]] = None
