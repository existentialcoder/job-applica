from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ....schemas import skills as schemas
from ...deps.db import get_db
from ...deps.pagination import pagination_params
from ....services import skill as skills_service

router = APIRouter(prefix='/skills')

@router.get('', response_model=skills_service.PaginatedSkills, description='List all skills')
def list_skills(pagination: dict = Depends(pagination_params), db: Session = Depends(get_db)):
    return skills_service.get_skills(db, pagination)
    
@router.post('/', response_model=schemas.Skill, description='Create a new skill')
def create_skill(skill_data: schemas.SkillCreate, db: Session = Depends(get_db)):
    return skills_service.create_skill(db, skill_data)
