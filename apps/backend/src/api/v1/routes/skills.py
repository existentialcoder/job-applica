from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ....schemas import skill as schemas
from ...deps.db import get_db
from ...deps.pagination import pagination_params
from ....services import skill as skills_service

router = APIRouter(prefix='/skills')

@router.get('', response_model=skills_service.PaginatedSkillsBase, description='List all skills')
async def list_skills(pagination: dict = Depends(pagination_params), db: AsyncSession = Depends(get_db)):
    return await skills_service.get_skills(db, pagination)

@router.post('/', response_model=schemas.SkillBase, description='Create a new skill')
async def create_skill(skill_data: schemas.SkillCreate, db: AsyncSession = Depends(get_db)):
    return await skills_service.create_skill(db, skill_data)
