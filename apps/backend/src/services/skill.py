from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from fastapi import HTTPException

from ..models.skill import Skill
from ..schemas.skill import SkillBase, SkillBaseLean, SkillCreate, SkillFilterParams
from ..api.deps.pagination import build_paginated_response, paginate_query, get_paginated_response_model

PaginatedSkillsBase = get_paginated_response_model(SkillBase)
PaginatedSkillsBaseLean = get_paginated_response_model(SkillBaseLean)


def extract_skill_name_from_label(label: str) -> str:
    name = ''.join(char.lower() if char.isalpha() or char.isspace() else '' for char in label)
    name = '_'.join(name.split())
    return name


async def get_skills(db: AsyncSession, pagination: dict, filter: SkillFilterParams = None, source: str = 'api'):
    count_result = await db.execute(select(func.count()).select_from(Skill))
    total = count_result.scalar()

    q = select(Skill)
    if pagination:
        q = paginate_query(q, pagination)
    if filter and (filter['name'] or filter['label']):
        q = q.where(or_(Skill.name == filter['name'], Skill.label == filter['label']))

    result = await db.execute(q)
    skills_objs = result.scalars().all()
    skills = [SkillBase.model_validate(s) if source == 'api' else s for s in skills_objs]

    return build_paginated_response(items=skills, total=total, **pagination) if pagination else skills


async def create_skill(db: AsyncSession, skill_data: SkillCreate, source: str = 'api') -> SkillBase:
    skill_name = extract_skill_name_from_label(skill_data.label)

    result = await db.execute(select(Skill).where(Skill.name == skill_name))
    existing = result.scalars().first()
    if existing:
        return SkillBase.model_validate(existing) if source == 'api' else existing

    skill_obj = Skill(name=skill_name, **skill_data.model_dump(exclude_unset=True))
    db.add(skill_obj)
    await db.commit()
    await db.refresh(skill_obj)
    return SkillBase.model_validate(skill_obj) if source == 'api' else skill_obj
