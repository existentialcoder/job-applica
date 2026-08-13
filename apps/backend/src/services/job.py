from urllib.parse import urlparse

import httpx
from fastapi import HTTPException
from pydantic import HttpUrl
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..api.deps.pagination import build_paginated_response, get_paginated_response_model, paginate_query
from ..core.constants import Constants
from ..models.company import Company
from ..models.job import Job
from ..schemas.company import CompanyCreate
from ..schemas.job import JobBase, JobCreate, JobFilterParams, JobUpdate
from ..schemas.skill import SkillCreate
from ..schemas.user import UserBase
from ..services import skill as skill_service
from ..services.board import get_default_board_id
from ..services.company import create_company, get_company_by_id, get_company_by_name

PaginatedJobs = get_paginated_response_model(JobBase)


def _eager(q):
    return q.options(
        selectinload(Job.required_skills),
        selectinload(Job.company),
    )


async def _derive_logo_url(website: str | HttpUrl | None) -> str | None:
    if not website:
        return None
    domain = urlparse(str(website)).netloc.lstrip('www.')
    if not domain:
        return None
    url = Constants.LOGO_URL_TEMPLATE.format(domain=domain)
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.head(url)
            return url if r.status_code == 200 else None
    except Exception:
        return None


async def get_job_with_id(db: AsyncSession, user: UserBase, job_id: int):
    result = await db.execute(_eager(select(Job).where(Job.user_id == user.id, Job.id == job_id)))
    return result.scalar_one_or_none()


async def transform_required_skills(db: AsyncSession, required_skills: list[str]):
    result = []
    seen_ids = set()
    for skill in required_skills:
        matched_skills = await skill_service.get_skills(
            db, None, filter={'name': skill, 'label': skill}, source='internal'
        )
        if len(matched_skills) > 0:
            resolved = matched_skills[0]
        else:
            resolved = await skill_service.create_skill(db, SkillCreate(label=skill), source='internal')
        if resolved.id not in seen_ids:
            seen_ids.add(resolved.id)
            result.append(resolved)
    return result


async def _retrieve_company_in_request(db: AsyncSession, data: dict) -> Company | None:
    if 'company_id' in data and isinstance(data['company_id'], int):
        return await get_company_by_id(db, data['company_id'])

    if 'company_name' in data and isinstance(data['company_name'], str):
        company = await get_company_by_name(db, data['company_name'])
        if not company:
            company = await create_company(db, CompanyCreate(name=data['company_name']))
        return company

    raw = data.get('company')
    if raw:
        company_data = CompanyCreate(**raw) if isinstance(raw, dict) else raw
        company = await get_company_by_name(db, company_data.name)
        if not company:
            if not company_data.logo_url:
                company_data.logo_url = await _derive_logo_url(company_data.website)

            company = await create_company(db, company_data)
        return company

    return None


async def get_jobs(db: AsyncSession, user: UserBase, pagination: dict, filter: JobFilterParams | None = None) -> dict:
    base_q = select(Job).where(Job.user_id == user.id)

    if filter:
        if filter.title:
            base_q = base_q.where(Job.title.ilike(f'%{filter.title}%'))
        if filter.company:
            base_q = base_q.join(Company, Job.company_id == Company.id).where(Company.name.in_(filter.company))
        if filter.city:
            base_q = base_q.where(Job.location['city'].astext.in_(filter.city))
        if filter.state:
            base_q = base_q.where(Job.location['state'].astext.in_(filter.state))
        if filter.country:
            base_q = base_q.where(Job.location['country'].astext.in_(filter.country))
        if filter.position:
            base_q = base_q.where(Job.position.in_(filter.position))
        if filter.query:
            base_q = base_q.where(Job.title.ilike(f'%{filter.query}%') | Job.description.ilike(f'%{filter.query}%'))
        if filter.status:
            base_q = base_q.where(Job.status.in_(filter.status))
        if filter.source_platform:
            base_q = base_q.where(Job.source_platform == filter.source_platform)
        if filter.work_model:
            base_q = base_q.where(Job.work_model.in_(filter.work_model))
        if filter.board_id:
            base_q = base_q.where(Job.board_id.in_(filter.board_id))
        if filter.created_from and filter.created_to:
            base_q = base_q.where(Job.created_at.between(filter.created_from, filter.created_to))
        if filter.applied_from and filter.applied_to:
            base_q = base_q.where(Job.applied_date.between(filter.applied_from, filter.applied_to))
        if filter.ats_score_min is not None:
            base_q = base_q.where(Job.ats_score >= filter.ats_score_min)
        if filter.ats_score_max is not None:
            base_q = base_q.where(Job.ats_score <= filter.ats_score_max)

    count_result = await db.execute(select(func.count()).select_from(base_q.subquery()))
    total = count_result.scalar() or 0

    result = await db.execute(paginate_query(_eager(base_q), pagination))
    jobs = [JobBase.model_validate(job) for job in result.scalars().all()]

    return build_paginated_response(items=jobs, total=total, **pagination)


async def get_job(db: AsyncSession, user: UserBase, job_id: int) -> JobBase | None:
    db_job = await get_job_with_id(db, user, job_id)
    if db_job:
        return JobBase.model_validate(db_job)
    return None


async def delete_job(db: AsyncSession, user: UserBase, job_id: int) -> bool:
    db_job = await get_job_with_id(db, user, job_id)
    if not db_job:
        return False
    await db.delete(db_job)
    await db.commit()
    return True


async def get_transformed_job(db: AsyncSession, job_in: JobCreate | JobUpdate, user: UserBase) -> dict:
    data = job_in.model_dump(exclude_unset=True)
    data['user_id'] = user.id

    if 'board_id' not in data and isinstance(job_in, JobCreate):
        assert user.id is not None
        data['board_id'] = await get_default_board_id(db, user.id)

    if isinstance(data.get('company_name'), str) and not data['company_name'].strip():
        data.pop('company_name', None)

    if 'company_id' in data or 'company_name' in data or 'company' in data:
        data['company'] = await _retrieve_company_in_request(db, data)
    data.pop('company_id', None)
    data.pop('company_name', None)

    if job_in.required_skills and len(job_in.required_skills) > 0:
        data['required_skills'] = await transform_required_skills(db, job_in.required_skills)

    return data


async def create_job(db: AsyncSession, user: UserBase, job_in: JobCreate) -> JobBase:
    job_data = await get_transformed_job(db, job_in, user)
    if not job_data.get('company'):
        raise HTTPException(status_code=400, detail='Company is required')
    db_job = Job(**job_data)
    db.add(db_job)
    await db.commit()
    result = await db.execute(_eager(select(Job).where(Job.id == db_job.id)))
    return JobBase.model_validate(result.scalar_one())


async def update_job(db: AsyncSession, job_id: int, user: UserBase, job_in: JobUpdate) -> JobBase | None:
    db_job = await get_job_with_id(db, user, job_id)
    if not db_job:
        return None

    job_data = await get_transformed_job(db, job_in, user)
    for key, value in job_data.items():
        setattr(db_job, key, value)

    await db.commit()
    result = await db.execute(_eager(select(Job).where(Job.id == db_job.id)))
    return JobBase.model_validate(result.scalar_one())
