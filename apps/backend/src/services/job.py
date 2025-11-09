from typing import Type
from sqlalchemy.orm import Session
from ..models.job import Job
from ..models.skill import Skill
from ..models.company import Company
from ..schemas.job import JobBase, JobUpdate, JobCreate, JobFilterParams
from ..api.deps.pagination import build_paginated_response, get_paginated_response_model, paginate_query

PaginatedJobs = get_paginated_response_model(JobBase)

def get_jobs(db: Session, pagination: dict, filter: JobFilterParams | None = None) -> PaginatedJobs:
    q = db.query(Job)

    if filter.title:
        q = q.filter(Job.title.ilike(f'%{filter.title}%'))
    if filter.company:
        q = q.filter(Job.company.ilike(f'%{filter.company}%'))
    if filter.location:
        q = q.filter(Job.location.ilike(f'%{filter.location}%'))
    if filter.query:
        q = q.filter(
            Job.title.ilike(f'%{filter.query}%') |
            Job.description.ilike(f'%{filter.query}%')
        )


    total = q.count()
    q = paginate_query(q, pagination)

    results = q.all()

    jobs = [JobBase.model_validate(job) for job in results]

    return build_paginated_response(
        items=jobs,
        total=total,
        **pagination
    )

def get_job(db: Session, job_id: int) -> JobBase | None:
    db_job = db.query(Job).get(job_id)
    if db_job:
        return JobBase.model_validate(db_job)
    return None

def delete_job(db: Session, job_id: int) -> bool:
    db_job = db.query(Job).get(job_id)
    if not db_job:
        return False
    db.delete(db_job)
    db.commit()
    return True

def get_tranformed_job(db: Session, job_in: JobCreate | JobUpdate) -> dict:
    data = job_in.model_dump(exclude_unset=True)

    # Replace skill IDs with actual Skill objects
    if job_in.required_skills_ids:
        data['required_skills'] = db.query(Skill).filter(Skill.id.in_(job_in.required_skills_ids)).all()
        data.pop('required_skills_ids', None)

    # Replace company_id with actual Company object
    if job_in.company_id:
        company = db.query(Company).get(job_in.company_id)
        if company:
            data['company'] = company
            del data['company_id']

    return data


def create_job(db: Session, job_in: JobCreate) -> JobBase:
    job_data = get_tranformed_job(db, job_in)

    db_job = Job(**job_data)

    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    return JobBase.model_validate(db_job)


def update_job(db: Session, job_id: int, job_in: JobUpdate) -> JobBase | None:
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        return None

    job_data = get_tranformed_job(db, job_in)

    for key, value in job_data.items():
        setattr(db_job, key, value)

    db.commit()
    db.refresh(db_job)
    return JobBase.model_validate(db_job)
