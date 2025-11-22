from sqlalchemy.orm import Session
from pydantic import HttpUrl
from fastapi import HTTPException

from ..models.skill import Skill
from ..schemas.skill import SkillBase, SkillCreate
from ..api.deps.pagination import build_paginated_response, get_paginated_response_model, paginate_query

PaginatedSkills = get_paginated_response_model(SkillBase)

def get_skills(db: Session, pagination: dict) -> PaginatedSkills:
    q = db.query(Skill)

    total = q.count()
    q = paginate_query(q, pagination)

    results = q.all()

    skills = [SkillBase.model_validate(skill) for skill in results]

    return build_paginated_response(
        items=skills,
        total=total,
        **pagination
    )


def create_skill(db: Session, skill_data: SkillCreate) -> SkillBase:
    existing_skills_with_name = db.query(Skill).filter(Skill.name == skill_data.name).all()
    if len(existing_skills_with_name) > 0:
        raise HTTPException(status_code=409, detail='Skill already exists')
    skill_data = Skill(
        **skill_data.model_dump(exclude_unset=True)
    )

    if isinstance(skill_data.website, HttpUrl):
        skill_data.website = str(skill_data.website)
    db.add(skill_data)
    db.commit()
    db.refresh(skill_data)

    return SkillBase.model_validate(skill_data)
