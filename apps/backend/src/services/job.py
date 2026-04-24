from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.job import Job
from ..models.skill import Skill
from ..models.company import Company
from ..models.location import Location
from ..services import skill as skill_service
from ..schemas.skill import SkillCreate
from ..schemas.user import UserBase
from ..schemas.job import JobBase, JobUpdate, JobCreate, JobFilterParams
from ..api.deps.pagination import build_paginated_response, get_paginated_response_model, paginate_query

PaginatedJobs = get_paginated_response_model(JobBase)


def get_job_with_id(db: Session, user: UserBase, job_id: int):
    return db.query(Job).filter(Job.user_id == user.id, Job.id == job_id).first()


def transform_required_skills(db: Session, required_skills: list[str]):
    result = []
    for skill in required_skills:
        matched_skills = skill_service.get_skills(db, None, filter={'name': skill, 'label': skill}, source='internal')
        if len(matched_skills) > 0:
            result.append(matched_skills[0])
        else:
            new_skill = skill_service.create_skill(db, SkillCreate(name=skill, label=skill), source='internal')
            result.append(new_skill)
    return result


def get_or_create_company(db: Session, company_name: str) -> Company:
    company = db.query(Company).filter(Company.name.ilike(company_name)).first()
    if not company:
        company = Company(name=company_name)
        db.add(company)
        db.flush()
    return company


def get_or_create_location(db: Session, location_str: str) -> Location:
    parts = [p.strip() for p in location_str.split(',')]
    city = parts[0] if len(parts) > 0 else location_str
    state = parts[1] if len(parts) > 1 else None
    country = parts[2] if len(parts) > 2 else None

    q = db.query(Location).filter(Location.city.ilike(city))
    if state:
        q = q.filter(Location.state.ilike(state))
    loc = q.first()
    if not loc:
        loc = Location(city=city, state=state or '', country=country or '')
        db.add(loc)
        db.flush()
    return loc


def get_jobs(db: Session, user: UserBase, pagination: dict, filter: JobFilterParams | None = None) -> PaginatedJobs:
    q = db.query(Job).filter(Job.user_id == user.id)

    if filter:
        if filter.title:
            q = q.filter(Job.title.ilike(f'%{filter.title}%'))
        if filter.company:
            q = q.join(Company, Job.company_id == Company.id).filter(Company.name.ilike(f'%{filter.company}%'))
        if filter.location:
            q = q.join(Location, Job.location_id == Location.id).filter(
                Location.city.ilike(f'%{filter.location}%') |
                Location.state.ilike(f'%{filter.location}%') |
                Location.country.ilike(f'%{filter.location}%')
            )
        if filter.query:
            q = q.filter(
                Job.title.ilike(f'%{filter.query}%') |
                Job.description.ilike(f'%{filter.query}%')
            )
        if filter.status:
            q = q.filter(Job.status == filter.status)
        if filter.source_platform:
            q = q.filter(Job.source_platform == filter.source_platform)

    total = q.count()
    q = paginate_query(q, pagination)
    results = q.all()
    jobs = [JobBase.model_validate(job) for job in results]

    return build_paginated_response(items=jobs, total=total, **pagination)


def get_job(db: Session, user: UserBase, job_id: int) -> JobBase | None:
    db_job = get_job_with_id(db, user, job_id)
    if db_job:
        return JobBase.model_validate(db_job)
    return None


def delete_job(db: Session, user: UserBase, job_id: int) -> bool:
    db_job = get_job_with_id(db, user, job_id)
    if not db_job:
        return False
    db.delete(db_job)
    db.commit()
    return True


def get_transformed_job(db: Session, job_in: JobCreate | JobUpdate, user: UserBase) -> dict:
    data = job_in.model_dump(exclude_unset=True)
    data['user_id'] = user.id

    # Handle company: prefer company_id, fall back to company_name string
    company_name = data.pop('company_name', None)
    if isinstance(data.get('company_id'), int):
        company = db.query(Company).get(data.pop('company_id'))
        if not company:
            raise HTTPException(status_code=400, detail='Invalid company_id')
        data['company'] = company
    elif company_name:
        data.pop('company_id', None)
        data['company'] = get_or_create_company(db, company_name)
    else:
        data.pop('company_id', None)

    # Handle location string → Location model
    location_str = data.pop('location', None)
    if location_str:
        data['location'] = get_or_create_location(db, location_str)

    # Replace skill names with Skill objects
    if job_in.required_skills and len(job_in.required_skills) > 0:
        data['required_skills'] = transform_required_skills(db, job_in.required_skills)

    return data


def create_job(db: Session, user: UserBase, job_in: JobCreate) -> JobBase:
    job_data = get_transformed_job(db, job_in, user)
    db_job = Job(**job_data)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return JobBase.model_validate(db_job)


def update_job(db: Session, job_id: int, user: UserBase, job_in: JobUpdate) -> JobBase | None:
    db_job = get_job_with_id(db, user, job_id)
    if not db_job:
        return None

    job_data = get_transformed_job(db, job_in, user)
    for key, value in job_data.items():
        setattr(db_job, key, value)

    db.commit()
    db.refresh(db_job)
    return JobBase.model_validate(db_job)
