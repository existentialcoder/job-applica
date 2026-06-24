from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from ..models.job import Job
from ..models.skill import Skill
from ..models.company import Company
from ..models.location import Location
from ..services import skill as skill_service
from ..services.board import get_default_board_id
from ..schemas.skill import SkillCreate
from ..schemas.user import UserBase
from ..schemas.job import JobBase, JobUpdate, JobCreate, JobFilterParams
from ..api.deps.pagination import build_paginated_response, get_paginated_response_model, paginate_query

PaginatedJobs = get_paginated_response_model(JobBase)


def _eager(q):
    return q.options(
        selectinload(Job.required_skills),
        selectinload(Job.company),
        selectinload(Job.location),
    )


async def get_job_with_id(db: AsyncSession, user: UserBase, job_id: int):
    result = await db.execute(_eager(select(Job).where(Job.user_id == user.id, Job.id == job_id)))
    return result.scalar_one_or_none()


async def transform_required_skills(db: AsyncSession, required_skills: list[str]):
    result = []
    for skill in required_skills:
        matched_skills = await skill_service.get_skills(db, None, filter={'name': skill, 'label': skill}, source='internal')
        if len(matched_skills) > 0:
            result.append(matched_skills[0])
        else:
            new_skill = await skill_service.create_skill(db, SkillCreate(name=skill, label=skill), source='internal')
            result.append(new_skill)
    return result


async def get_or_create_company(db: AsyncSession, company_name: str) -> Company:
    result = await db.execute(select(Company).where(Company.name.ilike(company_name)))
    company = result.scalar_one_or_none()
    if not company:
        company = Company(name=company_name)
        db.add(company)
        await db.flush()
    return company


async def get_or_create_location(db: AsyncSession, location_str: str) -> Location:
    parts = [p.strip() for p in location_str.split(',')]
    city = parts[0] if len(parts) > 0 else location_str
    state = parts[1] if len(parts) > 1 else None
    country = parts[2] if len(parts) > 2 else None

    q = select(Location).where(Location.city.ilike(city))
    if state:
        q = q.where(Location.state.ilike(state))

    result = await db.execute(q)
    loc = result.scalar_one_or_none()
    if not loc:
        loc = Location(city=city, state=state or '', country=country or '')
        db.add(loc)
        await db.flush()
    return loc


async def get_jobs(db: AsyncSession, user: UserBase, pagination: dict, filter: JobFilterParams | None = None) -> PaginatedJobs:
    base_q = select(Job).where(Job.user_id == user.id)

    if filter:
        if filter.title:
            base_q = base_q.where(Job.title.ilike(f'%{filter.title}%'))
        if filter.company:
            base_q = base_q.join(Company, Job.company_id == Company.id).where(Company.name.ilike(f'%{filter.company}%'))
        if filter.location:
            base_q = base_q.join(Location, Job.location_id == Location.id).where(
                Location.city.ilike(f'%{filter.location}%') |
                Location.state.ilike(f'%{filter.location}%') |
                Location.country.ilike(f'%{filter.location}%')
            )
        if filter.query:
            base_q = base_q.where(
                Job.title.ilike(f'%{filter.query}%') |
                Job.description.ilike(f'%{filter.query}%')
            )
        if filter.status:
            base_q = base_q.where(Job.status == filter.status)
        if filter.source_platform:
            base_q = base_q.where(Job.source_platform == filter.source_platform)
        if filter.board_id:
            base_q = base_q.where(Job.board_id == filter.board_id)

    count_result = await db.execute(select(func.count()).select_from(base_q.subquery()))
    total = count_result.scalar()

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
        data['board_id'] = await get_default_board_id(db, user.id)

    company_name = data.pop('company_name', None)
    if isinstance(data.get('company_id'), int):
        company_id = data.pop('company_id')
        result = await db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=400, detail='Invalid company_id')
        data['company'] = company
    elif company_name:
        data.pop('company_id', None)
        data['company'] = await get_or_create_company(db, company_name)
    else:
        data.pop('company_id', None)

    location_str = data.pop('location', None)
    if location_str:
        data['location'] = await get_or_create_location(db, location_str)

    if job_in.required_skills and len(job_in.required_skills) > 0:
        data['required_skills'] = await transform_required_skills(db, job_in.required_skills)

    return data


async def create_job(db: AsyncSession, user: UserBase, job_in: JobCreate) -> JobBase:
    job_data = await get_transformed_job(db, job_in, user)
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
