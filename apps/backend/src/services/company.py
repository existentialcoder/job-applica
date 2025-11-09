from sqlalchemy.orm import Session
from pydantic import HttpUrl
from fastapi import HTTPException
from ..models.company import Company
from ..schemas.company import CompanyBase, CompanyCreate, CompanyUpdate
from ..api.deps.pagination import build_paginated_response, get_paginated_response_model, paginate_query

PaginatedCompanies = get_paginated_response_model(CompanyBase)

def get_companies(db: Session, pagination: dict) -> PaginatedCompanies:
    q = db.query(Company)

    total = q.count()
    q = paginate_query(q, pagination)

    results = q.all()

    companies = [CompanyBase.model_validate(company) for company in results]

    return build_paginated_response(
        items=companies,
        total=total,
        **pagination
    )

# def get_job(db: Session, job_id: int) -> JobBase | None:
#     db_job = db.query(Job).get(job_id)
#     if db_job:
#         return JobBase.model_validate(db_job)
#     return None

# def delete_job(db: Session, job_id: int) -> bool:
#     db_job = db.query(Job).get(job_id)
#     if not db_job:
#         return False
#     db.delete(db_job)
#     db.commit()
#     return True

# def get_tranformed_job(db: Session, job_in: JobCreate | JobUpdate) -> dict:
#     data = job_in.model_dump(exclude_unset=True)

#     # Replace skill IDs with actual Skill objects
#     if job_in.required_skills_ids:
#         data['required_skills'] = db.query(Skill).filter(Skill.id.in_(job_in.required_skills_ids)).all()
#         data.pop('required_skills_ids', None)

#     # Replace company_id with actual Company object
#     if job_in.company_id:
#         company = db.query(Company).get(job_in.company_id)
#         if company:
#             data['company'] = company

#     return data


def create_company(db: Session, company_data: CompanyCreate) -> CompanyBase:
    existing_companies_with_name = db.query(Company).filter(Company.name == company_data.name).all()
    if len(existing_companies_with_name) > 0:
        raise HTTPException(status_code=409, detail='Company already exists')
    company_data = Company(
        **company_data.model_dump(exclude_unset=True)
    )

    if isinstance(company_data.website, HttpUrl):
        company_data.website = str(company_data.website)

    db.add(company_data)
    db.commit()
    db.refresh(company_data)

    return CompanyBase.model_validate(company_data)


# def update_job(db: Session, job_id: int, job_in: JobUpdate) -> JobBase | None:
#     db_job = db.query(Job).filter(Job.id == job_id).first()
#     if not db_job:
#         return None

#     job_data = get_tranformed_job(db, job_in)

#     for key, value in job_data.items():
#         setattr(db_job, key, value)

#     db.commit()
#     db.refresh(db_job)
#     return JobBase.model_validate(db_job)
