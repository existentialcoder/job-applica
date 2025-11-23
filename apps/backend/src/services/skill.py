from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.skill import Skill
from ..schemas.skill import SkillBase, SkillBaseLean, SkillCreate, SkillFilterParams
from ..api.deps.pagination import build_paginated_response, paginate_query, get_paginated_response_model

PaginatedSkillsBase = get_paginated_response_model(SkillBase)
PaginatedSkillsBaseLean = get_paginated_response_model(SkillBaseLean)

def extract_skill_name_from_label(label: str) -> str:
    '''
    Lower case, replace all spaces with underscores, remove numbers and special characters
    e.g. "Machine Learning 101!" -> "machine_learning"
    '''
    name = ''.join(char.lower() if char.isalpha() or char.isspace() else '' for char in label)
    name = '_'.join(name.split())
    return name


def get_skills(db: Session, pagination: dict, filter: SkillFilterParams = None, source: str='api') -> PaginatedSkillsBase | PaginatedSkillsBaseLean | list[SkillBase] | list[SkillBaseLean]:
    q = db.query(Skill)

    total = q.count()
    if pagination:
        q = paginate_query(q, pagination)

    if filter and (filter['name'] or filter['label']):
        q = q.filter(or_(Skill.name == filter['name'], Skill.label == filter['label']))

    results = q.all()

    skills = [SkillBase.model_validate(skill) if source == 'api' else skill for skill in results]

    return build_paginated_response(
        items=skills,
        total=total,
        **pagination
    ) if pagination else skills


def create_skill(db: Session, skill_data: SkillCreate, source: str = 'api') -> SkillBase:
    skill_name = extract_skill_name_from_label(skill_data.label)
    existing_skills_with_name = db.query(Skill).filter(Skill.name == skill_name).all()
    if len(existing_skills_with_name) > 0:
        raise HTTPException(status_code=409, detail='Skill already exists')
    skill_data = Skill(
        name=skill_name,
        **skill_data.model_dump(exclude_unset=True)
    )
    db.add(skill_data)
    db.commit()
    db.refresh(skill_data)

    return SkillBase.model_validate(skill_data) if source == 'api' else skill_data
