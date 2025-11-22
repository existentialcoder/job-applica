from sqlalchemy.orm import Session
from pydantic import HttpUrl
from fastapi import HTTPException
from ..models.company import Company
from ..schemas.company import CompanyBase, CompanyCreate
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
